
from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers import webhooks, baskets
from db import postgres

import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    await postgres.connect()
    yield
    await postgres.close()

app = FastAPI(lifespan=lifespan)
PORT = int(os.getenv("PORT", 3000))
HOST = "0.0.0.0"

app.include_router(webhooks.router)
app.include_router(baskets.router)

