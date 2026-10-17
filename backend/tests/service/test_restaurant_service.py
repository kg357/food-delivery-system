
"""
Tests for the restaurant service layer.

The service layer handles business logic between FastAPI routes
and the restaurant repository.

These tests verify:
    - Restaurant retrieval and filtering.
    - Restaurant creation and persistence.
    - Restaurant updates and preservation of existing data.
    - Restaurant ownership checks.
    - Handling missing restaurants and unauthorized operations.

Temporary JSON files and mocked repository functions are used
to keep tests independent of development data.
"""


import json

import pytest
from fastapi import HTTPException

import app.services.restaurant_service as restaurant_service
from app.repositories.restaurant_repository import load_restaurants
from app.schemas.restaurant import (
    Restaurant,
    RestaurantCreate,
    RestaurantUpdate,
)
from app.services.restaurant_service import (
    create_restaurant,
    get_all_restaurants,
    get_restaurant_by_id,
    update_restaurant,
    verify_restaurant_ownership,
)


# ============================================================
# Test Fixtures
# ============================================================

@pytest.fixture
def restaurant_file(tmp_path):
    """
    Provide two restaurants with different owners.

    Used to verify that owners can access their own restaurants
    but cannot access restaurants belonging to other owners.
    """
    path = tmp_path / "restaurants.json"

    restaurants = [
        {
            "id": 1,
            "owner_id": "owner_001",
            "name": "First Restaurant",
            "cuisine": "Italian",
            "rating": 4.5,
            "address": "100 Main Street",
        },
        {
            "id": 2,
            "owner_id": "owner_002",
            "name": "Second Restaurant",
            "cuisine": "Japanese",
            "rating": 4.2,
            "address": "200 Main Street",
        },
    ]

    path.write_text(json.dumps(restaurants), encoding="utf-8")
    return path


@pytest.fixture
def restaurant_creation_file(tmp_path):
    """
    Provide a JSON file containing one existing restaurant.

    Creation tests use this file to verify that new restaurant
    IDs are generated and existing records are preserved.
    """
    path = tmp_path / "restaurants.json"

    initial_data = [
        {
            "id": 1,
            "owner_id": "owner_001",
            "name": "Existing Restaurant",
            "cuisine": "Italian",
            "rating": 4.5,
            "address": "100 Main Street",
        }
    ]

    path.write_text(
        json.dumps(initial_data),
        encoding="utf-8",
    )

    return path


@pytest.fixture
def restaurant_update_file(tmp_path):
    """
    Provide one restaurant for testing updates.

    The initial values allow tests to verify which fields
    changed and whether unauthorized updates are rejected.
    """
    path = tmp_path / "restaurants.json"

    path.write_text(
        json.dumps([
            {
                "id": 1,
                "owner_id": "owner_001",
                "name": "Original Cafe",
                "cuisine": "Italian",
                "rating": 4.5,
                "address": "100 Main Street",
            }
        ]),
        encoding="utf-8",
    )

    return path


@pytest.fixture
def restaurant_modification_file(tmp_path):
    """
    Provide two restaurants for more detailed update tests.

    Having two records allows tests to confirm that modifying
    one restaurant does not affect another restaurant.
    """
    path = tmp_path / "restaurants.json"

    restaurants = [
        {
            "id": 1,
            "owner_id": "owner_001",
            "name": "Original Cafe",
            "cuisine": "Italian",
            "rating": 4.5,
            "address": "100 Main Street",
        },
        {
            "id": 2,
            "owner_id": "owner_002",
            "name": "Second Cafe",
            "cuisine": "French",
            "rating": 4.2,
            "address": "200 Main Street",
        },
    ]

    path.write_text(
        json.dumps(restaurants),
        encoding="utf-8",
    )

    return path


@pytest.fixture
def mock_restaurant_data(monkeypatch, restaurant_data):
    """
    Replace repository loading with predictable sample data.

    monkeypatch.setattr() temporarily replaces the service's
    load_restaurants function. This isolates filtering tests
    from JSON storage.

    Pytest automatically restores the original function
    after the test finishes.
    """
    monkeypatch.setattr(
        restaurant_service,
        "load_restaurants",
        lambda: restaurant_data,
    )

    return restaurant_data


# ============================================================
# Restaurant Retrieval
# ============================================================

def test_get_all_restaurants_returns_restaurant_objects(
    mock_restaurant_data,
):
    """
    Verify that retrieving all restaurants returns Restaurant models.

    The service should convert repository records into validated
    Pydantic Restaurant objects.
    """
    restaurants = get_all_restaurants()

    assert len(restaurants) == 3
    assert restaurants[0].name == "Restaurant One"
    assert all(
        isinstance(restaurant, Restaurant)
        for restaurant in restaurants
    )


def test_service_gets_restaurant_by_id(monkeypatch, restaurant_data):
    """
    Verify that the service retrieves the requested restaurant.

    The repository lookup is mocked to return a matching record
    without reading from the actual JSON file.
    """
    # next() returns the first matching restaurant, or None.
    monkeypatch.setattr(
        restaurant_service,
        "load_restaurant_by_id",
        lambda restaurant_id: next(
            (
                restaurant
                for restaurant in restaurant_data
                if restaurant["id"] == restaurant_id
            ),
            None,
        ),
    )

    restaurant = get_restaurant_by_id(2)

    assert restaurant.id == 2
    assert restaurant.name == "Restaurant Two"


def test_service_unknown_restaurant_returns_404(monkeypatch):
    """
    Verify that retrieving a nonexistent restaurant raises HTTP 404.

    The mocked repository always returns None, simulating
    a restaurant ID that cannot be found.
    """
    monkeypatch.setattr(
        restaurant_service,
        "load_restaurant_by_id",
        lambda restaurant_id: None,
    )

    # pytest.raises() captures the expected exception.
    with pytest.raises(HTTPException) as error:
        get_restaurant_by_id(999)

    assert error.value.status_code == 404
    assert error.value.detail == "Restaurant not found"


# ============================================================
# Restaurant Filtering
# ============================================================

def test_service_filters_restaurants_by_cuisine(mock_restaurant_data):
    """
    Verify that filtering by cuisine returns matching restaurants.

    The sample data contains one Italian restaurant.
    """
    restaurants = get_all_restaurants(cuisine="Italian")

    assert len(restaurants) == 1
    assert restaurants[0].name == "Restaurant One"


def test_service_cuisine_filter_is_case_insensitive(
    mock_restaurant_data,
):
    """
    Verify that cuisine filtering ignores capitalization.

    Searching for 'italian' should match a restaurant
    whose stored cuisine is 'Italian'.
    """
    restaurants = get_all_restaurants(cuisine="italian")

    assert len(restaurants) == 1
    assert restaurants[0].cuisine == "Italian"


def test_service_filters_restaurants_by_minimum_rating(
    mock_restaurant_data,
):
    """
    Verify that the minimum rating filter works correctly.

    Only restaurants meeting or exceeding the supplied
    rating threshold should be returned.
    """
    restaurants = get_all_restaurants(min_rating=4.5)

    assert len(restaurants) == 1
    assert restaurants[0].name == "Restaurant One"


def test_service_combines_cuisine_and_rating_filters(
    mock_restaurant_data,
):
    """
    Verify that cuisine and rating filters work together.

    A restaurant must satisfy both conditions to appear
    in the results.
    """
    restaurants = get_all_restaurants(
        cuisine="Italian",
        min_rating=4.5,
    )

    assert len(restaurants) == 1
    assert restaurants[0].name == "Restaurant One"


def test_service_returns_empty_list_for_no_matches(
    mock_restaurant_data,
):
    """
    Verify that unmatched search criteria return an empty list.

    An empty result is valid and should not raise an exception.
    """
    restaurants = get_all_restaurants(cuisine="Mexican")

    assert restaurants == []


# ============================================================
# Restaurant Creation
# ============================================================

def test_create_restaurant(restaurant_creation_file):
    """
    Verify that a restaurant is created with the correct properties.

    The new restaurant should receive a unique ID, its specified
    owner ID, and an initial rating of zero.
    """
    restaurant_data = RestaurantCreate(
        name="New Cafe",
        cuisine="American",
        address="200 Main Street",
    )

    restaurant = create_restaurant(
        restaurant_data,
        owner_id="owner_002",
        path=restaurant_creation_file,
    )

    assert restaurant.id == 2
    assert restaurant.owner_id == "owner_002"
    assert restaurant.name == "New Cafe"
    assert restaurant.rating == 0.0


def test_created_restaurant_is_saved(restaurant_creation_file):
    """
    Verify that creating a restaurant persists it to JSON.

    The file is reloaded after creation to confirm that
    the new restaurant was actually saved.
    """
    restaurant_data = RestaurantCreate(
        name="New Cafe",
        cuisine="American",
        address="200 Main Street",
    )

    create_restaurant(
        restaurant_data,
        owner_id="owner_002",
        path=restaurant_creation_file,
    )

    saved_restaurants = load_restaurants(restaurant_creation_file)

    assert len(saved_restaurants) == 2
    assert saved_restaurants[1]["name"] == "New Cafe"


def test_creation_preserves_existing_restaurants(
    restaurant_creation_file,
):
    """
    Verify that creating a restaurant preserves existing records.

    Adding a new restaurant must not overwrite or remove
    restaurants already stored in JSON.
    """
    restaurant_data = RestaurantCreate(
        name="New Cafe",
        cuisine="American",
        address="200 Main Street",
    )

    create_restaurant(
        restaurant_data,
        owner_id="owner_002",
        path=restaurant_creation_file,
    )

    saved_restaurants = load_restaurants(restaurant_creation_file)

    assert saved_restaurants[0]["name"] == "Existing Restaurant"
    assert saved_restaurants[0]["id"] == 1


# ============================================================
# Basic Restaurant Updates
# ============================================================

def test_owner_can_update_restaurant(restaurant_update_file):
    """
    Verify that a restaurant owner can update restaurant information.

    Updating the name should preserve other fields,
    including the cuisine.
    """
    update = RestaurantUpdate(name="Updated Cafe")

    restaurant = update_restaurant(
        restaurant_id=1,
        owner_id="owner_001",
        update_data=update,
        path=restaurant_update_file,
    )

    assert restaurant.name == "Updated Cafe"
    assert restaurant.cuisine == "Italian"


def test_restaurant_update_is_saved(restaurant_update_file):
    """
    Verify that an update is persisted to JSON storage.

    The service updates the address, then the repository
    reloads the file to confirm that the change was saved.
    """
    update_restaurant(
        restaurant_id=1,
        owner_id="owner_001",
        update_data=RestaurantUpdate(address="200 Main Street"),
        path=restaurant_update_file,
    )

    saved = load_restaurants(restaurant_update_file)

    assert saved[0]["address"] == "200 Main Street"


def test_non_owner_cannot_update(restaurant_update_file):
    """
    Verify that a different owner cannot update a restaurant.

    The service should raise HTTP 403 and preserve the
    restaurant's original name.
    """
    with pytest.raises(HTTPException) as error:
        update_restaurant(
            restaurant_id=1,
            owner_id="owner_999",
            update_data=RestaurantUpdate(name="Stolen Cafe"),
            path=restaurant_update_file,
        )

    assert error.value.status_code == 403
    assert load_restaurants(restaurant_update_file)[0]["name"] == "Original Cafe"


def test_update_nonexistent_restaurant(restaurant_update_file):
    """
    Verify that updating a nonexistent restaurant raises HTTP 404.

    An unknown restaurant ID must not create a new record
    through the update operation.
    """
    with pytest.raises(HTTPException) as error:
        update_restaurant(
            restaurant_id=999,
            owner_id="owner_001",
            update_data=RestaurantUpdate(name="New Name"),
            path=restaurant_update_file,
        )

    assert error.value.status_code == 404


# ============================================================
# Partial and Multiple-Field Updates
# ============================================================

def test_partial_update_preserves_other_fields(
    restaurant_modification_file,
):
    """
    Verify that updating one field preserves all other fields.

    A PATCH-style update should modify only the fields supplied
    in the RestaurantUpdate model.
    """
    before = load_restaurants(restaurant_modification_file)[0].copy()

    update_restaurant(
        restaurant_id=1,
        owner_id="owner_001",
        update_data=RestaurantUpdate(name="Renamed Cafe"),
        path=restaurant_modification_file,
    )

    after = load_restaurants(restaurant_modification_file)[0]

    assert after["name"] == "Renamed Cafe"
    assert after["cuisine"] == before["cuisine"]
    assert after["address"] == before["address"]
    assert after["rating"] == before["rating"]
    assert after["owner_id"] == before["owner_id"]
    assert after["id"] == before["id"]


def test_update_preserves_other_restaurants(
    restaurant_modification_file,
):
    """
    Verify that updating one restaurant leaves others unchanged.

    Restaurant 2 should remain identical after Restaurant 1
    is updated.
    """
    before = load_restaurants(restaurant_modification_file)[1].copy()

    update_restaurant(
        restaurant_id=1,
        owner_id="owner_001",
        update_data=RestaurantUpdate(address="999 New Street"),
        path=restaurant_modification_file,
    )

    after = load_restaurants(restaurant_modification_file)[1]

    assert after == before


def test_update_multiple_fields(restaurant_modification_file):
    """
    Verify that multiple restaurant fields can be updated together.

    The returned Restaurant model and the saved JSON data
    must both contain the updated values.
    """
    updated = update_restaurant(
        restaurant_id=1,
        owner_id="owner_001",
        update_data=RestaurantUpdate(
            name="New Restaurant",
            cuisine="Japanese",
            address="500 Updated Avenue",
        ),
        path=restaurant_modification_file,
    )

    assert updated.name == "New Restaurant"
    assert updated.cuisine == "Japanese"
    assert updated.address == "500 Updated Avenue"

    saved = load_restaurants(restaurant_modification_file)

    assert saved[0]["name"] == "New Restaurant"
    assert saved[0]["cuisine"] == "Japanese"
    assert saved[0]["address"] == "500 Updated Avenue"


def test_empty_update_changes_nothing(restaurant_modification_file):
    """
    Verify that an empty update leaves restaurant data unchanged.

    RestaurantUpdate() contains no requested changes, so
    existing fields should remain identical.
    """
    before = load_restaurants(restaurant_modification_file)

    update_restaurant(
        restaurant_id=1,
        owner_id="owner_001",
        update_data=RestaurantUpdate(),
        path=restaurant_modification_file,
    )

    after = load_restaurants(restaurant_modification_file)

    assert before == after


# ============================================================
# Preventing Unauthorized or Invalid Saves
# ============================================================

def test_unauthorized_update_does_not_save(
    restaurant_modification_file,
    monkeypatch,
):
    """
    Verify that unauthorized updates never reach the save function.

    monkeypatch replaces save_restaurants() with a function
    that fails the test if called. This confirms that the
    service rejects unauthorized modifications before saving.
    """

    def fail_if_called(*args, **kwargs):
        pytest.fail("Unauthorized update attempted to save data")

    monkeypatch.setattr(
        restaurant_service,
        "save_restaurants",
        fail_if_called,
    )

    with pytest.raises(HTTPException) as error:
        update_restaurant(
            restaurant_id=1,
            owner_id="owner_999",
            update_data=RestaurantUpdate(name="Stolen Cafe"),
            path=restaurant_modification_file,
        )

    assert error.value.status_code == 403


def test_nonexistent_update_does_not_save(
    restaurant_modification_file,
    monkeypatch,
):
    """
    Verify that updates to nonexistent restaurants never save data.

    The mocked save function causes the test to fail if
    the service attempts persistence after detecting
    an unknown restaurant ID.
    """

    def fail_if_called(*args, **kwargs):
        pytest.fail("Nonexistent restaurant update attempted to save")

    monkeypatch.setattr(
        restaurant_service,
        "save_restaurants",
        fail_if_called,
    )

    with pytest.raises(HTTPException) as error:
        update_restaurant(
            restaurant_id=999,
            owner_id="owner_001",
            update_data=RestaurantUpdate(name="Missing Cafe"),
            path=restaurant_modification_file,
        )

    assert error.value.status_code == 404


# ============================================================
# Restaurant Ownership Verification
# ============================================================

def test_owner_can_access_own_restaurant(restaurant_file):
    """
    Verify that an owner can access their own restaurant.

    The ownership service should return the matching Restaurant
    model when the owner ID is correct.
    """
    restaurant = verify_restaurant_ownership(
        restaurant_id=1,
        owner_id="owner_001",
        path=restaurant_file,
    )

    assert restaurant.id == 1
    assert restaurant.owner_id == "owner_001"


def test_owner_cannot_access_another_restaurant(restaurant_file):
    """
    Verify that an owner cannot access another owner's restaurant.

    A mismatched owner ID should cause the service to
    raise an HTTP 403 Forbidden exception.
    """
    with pytest.raises(HTTPException) as error:
        verify_restaurant_ownership(
            restaurant_id=1,
            owner_id="owner_002",
            path=restaurant_file,
        )

    assert error.value.status_code == 403


def test_nonexistent_restaurant_returns_404(restaurant_file):
    """
    Verify that ownership checks reject nonexistent restaurants.

    The service should return HTTP 404 when the requested
    restaurant ID does not exist in storage.
    """
    with pytest.raises(HTTPException) as error:
        verify_restaurant_ownership(
            restaurant_id=999,
            owner_id="owner_001",
            path=restaurant_file,
        )

    assert error.value.status_code == 404