from dataclasses import dataclass
from functools import lru_cache
import os

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class Settings:
    pg_host: str
    pg_port: int
    pg_user: str
    pg_password: str
    pg_database: str
    mongodb_url: str
    mongodb_database: str
    host: str
    port: int
    environment: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        pg_host=os.getenv("PGHOST") or "localhost",
        pg_port=int(os.getenv("PGPORT") or "5432"),
        pg_user=os.getenv("PGUSER") or "postgres",
        pg_password=os.getenv("PGPASSWORD", ""),
        pg_database=os.getenv("PGDATABASE") or "basketcase",
        mongodb_url=os.getenv("MONGODB_URL") or "mongodb://localhost:27017",
        mongodb_database=os.getenv("MONGODB_DATABASE") or "basketcase",
        host=os.getenv("HOST") or "127.0.0.1",
        port=int(os.getenv("PORT") or "8000"),
        environment=(os.getenv("APP_ENV") or "production").strip().lower(),
    )
