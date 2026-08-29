from dotenv import load_dotenv
load_dotenv()

import uuid

from contextlib  import asynccontextmanager
from fastapi     import APIRouter, Header, Response
from fastapi.responses import JSONResponse
from db.mongo    import db as mongo_db
from db          import postgres


router = APIRouter(prefix='/api')

@router.post('/baskets')
async def create_basket():
    async with postgres.pool.acquire() as connection:
        await connection.execute(
            "INSERT INTO baskets (name) VALUES ($1)",
            'test name'
        )
    pass

@router.get('/baskets')
async def get_baskets():
    return 'hello'
    # landing page for user, view all baskets 
    # -> frontend sends tokens from localstorage
    pass

@router.get('/baskets/{name}')
async def get_basket(name: str):
    pass


# ---------------------------------------------------------------------------
# Delete routes
#
# All three require the caller to prove they own the basket by sending the
# basket's token in an X-Basket-Token header. The frontend stores that token
# in localStorage when the basket is created.
#
# Every failure returns 404 with the same message, whether the basket name
# doesn't exist, the token is wrong, or the header is missing. That is
# deliberate: basket names are random slugs so they can't be guessed, and
# giving a different response for "real name, wrong token" would tell someone
# probing names which ones are real.
# ---------------------------------------------------------------------------

@router.delete('/baskets/{name}', status_code=204)
async def delete_basket(name: str, x_basket_token: str | None = Header(None, alias="X-Basket-Token")):
    """
    Delete a basket, and with it every request the basket holds.

    We don't delete the requests ourselves — requests.basket_id is declared
    ON DELETE CASCADE in schema.sql, so Postgres removes them automatically
    when the basket row goes away.
    """

    # The token column is a uuid, so turn the header into a UUID object before
    # querying. This also normalizes formatting: a client that sends its token
    # uppercase or without hyphens still matches. Anything that isn't a valid
    # uuid — including a missing header, which arrives as None — can't possibly
    # match a real token, so we stop here rather than hitting the database.
    try:
        token = uuid.UUID(x_basket_token)
    except (ValueError, TypeError):
        return JSONResponse(status_code=404, content={"error": "Basket not found"})

    async with postgres.pool.acquire() as connection:
        # One statement does both jobs: it only deletes when the name AND the
        # token match, so there's no gap between checking the token and acting
        # on it. RETURNING id gives us a row back when something was actually
        # deleted, and nothing when it wasn't.
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


@router.delete('/baskets/{name}/requests', status_code=204)
async def delete_all_requests(name: str, x_basket_token: str | None = Header(None, alias="X-Basket-Token")):
    """
    Delete every request inside a basket, leaving the basket itself alive.

    Emptying a basket that already has no requests is still a success (204) —
    the end state the caller asked for is what they get.
    """

    try:
        token = uuid.UUID(x_basket_token)
    except (ValueError, TypeError):
        return JSONResponse(status_code=404, content={"error": "Basket not found"})

    async with postgres.pool.acquire() as connection:
        # Here we do need two statements, because "basket doesn't exist" (404)
        # and "basket exists but is already empty" (204) are different answers
        # and a single DELETE can't tell them apart. Both run on the same
        # connection so they see a consistent view of the database.
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


# The {request_id:int} converter is doing real work here: it tells the router
# to only match this route when the last segment is digits. Without it, the
# route above (/baskets/{name}/requests) could be shadowed depending on which
# one is declared first, because a bare {request_id} matches the literal word
# "requests" too. The converter makes the two routes independent of order.
@router.delete('/baskets/{name}/{request_id:int}', status_code=204)
async def delete_request(name: str, request_id: int, x_basket_token: str | None = Header(None, alias="X-Basket-Token")):
    """
    Delete one specific request from a basket.
    """

    try:
        token = uuid.UUID(x_basket_token)
    except (ValueError, TypeError):
        return JSONResponse(status_code=404, content={"error": "Request not found"})

    # requests.id is a plain Postgres int (4 bytes), so the largest value it can
    # hold is 2147483647. A bigger number than that isn't a valid id and would
    # make the database driver raise an error, so treat it as "not found".
    if request_id > 2147483647:
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

        # basket_id in the WHERE clause matters: it stops a valid token for one
        # basket from deleting a request that belongs to a different basket.
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
