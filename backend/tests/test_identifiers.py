from uuid import UUID


from app.core.identifiers import (
    generate_restaurant_id,
    generate_owner_id
)


def test_generate_restaurant_id_unique():
    existing_restaurants = [
        {"id": 1, "owner_id": "owner1", "name": "Restaurant A", "cuisine": "Italian", "rating": 4.5, "address": "123 Main St"},
        {"id": 2, "owner_id": "owner2", "name": "Restaurant B", "cuisine": "Chinese", "rating": 4.0, "address": "456 Elm St"},
    ]
    new_id = generate_restaurant_id(existing_restaurants)
    assert new_id not in {restaurant["id"] for restaurant in existing_restaurants}
    assert isinstance(new_id, int)


def test_generate_restaurant_id_empty_list():
    new_id = generate_restaurant_id([])
    assert new_id == 1  # Should return 1 for an empty list


def test_generate_owner_id_unique():
    existing_owners = [
        {"id": "owner1", "name": "Owner A"},
        {"id": "owner2", "name": "Owner B"},
    ]
    new_id = generate_owner_id()
    assert new_id not in {owner["id"] for owner in existing_owners}
    assert isinstance(new_id, str)
    assert UUID(new_id)  # Verify it's a valid UUID


