from typing import Any

from pymongo import AsyncMongoClient

from db.config import get_settings

client: AsyncMongoClient | None = None
db: Any | None = None


async def connect() -> None:
    global client, db
    if client is not None:
        return

    settings = get_settings()
    if not settings.mongodb_url:
        raise RuntimeError("MONGODB_URL is required")

    created_client = AsyncMongoClient(
        settings.mongodb_url,
        minPoolSize=1,
        maxPoolSize=10,
    )
    client = created_client
    db = created_client[settings.mongodb_database]
    try:
        await ping()
    except BaseException:
        client = None
        db = None
        await created_client.close()
        raise


async def ping() -> None:
    if client is None:
        raise RuntimeError("MongoDB client is not connected")

    await client.admin.command("ping")


def get_database() -> Any:
    if db is None:
        raise RuntimeError("MongoDB client is not connected")

    return db


async def close() -> None:
    global client, db
    current_client = client
    client = None
    db = None
    if current_client is not None:
        await current_client.close()
