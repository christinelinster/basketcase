from fastapi import Request
from fastapi.responses import JSONResponse


async def catch_error(request: Request, exc: Exception):
    print(exc)

    status_code = getattr(exc, "status_code", 500)

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": str(exc) or "Internal server error"
        }
    )