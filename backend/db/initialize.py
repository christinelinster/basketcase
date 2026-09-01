import asyncio
from pathlib import Path

from pymongo import ASCENDING, DESCENDING

from db import mongo, postgres


POSTGRES_SCHEMA_OBJECTS = frozenset(
    {
        "baskets",
        "requests",
        "http_method",
        "baskets_name_index",
        "requests_basket_id_index",
    }
)

POSTGRES_SCHEMA_CATALOG_QUERY = """
SELECT object_name
FROM (
    SELECT 'baskets' AS object_name
    WHERE to_regclass('public.baskets') IS NOT NULL
    UNION ALL
    SELECT 'requests'
    WHERE to_regclass('public.requests') IS NOT NULL
    UNION ALL
    SELECT 'http_method'
    WHERE EXISTS (
        SELECT 1
        FROM pg_type
        WHERE typname = 'http_method'
          AND typnamespace = 'public'::regnamespace
    )
    UNION ALL
    SELECT 'baskets_name_index'
    WHERE to_regclass('public.baskets_name_index') IS NOT NULL
    UNION ALL
    SELECT 'requests_basket_id_index'
    WHERE to_regclass('public.requests_basket_id_index') IS NOT NULL
) AS existing_objects
"""

MONGO_RAW_REQUESTS_COLLECTION = "raw_requests"


async def initialize_postgres_schema() -> None:
    if postgres.pool is None:
        raise RuntimeError("PostgreSQL pool is not connected")

    async with postgres.pool.acquire() as connection:
        rows = await connection.fetch(POSTGRES_SCHEMA_CATALOG_QUERY)
        existing_objects = {row["object_name"] for row in rows}

        if POSTGRES_SCHEMA_OBJECTS.issubset(existing_objects):
            return

        present_objects = POSTGRES_SCHEMA_OBJECTS.intersection(existing_objects)
        if present_objects:
            missing_objects = sorted(POSTGRES_SCHEMA_OBJECTS - existing_objects)
            formatted_missing = ", ".join(missing_objects)
            raise RuntimeError(
                "PostgreSQL schema is incomplete; missing required objects: "
                f"{formatted_missing}"
            )

        schema_path = Path(__file__).with_name("schema.sql")
        schema_sql = schema_path.read_text(encoding="utf-8")
        async with connection.transaction():
            await connection.execute(schema_sql)


async def initialize_mongo_schema() -> None:
    database = mongo.get_database()
    collection_names = await database.list_collection_names()

    if MONGO_RAW_REQUESTS_COLLECTION not in collection_names:
        await database.create_collection(MONGO_RAW_REQUESTS_COLLECTION)

    collection = database[MONGO_RAW_REQUESTS_COLLECTION]
    await collection.create_index(
        [("received_at", DESCENDING)],
        name="raw_requests_received_at_desc",
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
