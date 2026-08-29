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

'''

dataclass gives Settings a clear, typed structure:

  Settings(
      postgres_url=...,
      mongodb_url=...,
      mongodb_database=...,
      host=...,
      port=...,
  )

  It automatically provides initialization,
  readable representation, and comparisons.
  frozen=True makes the settings immutable
  after creation, reducing accidental
  configuration changes. slots=True keeps
  instances lightweight and prevents
  unexpected attributes.

  @lru_cache(maxsize=1) ensures get_settings()
  loads environment variables only once per
  process. This means every module receives
  the same settings snapshot instead of
  repeatedly reading .env and environment
  variables.

  It also means configuration changes require
  an application restart. Tests can explicitly
  reset it with:

  get_settings.cache_clear()

  The cache is only for configuration.
  PostgreSQL and MongoDB maintain their own
  separate connection pools.
'''