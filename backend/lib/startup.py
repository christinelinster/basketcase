import os
from dotenv import load_dotenv

load_dotenv()

from lib.db_query import Database
from mongoDB import connect_to_mongodb

db = Database()

async def startup():
    global mongoDB

    db = Database()

    if os.getenv("USE_DB") == "true":
        await db.connect()

    else:
        print("DB Disabled: change at env")