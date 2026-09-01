import json
import logging

from fastapi import APIRouter, Request, HTTPException

from uuid6 import uuid7
from datetime import datetime, timezone

from db import postgres
from db import mongo

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


@router.api_route("/{name}", methods=WEBHOOK_METHODS)
async def receive_request(name: str, request: Request) -> dict[str, str]:
    if postgres.pool is None:
          raise HTTPException(503, "PostgreSQL unavailable")

    # Check if the basket exists
    name = name.split('/')[0]
    async with postgres.pool.acquire() as pg_connection:
        basket = await pg_connection.fetchrow(
            "SELECT id FROM baskets WHERE name = $1", name
        )

        if basket is None:
            raise HTTPException(status_code=404, detail="Page not found")


    # UUID7 > UUID4 for request_id;
    # UUID7 includes a built-in timestamp for chronological sorting.
    request_id = uuid7()

    # Insert the request body into Mongo:
    received_at = datetime.now(timezone.utc)
    body = await request.body() # Read the body as a stream of raw bytes

    request_document = {
        "_id":   request_id,
        "received_at":  received_at,
        "body": body
    }

    raw_requests_collection = mongo.get_database()["raw_requests"]
    await raw_requests_collection.insert_one(request_document)


    # Insert into Postgres:
    basket_id = basket["id"]
    try:
        async with postgres.pool.acquire() as pg_connection:
            await pg_connection.execute(
                """
                INSERT INTO requests
                (id, basket_id, method, path, headers, query_params, body, received_at)
                VALUES ($1, $2, $3, $4, $5::jsonb, $6::jsonb, $7, $8)
                """,
                request_id, basket_id, request.method, request.url.path, 

                json.dumps(dict(request.headers)),      # Convert headers and 
                json.dumps(dict(request.query_params)), # query params to JSON.

                body.decode("utf-8", errors="replace"), # Convert the request body (bytes) to string
                received_at
            )
    except Exception as error:
        logger.exception("Failed to insert parsed request into Postgres")
        raise HTTPException(status_code=500, detail="Internal server error") from error

    
    return { "status": "received" }
