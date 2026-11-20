"""
FastAPI routes for customer accounts.

    POST  /customers/register              create an account (public)
    GET   /customers/{customer_id}         read an account
    PATCH /customers/{customer_id}         update name or address
    POST  /customers/{customer_id}/deactivate   deactivate an account

Every route except registration requires a signed-in user. Who the
caller is comes from the token, never from the request body or URL.
The service checks that the caller owns the account.
"""


from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user
from app.schemas.customer import (
    Customer,
    CustomerCreate,
    CustomerUpdate,
)
from app.services.customer_service import (
    deactivate_customer,
    get_customer,
    register_customer,
    update_customer,
)


router = APIRouter()


@router.post(
    "/customers/register",
    response_model=Customer,
    status_code=status.HTTP_201_CREATED,
    summary="Register a customer account",
    description=(
        "Create a customer account. The password is stored hashed "
        "and is never returned. Returns 400 if the email is already "
        "registered and 422 for invalid input."
    ),
)
def register(customer_data: CustomerCreate):
    return register_customer(customer_data)


@router.get(
    "/customers/{customer_id}",
    response_model=Customer,
    summary="Get a customer account",
    description="Customers can read only their own account.",
)
def read_customer(
    customer_id: str,
    user: dict = Depends(get_current_user),
):
    return get_customer(customer_id, user)


@router.patch(
    "/customers/{customer_id}",
    response_model=Customer,
    summary="Update a customer account",
    description=(
        "Update the name and/or delivery address. "
        "Customers can update only their own account."
    ),
)
def edit_customer(
    customer_id: str,
    update_data: CustomerUpdate,
    user: dict = Depends(get_current_user),
):
    return update_customer(customer_id, update_data, user)


@router.post(
    "/customers/{customer_id}/deactivate",
    response_model=Customer,
    summary="Deactivate a customer account",
    description=(
        "Mark the account inactive. The record is kept, not deleted. "
        "A deactivated account can no longer sign in or use the API."
    ),
)
def deactivate(
    customer_id: str,
    user: dict = Depends(get_current_user),
):
    return deactivate_customer(customer_id, user)
