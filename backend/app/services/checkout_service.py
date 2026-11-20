from decimal import ROUND_HALF_UP, Decimal

from app.api.dependencies import CUSTOMER
from app.core.identifiers import generate_order_id
from app.repositories.cart_repository import (
    CartRepository,
)
from app.repositories.order_repository import create_order
from app.schemas.order import Order
from app.services.cart_service import CartService
from app.services.menu_service import (
    get_menu_item_for_restaurant,
)


class CheckoutValidationError(
    ValueError
):
    pass


def validate_checkout(
    customer_id: str,
    user: dict,
):
    """
    Perform checkout validation before
    creating an order.
    """

    # =====================================
    # G1.1
    # =====================================

    if user["role"] != CUSTOMER:

        raise CheckoutValidationError(
            "Only customers may checkout"
        )

    if not user["active"]:

        raise CheckoutValidationError(
            "Customer account is inactive"
        )

    if user["id"] != customer_id:

        raise CheckoutValidationError(
            "You do not own this cart"
        )


    repository = CartRepository()

    cart = repository.get(customer_id)

    if cart is None:

        raise CheckoutValidationError(
            "Active cart not found"
        )

    if not cart.items:

        raise CheckoutValidationError(
            "Cannot checkout an empty cart"
        )

    if cart.restaurant_id is None:

        raise CheckoutValidationError(
            "Cart restaurant missing"
        )


    subtotal = Decimal("0.00")

    validated_items = []

    for cart_item in cart.items:

        try:

            menu_item = (
                get_menu_item_for_restaurant(
                    cart.restaurant_id,
                    cart_item.item_id,
                )
            )

        except ValueError as error:

            raise CheckoutValidationError(
                str(error)
            ) from error

        if not menu_item["available"]:

            raise CheckoutValidationError(
                f"{menu_item['name']} is unavailable"
            )

        current_price = Decimal(
            str(menu_item["price"])
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        line_total = (
            current_price
            * cart_item.quantity
        )

        subtotal += line_total

        validated_items.append(
            {
                "item_id":
                    menu_item["id"],

                "name":
                    menu_item["name"],

                "description":
                    menu_item["description"],

                "quantity":
                    cart_item.quantity,

                "unit_price":
                    float(current_price),

                "total_price":
                    float(line_total),
            }
        )

    total = subtotal

    return {
        "customer_id":
            customer_id,

        "restaurant_id":
            cart.restaurant_id,

        "items":
            validated_items,

        "subtotal":
            float(subtotal),

        "total":
            float(total),
    }


def checkout(
    customer_id: str,
    user: dict,
    cart_service: CartService | None = None,
) -> Order:
    """
    G1.9–G1.12, G1.14
    Validate the cart, create and persist an order with historical data,
    clear the cart only after successful persistence, and return the order.
    """
    if cart_service is None:
        cart_service = CartService(CartRepository())

    # G1.1–G1.5 (your existing validation + historical snapshot)
    validated = validate_checkout(customer_id, user)

    order_data = {
        "id": generate_order_id(),
        "customer_id": validated["customer_id"],
        "restaurant_id": validated["restaurant_id"],
        "items": validated["items"],
        "subtotal": validated["subtotal"],
        "total": validated["total"],
    }

    # G1.11 – persist first
    try:
        create_order(order_data)
    except Exception as error:
        raise CheckoutValidationError(
            f"Failed to save order: {error}"
        ) from error

    # G1.12 – clear cart only after success
    cart_service.clear(customer_id, user)

    # G1.14
    return Order(**order_data)