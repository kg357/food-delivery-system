from app.repositories.order_repository import (
    load_order_by_id,
    load_orders_by_customer,
)

def get_order(order_id: str):
    """
    Retrieve an order by its ID.

    Args:
        order_id (str): The ID of the order to retrieve.

    Returns:
        A dictionary representing the order if found, otherwise None.
    """
    order = load_order_by_id(order_id);

    if order is None:
        raise ValueError("Order not found")
    
    return order



def get_orders_by_customer(customer_id: str):
    """
    Retrieve all orders for a specific customer.

    Args:
        customer_id (str): The ID of the customer whose orders to retrieve.

    Returns:
        A list of dictionaries representing the orders for the specified customer.
    """
    return load_orders_by_customer(customer_id)