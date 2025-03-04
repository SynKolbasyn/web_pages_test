"""Module for working with the database."""


from hashlib import sha3_512
from os import environ

from dotenv import load_dotenv
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from ujson import dumps, loads

from src import validators
from src.models import Post, User

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


async def is_correct(login: str, password: str) -> int:
    """Check if user credentials is correct."""
    async with Session.begin() as session:
        password_hash = sha3_512(password.encode()).hexdigest()
        stmt = select(User).column(User.id).where(
            User.login == login,
            User.password == password_hash,
        )
        user = (await session.execute(stmt)).scalar_one()
        return user.id


async def create_user(user_data: validators.User) -> dict[str, str]:
    """Create user in database."""
    password_hash = sha3_512(
        user_data.password.get_secret_value().encode(),
    ).hexdigest()
    async with Session.begin() as session:
        user = User(
            login=user_data.login,
            password=password_hash,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_admin=user_data.is_admin,
        )
        session.add(user)
        await session.flush()
        await session.refresh(user)
        await redis.setex(f"user:{user.id}", 3600, dumps(user.as_dict()))
        return user.as_dict()


async def get_user(user_id: int) -> dict[str, str]:
    """Get user from database."""
    user = await redis.get(f"user:{user_id}")
    if user:
        return loads(user)

    async with Session.begin() as session:
        stmt = select(User).where(User.id == user_id)
        user = (await session.execute(stmt)).scalar_one()
        redis.setex(f"user:{user_id}", 3600, user.as_dict())
        return user.as_dict()


async def get_all_users() -> list[dict[str, str]]:
    """Get all users from database."""
    async with Session.begin() as session:
        stmt = select(User)
        users = (await session.execute(stmt)).scalars().all()
        return [user.as_dict() for user in users]


async def update_user(
        user_id: int,
        user_data: validators.User,
    ) -> dict[str, str]:
    """Update user in database."""
    password_hash = sha3_512(
        user_data.password.get_secret_value().encode(),
    ).hexdigest()
    async with Session.begin() as session:
        stmt = select(User).where(User.id == user_id)
        user = (await session.execute(stmt)).scalar_one()
        user.login = user_data.login
        user.password = password_hash
        user.first_name = user_data.first_name
        user.last_name = user_data.last_name
        user.is_admin = user_data.is_admin
        await redis.setex(f"user:{user_id}", 3600, dumps(user.as_dict()))
        return user.as_dict()


async def delete_user(user_id: int) -> dict[str, str]:
    """Delete user from database."""
    async with Session.begin() as session:
        stmt = select(User).where(User.id == user_id)
        user = (await session.execute(stmt)).scalar_one()
        await session.delete(user)
        await redis.delete(f"user:{user_id}")
        return user.as_dict()


async def create_post(
        user_id: int,
        post_data: validators.Post,
    ) -> dict[str, str]:
    """Create post in database."""
    async with Session.begin() as session:
        post = Post(
            user_id=user_id,
            title=post_data.title,
            text=post_data.text,
        )
        session.add(post)
        await session.flush()
        await session.refresh(post)
        await redis.setex(f"post:{post.id}", 3600, dumps(post.as_dict()))
        return post.as_dict()


async def get_post(post_id: int) -> dict[str, str]:
    """Get post from database."""
    post = await redis.get(f"post:{post_id}")
    if post:
        return loads(post)

    async with Session.begin() as session:
        stmt = select(Post).where(Post.id == post_id)
        post = (await session.execute(stmt)).scalar_one()
        redis.setex(f"post:{post.id}", 3600, dumps(post.as_dict()))
        return post.as_dict()


async def get_all_posts() -> list[dict[str, str]]:
    """Get all posts from database."""
    async with Session.begin() as session:
        stmt = select(Post)
        posts = (await session.execute(stmt)).scalars().all()
        return [post.as_dict() for post in posts]


async def update_post(
        user_id: int,
        post_id: int,
        post_data: validators.Post,
    ) -> dict[str, str]:
    """Update post in database."""
    async with Session.begin() as session:
        stmt = select(Post).where(Post.id == user_id, Post.user_id == user_id)
        post = (await session.execute(stmt)).scalar_one()
        post.title = post_data.title
        post.text = post_data.text
        await redis.setex(f"post:{post_id}", 3600, dumps(post.as_dict()))
        return post.as_dict()


async def delete_post(user_id: int, post_id: int) -> dict[str, str]:
    """Delete post from database."""
    async with Session.begin() as session:
        stmt = select(Post).where(Post.id == post_id, Post.user_id == user_id)
        post = (await session.execute(stmt)).scalar_one()
        await session.delete(post)
        await redis.delete(f"post:{post_id}")
        return post.as_dict()
