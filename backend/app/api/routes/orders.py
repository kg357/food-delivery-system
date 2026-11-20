from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import CUSTOMER, require_role
from app.services.order_service import get_order, get_orders_by_customer

router = APIRouter()

@router.get("/orders/{order_id}")
def order_details(
    order_id: str,
    user: dict = Depends(require_role(CUSTOMER))  # noqa: B008
    ):
    """
    Retrieve an order by its ID.

    Args:
        order_id (str): The ID of the order to retrieve.

    Returns:
        A dictionary representing the order if found, otherwise raises an HTTPException.
    """
    try:
        order = get_order(order_id)

        if(order["customer_id"] != user["id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this order."
            )
        return order
    
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/customers/{customer_id}/orders")

def customer_orders(
    customer_id: str,
    user: dict = Depends(  # noqa: B008
        require_role(CUSTOMER)  # noqa: B008
    ),
):
    """
        Retrieve all orders for a specific customer.
    
        Args:
            customer_id (str): The ID of the customer whose orders to retrieve.
    
        Returns:
            A list of dictionaries representing the orders for the specified customer.
        """
    if customer_id != user["id"]:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to access this order history"
            ),
        )

    return get_orders_by_customer(
        customer_id
    )