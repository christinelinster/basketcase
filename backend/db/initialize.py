import asyncio
from pathlib import Path

from pymongo import DESCENDING
from db import mongo, postgres


async def initialize_postgres_schema() -> None:
    if postgres.pool is None:
        raise RuntimeError("PostgreSQL pool is not connected")

    async with postgres.pool.acquire() as connection:
        schema_path = Path(__file__).with_name("schema.sql")
        schema_sql = schema_path.read_text(encoding="utf-8")
        async with connection.transaction():
            await connection.execute(schema_sql)


async def initialize_mongo_schema() -> None:
    collection = mongo.get_database()["raw_requests"]
    await collection.create_index(
        [("received_at", DESCENDING)],
        name="raw_requests_received_at_desc",
    )
    await collection.create_index(
        [("basket_id", DESCENDING)],
        name="raw_requests_basket_id_desc",
    )


async def initialize_databases() -> None:
    await postgres.connect()
    try:
        await mongo.connect()
        await initialize_postgres_schema()
        await initialize_mongo_schema()
    finally:
        try:
            await mongo.close()
        finally:
            await postgres.close()


if __name__ == "__main__":
    asyncio.run(initialize_databases())
