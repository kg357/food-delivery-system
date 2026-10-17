
"""
FastAPI route for checking application health.

The health endpoint provides a simple way to verify that
the backend server is running and responding to HTTP requests.

Unlike restaurant and menu endpoints, this route does not
require the service or repository layers.
"""


from fastapi import APIRouter


router = APIRouter()


# ============================================================
# Application Health Check
# ============================================================

@router.get(
    "/health",
    summary="Check application health",
    description=(
        "Verify that the FastAPI application is running "
        "and responding to requests."
    ),
)
def health():
    """
    Return the application's basic health status.

    Returns:
        A JSON response containing {"status": "OK"}.

    FastAPI automatically serializes the returned Python
    dictionary into JSON and responds with HTTP 200.

    This endpoint checks that the application can respond
    to requests; it does not verify database or storage health.
    """
    return {
        "status": "OK"
    }