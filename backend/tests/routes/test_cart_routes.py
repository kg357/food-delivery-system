import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user
from app.api.routes.cart import get_cart_service
from app.main import app
from app.repositories.cart_repository import CartRepository
from app.services.cart_service import CartService


URL = "/customers/alice/cart"
ITEM = {"restaurant_id": 1, "item_id": "item-a", "quantity": 2}


@pytest.fixture
def cart_api(tmp_path, data_files, monkeypatch):
    user = {"id": "alice", "role": "customer", "active": True}
    service = CartService(CartRepository(tmp_path / "carts.json"), *data_files)
    monkeypatch.setitem(app.dependency_overrides, get_current_user, lambda: user)
    monkeypatch.setitem(app.dependency_overrides, get_cart_service, lambda: service)
    with TestClient(app) as client:
        yield client, user


def test_cart_api_lifecycle(cart_api):
    client, _ = cart_api
    empty = client.get(URL)
    assert empty.status_code == 200
    assert empty.headers["Cache-Control"] == "no-store"
    assert empty.json()["customer_id"] == "alice"
    assert empty.json()["subtotal"] == "0.00"
    assert client.get(URL).json() == empty.json()

    added = client.post(f"{URL}/items", json=ITEM)
    assert added.status_code == 200
    assert added.json()["items"] == [
        {
            "item_id": "item-a",
            "name": "Burger",
            "quantity": 2,
            "unit_price": "10.00",
            "total_price": "20.00",
        }
    ]
    assert added.json()["total"] == "20.00"
    assert client.get(URL).json() == added.json()

    changed = client.patch(f"{URL}/items/item-a", json={"quantity": 3})
    assert changed.status_code == 200
    assert changed.json()["subtotal"] == "30.00"
    assert client.delete(f"{URL}/items/item-a").json() == empty.json()

    client.post(f"{URL}/items", json=ITEM)
    assert client.delete(f"{URL}/items").json() == empty.json()
    assert client.delete(f"{URL}/items").json() == empty.json()


@pytest.mark.parametrize(
    ("method", "suffix", "body"),
    [
        ("GET", "", None),
        ("POST", "/items", ITEM),
        ("PATCH", "/items/item-a", {"quantity": 1}),
        ("DELETE", "/items/item-a", None),
        ("DELETE", "/items", None),
    ],
)
@pytest.mark.parametrize("identity", [{"id": "bob"}, {"active": False}, {"role": "admin"}])
def test_cart_endpoints_reject_other_inactive_or_wrong_role_users(
    cart_api, method, suffix, body, identity
):
    client, user = cart_api
    client.get(URL)
    original = client.post(f"{URL}/items", json=ITEM).json()
    owner = user.copy()
    user.update(identity)
    assert client.request(method, URL + suffix, json=body).status_code == 403
    user.update(owner)
    assert client.get(URL).json() == original


@pytest.mark.parametrize("quantity", [0, -1, 1.5, "2", True, None, 2_147_483_648])
def test_cart_api_rejects_invalid_quantities(cart_api, quantity):
    client, _ = cart_api
    client.get(URL)
    original = client.post(f"{URL}/items", json=ITEM).json()
    assert client.post(f"{URL}/items", json={**ITEM, "quantity": quantity}).status_code == 422
    assert client.patch(
        f"{URL}/items/item-a", json={"quantity": quantity}
    ).status_code == 422
    assert client.get(URL).json() == original


def test_cart_api_returns_business_rule_errors(cart_api):
    client, _ = cart_api
    assert client.post(f"{URL}/items", json=ITEM).status_code == 404
    client.get(URL)
    assert client.delete(f"{URL}/items/missing").status_code == 404
    assert client.patch(f"{URL}/items/missing", json={"quantity": 1}).status_code == 404
    assert client.post(f"{URL}/items", json={**ITEM, "item_id": "missing"}).status_code == 404
    assert client.post(f"{URL}/items", json={**ITEM, "unit_price": 0}).status_code == 422
    client.post(f"{URL}/items", json=ITEM)
    assert client.post(
        f"{URL}/items", json={"restaurant_id": 2, "item_id": "item-c"}
    ).status_code == 409
