from decimal import ROUND_HALF_UP, Decimal

from app.api.dependencies import CUSTOMER
from app.repositories.cart_repository import (
    CartRepository,
)
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

    # =====================================
    # G1.2
    # =====================================

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

    # =====================================
    # G1.3
    # =====================================

    if cart.restaurant_id is None:

        raise CheckoutValidationError(
            "Cart restaurant missing"
        )

    # =====================================
    # G1.4
    # G1.5
    # =====================================

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