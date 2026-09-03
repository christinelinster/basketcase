from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from routers import interface, live, webhooks
from routers.route_config import get_route_config

from db import mongo, postgres
from db.config import get_settings


'''

  - index.py defines the FastAPI app.
  - lifespan() manages database startup and shutdown.
  - main() starts Uvicorn programmatically.
  - if __name__ == "__main__" ensures main() only runs when you execute python index.py.
  - "index:app" gives Uvicorn an importable application target.

'''

@asynccontextmanager
async def lifespan(app: FastAPI):
    await postgres.connect()
    try:
        try:
            await mongo.connect()
            yield
        finally:
            await mongo.close()
    finally:
        await postgres.close()


app = FastAPI(lifespan=lifespan)
app.include_router(interface.router)
app.mount("/assets", StaticFiles(directory=get_route_config().frontend_dir / "assets"))
app.include_router(live.router)
# Webhooks router must be mounted last so it doesn't swallow other requests
app.include_router(webhooks.router)


def main() -> None:
    settings = get_settings()

    uvicorn.run(
        "index:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
    )


if __name__ == "__main__":
    main()
