"""
FastAPI route for logging in.

    POST /auth/login   exchange an email and password for a token

Send the token on later requests in this header:

    Authorization: Bearer <token>
"""


from fastapi import APIRouter

from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import login


router = APIRouter()


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    summary="Log in",
    description=(
        "Send the email and password in the request body. Returns an "
        "access token. Returns 401 for a wrong password or unknown "
        "email (same message for both) and 403 for a deactivated "
        "account."
    ),
)
def log_in(credentials: LoginRequest):
    return login(credentials.email, credentials.password)
