from datetime import datetime
import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel, Field, field_validator

from routers.route_config import get_route_config

from db import mongo
from db.dependencies import BasketToken, PostgresPool


router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)

class CreateBasketRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50, pattern=r"^[A-Za-z0-9]+$")

    @field_validator("name")
    @classmethod
    def reject_reserved_name(cls, name: str) -> str:
        if name.casefold() in get_route_config().reserved_names:
            raise ValueError(f"The name '{name}' is reserved.")
        return name


class BasketResponse(BaseModel):
    name: str
    webhook_url: str
    token: UUID
    expires_at: datetime


class BasketRequestResponse(BaseModel):
    id: UUID
    method: str
    path: str
    headers: dict[str, str | list[str]]
    query_params: dict[str, str | list[str]]
    body: str | None
    received_at: datetime


class BasketDetailResponse(BaseModel):
    name: str
    capacity: int
    expires_at: datetime
    requests: list[BasketRequestResponse]


@router.post(
    "/baskets",
    response_model=BasketResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_basket(
    basket: CreateBasketRequest,
    request: Request,
    pool: PostgresPool,
) -> BasketResponse:
    try:
        async with pool.acquire() as connection:
            created_basket = await connection.fetchrow(
                """
                INSERT INTO baskets (name)
                VALUES ($1)
                ON CONFLICT (name) DO NOTHING
                RETURNING name, token, expires_at
                """,
                basket.name,
            )
    except Exception as error:
        logger.exception("Unexpected error while creating basket")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from error

    if created_basket is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Failed to create basket - {basket.name} already exists.",
        )

    webhook_url = f"{str(request.base_url).rstrip('/')}/{created_basket['name']}"
    return BasketResponse(
        name=created_basket["name"],
        webhook_url=webhook_url,
        token=created_basket["token"],
        expires_at=created_basket["expires_at"],
    )


@router.get("/baskets/{name}", response_model=BasketDetailResponse)
async def get_basket(name: str, pool: PostgresPool) -> BasketDetailResponse:
    async with pool.acquire() as connection:
        basket = await connection.fetchrow(
            """
            SELECT id, name, capacity, expires_at
            FROM baskets
            WHERE name = $1
            """,
            name,
        )
        if basket is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Basket not found",
            )

        requests = await connection.fetch(
            """
            SELECT id, method, path, headers, query_params, body, received_at
            FROM requests
            WHERE basket_id = $1
            ORDER BY received_at DESC, id DESC
            """,
            basket["id"],
        )


    return BasketDetailResponse(
        name=basket["name"],
        capacity=basket["capacity"],
        expires_at=basket["expires_at"],
        requests=[
            BasketRequestResponse(
                id=request["id"],
                method=request["method"],
                path=request["path"],
                headers=request["headers"],
                query_params=request["query_params"],
                body=request["body"],
                received_at=request["received_at"],
            )
            for request in requests
        ],
    )


@router.delete("/baskets/{name}")
async def delete_basket(
    name: str,
    token: BasketToken,
    pool: PostgresPool,
) -> Response:
    """Delete the specified basket. Associated requests are deleted via cascade."""

    # Delete the basket from Postgres:
    async with pool.acquire() as connection:
        deleted = await connection.fetchrow(
            """
            DELETE FROM baskets
            WHERE name = $1 AND token = $2
            RETURNING id
            """,
            name,
            token
        )
    if deleted is None:
        raise HTTPException(status_code=404, detail="Basket not found")

    # Delete all associated requests from Mongo:
    raw_requests_collection = mongo.get_database()["raw_requests"]
    await raw_requests_collection.delete_many({"basket_id": deleted["id"]})

    return Response(status_code=204)


@router.delete('/baskets/{name}/requests/{request_id:uuid}', status_code=204)
async def delete_request(
    name: str,
    request_id: UUID,
    token: BasketToken,
    pool: PostgresPool,
):
    """Delete one specific request from a basket by request ID."""

    # Delete the request from Postgres:
    async with pool.acquire() as connection:
        basket = await connection.fetchrow(
            """
            SELECT id
            FROM baskets
            WHERE name = $1 AND token = $2
            """,
            name,
            token
        )
        if basket is None:
            raise HTTPException(status_code=404, detail="Request not found")

        # Ensure that DELETE can only remove a request in the identifying token's basket.
        deleted = await connection.fetchrow(
            """
            DELETE FROM requests
            WHERE id = $1 AND basket_id = $2
            RETURNING id
            """,
            request_id,
            basket["id"]
        )
    if deleted is None:
        raise HTTPException(status_code=404, detail="Request not found")

    # Delete the request from Mongo:
    raw_requests_collection = mongo.get_database()["raw_requests"]
    await raw_requests_collection.delete_one({"_id": deleted["id"]})

    return Response(status_code=204)


@router.delete('/baskets/{name}/requests', status_code=204)
async def delete_all_requests(
    name: str,
    token: BasketToken,
    pool: PostgresPool,
):
    """Delete every request inside a basket without deleting the basket itself."""

    # Delete requests from Postgres:
    async with pool.acquire() as connection:
        basket = await connection.fetchrow(
            """
            SELECT id
            FROM baskets
            WHERE name = $1 AND token = $2
            """,
            name,
            token
        )
        if basket is None:
            raise HTTPException(status_code=404, detail="Basket not found")

        await connection.execute(
            """
            DELETE FROM requests
            WHERE basket_id = $1
            """,
            basket["id"]
        )

    # Delete all associated requests from Mongo:
    raw_requests_collection = mongo.get_database()["raw_requests"]
    await raw_requests_collection.delete_many({"basket_id": basket["id"]})

    return Response(status_code=204)
