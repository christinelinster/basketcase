from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from routers import interface, webhooks
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
    await mongo.connect()

    yield

    await mongo.close()
    await postgres.close()


app = FastAPI(lifespan=lifespan)

app.include_router(interface.router)
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
