
"""
Tests for the restaurant repository layer.

The repository is responsible for reading and writing restaurant
records to JSON files.

These tests verify:
    - Loading restaurant records from JSON.
    - Handling an empty restaurant list.
    - Finding individual restaurants by ID.
    - Handling nonexistent restaurant IDs.
    - Saving restaurant records.
    - Overwriting existing stored data.

All tests use temporary files to avoid modifying the
application's development restaurant data.
"""


import json

from app.repositories.restaurant_repository import (
    load_restaurants,
    load_restaurant_by_id,
    save_restaurants,
)


# ============================================================
# Loading Restaurants
# ============================================================

def test_load_restaurants_reads_isolated_test_data(tmp_path):
    """
    Verify that the repository loads restaurant records from JSON.

    Creates a temporary file containing two restaurants, then
    checks that load_restaurants() returns the expected records.
    """

    test_data = [
        {
            "id": 1,
            "owner_id": "owner01",
            "name": "Test Diner",
            "cuisine": "American",
            "rating": 4.0,
            "address": "1 Test St",
        },
        {
            "id": 2,
            "owner_id": "owner02",
            "name": "Test Bistro",
            "cuisine": "French",
            "rating": 4.8,
            "address": "2 Test Ave",
        },
    ]

    # tmp_path is a built-in pytest fixture providing a
    # temporary directory for this test.
    test_file = tmp_path / "restaurants.json"

    # json.dumps() converts Python data into a JSON string.
    test_file.write_text(
        json.dumps(test_data),
        encoding="utf-8",
    )

    data = load_restaurants(path=test_file)

    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["name"] == "Test Diner"


def test_load_restaurants_returns_empty_list(tmp_path):
    """
    Verify that an empty JSON array produces an empty list.

    An empty restaurant file should not cause an error when
    it contains valid JSON representing an empty collection.
    """

    test_file = tmp_path / "restaurants.json"
    test_file.write_text("[]", encoding="utf-8")

    restaurants = load_restaurants(path=test_file)

    assert restaurants == []


# ============================================================
# Loading Individual Restaurants
# ============================================================

def test_load_restaurant_by_id_finds_existing_restaurant(data_files):
    """
    Verify that an existing restaurant can be retrieved by ID.

    The shared data_files fixture provides three sample
    restaurants in a temporary JSON file.
    """

    # The underscore ignores the unused menu-items file.
    restaurants_file, _ = data_files

    restaurant = load_restaurant_by_id(
        restaurant_id=2,
        path=restaurants_file,
    )

    assert restaurant is not None
    assert restaurant["id"] == 2
    assert restaurant["name"] == "Restaurant Two"


def test_load_restaurant_by_id_returns_none_for_unknown_id(data_files):
    """
    Verify that an unknown restaurant ID returns None.

    Returning None allows the service layer to decide
    how to handle a restaurant that does not exist.
    """

    restaurants_file, _ = data_files

    restaurant = load_restaurant_by_id(
        restaurant_id=999,
        path=restaurants_file,
    )

    assert restaurant is None


# ============================================================
# Saving Restaurants
# ============================================================

def test_save_restaurants_writes_json_file(tmp_path, restaurant_data):
    """
    Verify that restaurant records can be saved to JSON.

    The shared restaurant_data fixture supplies sample records.
    The test confirms that the file is created and that its
    contents match the supplied data.
    """

    test_file = tmp_path / "restaurants.json"

    save_restaurants(
        restaurants=restaurant_data,
        path=test_file,
    )

    assert test_file.exists()

    # Load the saved JSON to verify the actual file contents.
    with test_file.open(encoding="utf-8") as file:
        saved_data = json.load(file)

    assert saved_data == restaurant_data


def test_save_restaurants_overwrites_existing_data(
    tmp_path, restaurant_data
):
    """
    Verify that saving a restaurant collection replaces old data.

    An existing file contains a restaurant with ID 999.
    After saving the new collection, that old record should
    no longer be present.
    """

    test_file = tmp_path / "restaurants.json"

    test_file.write_text(
        json.dumps([{"id": 999, "name": "Old Restaurant"}]),
        encoding="utf-8",
    )

    save_restaurants(
        restaurants=restaurant_data,
        path=test_file,
    )

    saved_data = load_restaurants(path=test_file)

    assert saved_data == restaurant_data
    assert all(item["id"] != 999 for item in saved_data)