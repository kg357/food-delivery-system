import json
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from uuid import UUID

import pytest
from app.repositories.cart_repository import CartRepository
from app.schemas.cart import MAX_QUANTITY, CartItemCreate, CartQuantityUpdate
from app.services.cart_service import (
    CartConflict,
    CartForbidden,
    CartNotFound,
    CartService,
)

CUSTOMER = {"id": "alice", "role": "customer", "active": True}
BURGER = CartItemCreate(restaurant_id=1, item_id="item-a", quantity=2)

@pytest.fixture
def service(tmp_path, data_files):
    return CartService(CartRepository(tmp_path / "carts.json"), *data_files)

def test_get_or_create_returns_stable_customer_specific_cart(service):
    first = service.get_or_create("alice", CUSTOMER)
    other = service.get_or_create("bob", {**CUSTOMER, "id": "bob"})

    assert service.get_or_create("alice", CUSTOMER) == first
    assert UUID(first.id).version == 4
    assert first.id != other.id
    assert first.restaurant_id is None
    assert first.items == []
    assert first.total == Decimal("0.00")

@pytest.mark.parametrize(
    "user",
    [
        {**CUSTOMER, "id": "bob"},
        {**CUSTOMER, "active": False},
        {**CUSTOMER, "role": "restaurant_owner"},
    ],
)
def test_invalid_customer_cannot_create_or_modify_cart(service, user):
    with pytest.raises(CartForbidden):
        service.get_or_create("alice", user)
    assert service.repository.get("alice") is None

    original = service.get_or_create("alice", CUSTOMER)
    with pytest.raises(CartForbidden):
        service.add("alice", user, BURGER)
    assert service.repository.get("alice") == original

def test_cart_mutations_require_an_existing_cart(service):
    with pytest.raises(CartNotFound, match="Active cart"):
        service.add("alice", CUSTOMER, BURGER)
    assert service.repository.get("alice") is None

def test_add_update_remove_and_clear(service):
    original = service.get_or_create("alice", CUSTOMER)
    service.add("alice", CUSTOMER, BURGER)
    cart = service.add("alice", CUSTOMER, BURGER)
    assert len(cart.items) == 1
    assert cart.items[0].quantity == 4
    assert cart.restaurant_id == 1
    assert cart.subtotal == cart.total == Decimal("40.00")

    cart = service.update_quantity("alice", CUSTOMER, "item-a", CartQuantityUpdate(quantity=3))
    assert cart.total == Decimal("30.00")

    service.add("alice", CUSTOMER, CartItemCreate(restaurant_id=1, item_id="item-b"))
    cart = service.remove("alice", CUSTOMER, "item-a")
    assert cart.restaurant_id == 1
    assert cart.total == Decimal("5.00")
    assert service.remove("alice", CUSTOMER, "item-b") == original

    service.add("alice", CUSTOMER, CartItemCreate(restaurant_id=2, item_id="item-c"))
    assert service.clear("alice", CUSTOMER) == original

def test_add_validates_catalog_and_preserves_contents_on_failure(service, menu_data):
    menu_data[1]["available"] = False
    service.menu_items_path.write_text(json.dumps(menu_data), encoding="utf-8")
    service.get_or_create("alice", CUSTOMER)

    with pytest.raises(CartNotFound, match="Restaurant"):
        service.add("alice", CUSTOMER, CartItemCreate(restaurant_id=99, item_id="item-a"))
    with pytest.raises(CartNotFound, match="Menu item"):
        service.add("alice", CUSTOMER, CartItemCreate(restaurant_id=1, item_id="item-c"))
    with pytest.raises(CartConflict, match="unavailable"):
        service.add("alice", CUSTOMER, CartItemCreate(restaurant_id=1, item_id="item-b"))

    original = service.add("alice", CUSTOMER, BURGER)
    with pytest.raises(CartConflict, match="one restaurant"):
        service.add("alice", CUSTOMER, CartItemCreate(restaurant_id=2, item_id="item-c"))
    with pytest.raises(CartNotFound, match="Cart item"):
        service.remove("alice", CUSTOMER, "item-b")
    assert service.repository.get("alice") == original

def test_server_calculates_totals_exactly_from_catalog_prices(service, menu_data):
    menu_data[0]["price"] = 0.105
    menu_data[1]["price"] = 0.20
    service.menu_items_path.write_text(json.dumps(menu_data), encoding="utf-8")
    service.get_or_create("alice", CUSTOMER)

    service.add("alice", CUSTOMER, BURGER)
    cart = service.add("alice", CUSTOMER, CartItemCreate(restaurant_id=1, item_id="item-b"))
    assert cart.items[0].unit_price == Decimal("0.11")
    assert cart.items[0].total_price == Decimal("0.22")
    assert cart.subtotal == cart.total == Decimal("0.42")
    assert CartRepository(service.repository.path).get("alice") == cart

def test_add_rejects_quantity_overflow(service):
    service.get_or_create("alice", CUSTOMER)
    cart = service.add("alice", CUSTOMER, BURGER.model_copy(update={"quantity": MAX_QUANTITY}))
    with pytest.raises(CartConflict, match="maximum"):
        service.add("alice", CUSTOMER, BURGER)
    assert service.repository.get("alice") == cart

def test_concurrent_adds_do_not_lose_items(service):
    service.get_or_create("alice", CUSTOMER)
    with ThreadPoolExecutor(max_workers=4) as workers:
        list(workers.map(lambda _: service.add("alice", CUSTOMER, BURGER), range(8)))
    assert service.repository.get("alice").items[0].quantity == 16
