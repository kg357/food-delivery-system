"""
Shared authentication and authorization dependencies.

A FastAPI "dependency" is a function that FastAPI runs before a route
handler. Whatever it returns is passed into the handler as a parameter.
A route that needs to know who is calling adds one parameter:

    @router.get("/example")
    def example(user: dict = Depends(get_current_user)):
        ...

STUB NOTICE
-----------
For now, get_current_user ignores the request and returns a fixed fake
customer. This lets the cart, checkout and order routes be built and
tested before real authentication exists. Task E2.5 replaces the body of
get_current_user with a real token check. The function keeps the same
name and the same return shape, so no route that uses it has to change.

Contract (agreed with the team):
    get_current_user()   -> {"id": str, "role": str, "active": bool}
    require_role(*roles) -> a dependency that returns the same user dict,
                            or raises HTTP 403 if the role is not allowed.

Using a different user in a test:

    app.dependency_overrides[get_current_user] = lambda: {
        "id": "owner-1",
        "role": "restaurant_owner",
        "active": True,
    }
    ...make requests...
    app.dependency_overrides.clear()
"""


from fastapi import Depends, HTTPException, status


# ============================================================
# Role Names
# ============================================================

# These are the only roles the backend uses. Import these constants
# instead of typing the strings, so a typo is caught immediately.
CUSTOMER = "customer"
RESTAURANT_OWNER = "restaurant_owner"
ADMIN = "admin"


# ============================================================
# Stub User
# ============================================================

# The fake user that get_current_user returns while it is a stub.
_STUB_USER = {
    "id": "dev-customer",
    "role": CUSTOMER,
    "active": True,
}


# ============================================================
# Dependencies
# ============================================================

def get_current_user() -> dict:
    """
    Return the user making the current request.

    STUB: always returns a fixed fake customer. The real version
    (task E2.5) reads the Authorization header, verifies the token,
    and returns the same shape.

    Returns:
        A dictionary with the keys "id" (str), "role" (str),
        and "active" (bool).
    """
    # Return a copy so a caller cannot change the shared stub user.
    return dict(_STUB_USER)


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
