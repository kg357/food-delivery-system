"""Cart business rules and coordination with the restaurant menu."""

from collections.abc import Callable
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

from app.core.config import MENU_ITEMS_FILE, RESTAURANTS_FILE
from app.core.identifiers import generate_cart_id
from app.repositories.cart_repository import CartRepository
from app.schemas.cart import MAX_QUANTITY, Cart, CartItem, CartItemCreate, CartQuantityUpdate
from app.services.menu_service import get_menu_item_for_restaurant


class CartError(ValueError):
    pass


class CartNotFound(CartError):
    pass


class CartConflict(CartError):
    pass


class CartForbidden(CartError):
    pass


class CartService:
    def __init__(
        self,
        repository: CartRepository,
        restaurants_path: Path = RESTAURANTS_FILE,
        menu_items_path: Path = MENU_ITEMS_FILE,
    ):
        self.repository = repository
        self.restaurants_path = restaurants_path
        self.menu_items_path = menu_items_path

    @staticmethod
    def _check_customer(customer_id: str, user: dict) -> None:
        if user["id"] != customer_id or user["role"] != "customer":
            raise CartForbidden("Only the customer can access their cart")
        if not user["active"]:
            raise CartForbidden("Customer account is inactive")

    def get_or_create(self, customer_id: str, user: dict) -> Cart:
        self._check_customer(customer_id, user)
        return self.repository.change(
            customer_id,
            lambda cart: cart or Cart(id=generate_cart_id(), customer_id=customer_id),
        )

    def _modify(
        self, customer_id: str, user: dict, action: Callable[[Cart], None]
    ) -> Cart:
        self._check_customer(customer_id, user)

        def update(cart: Cart | None) -> Cart:
            if cart is None:
                raise CartNotFound("Active cart not found")
            action(cart)
            return cart

        return self.repository.change(customer_id, update)

    def add(self, customer_id: str, user: dict, request: CartItemCreate) -> Cart:
        def add_item(cart: Cart) -> None:
            if cart.restaurant_id is not None and cart.restaurant_id != request.restaurant_id:
                raise CartConflict("Cart items must belong to one restaurant")

            try:
                menu_item = get_menu_item_for_restaurant(
                    request.restaurant_id,
                    request.item_id,
                    self.restaurants_path,
                    self.menu_items_path,
                )
            except ValueError as error:
                raise CartNotFound(str(error)) from error

            if not menu_item["available"]:
                raise CartConflict("Menu item is unavailable")

            try:
                unit_price = Decimal(str(menu_item["price"]))
                if not unit_price.is_finite() or unit_price < 0:
                    raise InvalidOperation
                unit_price = unit_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            except InvalidOperation as error:
                raise CartConflict("Menu item has an invalid price") from error

            quantity = request.quantity
            for index, item in enumerate(cart.items):
                if item.item_id == request.item_id:
                    quantity += item.quantity
                    if quantity > MAX_QUANTITY:
                        raise CartConflict("Cart item quantity exceeds the maximum")
                    break
            else:
                index = len(cart.items)

            cart.items[index:index + 1] = [
                CartItem(
                    item_id=request.item_id,
                    name=menu_item["name"],
                    unit_price=unit_price,
                    quantity=quantity,
                )
            ]
            cart.restaurant_id = request.restaurant_id

        return self._modify(customer_id, user, add_item)

    def update_quantity(
        self, customer_id: str, user: dict, item_id: str, request: CartQuantityUpdate
    ) -> Cart:
        def update_item(cart: Cart) -> None:
            cart.items[self._item_index(cart, item_id)].quantity = request.quantity

        return self._modify(customer_id, user, update_item)

    def remove(self, customer_id: str, user: dict, item_id: str) -> Cart:
        def remove_item(cart: Cart) -> None:
            del cart.items[self._item_index(cart, item_id)]
            if not cart.items:
                cart.restaurant_id = None

        return self._modify(customer_id, user, remove_item)

    def clear(self, customer_id: str, user: dict) -> Cart:
        def clear_items(cart: Cart) -> None:
            cart.items.clear()
            cart.restaurant_id = None

        return self._modify(customer_id, user, clear_items)

    @staticmethod
    def _item_index(cart: Cart, item_id: str) -> int:
        for index, item in enumerate(cart.items):
            if item.item_id == item_id:
                return index
        raise CartNotFound("Cart item not found")
