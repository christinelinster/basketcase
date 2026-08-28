import os
from pymongo import AsyncMongoClient

client = AsyncMongoClient(
    os.getenv("MONGODB_URL", "mongodb://localhost:27017")
)

db = client["basketcase"]
