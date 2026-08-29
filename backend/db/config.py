from dataclasses import dataclass
from functools import lru_cache
import os

from dotenv import load_dotenv

'''
This code creates a centralized, immutable configuration object for your application and ensures your environment variables are loaded into that object only once.

Instead of writing:
class Settings:
    def __init__(self, postgres_url, mongodb_url):
        self.postgres_url = postgres_url
        self.mongodb_url = mongodb_url

Using dataclass generates the boilerplate for you.
frozen=True: Makes the object immutable after creation.
slots=True tells Python: These are the only attributes this object is supposed to have.

'''

DEFAULT_DATABASE = "basketcase"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_ENVIRONMENT = "production"


@dataclass(frozen=True, slots=True)
class Settings:
    postgres_url: str
    mongodb_url: str
    mongodb_database: str = DEFAULT_DATABASE
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    environment: str = DEFAULT_ENVIRONMENT


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        postgres_url=os.getenv("POSTGRES_URL", ""),
        mongodb_url=os.getenv("MONGODB_URL", ""),
        mongodb_database=os.getenv("MONGODB_DATABASE") or DEFAULT_DATABASE,
        host=os.getenv("HOST") or DEFAULT_HOST,
        port=int(os.getenv("PORT") or DEFAULT_PORT),
        environment=(os.getenv("APP_ENV") or DEFAULT_ENVIRONMENT).strip().lower(),
    )
