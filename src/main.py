"""Test task for web pages."""


from os import environ

from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

load_dotenv()


POSTGRES_USER = environ["POSTGRES_USER"]
POSTGRES_PASSWORD = environ["POSTGRES_PASSWORD"]
POSTGRES_DB = environ["POSTGRES_DB"]
DB_PORT = environ["DB_PORT"]
DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgresql:{DB_PORT}/{POSTGRES_DB}"

engine = create_async_engine(DATABASE_URL, echo=True)
Session = async_sessionmaker(engine)

app = FastAPI()


@app.get("/help/")
async def get_help() -> dict[str, str]:
    """Show info about service."""
    return {
        "status": "ok",
        "help": "This is a service to manage posts",
    }
