import pytest

from app.services.checkout_service import (
    validate_checkout,
    CheckoutValidationError,
)


def test_inactive_customer_fails():

    with pytest.raises(
        CheckoutValidationError,
        match="inactive",
    ):

        validate_checkout(
            "customer-1",
            {
                "id":
                    "customer-1",

                "role":
                    "customer",

                "active":
                    False,
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
                "id":
                    "customer-2",

                "role":
                    "customer",

                "active":
                    True,
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
                "id":
                    "admin-1",

                "role":
                    "admin",

                "active":
                    True,
            },
        )