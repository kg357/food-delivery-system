import json

from app.repositories.order_repository import (
    create_order,
    load_order_by_id,
    load_orders_by_customer,
)


def test_create_order_persists_order(tmp_path):
    """
    Verify that a new order is persisted to storage.
    """

    test_file = tmp_path / "orders.json"

    test_file.write_text("[]")

    order = {
        "id": "order-1",
        "customer_id": "customer-1",
        "restaurant_id": 2,
        "items": ["Pizza"],
        "subtotal": 20.0,
        "total": 25.0,
    }

    create_order(
        order=order,
        path=test_file,
    )

    with test_file.open(
        encoding="utf-8"
    ) as file:

        saved_orders = json.load(file)

    assert len(saved_orders) == 1

    assert saved_orders[0] == order


def test_load_order_by_id(tmp_path):
    """
    Verify that an order can be retrieved by ID.
    """

    test_file = tmp_path / "orders.json"

    order = {
        "id": "order-1",
        "customer_id": "customer-1",
        "restaurant_id": 2,
        "items": [],
        "subtotal": 10.0,
        "total": 10.0,
    }

    test_file.write_text(
        json.dumps([order])
    )

    result = load_order_by_id(
        "order-1",
        test_file,
    )

    assert result == order


def test_load_order_by_id_returns_none_for_missing_order(tmp_path):
    """
    Verify that None is returned for a missing order.
    """

    test_file = tmp_path / "orders.json"

    test_file.write_text("[]")

    result = load_order_by_id(
        "missing",
        test_file,
    )

    assert result is None


def test_load_orders_by_customer(tmp_path):
    """
    Verify that only the selected customer's
    orders are returned.
    """

    test_file = tmp_path / "orders.json"

    orders = [
        {
            "id": "order-1",
            "customer_id": "customer-1",
            "restaurant_id": 1,
            "items": [],
            "subtotal": 10.0,
            "total": 10.0,
        },
        {
            "id": "order-2",
            "customer_id": "customer-2",
            "restaurant_id": 2,
            "items": [],
            "subtotal": 20.0,
            "total": 20.0,
        },
    ]

    test_file.write_text(
        json.dumps(orders)
    )

    result = load_orders_by_customer(
        "customer-1",
        test_file,
    )

    assert len(result) == 1

    assert result[0]["id"] == "order-1"


def test_load_orders_by_customer_returns_empty_list(tmp_path):
    """
    Verify an empty order history returns an empty list.
    """

    test_file = tmp_path / "orders.json"

    test_file.write_text("[]")

    result = load_orders_by_customer(
        "unknown-customer",
        test_file,
    )

    assert result == []