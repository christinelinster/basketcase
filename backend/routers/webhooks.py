from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse

from uuid6    import uuid7
from datetime import datetime, timezone
import logging
import re

from routers.route_config import get_route_config

from db import mongo
from routers.live import broadcast_refresh
from db.dependencies import PostgresPool

router = APIRouter()
logger = logging.getLogger(__name__)

WEBHOOK_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "HEAD",
    "OPTIONS",
    "TRACE",
]


BASKET_NAME_PATTERN = re.compile(r"^[A-Za-z0-9]{1,50}$")

# Catch all requests to /{possibly_nested_path}:
@router.api_route("/{full_path:path}", methods=WEBHOOK_METHODS, response_model=None)
async def dispatch_request(
    full_path: str,
    request: Request,
    pool: PostgresPool
) -> dict[str, str] | FileResponse:
    name = full_path.split('/', 1)[0]

    if name == "" or name.casefold() in get_route_config().reserved_names:
        return serve_frontend()
    elif not BASKET_NAME_PATTERN.match(name):
        raise HTTPException(status_code=404, detail="Page not found")
    else:
        return await receive_request(name, request, pool)


# Serve frontend SPA if a reserved path (ie. / or /baskets) is requested.
def serve_frontend():
    return FileResponse(get_route_config().frontend_dir / "index.html")


# Capture requests to /{basketname}
async def receive_request(
    name: str,
    request: Request,
    pool: PostgresPool,
) -> dict[str, str]:

    # If the basket name is valid, check if it exists
    async with pool.acquire() as pg_connection:
        basket = await pg_connection.fetchrow(
            "SELECT id FROM baskets WHERE name = $1", name
        )

        if basket is None:
            raise HTTPException(status_code=404, detail="Page not found")

    # UUID7 for request_id for built-in timestamping
    request_id = uuid7()


    # Insert the raw request body into Mongo:
    received_at = datetime.now(timezone.utc)
    body = await request.body()

    request_document = { 
        "_id": request_id,
        "basket_id": basket["id"],
        "received_at": received_at,
        "body": body
    }

    raw_requests_collection = mongo.get_database()["raw_requests"]
    await raw_requests_collection.insert_one(request_document)


    # Insert the parsed request into Postgres:
    basket_id = basket["id"]
    try:
        async with pool.acquire() as pg_connection:
            await pg_connection.execute(
                """
                INSERT INTO requests
                (id, basket_id, method, path, headers, query_params, body, received_at)
                VALUES ($1, $2, $3, $4, $5::jsonb, $6::jsonb, $7, $8)
                """,
                request_id, basket_id, request.method, request.url.path, 

                dict(request.headers),
                dict(request.query_params),

                body.decode("utf-8", errors="replace"), # Convert the request body (bytes) to string
                received_at
            )
    except Exception as error:
        logger.exception("Failed to insert parsed request into Postgres")
        raise HTTPException(status_code=500, detail="Internal server error") from error

    # Tell anyone viewing this basket to reload. Deliberately outside the
    # acquire() block above: this awaits network sends to browsers, and holding a
    # pooled database connection while doing so would tie up the pool. It also
    # has to run after the insert commits, since the signal tells the browser to
    # go and read what was just written.
    await broadcast_refresh(name)

    return { "status": "received" }

