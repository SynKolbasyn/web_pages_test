"""Module for working with the database."""


from os import environ

from dotenv import load_dotenv
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.models import User

load_dotenv()


POSTGRES_USER = environ["POSTGRES_USER"]
POSTGRES_PASSWORD = environ["POSTGRES_PASSWORD"]
POSTGRES_DB = environ["POSTGRES_DB"]
DB_PORT = environ["DB_PORT"]
DB_HOST = environ["DB_HOST"]
REDIS_HOST = environ["REDIS_HOST"]
REDIS_PORT = int(environ["REDIS_PORT"])
REDIS_PASSWORD = environ["REDIS_PASSWORD"]
DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}"

redis = Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
engine = create_async_engine(DATABASE_URL, echo=True)
Session = async_sessionmaker(engine)


async def get_user(user_id: int) -> User:
    """Get user from database by id."""
    user = await redis.get(f"user:{user_id}")
    if user:
        return User(**user.decode())

    async with Session.begin() as session:
        stmt = select(User).where(User.id == user_id)
        user = await session.execute(stmt)
        user = user.scalar_one()
        redis.setex(f"user:{user_id}", 3600, user.as_dict())
        return user
