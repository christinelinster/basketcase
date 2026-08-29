from datetime import datetime
import logging
from typing import Any
from uuid import UUID

import asyncpg
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
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
    id: int
    method: str
    path: str
    headers: dict[str, Any]
    query_params: dict[str, Any]
    body: str | None
    received_at: datetime


class BasketDetailResponse(BaseModel):
    name: str
    capacity: int
    expires_at: datetime
    requests: list[BasketRequestResponse]


def not_implemented() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={"detail": "Not implemented"},
    )


@router.get("/baskets/hello")
async def hello() -> dict[str, str]:
    return {"message": "hello world"}


# This is handled in the frontend local storage.

# @router.get("/baskets")
# async def list_baskets() -> JSONResponse:
#     return not_implemented()


@router.post(
    "/baskets",
    response_model=BasketResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_basket(
    basket: CreateBasketRequest,
    request: Request,
) -> BasketResponse:
    if postgres.pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )

    try:
        async with postgres.pool.acquire() as connection:
            created_basket = await connection.fetchrow(
                """
                INSERT INTO baskets (name)
                VALUES ($1)
                RETURNING id, name, token, capacity expires_at
                """,
                basket.name,
            )
    except asyncpg.UniqueViolationError as error:
        if error.constraint_name == "baskets_name_key":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Failed to create basket - {basket.name} already exists.",
            ) from error

        logger.exception("Unexpected uniqueness violation while creating basket")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from error
    except Exception as error:
        logger.exception("Unexpected error while creating basket")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from error

    if created_basket is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Basket could not be created",
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
async def delete_basket(name: str) -> JSONResponse:
    return not_implemented()


@router.delete("/baskets/{name}/requests")
async def delete_requests(name: str) -> JSONResponse:
    return not_implemented()


@router.get("/baskets/{name}/requests/{request_id}")
async def get_request(name: str, request_id: str) -> JSONResponse:
    return not_implemented()


@router.delete("/baskets/{name}/requests/{request_id}")
async def delete_request(name: str, request_id: str) -> JSONResponse:
    return not_implemented()
