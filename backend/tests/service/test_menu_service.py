
"""
Tests for the menu service layer.

The menu service handles business logic between the API routes
and the menu repository.

These tests verify:
    - Adding menu items to existing restaurants.
    - Rejecting menu creation for nonexistent restaurants.
    - Editing existing menu items.
    - Preventing edits under an incorrect restaurant ID.
    - Retrieving restaurant menus.
    - Retrieving individual menu items.
    - Handling missing restaurants and menu items.

Tests use temporary JSON files so the application's
development data is never modified.
"""


import json

import pytest

from app.repositories.menu_repository import load_menu_items
from app.services.menu_service import (
    add_menu_item,
    edit_menu_item,
    get_menu_for_restaurant,
    get_menu_item_for_restaurant,
)


# ============================================================
# Menu Item Creation
# ============================================================

def test_add_menu_item_existing_restaurant(tmp_path):
    """
    Verify that a menu item can be added to an existing restaurant.

    The service should associate the item with Restaurant 1
    and persist the item to JSON storage.
    """

    # tmp_path provides a temporary directory unique to this test.
    restaurants_file = tmp_path / "restaurants.json"
    menu_items_file = tmp_path / "menu_items.json"

    restaurants_file.write_text(
        json.dumps([
            {"id": 1, "name": "Test Restaurant"}
        ]),
        encoding="utf-8",
    )

    # Start with an empty menu so the created item is easy to verify.
    menu_items_file.write_text("[]", encoding="utf-8")

    new_item = add_menu_item(
        restaurant_id=1,
        item_data={
            "name": "Burger",
            "description": "Beef burger",
            "price": 12.99,
            "available": True,
        },
        restaurants_path=restaurants_file,
        menu_items_path=menu_items_file,
    )

    assert new_item["name"] == "Burger"
    assert new_item["restaurant_id"] == 1

    # Reload from disk to confirm the item was saved.
    assert len(load_menu_items(menu_items_file)) == 1


def test_add_menu_item_nonexistent_restaurant(tmp_path):
    """
    Verify that adding an item to a nonexistent restaurant fails.

    The service should raise a ValueError and must not create
    a menu item when the restaurant cannot be found.
    """
    restaurants_file = tmp_path / "restaurants.json"
    menu_items_file = tmp_path / "menu_items.json"

    restaurants_file.write_text("[]", encoding="utf-8")
    menu_items_file.write_text("[]", encoding="utf-8")

    # pytest.raises() checks that the expected exception occurs.
    # match also verifies part of the exception message.
    with pytest.raises(ValueError, match="Restaurant not found"):
        add_menu_item(
            restaurant_id=99,
            item_data={
                "name": "Burger",
                "description": "Beef burger",
                "price": 12.99,
                "available": True,
            },
            restaurants_path=restaurants_file,
            menu_items_path=menu_items_file,
        )

    assert load_menu_items(menu_items_file) == []


# ============================================================
# Menu Item Editing
# ============================================================

def test_edit_menu_item(tmp_path):
    """
    Verify that an existing menu item's price can be updated.

    Editing the price should preserve the item's name and ID.
    """
    restaurants_file = tmp_path / "restaurants.json"
    menu_items_file = tmp_path / "menu_items.json"

    restaurants_file.write_text(
        '[{"id": 1, "name": "Burger Place"}]',
        encoding="utf-8",
    )

    menu_items_file.write_text(
        """
        [{
            "id": "item-123",
            "restaurant_id": 1,
            "name": "Burger",
            "description": "Beef burger",
            "price": 12.99,
            "available": true
        }]
        """,
        encoding="utf-8",
    )

    result = edit_menu_item(
        restaurant_id=1,
        item_id="item-123",
        updates={"price": 14.99},
        restaurants_path=restaurants_file,
        menu_items_path=menu_items_file,
    )

    assert result["price"] == 14.99
    assert result["name"] == "Burger"
    assert result["id"] == "item-123"


def test_edit_menu_item_wrong_restaurant(tmp_path):
    """
    Verify that a menu item cannot be edited under another restaurant.

    Item 'item-123' belongs to Restaurant 1.
    Attempting to edit it under Restaurant 2 should raise
    a ValueError indicating that the item was not found.
    """
    restaurants_file = tmp_path / "restaurants.json"
    menu_items_file = tmp_path / "menu_items.json"

    restaurants_file.write_text(
        """
        [
            {"id": 1, "name": "Burger Place"},
            {"id": 2, "name": "Pizza Place"}
        ]
        """,
        encoding="utf-8",
    )

    menu_items_file.write_text(
        """
        [{
            "id": "item-123",
            "restaurant_id": 1,
            "name": "Burger",
            "description": "Beef burger",
            "price": 12.99,
            "available": true
        }]
        """,
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Menu item not found"):
        edit_menu_item(
            restaurant_id=2,
            item_id="item-123",
            updates={"price": 14.99},
            restaurants_path=restaurants_file,
            menu_items_path=menu_items_file,
        )


# ============================================================
# Restaurant Menu Browsing
# ============================================================

def test_service_returns_menu_for_existing_restaurant(data_files):
    """
    Verify that the service retrieves an existing restaurant's menu.

    Restaurant 1 has two menu items in the shared test data.
    """
    restaurants_file, menu_items_file = data_files

    menu = get_menu_for_restaurant(
        1,
        restaurants_file,
        menu_items_file,
    )

    assert len(menu) == 2


def test_service_never_returns_items_from_other_restaurants(data_files):
    """
    Verify that menu browsing returns items for only one restaurant.

    Restaurant 2 has one menu item, Pizza. Items belonging
    to Restaurant 1 must not appear in the response.
    """
    restaurants_file, menu_items_file = data_files

    menu = get_menu_for_restaurant(
        2,
        restaurants_file,
        menu_items_file,
    )

    assert [item["name"] for item in menu] == ["Pizza"]

    # all() checks that every item meets the specified condition.
    assert all(item["restaurant_id"] == 2 for item in menu)


def test_service_unknown_restaurant_menu_raises_error(data_files):
    """
    Verify that browsing the menu of an unknown restaurant fails.

    The service should distinguish a nonexistent restaurant
    from an existing restaurant whose menu is simply empty.
    """
    restaurants_file, menu_items_file = data_files

    with pytest.raises(ValueError, match="Restaurant not found"):
        get_menu_for_restaurant(
            99,
            restaurants_file,
            menu_items_file,
        )


# ============================================================
# Individual Menu Item Retrieval
# ============================================================

def test_service_returns_requested_item(data_files):
    """
    Verify that the service retrieves a specific menu item.

    Item 'item-a' belongs to Restaurant 1 and should
    be returned when both identifiers match.
    """
    restaurants_file, menu_items_file = data_files

    item = get_menu_item_for_restaurant(
        1,
        "item-a",
        restaurants_file,
        menu_items_file,
    )

    assert item["id"] == "item-a"
    assert item["restaurant_id"] == 1


def test_service_unknown_restaurant_item_raises_error(data_files):
    """
    Verify that requesting an item from an unknown restaurant fails.

    The service should reject the restaurant lookup before
    returning any associated menu-item information.
    """
    restaurants_file, menu_items_file = data_files

    with pytest.raises(ValueError, match="Restaurant not found"):
        get_menu_item_for_restaurant(
            99,
            "item-a",
            restaurants_file,
            menu_items_file,
        )


def test_service_unknown_item_raises_error(data_files):
    """
    Verify that requesting a nonexistent menu item raises an error.

    Restaurant 1 exists, but the requested item ID does not.
    """
    restaurants_file, menu_items_file = data_files

    with pytest.raises(ValueError, match="Menu item not found"):
        get_menu_item_for_restaurant(
            1,
            "does-not-exist",
            restaurants_file,
            menu_items_file,
        )


def test_service_item_of_another_restaurant_raises_error(data_files):
    """
    Verify that an item cannot be retrieved under the wrong restaurant.

    Item 'item-a' belongs to Restaurant 1, so requesting
    it under Restaurant 2 should raise a ValueError.
    """
    restaurants_file, menu_items_file = data_files

    with pytest.raises(ValueError, match="Menu item not found"):
        get_menu_item_for_restaurant(
            2,
            "item-a",
            restaurants_file,
            menu_items_file,
        )