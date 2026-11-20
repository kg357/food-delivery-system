"""
Pydantic schemas for logging in.
"""


from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.customer import normalize_email


class LoginRequest(BaseModel):
    """
    Credentials sent to POST /auth/login in the request body.

    The password is never sent in the URL, because URLs end up in
    logs and browser history.
    """

    model_config = ConfigDict(extra="forbid")

    email: str
    password: str

    @field_validator("email")
    @classmethod
    def check_email(cls, value: str) -> str:
        return normalize_email(value)


class TokenResponse(BaseModel):
    """The token returned after a successful login."""

    access_token: str
    token_type: str = "bearer"
