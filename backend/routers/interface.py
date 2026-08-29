from fastapi           import APIRouter, status, Response, Header
from fastapi.responses import JSONResponse
from db                import postgres, mongo
import uuid

router = APIRouter(prefix="/api")


def not_implemented() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={"detail": "Not implemented"},
    )


@router.get("/baskets/hello")
async def hello() -> dict[str, str]:
    return {"message": "hello world"}


@router.get("/baskets")
async def list_baskets() -> JSONResponse:
    return not_implemented()


@router.post("/baskets")
async def create_basket() -> JSONResponse:
    return not_implemented()


@router.get("/baskets/{name}")
async def get_basket(name: str) -> JSONResponse:
    return not_implemented()


@router.get("/baskets/{name}/requests")
async def list_requests(name: str) -> JSONResponse:
    return not_implemented()


@router.get("/baskets/{name}/requests/{request_id}")
async def get_request(name: str, request_id: str) -> JSONResponse:
    return not_implemented()


# ---------------------------------------------------------------------------
# Delete Routes
# - X-Basket-Token represents the per-basket token used for authentication,
#   from localStorage.
# - All failures return 404 with identical messages to obscure basket existence
#   from bad actors.
# ---------------------------------------------------------------------------

@router.delete("/baskets/{name}")
async def delete_basket(name: str, x_basket_token: str | None = Header(None, alias="X-Basket-Token")) -> JSONResponse:
    """Delete a basket by name and token, and associated requests via cascade."""
    try:
        token = uuid.UUID(x_basket_token)
    except (ValueError, TypeError):
        return JSONResponse(status_code=404, content={"error": "Basket not found"})

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
        return JSONResponse(status_code=404, content={"error": "Basket not found"})

    return Response(status_code=204)


@router.delete('/baskets/{name}/requests/{request_id:int}', status_code=204)
async def delete_request(name: str, request_id: int, x_basket_token: str | None = Header(None, alias="X-Basket-Token")):
    """Delete one specific request from a basket by request ID."""

    try:
        token = uuid.UUID(x_basket_token)
    except (ValueError, TypeError):
        return JSONResponse(status_code=404, content={"error": "Request not found"})

    MAX_POSTGRES_INT = 2147483647
    if request_id > MAX_POSTGRES_INT:
        return JSONResponse(status_code=404, content={"error": "Request not found"})

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
            return JSONResponse(status_code=404, content={"error": "Request not found"})

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
        return JSONResponse(status_code=404, content={"error": "Request not found"})

    return Response(status_code=204)


@router.delete('/baskets/{name}/requests', status_code=204)
async def delete_all_requests(name: str, x_basket_token: str | None = Header(None, alias="X-Basket-Token")):
    """Delete every request inside a basket without deleting the basket itself."""
    try:
        token = uuid.UUID(x_basket_token)
    except (ValueError, TypeError):
        return JSONResponse(status_code=404, content={"error": "Basket not found"})

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
            return JSONResponse(status_code=404, content={"error": "Basket not found"})

        await connection.execute(
            """
            DELETE FROM requests
            WHERE basket_id = $1
            """,
            basket["id"]
        )

    return Response(status_code=204)
