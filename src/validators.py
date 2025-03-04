"""Module for validate input data."""


from pydantic import BaseModel, SecretStr


class User(BaseModel):

    """User object validator."""

    login: str
    password: SecretStr
    first_name: str
    last_name: str
    is_admin: bool
