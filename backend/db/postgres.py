import asyncpg

from db.config import get_settings

pool: asyncpg.Pool | None = None


async def connect() -> None:
    global pool
    if pool is not None:
        return

    settings = get_settings()
    if not settings.postgres_url:
        raise RuntimeError("POSTGRES_URL is required")

    created_pool = await asyncpg.create_pool(
        settings.postgres_url,
        min_size=1,
        max_size=10,
    )
    pool = created_pool
    try:
        await ping()
    except BaseException:
        pool = None
        await created_pool.close()
        raise


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