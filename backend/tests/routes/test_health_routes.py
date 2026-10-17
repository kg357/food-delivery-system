
"""
Tests for basic FastAPI application health and routing.

These tests verify:
    - The health-check endpoint responds successfully.
    - Requests to nonexistent endpoints return HTTP 404.

Unlike the restaurant and menu tests, these tests do not
require temporary JSON files or mocked dependencies.
"""


from fastapi.testclient import TestClient

from app.main import app


# TestClient simulates HTTP requests to FastAPI without
# requiring a separately running backend server.
client = TestClient(app)


# ============================================================
# Application Health Check
# ============================================================

def test_health():
    """
    Verify that the application's health endpoint is working.

    HTTP 200 indicates that the request was successful.
    The response should contain the expected status message.
    """
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "OK"}


# ============================================================
# Unknown Endpoint Handling
# ============================================================

def test_invalid_endpoint():
    """
    Verify that FastAPI returns HTTP 404 for an unknown endpoint.

    This confirms that requests to undefined routes are
    handled with the appropriate Not Found response.
    """
    response = client.get("/does-not-exist")

    assert response.status_code == 404
