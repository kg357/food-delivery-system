"""
Tests for the shared authentication dependencies.

These tests build a tiny FastAPI app with three routes, so they check
get_current_user and require_role on their own, using real login tokens
and a temporary customers file.
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
from app.core import config
from app.core.security import create_access_token


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
def client(app, customers_file):
    return TestClient(app)


def as_user(app, role):
    """Make get_current_user return a user with the given role."""
    app.dependency_overrides[get_current_user] = lambda: {
        "id": f"{role}-1",
        "role": role,
        "active": True,
    }


# ============================================================
# get_current_user: who is calling?
# ============================================================

def test_valid_token_returns_the_agreed_shape(
    client,
    add_account,
    auth_headers,
):
    add_account("customer-1")

    response = client.get("/who-am-i", headers=auth_headers("customer-1"))

    assert response.status_code == 200
    assert response.json() == {
        "id": "customer-1",
        "role": CUSTOMER,
        "active": True,
    }


def test_missing_token_returns_401(client):
    response = client.get("/who-am-i")

    assert response.status_code == 401


def test_garbage_token_returns_401(client):
    response = client.get(
        "/who-am-i",
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert response.status_code == 401


def test_token_signed_with_another_secret_returns_401(
    client,
    add_account,
    monkeypatch,
):
    add_account("customer-1")

    # context() limits the change to this block. A plain undo() would
    # also undo the temporary customers file set up by the fixtures.
    with monkeypatch.context() as other_secret:
        other_secret.setattr(config, "JWT_SECRET", "a-different-secret-" * 3)
        forged = create_access_token("customer-1", CUSTOMER)

    response = client.get(
        "/who-am-i",
        headers={"Authorization": f"Bearer {forged}"},
    )

    assert response.status_code == 401


def test_expired_token_returns_401(
    client,
    add_account,
    auth_headers,
    monkeypatch,
):
    add_account("customer-1")

    # A negative lifetime makes the token expire before it is issued.
    monkeypatch.setattr(config, "ACCESS_TOKEN_EXPIRE_MINUTES", -1)
    headers = auth_headers("customer-1")

    response = client.get("/who-am-i", headers=headers)

    assert response.status_code == 401


def test_token_for_an_account_that_does_not_exist_returns_401(
    client,
    auth_headers,
):
    response = client.get("/who-am-i", headers=auth_headers("ghost"))

    assert response.status_code == 401


def test_deactivated_account_returns_403(
    client,
    add_account,
    auth_headers,
):
    add_account("customer-1", active=False)

    response = client.get("/who-am-i", headers=auth_headers("customer-1"))

    assert response.status_code == 403


def test_role_comes_from_storage_not_from_the_token(
    client,
    add_account,
    auth_headers,
):
    """A token that claims "admin" cannot make a customer an admin."""
    add_account("customer-1", role=CUSTOMER)

    headers = auth_headers("customer-1", role=ADMIN)
    response = client.get("/who-am-i", headers=headers)

    assert response.json()["role"] == CUSTOMER
    assert client.get("/owner-or-admin", headers=headers).status_code == 403


# ============================================================
# require_role
# ============================================================

def test_require_role_allows_a_matching_role(
    client,
    add_account,
    auth_headers,
):
    add_account("customer-1")

    response = client.get(
        "/customer-only",
        headers=auth_headers("customer-1"),
    )

    assert response.status_code == 200
    assert response.json()["role"] == CUSTOMER


def test_require_role_returns_403_for_a_different_role(
    client,
    add_account,
    auth_headers,
):
    add_account("customer-1")

    response = client.get(
        "/owner-or-admin",
        headers=auth_headers("customer-1"),
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "You do not have permission to perform this action"
    }


def test_require_role_without_a_token_returns_401_not_403(client):
    """No token means "who are you?" (401), not "not allowed" (403)."""
    assert client.get("/customer-only").status_code == 401


def test_require_role_accepts_any_of_several_allowed_roles(
    client,
    add_account,
    auth_headers,
):
    add_account("owner-1", role=RESTAURANT_OWNER)
    add_account("admin-1", role=ADMIN)

    owner = client.get("/owner-or-admin", headers=auth_headers("owner-1"))
    admin = client.get("/owner-or-admin", headers=auth_headers("admin-1"))

    assert owner.status_code == 200
    assert admin.status_code == 200


# ============================================================
# Overriding the user in tests
# ============================================================

def test_dependency_override_changes_who_the_caller_is(app, client):
    as_user(app, RESTAURANT_OWNER)

    assert client.get("/who-am-i").json()["role"] == RESTAURANT_OWNER
    # The same override now fails the customer-only route.
    assert client.get("/customer-only").status_code == 403
