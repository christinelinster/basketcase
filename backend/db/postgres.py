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

#  import os
#   import asyncpg

#   POSTGRES_URL = os.getenv(
#       "POSTGRES_URL",
#       "postgresql://postgres:YOUR_PASSWORD@localhost:5432/request_bin",
#   )




# class Database:

#     def __init__(self):
#         self.database_url = os.getenv("DB_URL")
#         self.pool = None

#     # DELETE FOR PRODUCTION
#     def log_query(self, statement, params):
#         timestamp = datetime.now().strftime("%b %d %H:%M:%S")

#         print(
#             timestamp,
#             statement,
#             params
#         )

#     async def connect(self):
#         self.pool = await asyncpg.create_pool(
#             self.database_url,
#             ssl=False
#         )

#         async with self.pool.acquire() as connection:
#             await connection.execute("SELECT 1")

#         print("Database connected")

#     async def close(self):
#         if self.pool:
#             await self.pool.close()

#     async def db_query(self, statement, *params):
#         if not self.pool:
#             raise Exception("Database not connected")

#         self.log_query(statement, params)

#         connection = await self.pool.acquire()

#         try:
#             result = await connection.fetch(
#                 statement,
#                 *params
#             )

#             return result

#         except Exception as error:
#             print(
#                 "Database query error:",
#                 error
#             )

#             raise

#         finally:
#             await self.pool.release(connection)

#     async def get_client(self):
#         if not self.pool:
#             raise Exception("Database not connected")

#         return await self.pool.acquire()

#     async def begin_transaction(self, client):
#         await client.execute("BEGIN")

#     async def commit_transaction(self, client):
#         await client.execute("COMMIT")
#         await self.pool.release(client)

#     async def rollback_transaction(self, client):
#         await client.execute("ROLLBACK")
#         await self.pool.release(client)