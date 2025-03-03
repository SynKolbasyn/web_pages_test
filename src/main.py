"""Test task for web pages."""

from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.responses import UJSONResponse
from sqlalchemy.exc import NoResultFound

from src import database

app = FastAPI()


@app.get("/help/")
async def get_help() -> dict[str, str]:
    """Show info about service."""
    return {
        "status": "ok",
        "help": "This is a service to manage posts",
    }


@app.get("/user/get/{user_id:int}/")
async def get_user(_: Request, user_id: int) -> UJSONResponse:
    """Return info about user."""
    try:
        user = await database.get_user(user_id)
    except NoResultFound:
        return UJSONResponse(
            {"status": "error", "reason": "User not found"},
            HTTPStatus.NOT_FOUND,
        )
    return UJSONResponse(user)


@app.post("/user/create/")
async def create_user(request: Request) -> UJSONResponse:
    """Create user and return info about it."""
    data = await request.json()
    user = await database.create_user(**data)
    return UJSONResponse(user)


@app.delete("/user/delete/{user_id:int}/")
async def delete_user(_: Request, user_id: int) -> UJSONResponse:
    """Delete user and return info about it."""
    try:
        user = await database.delete_user(user_id)
    except NoResultFound:
        return UJSONResponse(
            {"status": "error", "reason": "User not found"},
            HTTPStatus.NOT_FOUND,
        )
    return UJSONResponse(user)
