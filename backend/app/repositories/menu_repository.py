
"""
Repository functions for menu item JSON persistence.

The menu repository manages menu items stored in
backend/data/menu_items.json.

Its responsibilities include:
    - Loading and saving menu item records.
    - Creating menu items with unique identifiers.
    - Updating existing menu items.
    - Retrieving all items belonging to a restaurant.
    - Retrieving an individual item by its ID.

Menu items are associated with restaurants through the
restaurant_id field.

The optional path parameters allow tests to use temporary
JSON files without modifying development data.
"""


import json
from pathlib import Path
from uuid import uuid4

from app.core.config import MENU_ITEMS_FILE


# ============================================================
# Loading and Saving Menu Items
# ============================================================

def load_menu_items(path: Path = MENU_ITEMS_FILE) -> list[dict]:
    """
    Load all menu item records from a JSON file.

    Args:
        path: Location of the menu items JSON file.

    Returns:
        A list of dictionaries representing menu items.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """

    # The with statement automatically closes the file.
    # json.load() converts JSON data into Python objects.
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_menu_items(
    items: list[dict],
    path: Path = MENU_ITEMS_FILE,
) -> None:
    """
    Save a complete collection of menu items to JSON.

    Args:
        items: Menu item dictionaries to save.
        path: Destination JSON file.

    The existing file is overwritten with the supplied items.

    indent=4 formats the JSON with four spaces per indentation
    level, making stored records easier to inspect.
    """

    # Opening in write mode replaces the file's existing contents.
    with path.open("w", encoding="utf-8") as file:
        json.dump(items, file, indent=4)


# ============================================================
# Creating Menu Items
# ============================================================

def create_menu_item(
    restaurant_id: int,
    item_data: dict,
    path: Path = MENU_ITEMS_FILE,
) -> dict:
    """
    Create and save a menu item for a restaurant.

    Args:
        restaurant_id: ID of the restaurant receiving the item.
        item_data: Validated menu item fields.
        path: Location of the menu items JSON file.

    Returns:
        A dictionary containing the new menu item, including
        its generated ID and associated restaurant ID.

    The caller is responsible for verifying that the
    restaurant exists before invoking this function.
    """

    # Load existing items so they are preserved when saving.
    items = load_menu_items(path)

    # ** copies the submitted fields into the new dictionary.
    # uuid4() generates a random UUID for the menu item.
    # The identifiers are set after item_data so these values
    # take precedence if matching keys appear in item_data.
    new_item = {
        **item_data,
        "id": str(uuid4()),
        "restaurant_id": restaurant_id,
    }

    items.append(new_item)

    # Persist the complete updated menu collection.
    save_menu_items(items, path)

    return new_item


# ============================================================
# Updating Menu Items
# ============================================================

def update_menu_item(
    restaurant_id: int,
    item_id: str,
    updates: dict,
    path: Path = MENU_ITEMS_FILE,
) -> dict | None:
    """
    Update an existing menu item associated with a restaurant.

    Args:
        restaurant_id: ID of the restaurant owning the menu item.
        item_id: Unique ID of the menu item to update.
        updates: Dictionary containing the requested changes.
        path: Location of the menu items JSON file.

    Returns:
        The updated menu item dictionary if found.
        None if no item matches both identifiers.

    Both restaurant_id and item_id must match to prevent
    updating an item through an unrelated restaurant.
    """

    items = load_menu_items(path)

    for item in items:
        if (
            item["id"] == item_id
            and item["restaurant_id"] == restaurant_id
        ):
            # update() changes only the supplied dictionary keys.
            # Unspecified fields retain their existing values.
            item.update(updates)

            save_menu_items(items, path)

            return item

    return None


# ============================================================
# Retrieving Restaurant Menus
# ============================================================

def load_menu_items_by_restaurant(
    restaurant_id: int,
    path: Path = MENU_ITEMS_FILE,
) -> list[dict]:
    """
    Retrieve all menu items associated with one restaurant.

    Args:
        restaurant_id: ID of the requested restaurant.
        path: Location of the menu items JSON file.

    Returns:
        A list of matching menu item dictionaries.
        An empty list if no menu items belong to the restaurant.
    """

    items = load_menu_items(path)

    # A list comprehension selects only matching restaurant IDs.
    return [
        item
        for item in items
        if item["restaurant_id"] == restaurant_id
    ]


# ============================================================
# Retrieving Individual Menu Items
# ============================================================

def load_menu_item_by_id(
    restaurant_id: int,
    item_id: str,
    path: Path = MENU_ITEMS_FILE,
) -> dict | None:
    """
    Retrieve a specific menu item belonging to a restaurant.

    Args:
        restaurant_id: ID of the associated restaurant.
        item_id: Unique ID of the requested menu item.
        path: Location of the menu items JSON file.

    Returns:
        The matching menu item dictionary, if found.
        None if the item does not exist or belongs to
        another restaurant.

    Checking both IDs ensures that items are retrieved
    only through their associated restaurant.
    """

    items = load_menu_items(path)

    for item in items:
        if (
            item["id"] == item_id
            and item["restaurant_id"] == restaurant_id
        ):
            return item

    return None