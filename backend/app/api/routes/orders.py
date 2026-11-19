from fastapi import APIRouter, HTTPException

from app.services.order_service import get_order, get_orders_by_customer

router = APIRouter()

@router.get("/orders/{order_id}")
def order_details(order_id: str):
    """
    Retrieve an order by its ID.

    Args:
        order_id (str): The ID of the order to retrieve.

    Returns:
        A dictionary representing the order if found, otherwise raises an HTTPException.
    """
    try:
        return get_order(order_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/customers/{customer_id}/orders")
def customer_orders(customer_id: str):
    """
    Retrieve all orders for a specific customer.

    Args:
        customer_id (str): The ID of the customer whose orders to retrieve.

    Returns:
        A list of dictionaries representing the orders for the specified customer.
    """
    return get_orders_by_customer(customer_id)