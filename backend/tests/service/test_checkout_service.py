import pytest
from decimal import Decimal

from app.services.checkout_service import (
    CheckoutValidationError,
    validate_checkout,
    checkout,
)
from app.services.cart_service import CartService
from app.repositories.cart_repository import CartRepository
from app.schemas.cart import Cart, CartItem


def test_inactive_customer_fails():
    with pytest.raises(
        CheckoutValidationError,
        match="inactive",
    ):
        validate_checkout(
            "customer-1",
            {
                "id": "customer-1",
                "role": "customer",
                "active": False,
            },
        )


def test_wrong_customer_fails():
    with pytest.raises(
        CheckoutValidationError,
        match="own this cart",
    ):
        validate_checkout(
            "customer-1",
            {
                "id": "customer-2",
                "role": "customer",
                "active": True,
            },
        )


def test_wrong_role_fails():
    with pytest.raises(
        CheckoutValidationError,
        match="Only customers",
    ):
        validate_checkout(
            "customer-1",
            {
                "id": "admin-1",
                "role": "admin",
                "active": True,
            },
        )


@pytest.fixture
def customer():
    return {"id": "cust-1", "role": "customer", "active": True}


@pytest.fixture
def cart_service(tmp_path):
    path = tmp_path / "carts.json"
    path.write_text("{}")
    return CartService(CartRepository(path))


def _seed(service, customer_id, items, restaurant_id=1):
    cart = Cart(
        id="cart-1",
        customer_id=customer_id,
        restaurant_id=restaurant_id,
        items=items,
    )
    service.repository.change(customer_id, lambda _: cart)


def test_successful_checkout_creates_order_and_clears_cart(
    customer, cart_service, monkeypatch
):
    _seed(
        cart_service,
        "cust-1",
        [CartItem(item_id="item-1", name="Old", unit_price=Decimal("10.00"), quantity=2)],
    )

    # Make validate_checkout use the same temporary repository
    monkeypatch.setattr(
        "app.services.checkout_service.CartRepository",
        lambda: cart_service.repository,
    )

    monkeypatch.setattr(
        "app.services.checkout_service.get_menu_item_for_restaurant",
        lambda restaurant_id, item_id, **kwargs: {
            "id": "item-1",
            "name": "Burger",
            "description": "Tasty",
            "price": 10.00,
            "available": True,
        },
    )

    monkeypatch.setattr(
        "app.services.checkout_service.create_order",
        lambda order_data, path=None: order_data,
    )

    order = checkout("cust-1", customer, cart_service=cart_service)

    assert order.customer_id == "cust-1"
    assert order.items[0].name == "Burger"
    assert order.total == 20.0

    remaining = cart_service.repository.get("cust-1")
    assert remaining.items == []

def test_failed_checkout_does_not_clear_cart(customer, cart_service, monkeypatch):
    _seed(
        cart_service,
        "cust-1",
        [CartItem(item_id="item-1", name="X", unit_price=Decimal("5"), quantity=1)],
    )

    # Use the temporary repository
    monkeypatch.setattr(
        "app.services.checkout_service.CartRepository",
        lambda: cart_service.repository,
    )

    monkeypatch.setattr(
        "app.services.checkout_service.get_menu_item_for_restaurant",
        lambda *a, **k: {
            "name": "X",
            "description": "",
            "price": 5.0,
            "available": False,
        },
    )

    with pytest.raises(CheckoutValidationError):
        checkout("cust-1", customer, cart_service=cart_service)

    remaining = cart_service.repository.get("cust-1")
    assert len(remaining.items) == 1


def test_empty_cart_rejected(customer, cart_service, monkeypatch):
    # Force validate_checkout to use the empty temp repository
    monkeypatch.setattr(
        "app.services.checkout_service.CartRepository",
        lambda: cart_service.repository,
    )

    with pytest.raises(CheckoutValidationError):
        checkout("cust-1", customer, cart_service=cart_service)