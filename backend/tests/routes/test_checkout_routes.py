from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import CUSTOMER, require_role
from app.schemas.order import Order
from app.services.checkout_service import CheckoutValidationError, checkout

router = APIRouter()

Customer = Annotated[dict, Depends(require_role(CUSTOMER))]


@router.post(
    "/customers/{customer_id}/checkout",
    response_model=Order,
    summary="Checkout cart into an order",
    description="Creates an order from the customer's cart. Cart is cleared only after the order is successfully saved.",
)
def checkout_endpoint(customer_id: str, user: Customer) -> Order:
    
    try:
        return checkout(customer_id, user)
    except CheckoutValidationError as error:
        detail = str(error)
        if any(w in detail.lower() for w in ("not found", "empty", "missing")):
            status = 400
        elif "unavailable" in detail.lower():
            status = 409
        elif any(w in detail.lower() for w in ("own", "inactive", "only customers")):
            status = 403
        else:
            status = 400
        raise HTTPException(status_code=status, detail=detail) from error