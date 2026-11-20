"""
Tests for the customer account routes.

These send real HTTP requests to the app with real login tokens.
Only the customers file is replaced, by a temporary one.
"""


import json

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(customers_file):
    yield TestClient(app)
    app.dependency_overrides.clear()


def register(client, email="ana@example.com", **overrides):
    body = {
        "name": "Ana",
        "email": email,
        "password": "Password123",
        "address": "1 Main St",
    }
    body.update(overrides)
    return client.post("/customers/register", json=body)


# ============================================================
# POST /customers/register
# ============================================================

def test_register_returns_201_and_the_customer(client):
    response = register(client)

    body = response.json()

    assert response.status_code == 201
    assert body["name"] == "Ana"
    assert body["email"] == "ana@example.com"
    assert body["role"] == "customer"
    assert body["active"] is True
    assert isinstance(body["id"], str)


def test_register_never_returns_the_password_or_its_hash(client):
    body = register(client).json()

    assert "password" not in body
    assert "password_hash" not in body


def test_register_stores_a_hash_in_the_file(client, customers_file):
    register(client)

    stored = json.loads(customers_file.read_text(encoding="utf-8"))[0]

    assert stored["password_hash"] != "Password123"
    assert stored["password_hash"].startswith("$2")


def test_register_duplicate_email_returns_400(client):
    register(client)

    response = register(client)

    assert response.status_code == 400


def test_register_duplicate_email_ignores_case(client):
    register(client, email="ana@example.com")

    assert register(client, email="ANA@example.com").status_code == 400


@pytest.mark.parametrize(
    "overrides",
    [
        {"name": ""},
        {"email": "not-an-email"},
        {"password": "short"},
        {"password": "x" * 73},
        {"password": "é" * 40},
        {"role": "admin"},
        {"active": False},
        {"id": "chosen-by-client"},
    ],
)
def test_register_rejects_invalid_or_forbidden_input(client, overrides):
    assert register(client, **overrides).status_code == 422


def test_register_with_missing_field_returns_422(client):
    response = client.post(
        "/customers/register",
        json={"name": "Ana", "email": "ana@example.com"},
    )

    assert response.status_code == 422


# ============================================================
# GET /customers/{id}
# ============================================================

def test_customer_can_read_their_own_account(client, auth_headers):
    customer = register(client).json()

    response = client.get(
        f"/customers/{customer['id']}",
        headers=auth_headers(customer["id"]),
    )

    assert response.status_code == 200
    assert response.json() == customer


def test_customer_cannot_read_another_account(client, auth_headers):
    first = register(client, email="a@example.com").json()
    second = register(client, email="b@example.com").json()

    response = client.get(
        f"/customers/{first['id']}",
        headers=auth_headers(second["id"]),
    )

    assert response.status_code == 403


def test_reading_without_a_token_returns_401(client):
    customer = register(client).json()

    assert client.get(f"/customers/{customer['id']}").status_code == 401


def test_admin_can_read_any_account(client, add_account, auth_headers):
    customer = register(client).json()
    add_account("admin-1", role="admin")

    response = client.get(
        f"/customers/{customer['id']}",
        headers=auth_headers("admin-1", role="admin"),
    )

    assert response.status_code == 200


def test_admin_reading_a_missing_account_returns_404(
    client,
    add_account,
    auth_headers,
):
    add_account("admin-1", role="admin")

    response = client.get(
        "/customers/does-not-exist",
        headers=auth_headers("admin-1", role="admin"),
    )

    assert response.status_code == 404


# ============================================================
# PATCH /customers/{id}
# ============================================================

def test_customer_can_update_name_and_address(client, auth_headers):
    customer = register(client).json()

    response = client.patch(
        f"/customers/{customer['id']}",
        json={"name": "Ana B", "address": "9 New Rd"},
        headers=auth_headers(customer["id"]),
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Ana B"
    assert response.json()["address"] == "9 New Rd"


def test_partial_update_leaves_other_fields_alone(client, auth_headers):
    customer = register(client).json()

    response = client.patch(
        f"/customers/{customer['id']}",
        json={"address": "9 New Rd"},
        headers=auth_headers(customer["id"]),
    )

    assert response.json()["name"] == "Ana"
    assert response.json()["email"] == "ana@example.com"


def test_update_is_saved_in_the_file(client, customers_file, auth_headers):
    customer = register(client).json()

    client.patch(
        f"/customers/{customer['id']}",
        json={"name": "Ana B"},
        headers=auth_headers(customer["id"]),
    )

    stored = json.loads(customers_file.read_text(encoding="utf-8"))[0]
    assert stored["name"] == "Ana B"


def test_customer_cannot_update_another_account(client, auth_headers):
    first = register(client, email="a@example.com").json()
    second = register(client, email="b@example.com").json()

    response = client.patch(
        f"/customers/{first['id']}",
        json={"name": "Hacked"},
        headers=auth_headers(second["id"]),
    )

    assert response.status_code == 403

    check = client.get(
        f"/customers/{first['id']}",
        headers=auth_headers(first["id"]),
    )
    assert check.json()["name"] == "Ana"


@pytest.mark.parametrize(
    "body",
    [
        {"role": "admin"},
        {"active": False},
        {"email": "new@example.com"},
        {"password": "NewPassword123"},
        {"name": None},
        {"name": ""},
    ],
)
def test_update_rejects_protected_or_invalid_fields(
    client,
    auth_headers,
    body,
):
    customer = register(client).json()

    response = client.patch(
        f"/customers/{customer['id']}",
        json=body,
        headers=auth_headers(customer["id"]),
    )

    assert response.status_code == 422


def test_update_without_a_token_returns_401(client):
    customer = register(client).json()

    response = client.patch(
        f"/customers/{customer['id']}",
        json={"name": "X"},
    )

    assert response.status_code == 401


# ============================================================
# POST /customers/{id}/deactivate
# ============================================================

def test_customer_can_deactivate_their_own_account(
    client,
    customers_file,
    auth_headers,
):
    customer = register(client).json()

    response = client.post(
        f"/customers/{customer['id']}/deactivate",
        headers=auth_headers(customer["id"]),
    )

    assert response.status_code == 200
    assert response.json()["active"] is False

    # The record is kept, not deleted.
    stored = json.loads(customers_file.read_text(encoding="utf-8"))
    assert len(stored) == 1
    assert stored[0]["active"] is False


def test_customer_cannot_deactivate_another_account(client, auth_headers):
    first = register(client, email="a@example.com").json()
    second = register(client, email="b@example.com").json()

    response = client.post(
        f"/customers/{first['id']}/deactivate",
        headers=auth_headers(second["id"]),
    )

    assert response.status_code == 403


def test_deactivated_customer_is_locked_out(client, auth_headers):
    customer = register(client).json()
    headers = auth_headers(customer["id"])

    client.post(f"/customers/{customer['id']}/deactivate", headers=headers)

    # Their old token no longer works...
    assert client.get(
        f"/customers/{customer['id']}",
        headers=headers,
    ).status_code == 403

    # ...and they cannot sign in again.
    login = client.post(
        "/auth/login",
        json={"email": "ana@example.com", "password": "Password123"},
    )
    assert login.status_code == 403
