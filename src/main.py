"""Test task for web pages."""

import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import UJSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.exc import IntegrityError, NoResultFound

from src import database, validators

app = FastAPI()
security = HTTPBasic()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(filename="./logs.log", encoding="utf-8"),
    ],
)


async def check_admin(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    ) -> str:
    """Check admin access."""
    logging.info("AUTHORIZATION: %s", credentials.username)

    try:
        if await database.is_admin(credentials.username, credentials.password):
            return credentials.username
        raise HTTPException(HTTPStatus.UNAUTHORIZED)
    except NoResultFound:
        raise HTTPException(HTTPStatus.UNAUTHORIZED) from None


async def check_user(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    ) -> int:
    """Check user access."""
    logging.info("AUTHORIZATION: %s", credentials.username)

    try:
        return await database.is_correct(
            credentials.username,
            credentials.password,
        )
    except NoResultFound:
        raise HTTPException(HTTPStatus.UNAUTHORIZED) from None


@app.get("/help/")
async def get_help() -> dict[str, str]:
    """Show info about service."""
    return {
        "status": "ok",
        "help": "This is a service to manage posts",
    }


@app.post("/user/create/")
async def create_user(
        request: Request,
        admin_username: Annotated[str, Depends(check_admin)],
    ) -> UJSONResponse:
    """Create user and return info about it."""
    try:
        data = await request.json()
        user_data = validators.User.model_validate(data)
    except ValueError:
        return UJSONResponse(
            {"status": "error", "reason": "Bad request"},
            HTTPStatus.BAD_REQUEST,
        )

    logging.info("CREATE USER: %s -> %s", admin_username, user_data)

    try:
        user = await database.create_user(user_data)
    except IntegrityError:
        return UJSONResponse(
            {"status": "error", "reason": "User already exists"},
            HTTPStatus.CONFLICT,
        )
    return UJSONResponse(user)


@app.get("/user/get/{user_id:int}/")
async def get_user(
        _: Request,
        user_id: int,
        admin_username: Annotated[str, Depends(check_admin)],
    ) -> UJSONResponse:
    """Return info about user."""
    logging.info("GET USER: %s -> %s", admin_username, user_id)

    try:
        user = await database.get_user(user_id)
    except NoResultFound:
        return UJSONResponse(
            {"status": "error", "reason": "User not found"},
            HTTPStatus.NOT_FOUND,
        )
    return UJSONResponse(user)


@app.get("/user/get/all/")
async def get_all_users(
        _: Request,
        admin_username: Annotated[str, Depends(check_admin)],
    ) -> UJSONResponse:
    """Return info about all users."""
    logging.info("GET ALL USERS: %s", admin_username)
    users = await database.get_all_users()
    return UJSONResponse(users)


@app.put("/user/update/{user_id:int}/")
async def update_user(
        request: Request,
        user_id: int,
        admin_username: Annotated[str, Depends(check_admin)],
    ) -> UJSONResponse:
    """Update user and return info about it."""
    try:
        data = await request.json()
        user_data = validators.User.model_validate(data)
    except ValueError:
        return UJSONResponse(
            {"status": "error", "reason": "Bad request"},
            HTTPStatus.BAD_REQUEST,
        )

    logging.info(
        "UPDATE USER: %s -> %s -> %s", admin_username, user_id, user_data,
    )

    try:
        user = await database.update_user(user_id, user_data)
    except NoResultFound:
        return UJSONResponse(
            {"status": "error", "reason": "User not found"},
            HTTPStatus.NOT_FOUND,
        )
    return UJSONResponse(user)


@app.delete("/user/delete/{user_id:int}/")
async def delete_user(
        _: Request,
        user_id: int,
        admin_username: Annotated[str, Depends(check_admin)],
    ) -> UJSONResponse:
    """Delete user and return info about it."""
    logging.info("DELETE USER: %s -> %s", admin_username, user_id)

    try:
        user = await database.delete_user(user_id)
    except NoResultFound:
        return UJSONResponse(
            {"status": "error", "reason": "User not found"},
            HTTPStatus.NOT_FOUND,
        )
    return UJSONResponse(user)


@app.post("/post/create/")
async def create_post(
        request: Request,
        user_id: Annotated[int, Depends(check_user)],
    ) -> UJSONResponse:
    """Create post and return info about it."""
    try:
        data = await request.json()
        post_data = validators.Post.model_validate(data)
    except ValueError:
        return UJSONResponse(
            {"status": "error", "reason": "Bad request"},
            HTTPStatus.BAD_REQUEST,
        )

    logging.info("CREATE POST: %s -> %s", user_id, post_data)
    post = await database.create_post(user_id, post_data)
    return UJSONResponse(post)


@app.get("/post/get/{post_id:int}/")
async def get_post(
        _: Request,
        post_id: int,
        user_id: Annotated[int, Depends(check_user)],
    ) -> UJSONResponse:
    """Return info about post."""
    logging.info("GET POST: %s -> %s", user_id, post_id)

    try:
        post = await database.get_post(post_id)
    except NoResultFound:
        return UJSONResponse(
            {"status": "error", "reason": "Post not found"},
            HTTPStatus.NOT_FOUND,
        )
    return UJSONResponse(post)


@app.get("/post/get/all/")
async def get_all_posts(
        _: Request,
        user_id: Annotated[int, Depends(check_user)],
    ) -> UJSONResponse:
    """Return info about all posts."""
    logging.info("GET ALL POSTS: %s", user_id)
    posts = await database.get_all_posts()
    return UJSONResponse(posts)


@app.put("/post/update/{post_id:int}/")
async def update_post(
        request: Request,
        post_id: int,
        user_id: Annotated[int, Depends(check_user)],
    ) -> UJSONResponse:
    """Update post and return info about it."""
    try:
        data = await request.json()
        post_data = validators.User.model_validate(data)
    except ValueError:
        return UJSONResponse(
            {"status": "error", "reason": "Bad request"},
            HTTPStatus.BAD_REQUEST,
        )

    logging.info("UPDATE POST: %s -> %s -> %s", user_id, post_id, post_data)

    try:
        post = await database.update_user(user_id, post_data)
    except NoResultFound:
        return UJSONResponse(
            {"status": "error", "reason": "Post not found"},
            HTTPStatus.NOT_FOUND,
        )
    return UJSONResponse(post)


@app.delete("/post/delete/{post_id:int}/")
async def delete_post(
        _: Request,
        post_id: int,
        user_id: Annotated[int, Depends(check_user)],
    ) -> UJSONResponse:
    """Delete post and return info about it."""
    logging.info("DELETE USER: %s -> %s", user_id, post_id)

    try:
        post = await database.delete_post(user_id, post_id)
    except NoResultFound:
        return UJSONResponse(
            {"status": "error", "reason": "Post not found"},
            HTTPStatus.NOT_FOUND,
        )
    return UJSONResponse(post)
