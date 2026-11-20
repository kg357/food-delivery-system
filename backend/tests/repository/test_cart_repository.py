import json
from concurrent.futures import ThreadPoolExecutor

import pytest

from app.repositories.cart_repository import CartRepository
from app.schemas.cart import Cart


def test_cart_survives_repository_recreation(tmp_path):
    path = tmp_path / "carts.json"
    repository = CartRepository(path)
    assert repository.get("customer-1") is None

    cart = Cart(id="cart-1", customer_id="customer-1")
    repository.change("customer-1", lambda existing: cart)
    assert CartRepository(path).get("customer-1") == cart
    assert "subtotal" not in json.loads(path.read_text())["customer-1"]


def test_concurrent_creates_keep_one_cart_per_customer(tmp_path):
    path = tmp_path / "carts.json"

    def create(index):
        return CartRepository(path).change(
            "customer-1",
            lambda cart: cart or Cart(id=f"cart-{index}", customer_id="customer-1"),
        )

    with ThreadPoolExecutor(max_workers=8) as workers:
        carts = list(workers.map(create, range(16)))

    assert len({cart.id for cart in carts}) == 1
    assert set(json.loads(path.read_text())) == {"customer-1"}


def test_failed_replace_preserves_existing_data(tmp_path, monkeypatch):
    path = tmp_path / "carts.json"
    repository = CartRepository(path)
    cart = Cart(id="cart-1", customer_id="customer-1")
    repository.change("customer-1", lambda existing: cart)
    original = path.read_bytes()
    original_files = set(tmp_path.iterdir())

    def fail_replace(self, target):
        raise OSError("Could not replace file")

    monkeypatch.setattr(type(path), "replace", fail_replace)
    with pytest.raises(OSError, match="Could not replace file"):
        repository.change(
            "customer-2", lambda existing: Cart(id="cart-2", customer_id="customer-2")
        )
    assert path.read_bytes() == original
    assert set(tmp_path.iterdir()) == original_files
