"""
Tests for the shared authentication dependencies.

These tests build a tiny FastAPI app with three routes, so they check
get_current_user and require_role on their own, without depending on any
real route in the project.
"""


import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import (
    ADMIN,
    CUSTOMER,
    RESTAURANT_OWNER,
    get_current_user,
    require_role,
)


# ============================================================
# Test App and Fixtures
# ============================================================

@pytest.fixture
def app():
    """Build a small app with routes protected in different ways."""
    app = FastAPI()

    @app.get("/who-am-i")
    def who_am_i(user: dict = Depends(get_current_user)):
        return user

    @app.get("/customer-only")
    def customer_only(user: dict = Depends(require_role(CUSTOMER))):
        return user

    @app.get("/owner-or-admin")
    def owner_or_admin(
        user: dict = Depends(require_role(RESTAURANT_OWNER, ADMIN)),
    ):
        return user

    yield app

    # Never let one test's fake user leak into the next test.
    app.dependency_overrides.clear()


@pytest.fixture
def client(app):
    return TestClient(app)


def as_user(app, role):
    """Make get_current_user return a user with the given role."""
    app.dependency_overrides[get_current_user] = lambda: {
        "id": f"{role}-1",
        "role": role,
        "active": True,
    }


# ============================================================
# get_current_user
# ============================================================

def test_get_current_user_returns_the_agreed_shape():
    user = get_current_user()

    assert set(user.keys()) == {"id", "role", "active"}
    assert isinstance(user["id"], str)
    assert isinstance(user["role"], str)
    assert isinstance(user["active"], bool)


def test_get_current_user_stub_is_an_active_customer():
    user = get_current_user()

    assert user["role"] == CUSTOMER
    assert user["active"] is True


def test_changing_the_returned_user_does_not_change_the_stub():
    first = get_current_user()
    first["role"] = ADMIN

    assert get_current_user()["role"] == CUSTOMER


# ============================================================
# require_role
# ============================================================

def test_require_role_allows_a_matching_role(client):
    response = client.get("/customer-only")

    assert response.status_code == 200
    assert response.json()["role"] == CUSTOMER


def test_require_role_returns_403_for_a_different_role(client):
    response = client.get("/owner-or-admin")

    assert response.status_code == 403
    assert response.json() == {
        "detail": "You do not have permission to perform this action"
    }


def test_require_role_accepts_any_of_several_allowed_roles(app, client):
    as_user(app, RESTAURANT_OWNER)
    assert client.get("/owner-or-admin").status_code == 200

    as_user(app, ADMIN)
    assert client.get("/owner-or-admin").status_code == 200


# ============================================================
# Overriding the user in tests
# ============================================================

def test_dependency_override_changes_who_the_caller_is(app, client):
    as_user(app, RESTAURANT_OWNER)

    assert client.get("/who-am-i").json()["role"] == RESTAURANT_OWNER
    # The same override now fails the customer-only route.
    assert client.get("/customer-only").status_code == 403
