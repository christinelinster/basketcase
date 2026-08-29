from fastapi import APIRouter, status
from fastapi.responses import JSONResponse


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


@router.delete("/baskets/{name}")
async def delete_basket(name: str) -> JSONResponse:
    return not_implemented()


@router.get("/baskets/{name}/requests")
async def list_requests(name: str) -> JSONResponse:
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
