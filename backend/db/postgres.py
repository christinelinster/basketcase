import os
import asyncpg

POSTGRES_URL = os.getenv(
    "POSTGRES_URL",
    "postgresql://postgres:YOUR_PASSWORD@localhost:5432/request_bin",
)

pool: asyncpg.Pool | None = None

async def connect():
    global pool
    pool = await asyncpg.create_pool(
        POSTGRES_URL,
        min_size=1,
        max_size=10,
    )

async def close():
    global pool
    if pool:
        await pool.close()
