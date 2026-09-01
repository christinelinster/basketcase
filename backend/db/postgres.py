import asyncpg
import json

from db.config import Settings, get_settings

pool: asyncpg.Pool | None = None


def connection_parameters(
    settings: Settings,
    *,
    database: str | None = None,
) -> dict[str, str | int]:
    required_settings = {
        "PGHOST": settings.pg_host,
        "PGUSER": settings.pg_user,
        "PGDATABASE": settings.pg_database,
    }
    missing_settings = [
        name for name, value in required_settings.items() if not value
    ]
    if missing_settings:
        formatted_names = ", ".join(missing_settings)
        raise RuntimeError(f"Missing required PostgreSQL settings: {formatted_names}")

    return {
        "host": settings.pg_host,
        "port": settings.pg_port,
        "user": settings.pg_user,
        "password": settings.pg_password,
        "database": database or settings.pg_database,
    }


async def connect() -> None:
    global pool
    if pool is not None:
        return

    settings = get_settings()
    parameters = connection_parameters(settings)

    created_pool = await asyncpg.create_pool(
        **parameters,
        min_size=1,
        max_size=10,
        init=configure_connection,
    )
    pool = created_pool
    try:
        await ping()
    except BaseException:
        pool = None
        await created_pool.close()
        raise


async def configure_connection(connection: asyncpg.Connection):
    await connection.set_type_codec(
        "jsonb", encoder=json.dumps, decoder=json.loads,
        schema="pg_catalog", format="text"
    )


async def ping() -> None:
    if pool is None:
        raise RuntimeError("PostgreSQL pool is not connected")

    async with pool.acquire() as connection:
        await connection.execute("SELECT 1")


async def close() -> None:
    global pool
    current_pool = pool
    pool = None
    if current_pool is not None:
        await current_pool.close()
