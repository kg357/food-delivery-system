"""
Tests for the customer service (registration, ownership, updates).

These call the service directly with a temporary file, so they test
the business rules without any HTTP involved.
"""


import pytest
from fastapi import HTTPException

from app.core.security import verify_password
from app.repositories.customer_repository import load_customers
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.customer_service import (
    deactivate_customer,
    get_customer,
    register_customer,
    update_customer,
    verify_customer_access,
)


@pytest.fixture
def path(tmp_path):
    return tmp_path / "customers.json"


def new_customer(email="ana@example.com", password="Password123"):
    return CustomerCreate(
        name="Ana",
        email=email,
        password=password,
        address="1 Main St",
    )


def user(user_id, role="customer"):
    return {"id": user_id, "role": role, "active": True}


# ============================================================
# Registration
# ============================================================

def test_register_creates_an_active_customer(path):
    customer = register_customer(new_customer(), path)

    assert customer.role == "customer"
    assert customer.active is True
    assert customer.email == "ana@example.com"
    assert isinstance(customer.id, str)


def test_register_stores_a_hash_not_the_password(path):
    register_customer(new_customer(), path)

    stored = load_customers(path)[0]

    assert stored["password_hash"] != "Password123"
    assert verify_password("Password123", stored["password_hash"])


def test_register_result_has_no_password_fields(path):
    customer = register_customer(new_customer(), path)

    assert "password" not in customer.model_dump()
    assert "password_hash" not in customer.model_dump()


def test_register_gives_each_customer_a_unique_id(path):
    first = register_customer(new_customer("a@example.com"), path)
    second = register_customer(new_customer("b@example.com"), path)

    assert first.id != second.id


def test_register_rejects_a_duplicate_email(path):
    register_customer(new_customer(), path)

    with pytest.raises(HTTPException) as error:
        register_customer(new_customer(), path)

    assert error.value.status_code == 400
    assert len(load_customers(path)) == 1


def test_register_treats_emails_as_case_insensitive(path):
    register_customer(new_customer("ana@example.com"), path)

    with pytest.raises(HTTPException) as error:
        register_customer(new_customer("ANA@Example.com"), path)

    assert error.value.status_code == 400


# ============================================================
# Ownership
# ============================================================

def test_owner_may_access_their_own_account():
    verify_customer_access("c1", user("c1"))


def test_another_customer_may_not_access_the_account():
    with pytest.raises(HTTPException) as error:
        verify_customer_access("c1", user("c2"))

    assert error.value.status_code == 403


def test_admin_may_access_any_account():
    verify_customer_access("c1", user("admin-1", role="admin"))


def test_access_is_checked_before_existence(path):
    """A stranger gets 403 even for an ID that does not exist."""
    with pytest.raises(HTTPException) as error:
        get_customer("does-not-exist", user("c2"), path)

    assert error.value.status_code == 403


# ============================================================
# Retrieval, update, deactivation
# ============================================================

def test_get_returns_own_account(path):
    created = register_customer(new_customer(), path)

    assert get_customer(created.id, user(created.id), path).name == "Ana"


def test_get_missing_account_as_admin_returns_404(path):
    with pytest.raises(HTTPException) as error:
        get_customer("nope", user("admin-1", role="admin"), path)

    assert error.value.status_code == 404


def test_update_changes_only_the_supplied_fields(path):
    created = register_customer(new_customer(), path)

    updated = update_customer(
        created.id,
        CustomerUpdate(address="9 New Rd"),
        user(created.id),
        path,
    )

    assert updated.address == "9 New Rd"
    assert updated.name == "Ana"
    assert load_customers(path)[0]["address"] == "9 New Rd"


def test_update_by_another_customer_is_rejected_and_changes_nothing(path):
    created = register_customer(new_customer(), path)

    with pytest.raises(HTTPException) as error:
        update_customer(
            created.id,
            CustomerUpdate(name="Hacked"),
            user("someone-else"),
            path,
        )

    assert error.value.status_code == 403
    assert load_customers(path)[0]["name"] == "Ana"


def test_deactivate_keeps_the_record(path):
    created = register_customer(new_customer(), path)

    result = deactivate_customer(created.id, user(created.id), path)

    assert result.active is False
    stored = load_customers(path)
    assert len(stored) == 1
    assert stored[0]["active"] is False


def test_deactivating_twice_is_harmless(path):
    created = register_customer(new_customer(), path)

    deactivate_customer(created.id, user(created.id), path)
    again = deactivate_customer(created.id, user(created.id), path)

    assert again.active is False


def test_deactivate_by_another_customer_is_rejected(path):
    created = register_customer(new_customer(), path)

    with pytest.raises(HTTPException) as error:
        deactivate_customer(created.id, user("someone-else"), path)

    assert error.value.status_code == 403
    assert load_customers(path)[0]["active"] is True
