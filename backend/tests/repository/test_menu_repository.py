
"""
Tests for the menu repository layer.

The menu repository is responsible for creating, updating,
saving, and retrieving menu items from JSON storage.

These tests verify:
    - Creating and saving menu items.
    - Updating existing menu items.
    - Preventing updates through the wrong restaurant ID.
    - Retrieving items associated with a specific restaurant.
    - Handling restaurants without menu items.
    - Retrieving individual items by ID.
    - Handling unknown items and incorrect restaurant associations.

All tests use temporary JSON files to avoid modifying
the application's development menu data.
"""


from app.repositories.menu_repository import (
    create_menu_item,
    load_menu_item_by_id,
    load_menu_items,
    load_menu_items_by_restaurant,
    save_menu_items,
    update_menu_item,
)


# ============================================================
# Menu Item Creation
# ============================================================

def test_create_menu_item(tmp_path):
    """
    Verify that a new menu item is created and saved correctly.

    The repository should generate an item ID, associate the
    item with the specified restaurant, and persist its data.
    """

    # tmp_path provides an isolated temporary directory.
    test_file = tmp_path / "menu_items.json"

    # Initialize storage with an empty menu collection.
    save_menu_items([], test_file)

    new_item = create_menu_item(
        restaurant_id=1,
        item_data={
            "name": "Burger",
            "description": "Beef burger",
            "price": 12.99,
            "available": True,
        },
        path=test_file,
    )

    # Reload from disk to confirm the item was persisted.
    saved_items = load_menu_items(test_file)

    assert len(saved_items) == 1
    assert saved_items[0]["id"] == new_item["id"]
    assert saved_items[0]["name"] == "Burger"
    assert saved_items[0]["restaurant_id"] == 1


# ============================================================
# Menu Item Updates
# ============================================================

def test_update_menu_item(tmp_path):
    """
    Verify that an existing menu item's information can be updated.

    Updating the price should preserve the item's original
    name and identifier, both in the returned result and storage.
    """

    test_file = tmp_path / "menu_items.json"

    original_item = {
        "id": "item-123",
        "restaurant_id": 1,
        "name": "Burger",
        "description": "Beef burger",
        "price": 12.99,
        "available": True,
    }

    save_menu_items([original_item], test_file)

    updated_item = update_menu_item(
        restaurant_id=1,
        item_id="item-123",
        updates={"price": 14.99},
        path=test_file,
    )

    # Read the file again to verify that changes were saved.
    saved_items = load_menu_items(test_file)

    assert updated_item["price"] == 14.99
    assert saved_items[0]["price"] == 14.99
    assert saved_items[0]["name"] == "Burger"
    assert saved_items[0]["id"] == "item-123"


def test_update_menu_item_wrong_restaurant(tmp_path):
    """
    Verify that an item cannot be updated under another restaurant.

    The repository should return None when the requested
    restaurant ID does not match the item's restaurant ID.
    The original menu item must remain unchanged.
    """

    test_file = tmp_path / "menu_items.json"

    original_item = {
        "id": "item-456",
        "restaurant_id": 1,
        "name": "Burger",
        "description": "Beef burger",
        "price": 12.99,
        "available": True,
    }

    save_menu_items([original_item], test_file)

    updated_item = update_menu_item(
        restaurant_id=2,
        item_id="item-456",
        updates={"price": 14.99},
        path=test_file,
    )

    assert updated_item is None
    assert load_menu_items(test_file)[0]["price"] == 12.99


# ============================================================
# Retrieving Restaurant Menus
# ============================================================

def test_repository_returns_only_items_for_that_restaurant(data_files):
    """
    Verify that menu retrieval is restricted to one restaurant.

    Restaurant 1 has two menu items in the shared test data.
    Items belonging to other restaurants must not be returned.
    """

    # Ignore the restaurant file because only menu storage is needed.
    _, menu_items_file = data_files

    items = load_menu_items_by_restaurant(1, menu_items_file)

    assert [item["name"] for item in items] == ["Burger", "Fries"]


def test_repository_returns_empty_list_when_restaurant_has_no_items(data_files):
    """
    Verify that a restaurant without menu items returns an empty list.

    Restaurant 3 exists in the shared data but has no menu items.
    """

    _, menu_items_file = data_files

    assert load_menu_items_by_restaurant(3, menu_items_file) == []


# ============================================================
# Retrieving Individual Menu Items
# ============================================================

def test_repository_finds_item_by_id(data_files):
    """
    Verify that a specific menu item can be retrieved by ID.

    The restaurant ID and item ID must identify the same record.
    """

    _, menu_items_file = data_files

    item = load_menu_item_by_id(1, "item-a", menu_items_file)

    assert item["name"] == "Burger"


def test_repository_returns_none_for_unknown_item_id(data_files):
    """
    Verify that an unknown menu item ID returns None.

    The repository does not raise an HTTP error; handling
    missing records is the responsibility of the service layer.
    """

    _, menu_items_file = data_files

    assert load_menu_item_by_id(
        1,
        "does-not-exist",
        menu_items_file,
    ) is None


def test_repository_returns_none_for_item_of_another_restaurant(data_files):
    """
    Verify that a menu item cannot be retrieved under the wrong restaurant.

    Item 'item-a' belongs to Restaurant 1, so requesting
    it under Restaurant 2 must return None.
    """

    _, menu_items_file = data_files

    assert load_menu_item_by_id(
        2,
        "item-a",
        menu_items_file,
    ) is None
