from typing import Annotated
from uuid import UUID

import asyncpg
from fastapi import Depends, Header, HTTPException, status

from db import postgres


def get_postgres_pool() -> asyncpg.Pool:
    pool = postgres.pool
    if pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )
    return pool


def get_basket_token(
    token: Annotated[str | None, Header(alias="X-Basket-Token")] = None,
) -> UUID:
    try:
        return UUID(token)
    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        ) from error


PostgresPool = Annotated[asyncpg.Pool, Depends(get_postgres_pool)]
BasketToken = Annotated[UUID, Depends(get_basket_token)]
