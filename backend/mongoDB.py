import os
from pymongo import AsyncMongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGO_URI")

client = AsyncMongoClient(
    uri,
    server_api=ServerApi(
        "1",
        strict=True,
        deprecation_errors=True
    )
)

db = client["bloglist"]

users_collection = db["users"]
notes_collection = db["notes"]


async def connect_to_mongodb():
    try:
        await client.admin.command("ping")
        print("Connected to MongoDB")
    except Exception as error:
        print("Error connecting to MongoDB:", error)
        raise
