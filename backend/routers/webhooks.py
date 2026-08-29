from fastapi import APIRouter, Request

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


@router.api_route("/{name}", methods=WEBHOOK_METHODS)
async def receive_request(name: str, request: Request) -> dict[str, str]:
    return {"status": "received"}
