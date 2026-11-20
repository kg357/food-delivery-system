from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_current_user,
)
from app.main import app

client = TestClient(app)


def test_customer_cannot_access_other_history():

    app.dependency_overrides[
        get_current_user
    ] = lambda: {
        "id": "customer-1",
        "role": "customer",
        "active": True,
    }

    response = client.get(
        "/customers/customer-2/orders"
    )

    assert response.status_code == 403

    app.dependency_overrides.clear()

def test_non_customer_cannot_access_order_history():

    app.dependency_overrides[
        get_current_user
    ] = lambda: {
        "id": "owner-1",
        "role": "restaurant_owner",
        "active": True,
    }

    response = client.get(
        "/customers/customer-1/orders"
    )

    assert response.status_code == 403

    app.dependency_overrides.clear()


def test_customer_can_access_own_history():

    app.dependency_overrides[
        get_current_user
    ] = lambda: {
        "id": "customer-1",
        "role": "customer",
        "active": True,
    }

    response = client.get(
        "/customers/customer-1/orders"
    )

    assert response.status_code == 200

    app.dependency_overrides.clear()