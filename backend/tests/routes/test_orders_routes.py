from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_order_returns_404_for_missing_order():
    """
    Verify that requesting a nonexistent order
    returns HTTP 404.
    """

    response = client.get(
        "/orders/nonexistent-order"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Order not found"
    }


def test_get_customer_orders_returns_success():
    """
    Verify that customer order history endpoint
    returns HTTP 200.
    """

    response = client.get(
        "/customers/customer-1/orders"
    )

    assert response.status_code == 200


def test_get_customer_orders_returns_list():
    """
    Verify that the response body is a list.
    """

    response = client.get(
        "/customers/customer-1/orders"
    )

    assert isinstance(
        response.json(),
        list,
    )