"""Test task for web pages."""

import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import UJSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.exc import IntegrityError, NoResultFound

from src import database

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


async def check_user(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    ) -> str:
    """Check user access."""
    logging.info("AUTHORIZATION: %s", credentials.username)
    try:
        if await database.is_admin(credentials.username, credentials.password):
            return credentials.username
        raise HTTPException(HTTPStatus.UNAUTHORIZED)
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
        admin_username: Annotated[str, Depends(check_user)],
    ) -> UJSONResponse:
    """Create user and return info about it."""
    data = await request.json()
    logging.info("CREATE USER: %s -> %s", admin_username, data)
    try:
        user = await database.create_user(**data)
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
        admin_username: Annotated[str, Depends(check_user)],
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


@app.put("/user/update/{user_id:int}/")
async def update_user(
        request: Request,
        user_id: int,
        admin_username: Annotated[str, Depends(check_user)],
    ) -> UJSONResponse:
    """Update user and return info about it."""
    data = await request.json()
    logging.info("UPDATE USER: %s -> %s -> %s", admin_username, user_id, data)
    try:
        user = await database.update_user(user_id, data)
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
        admin_username: Annotated[str, Depends(check_user)],
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
