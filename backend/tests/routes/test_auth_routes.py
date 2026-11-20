"""
Tests for POST /auth/login and for how login connects the other parts
of the system (customers, tokens, role checks, restaurants).
"""


import pytest
from fastapi.testclient import TestClient

from app.api.routes import restaurants as restaurant_routes
from app.main import app
from app.schemas.restaurant import Restaurant


@pytest.fixture
def client(customers_file):
    yield TestClient(app)
    app.dependency_overrides.clear()


def log_in(client, email="ana@example.com", password="Password123"):
    return client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )


def register(client, email="ana@example.com"):
    return client.post(
        "/customers/register",
        json={"name": "Ana", "email": email, "password": "Password123"},
    )


# ============================================================
# POST /auth/login
# ============================================================

def test_login_with_valid_credentials_returns_a_token(client):
    register(client)

    response = log_in(client)

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_ignores_email_capitalization(client):
    register(client)

    assert log_in(client, email="ANA@Example.com").status_code == 200


def test_wrong_password_returns_401(client):
    register(client)

    assert log_in(client, password="WrongPassword").status_code == 401


def test_unknown_email_returns_the_same_401_as_a_wrong_password(client):
    register(client)

    wrong_password = log_in(client, password="WrongPassword")
    unknown_email = log_in(client, email="nobody@example.com")

    assert unknown_email.status_code == 401
    assert unknown_email.json() == wrong_password.json()


def test_login_does_not_accept_credentials_in_the_url(client):
    register(client)

    response = client.post(
        "/auth/login?email=ana@example.com&password=Password123",
    )

    assert response.status_code == 422


def test_login_rejects_extra_fields(client):
    register(client)

    response = client.post(
        "/auth/login",
        json={
            "email": "ana@example.com",
            "password": "Password123",
            "role": "admin",
        },
    )

    assert response.status_code == 422


def test_deactivated_account_cannot_log_in(client, add_account):
    add_account("c1", email="ana@example.com", active=False)

    assert log_in(client).status_code == 403


# ============================================================
# Whole flow
# ============================================================

def test_register_login_use_token_and_log_in_again_later(client):
    """
    Register, log in, use the token, then "restart" and log in again.

    The app keeps nothing in memory between requests; accounts live
    in the customers file. A new TestClient on the same file stands
    in for restarting the server.
    """
    customer = register(client).json()
    token = log_in(client).json()["access_token"]

    own = client.get(
        f"/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert own.status_code == 200

    restarted = TestClient(app)
    again = log_in(restarted)

    assert again.status_code == 200
    assert restarted.get(
        f"/customers/{customer['id']}",
        headers={"Authorization": f"Bearer {again.json()['access_token']}"},
    ).json()["id"] == customer["id"]


# ============================================================
# Role checks on restaurant routes (auth + customers + restaurants)
# ============================================================

def test_owner_creates_a_restaurant_under_their_own_id(
    client,
    add_account,
    auth_headers,
    monkeypatch,
):
    add_account("owner-7", role="restaurant_owner")
    seen = {}

    def fake_create(restaurant_data, owner_id):
        seen["owner_id"] = owner_id
        return Restaurant(
            id=9,
            owner_id=owner_id,
            name=restaurant_data.name,
            cuisine=restaurant_data.cuisine,
            rating=0.0,
            address=restaurant_data.address,
        )

    monkeypatch.setattr(restaurant_routes, "create_restaurant", fake_create)

    response = client.post(
        "/restaurants",
        json={"name": "Cafe", "cuisine": "Canadian", "address": "1 Rd"},
        headers=auth_headers("owner-7", role="restaurant_owner"),
    )

    assert response.status_code == 201
    # The owner comes from the token, not from anything the client sent.
    assert seen["owner_id"] == "owner-7"


def test_customer_cannot_create_a_restaurant(
    client,
    add_account,
    auth_headers,
):
    add_account("customer-1")

    response = client.post(
        "/restaurants",
        json={"name": "Cafe", "cuisine": "Canadian", "address": "1 Rd"},
        headers=auth_headers("customer-1"),
    )

    assert response.status_code == 403


def test_creating_a_restaurant_without_a_token_returns_401(client):
    response = client.post(
        "/restaurants",
        json={"name": "Cafe", "cuisine": "Canadian", "address": "1 Rd"},
    )

    assert response.status_code == 401


def test_customer_cannot_edit_a_restaurant(
    client,
    add_account,
    auth_headers,
):
    add_account("customer-1")

    response = client.patch(
        "/restaurants/1",
        json={"name": "Renamed"},
        headers=auth_headers("customer-1"),
    )

    assert response.status_code == 403


# ============================================================
# Regression: a still-valid token must stop working on deactivation
# ============================================================

def test_regression_token_issued_before_deactivation_stops_working(client):
    """
    A token stays cryptographically valid for an hour. If the API only
    checked the token, a deactivated customer could keep ordering with
    the one they already held. The account is therefore re-checked on
    every request.
    """
    customer = register(client).json()
    token = log_in(client).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get(
        f"/customers/{customer['id']}",
        headers=headers,
    ).status_code == 200

    client.post(f"/customers/{customer['id']}/deactivate", headers=headers)

    assert client.get(
        f"/customers/{customer['id']}",
        headers=headers,
    ).status_code == 403
