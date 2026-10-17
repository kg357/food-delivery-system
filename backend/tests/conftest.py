"""
Shared fixtures for the backend automated tests.

Pytest automatically discovers fixtures defined in conftest.py
and makes them available to tests in this directory.

These fixtures provide:
    - A FastAPI test client for testing HTTP endpoints.
    - Sample restaurant records.
    - Sample menu item records.
    - Temporary JSON files for testing without modifying
      the application's development data.
"""


import json

import pytest


# ============================================================
# Sample Restaurant Data
# ============================================================

@pytest.fixture
def restaurant_data():
    """
    Provide three sample restaurants for isolated testing.

    The restaurants have different owners, cuisines, and
    ratings so tests can verify retrieval, filtering,
    and restaurant ownership behavior.

    Restaurant 3 intentionally has no associated menu items
    to support testing empty menu responses.
    """
    return [
        {
            "id": 1,
            "owner_id": "owner1",
            "name": "Restaurant One",
            "cuisine": "Italian",
            "rating": 4.5,
            "address": "123 Main Street",
        },
        {
            "id": 2,
            "owner_id": "owner2",
            "name": "Restaurant Two",
            "cuisine": "Japanese",
            "rating": 4.0,
            "address": "456 Oak Avenue",
        },
        {
            "id": 3,
            "owner_id": "owner3",
            "name": "Restaurant With No Menu",
            "cuisine": "Canadian",
            "rating": 3.5,
            "address": "789 Pine Road",
        },
    ]


# ============================================================
# Sample Menu Item Data
# ============================================================

@pytest.fixture
def menu_data():
    """
    Provide sample menu items belonging to test restaurants.

    Restaurant 1 has two menu items, Restaurant 2 has one,
    and Restaurant 3 has none.

    This allows tests to verify that menu items are retrieved
    only for their associated restaurant.
    """
    return [
        {
            "id": "item-a",
            "restaurant_id": 1,
            "name": "Burger",
            "description": "Test item",
            "price": 10.0,
            "available": True,
        },
        {
            "id": "item-b",
            "restaurant_id": 1,
            "name": "Fries",
            "description": "Test item",
            "price": 5.0,
            "available": True,
        },
        {
            "id": "item-c",
            "restaurant_id": 2,
            "name": "Pizza",
            "description": "Test item",
            "price": 12.0,
            "available": True,
        },
    ]


# ============================================================
# Temporary JSON Data Files
# ============================================================

@pytest.fixture
def data_files(tmp_path, restaurant_data, menu_data):
    """
    Create temporary restaurant and menu JSON files.

    Parameters:
        tmp_path:
            Built-in pytest fixture providing a unique
            temporary directory for each test.

        restaurant_data:
            Sample restaurant records defined above.

        menu_data:
            Sample menu item records defined above.

    Returns:
        tuple:
            (restaurants_file, menu_items_file)

            Both values are pathlib.Path objects pointing
            to the temporary JSON files.

    Using temporary files prevents tests from reading or
    overwriting the application's development data.
    """

    # Create file paths inside pytest's temporary directory.
    restaurants_file = tmp_path / "restaurants.json"
    menu_items_file = tmp_path / "menu_items.json"

    # Write the restaurant records as JSON.
    restaurants_file.write_text(
        json.dumps(restaurant_data),
        encoding="utf-8",
    )

    # Write the menu item records as JSON.
    menu_items_file.write_text(
        json.dumps(menu_data),
        encoding="utf-8",
    )

    # Return both paths so tests can access the files.
    return restaurants_file, menu_items_file
