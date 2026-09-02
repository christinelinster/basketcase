import json

import asyncpg

from db.config import get_settings

pool: asyncpg.Pool | None = None


async def connect() -> None:
    global pool
    if pool is not None:
        return

    settings = get_settings()
    pool = await asyncpg.create_pool(
        host=settings.pg_host,
        port=settings.pg_port,
        user=settings.pg_user,
        password=settings.pg_password,
        database=settings.pg_database,
        min_size=1,
        max_size=10,
        init=configure_connection,
    )


async def configure_connection(connection: asyncpg.Connection) -> None:
    await connection.set_type_codec(
        "jsonb", encoder=json.dumps, decoder=json.loads,
        schema="pg_catalog", format="text"
    )

async def close() -> None:
    global pool
    current_pool = pool
    pool = None
    if current_pool is not None:
        await current_pool.close()
