from datetime import datetime
import logging
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Request, Response, status
from pydantic import BaseModel, Field, field_validator

from db import postgres


router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)

class CreateBasketRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50, pattern=r"^[A-Za-z0-9]+$")

    @field_validator("name")
    @classmethod
    def reject_reserved_name(cls, name: str) -> str:
        if name.casefold() == "baskets":
            raise ValueError("The name 'baskets' is reserved")
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


@router.get("/baskets/hello")
async def hello() -> dict[str, str]:
    return {"message": "hello world"}

@router.post(
    "/baskets",
    response_model=BasketResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_basket(
    basket: CreateBasketRequest,
    request: Request,
) -> BasketResponse:
    pool = postgres.pool
    if pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )

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
async def get_basket(name: str) -> BasketDetailResponse:
    if postgres.pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )

    async with postgres.pool.acquire() as connection:
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
async def delete_basket(name: str, x_basket_token: str | None = Header(None, alias="X-Basket-Token")) -> Response:
    """Delete a basket by name and token, and associated requests via cascade."""
    try:
        token = UUID(x_basket_token)
    except (ValueError, TypeError):
        raise HTTPException(status_code=404, detail="Basket not found")

    async with postgres.pool.acquire() as connection:
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

    return Response(status_code=204)


@router.delete('/baskets/{name}/requests/{request_id:uuid}', status_code=204)
async def delete_request(name: str, request_id: UUID, x_basket_token: str | None = Header(None, alias="X-Basket-Token")):
    """Delete one specific request from a basket by request ID."""

    try:
        token = UUID(x_basket_token)
    except (ValueError, TypeError):
        raise HTTPException(status_code=404, detail="Request not found")


    async with postgres.pool.acquire() as connection:
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

    return Response(status_code=204)


@router.delete('/baskets/{name}/requests', status_code=204)
async def delete_all_requests(name: str, x_basket_token: str | None = Header(None, alias="X-Basket-Token")):
    """Delete every request inside a basket without deleting the basket itself."""
    try:
        token = UUID(x_basket_token)
    except (ValueError, TypeError):
        raise HTTPException(status_code=404, detail="Basket not found")

    async with postgres.pool.acquire() as connection:
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

    return Response(status_code=204)
