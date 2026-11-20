from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_current_user,
)
from app.main import app

client = TestClient(app)


def test_get_order_returns_404_for_missing_order():

    app.dependency_overrides[
        get_current_user
    ] = lambda: {
        "id": "customer-1",
        "role": "customer",
        "active": True,
    }

    try:

        response = client.get(
            "/orders/nonexistent-order"
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": "Order not found"
        }

    finally:

        app.dependency_overrides.clear()


def test_get_customer_orders_returns_success():

    app.dependency_overrides[
        get_current_user
    ] = lambda: {
        "id": "customer-1",
        "role": "customer",
        "active": True,
    }

    try:

        response = client.get(
            "/customers/customer-1/orders"
        )

        assert response.status_code == 200

    finally:

        app.dependency_overrides.clear()


def test_get_customer_orders_returns_list():

    app.dependency_overrides[
        get_current_user
    ] = lambda: {
        "id": "customer-1",
        "role": "customer",
        "active": True,
    }

    try:

        response = client.get(
            "/customers/customer-1/orders"
        )

        assert isinstance(
            response.json(),
            list,
        )

    finally:

        app.dependency_overrides.clear()