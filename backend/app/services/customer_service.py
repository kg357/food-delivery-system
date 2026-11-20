"""
Business logic for customer accounts.

The service sits between the routes and the customer repository.
It hashes passwords, rejects duplicate emails, and decides who is
allowed to see or change which account.

Ownership rule: a signed-in user may use only their own account.
An admin may use any account. The check runs BEFORE the lookup, so
asking for someone else's account gives 403 whether or not it exists,
and nobody can use the API to find out which accounts exist.
"""


from pathlib import Path

from fastapi import HTTPException

from app.core.identifiers import generate_customer_id
from app.core.roles import ADMIN, CUSTOMER
from app.core.security import hash_password
from app.repositories.customer_repository import (
    load_customer_by_email,
    load_customer_by_id,
    load_customers,
    save_customers,
)
from app.schemas.customer import (
    Customer,
    CustomerCreate,
    CustomerUpdate,
)


# ============================================================
# Ownership
# ============================================================

def verify_customer_access(customer_id: str, user: dict) -> None:
    """
    Allow the account's owner or an admin; otherwise raise 403.

    Args:
        customer_id: The account being accessed.
        user: The signed-in user, as returned by get_current_user.
    """
    if user["role"] == ADMIN or user["id"] == customer_id:
        return

    raise HTTPException(
        status_code=403,
        detail="You do not have permission to access this account.",
    )


# ============================================================
# Registration
# ============================================================

def register_customer(
    data: CustomerCreate,
    path: Path | None = None,
) -> Customer:
    """
    Create a new customer account.

    Raises:
        HTTPException: 400 if the email is already registered.

    New accounts always get the customer role and start active.
    The password is stored only as a bcrypt hash.
    """
    if load_customer_by_email(data.email, path) is not None:
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists.",
        )

    record = {
        "id": generate_customer_id(),
        "name": data.name,
        "email": data.email,
        "address": data.address,
        "role": CUSTOMER,
        "active": True,
        "password_hash": hash_password(data.password),
    }

    customers = load_customers(path)
    customers.append(record)
    save_customers(customers, path)

    # Customer has no password_hash field, so it is left out.
    return Customer(**record)


# ============================================================
# Retrieval
# ============================================================

def get_customer(
    customer_id: str,
    user: dict,
    path: Path | None = None,
) -> Customer:
    """
    Return one account.

    Raises:
        HTTPException: 403 if the user may not access it,
            404 if it does not exist.
    """
    verify_customer_access(customer_id, user)

    record = load_customer_by_id(customer_id, path)

    if record is None:
        raise HTTPException(status_code=404, detail="Customer not found.")

    return Customer(**record)


# ============================================================
# Update
# ============================================================

def update_customer(
    customer_id: str,
    data: CustomerUpdate,
    user: dict,
    path: Path | None = None,
) -> Customer:
    """
    Update the name and/or delivery address of an account.

    Raises:
        HTTPException: 403 if the user may not access it,
            404 if it does not exist.
    """
    verify_customer_access(customer_id, user)

    customers = load_customers(path)

    # exclude_unset keeps only the fields the client actually sent.
    changes = data.model_dump(exclude_unset=True)

    for record in customers:
        if record["id"] == customer_id:
            record.update(changes)
            save_customers(customers, path)
            return Customer(**record)

    raise HTTPException(status_code=404, detail="Customer not found.")


# ============================================================
# Deactivation
# ============================================================

def deactivate_customer(
    customer_id: str,
    user: dict,
    path: Path | None = None,
) -> Customer:
    """
    Deactivate an account without deleting its record.

    The record stays so existing orders still point at a real customer.
    Deactivating twice is harmless.

    Raises:
        HTTPException: 403 if the user may not access it,
            404 if it does not exist.
    """
    verify_customer_access(customer_id, user)

    customers = load_customers(path)

    for record in customers:
        if record["id"] == customer_id:
            record["active"] = False
            save_customers(customers, path)
            return Customer(**record)

    raise HTTPException(status_code=404, detail="Customer not found.")
