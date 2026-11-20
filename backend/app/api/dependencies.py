"""
Shared authentication and authorization dependencies.

A FastAPI "dependency" is a function that FastAPI runs before a route
handler. Whatever it returns is passed into the handler as a parameter.
A route that needs to know who is calling adds one parameter:

    @router.get("/example")
    def example(user: dict = Depends(get_current_user)):
        ...

Contract (agreed with the team, unchanged since the stub):
    get_current_user()   -> {"id": str, "role": str, "active": bool}
    require_role(*roles) -> a dependency that returns the same user dict,
                            or raises HTTP 403 if the role is not allowed.

get_current_user reads the "Authorization: Bearer <token>" header:
    no header, or a bad or expired token  -> 401
    account deactivated                   -> 403

Using a different user in a test (no token or customers file needed):

    app.dependency_overrides[get_current_user] = lambda: {
        "id": "owner-1",
        "role": "restaurant_owner",
        "active": True,
    }
    ...make requests...
    app.dependency_overrides.clear()
"""


from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.roles import ADMIN, CUSTOMER, RESTAURANT_OWNER
from app.services.auth_service import get_user_from_token

# Re-exported so existing code can keep importing the role names from
# this module. They live in app.core.roles.
__all__ = [
    "ADMIN",
    "CUSTOMER",
    "RESTAURANT_OWNER",
    "get_current_user",
    "require_role",
]


# ============================================================
# Dependencies
# ============================================================

# Reads the Authorization header. auto_error=False lets us return
# 401 ourselves. FastAPI's docs page also uses this to show an
# "Authorize" button.
_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        _bearer_scheme
    ),
) -> dict:
    """
    Return the user making the current request.

    The user comes from the bearer token only, never from the request
    body or URL.

    Raises:
        HTTPException: 401 if the token is missing, invalid or
            expired; 403 if the account is deactivated.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return get_user_from_token(credentials.credentials)


def require_role(*allowed_roles: str):
    """
    Build a dependency that only lets users with an allowed role through.

    Usage:
        @router.post("/restaurants")
        def create(user: dict = Depends(require_role(RESTAURANT_OWNER))):
            ...

    Args:
        *allowed_roles: One or more role names that may use the route.

    Returns:
        A dependency function that returns the current user when their
        role is allowed, and otherwise raises HTTP 403 (Forbidden).
    """

    def check_role(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return user

    return check_role
