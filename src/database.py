"""Module for working with the database."""


from hashlib import sha3_512
from os import environ

from dotenv import load_dotenv
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from ujson import dumps, loads

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


async def is_admin(login: str, password: str) -> bool:
    """Check if user is admin."""
    async with Session.begin() as session:
        password_hash = sha3_512(password.encode()).hexdigest()
        stmt = select(User).column(User.is_admin).where(
            User.login == login,
            User.password == password_hash,
        )
        user = (await session.execute(stmt)).scalar_one()
        return user.is_admin


async def get_user(user_id: int) -> dict[str, str]:
    """Get user from database by id."""
    user = await redis.get(f"user:{user_id}")
    if user:
        return loads(user)

    async with Session.begin() as session:
        stmt = select(User).where(User.id == user_id)
        user = (await session.execute(stmt)).scalar_one()
        redis.setex(f"user:{user_id}", 3600, user.as_dict())
        return user.as_dict()


async def create_user(
        login: str,
        password: str,
        first_name: str,
        last_name: str,
        *,
        is_admin: bool,
    ) -> dict[str, str]:
    """Create user in database."""
    password_hash = sha3_512(password.encode()).hexdigest()
    async with Session.begin() as session:
        user = User(
            login=login,
            password=password_hash,
            first_name=first_name,
            last_name=last_name,
            is_admin=is_admin,
        )
        session.add(user)
        await session.flush()
        await session.refresh(user)
        await redis.setex(f"user:{user.id}", 3600, dumps(user.as_dict()))
        return user.as_dict()


async def delete_user(user_id: int) -> dict[str, str]:
    """Get user from database by id."""
    async with Session.begin() as session:
        stmt = select(User).where(User.id == user_id)
        user = (await session.execute(stmt)).scalar_one()
        await session.delete(user)
        redis.delete(f"user:{user_id}")
        return user.as_dict()
