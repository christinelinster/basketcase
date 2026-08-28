from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

async def rate_limit_handler(
    request: Request,
    exc: RateLimitExceeded
):
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "error": "rate_limited",
            "message": "Too many attempts. Try again after 15 minutes.",
            "retry_after": 900
        }
    )