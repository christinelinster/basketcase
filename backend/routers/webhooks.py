from fastapi import APIRouter, Request

from uuid6 import uuid7
from datetime import datetime, timezone

from db import postgres
from db import mongo

router = APIRouter()

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

# {name:path} matches both /name and /name/with/path
@router.api_route("/{name:path}", methods=WEBHOOK_METHODS)
async def receive_request(name: str, request: Request) -> dict[str, str]:
    # UUID7 > UUID4 for request_id because UUID7 includes a built-in timestamp
    # which allows for chronological ordering -> better performance.
    request_id = uuid7()

    raw_request = {
        "request_id": request_id,
        "basket_name": name,
        "method": request.method,
        "path": request.url.path,
        "query_string": request.url.query,
        "headers": [
            [header_name.decode("latin-1"), header_value.decode("latin-1")]
            for header_name, header_value in request.headers.raw
        ],
        "body": await request.body(),
        "received_at": datetime.now(timezone.utc),
    }

    collection = mongo.get_database()["raw_requests"]
    await collection.insert_one(raw_request)

    return {"status": "received"}
