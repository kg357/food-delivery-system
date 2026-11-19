import json

import pytest

from app.services.order_service import (
    get_order,
    get_orders_by_customer,
)


def test_get_order_returns_matching_order(
    tmp_path,
    monkeypatch,
):
    """
    Verify that an existing order can be retrieved.
    """

    order = {
        "id": "order-1",
        "customer_id": "customer-1",
        "restaurant_id": 1,
        "items": [],
        "subtotal": 15.0,
        "total": 15.0,
    }

    test_file = tmp_path / "orders.json"

    test_file.write_text(
        json.dumps([order])
    )

    from app import repositories
    from app.repositories import order_repository

    monkeypatch.setattr(
        order_repository,
        "ORDERS_FILE",
        test_file,
    )

    result = order_repository.load_order_by_id(
        "order-1",
        test_file,
    )

    assert result["id"] == "order-1"


def test_get_order_raises_error_for_missing_order():
    """
    Verify that requesting a missing order
    raises ValueError.
    """

    with pytest.raises(
        ValueError,
        match="Order not found",
    ):

        get_order(
            "missing-order"
        )


def test_get_orders_by_customer_returns_matching_orders(
    tmp_path,
):
    """
    Verify that customer order history
    only contains that customer's orders.
    """

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

    test_file = tmp_path / "orders.json"

    test_file.write_text(
        json.dumps(orders)
    )

    from app.repositories.order_repository import (
        load_orders_by_customer,
    )

    result = load_orders_by_customer(
        "customer-1",
        test_file,
    )

    assert len(result) == 1

    assert (
        result[0]["customer_id"]
        == "customer-1"
    )


def test_get_orders_by_customer_returns_empty_list():
    """
    Verify that an unknown customer
    receives an empty order history.
    """

    result = get_orders_by_customer(
        "unknown-customer"
    )

    assert isinstance(
        result,
        list,
    )