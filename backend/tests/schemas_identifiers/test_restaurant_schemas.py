
"""
Tests for the restaurant Pydantic schemas.

Pydantic models define the structure and validation rules
for restaurant data entering and leaving the application.

These tests verify:
    - Restaurant models reject invalid field types.
    - Restaurant records require an owner ID.
    - Restaurant creation validates required fields.
    - Restaurant creation rejects unexpected fields.
    - Partial updates accept omitted fields.
    - Update values are cleaned and validated.
    - Protected fields cannot be modified through updates.

These tests validate schemas directly without making HTTP
requests or accessing the repository's JSON files.
"""


import pytest
from pydantic import ValidationError

from app.schemas.restaurant import (
    Restaurant,
    RestaurantCreate,
    RestaurantUpdate,
)


# ============================================================
# Restaurant Schema
# ============================================================

def test_invalid_restaurant_data_raises_validation_error():
    """
    Verify that the Restaurant model rejects an invalid ID.

    The Restaurant schema expects an integer ID. Providing
    a nonnumeric string should raise a Pydantic ValidationError.
    """
    bad_item = {
        "id": "not-a-number",
        "owner_id": "ownerX",
        "name": "Broken Place",
        "cuisine": "Unknown",
        "rating": 3.0,
        "address": "3 Test Rd",
    }

    # pytest.raises() verifies that the specified exception occurs.
    with pytest.raises(ValidationError):
        Restaurant(**bad_item)


def test_restaurant_has_owner():
    """
    Verify that a valid Restaurant model stores its owner ID.

    The owner_id field identifies which owner is associated
    with the restaurant.
    """
    restaurant = Restaurant(
        id=1,
        owner_id="owner11",
        name="Wasabi Ramen",
        cuisine="Japanese",
        rating=4.5,
        address="123 Main St",
    )

    assert restaurant.owner_id == "owner11"


def test_restaurant_requires_owner():
    """
    Verify that the Restaurant schema requires an owner ID.

    Creating a Restaurant without owner_id should cause
    Pydantic validation to fail.
    """
    with pytest.raises(ValidationError):
        Restaurant(
            id=1,
            name="Wasabi Ramen",
            cuisine="Japanese",
            rating=4.5,
            address="123 Main St",
        )


# ============================================================
# Restaurant Creation Schema
# ============================================================

def test_restaurant_creation_schema():
    """
    Verify that RestaurantCreate accepts valid input data.

    The creation schema contains information a user supplies
    when creating a restaurant.
    """
    restaurant = RestaurantCreate(
        name="Test Cafe",
        cuisine="Cafe",
        address="4 Test Ln",
    )

    assert restaurant.name == "Test Cafe"
    assert restaurant.cuisine == "Cafe"


def test_restaurant_creation_schema_requires_name():
    """
    Verify that a restaurant cannot be created without a name.

    Missing required fields cause Pydantic to raise
    a ValidationError.
    """
    with pytest.raises(ValidationError):
        RestaurantCreate(
            cuisine="Cafe",
            address="4 Test Ln",
        )


def test_restaurant_creation_schema_forbids_extra_fields():
    """
    Verify that RestaurantCreate rejects unexpected fields.

    The schema does not permit arbitrary extra data such as
    extra_field, preventing unsupported values from being
    accepted during restaurant creation.
    """
    with pytest.raises(ValidationError):
        RestaurantCreate(
            name="Test Cafe",
            cuisine="Cafe",
            address="4 Test Ln",
            extra_field="not allowed",
        )


# ============================================================
# Restaurant Update Schema
# ============================================================

def test_valid_partial_update():
    """
    Verify that RestaurantUpdate accepts a partial update.

    model_dump(exclude_unset=True) returns only the fields
    explicitly supplied when creating the Pydantic model.

    This allows PATCH operations to distinguish omitted
    fields from fields the user intends to modify.
    """
    update = RestaurantUpdate(name="Updated Cafe")

    assert update.name == "Updated Cafe"
    assert update.model_dump(exclude_unset=True) == {
        "name": "Updated Cafe"
    }


def test_update_strips_whitespace():
    """
    Verify that restaurant update values are normalized.

    Leading and trailing whitespace should be removed
    from the submitted restaurant name.
    """
    update = RestaurantUpdate(
        name="   Updated Cafe   "
    )

    assert update.name == "Updated Cafe"


def test_update_allows_omitted_fields():
    """
    Verify that an update can contain no requested changes.

    RestaurantUpdate allows fields to be omitted because
    PATCH requests do not require a complete restaurant record.

    An empty update should produce an empty dictionary when
    only explicitly supplied fields are extracted.
    """
    update = RestaurantUpdate()

    assert update.model_dump(exclude_unset=True) == {}


# ============================================================
# Protected Field Validation
# ============================================================

@pytest.mark.parametrize(
    "protected_field",
    [
        {"id": 999},
        {"owner_id": "another_owner"},
        {"rating": 5.0},
    ],
)
def test_protected_fields_cannot_be_updated(protected_field):
    """
    Verify that protected restaurant fields cannot be updated.

    @pytest.mark.parametrize runs this test three times:
        1. Attempting to change the restaurant ID.
        2. Attempting to change the owner ID.
        3. Attempting to change the rating.

    These fields are not accepted by RestaurantUpdate.
    Each attempt should raise a Pydantic ValidationError.
    """
    with pytest.raises(ValidationError):
        RestaurantUpdate(**protected_field)
