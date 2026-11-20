"""
Password hashing and login-token helpers.

Passwords are hashed with bcrypt. A bcrypt hash cannot be turned
back into the password, and every hash includes its own random salt,
so two users with the same password get different hashes.

Login tokens are JSON Web Tokens (JWT) signed with a secret. The
server can later check that a token was issued by this server and has
not expired, without storing anything about it.
"""


from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core import config


# ============================================================
# Passwords
# ============================================================

def hash_password(password: str) -> str:
    """
    Hash a plain-text password with bcrypt.

    Returns:
        The hash as a string, safe to store in a JSON file.
    """
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """
    Check a plain-text password against a stored bcrypt hash.

    Returns:
        True if the password matches. False if it does not, or if
        the stored hash or the password cannot be processed.
    """
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False


# ============================================================
# Access Tokens
# ============================================================

def create_access_token(user_id: str, role: str) -> str:
    """
    Create a signed token that identifies a user.

    The token holds the user's ID ("sub"), their role, and an expiry
    time ("exp"). The ID is what the backend trusts; the current role
    is always re-read from storage when a request arrives.
    """
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user_id,
        "role": role,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        config.JWT_SECRET,
        algorithm=config.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> str | None:
    """
    Verify a token and return the user ID inside it.

    Returns:
        The user ID if the token is genuine and not expired.
        None if the token is malformed, forged, or expired.
    """
    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=[config.JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        return None

    user_id = payload.get("sub")

    if not isinstance(user_id, str):
        return None

    return user_id
