
"""
Tests for restaurant and owner identifier generation.

The identifier utilities generate unique IDs for restaurants
and owners.

These tests verify:
    - New restaurant IDs do not conflict with existing IDs.
    - The first restaurant receives ID 1 when no records exist.
    - Owner IDs are generated as UUID strings.

Identifier tests run independently of FastAPI routes,
services, and JSON storage.
"""

from uuid import UUID

from app.core.identifiers import (
    generate_owner_id,
    generate_restaurant_id,
)


# ============================================================
# Restaurant ID Generation
# ============================================================

def test_generate_restaurant_id_unique():
    """
    Verify that newly generated restaurant IDs are unique.

    When existing restaurants already have IDs 1 and 2,
    the generated ID must not match either existing ID.

    Restaurant IDs should also be integers.
    """
    existing_restaurants = [
        {
            "id": 1,
            "owner_id": "owner1",
            "name": "Restaurant A",
            "cuisine": "Italian",
            "rating": 4.5,
            "address": "123 Main St",
        },
        {
            "id": 2,
            "owner_id": "owner2",
            "name": "Restaurant B",
            "cuisine": "Chinese",
            "rating": 4.0,
            "address": "456 Elm St",
        },
    ]

    new_id = generate_restaurant_id(existing_restaurants)

    # A set comprehension collects all existing restaurant IDs.
    existing_ids = {
        restaurant["id"]
        for restaurant in existing_restaurants
    }

    assert new_id not in existing_ids
    assert isinstance(new_id, int)


def test_generate_restaurant_id_empty_list():
    """
    Verify that restaurant ID generation handles empty storage.

    When no restaurants exist, the first generated
    restaurant ID should be 1.
    """
    new_id = generate_restaurant_id([])

    assert new_id == 1


# ============================================================
# Owner ID Generation
# ============================================================

def test_generate_owner_id_unique():
    """
    Verify that an owner ID is generated as a UUID string.

    The generated identifier should not match either
    existing owner ID in the sample collection.

    UUID() validates that the string has a valid UUID format.
    It raises ValueError if the format is invalid.
    """
    existing_owners = [
        {"id": "owner1", "name": "Owner A"},
        {"id": "owner2", "name": "Owner B"},
    ]

    new_id = generate_owner_id()

    # Gather existing IDs using a set comprehension.
    existing_ids = {
        owner["id"]
        for owner in existing_owners
    }

    assert new_id not in existing_ids
    assert isinstance(new_id, str)

    # UUID() raises ValueError if the generated ID is invalid.
    assert UUID(new_id)