import json
from pathlib import Path

from app.core.config import ORDERS_FILE


def load_orders(path: Path = ORDERS_FILE) -> list:
    """
    Load orders from a JSON file.

    Args:
        path (Path): The path to the JSON file containing orders.

    Returns:
        A list of order dictionaries.
    """
    with open(encoding="utf-8") as file:
        return json.load(file)


def save_orders(orders: list[dict], path: Path = ORDERS_FILE):
    with path.open("w", encoding="utf-8") as file:
        json.dump(orders, file, indent=4)

def create_order(order: dict, path: Path = ORDERS_FILE):
    """
    Create a new order and save it to the JSON file.

    Args:
        order (dict): The order data to be saved.
        path (Path): The path to the JSON file containing orders.
    """
    orders = load_orders(path)
    orders.append(order)
    save_orders(orders, path)

    return order

def load_order_by_id(order_id: str, path: Path = ORDERS_FILE):
    """
    Load an order by its ID from a JSON file.

    Args:
        order_id (str): The ID of the order to retrieve.
        path (Path): The path to the JSON file containing orders.

    Returns:
        A dictionary representing the order if found, otherwise None.
    """
    orders = load_orders(path)
    for order in orders:
        if order["id"] == order_id:
            return order
    return None

def load_orders_by_customer(customer_id: str, path: Path = ORDERS_FILE):
    """
    Load all orders for a specific customer from a JSON file.

    Args:
        customer_id (str): The ID of the customer whose orders to retrieve.
        path (Path): The path to the JSON file containing orders.

    Returns:
        A list of dictionaries representing the orders for the specified customer.
    """
    orders = load_orders(path)
    return [order for order in orders if order["customer_id"] == customer_id]