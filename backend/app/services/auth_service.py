"""
Business logic for logging in and identifying the caller.

    login:
        Checks an email and password and issues a token.

    get_user_from_token:
        Turns a token back into the current user. It reads the
        account from storage on every request, so deactivating an
        account or changing its role takes effect immediately, even
        for tokens that were issued earlier.
"""


from pathlib import Path

from fastapi import HTTPException

from app.core.security import (
    create_access_token,
    decode_access_token,
    verify_password,
)
from app.repositories.customer_repository import (
    load_customer_by_email,
    load_customer_by_id,
)
from app.schemas.auth import TokenResponse


def login(
    email: str,
    password: str,
    path: Path | None = None,
) -> TokenResponse:
    """
    Check credentials and return an access token.

    Raises:
        HTTPException:
            401 for an unknown email or a wrong password, with the
            same message for both so the API does not reveal which
            emails are registered.
            403 if the password is right but the account is deactivated.
    """
    record = load_customer_by_email(email, path)

    if record is None or not verify_password(
        password,
        record["password_hash"],
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not record["active"]:
        raise HTTPException(
            status_code=403,
            detail="This account has been deactivated.",
        )

    return TokenResponse(
        access_token=create_access_token(record["id"], record["role"]),
    )


def get_user_from_token(token: str, path: Path | None = None) -> dict:
    """
    Identify the caller from an access token.

    Returns:
        {"id": str, "role": str, "active": bool}, the same shape the
        authentication stub returned.

    Raises:
        HTTPException:
            401 if the token is invalid or expired, or the account
            no longer exists.
            403 if the account is deactivated.
    """
    unauthorized = HTTPException(
        status_code=401,
        detail="Invalid or expired token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_access_token(token)

    if user_id is None:
        raise unauthorized

    record = load_customer_by_id(user_id, path)

    if record is None:
        raise unauthorized

    if not record["active"]:
        raise HTTPException(
            status_code=403,
            detail="This account has been deactivated.",
        )

    return {
        "id": record["id"],
        "role": record["role"],
        "active": record["active"],
    }
