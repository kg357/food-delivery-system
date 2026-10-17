
"""
Business logic for restaurant menu operations.

The menu service layer coordinates the restaurant and menu
repositories to enforce rules governing menu items.

Its responsibilities include:
    - Verifying that restaurants exist before menu operations.
    - Creating new menu items for existing restaurants.
    - Editing items associated with the requested restaurant.
    - Retrieving all menu items belonging to a restaurant.
    - Retrieving individual menu items.

The repository layer handles JSON storage, while the API
route layer translates service errors into HTTP responses.
"""


from pathlib import Path

from app.core.config import MENU_ITEMS_FILE, RESTAURANTS_FILE
from app.repositories.menu_repository import (
    create_menu_item,
    load_menu_item_by_id,
    load_menu_items_by_restaurant,
    update_menu_item,
)
from app.repositories.restaurant_repository import (
    load_restaurant_by_id,
    load_restaurants,
)


# ============================================================
# Menu Item Creation
# ============================================================

def add_menu_item(
    restaurant_id: int,
    item_data: dict,
    restaurants_path: Path | None = None,
    menu_items_path: Path | None = None,
) -> dict:
    """
    Create a menu item for an existing restaurant.

    Args:
        restaurant_id: ID of the restaurant receiving the item.
        item_data: Validated menu item information.
        restaurants_path: Optional restaurant JSON file path.
        menu_items_path: Optional menu items JSON file path.

    Returns:
        The created menu item dictionary, including its
        generated ID and associated restaurant ID.

    Raises:
        ValueError: If the restaurant does not exist.

    Optional paths allow tests to operate on temporary JSON
    files instead of the application's development data.
    """

    # Use the configured data files when alternate paths
    # have not been provided by the caller.
    if restaurants_path is None:
        restaurants_path = RESTAURANTS_FILE

    if menu_items_path is None:
        menu_items_path = MENU_ITEMS_FILE

    restaurants = load_restaurants(restaurants_path)

    # any() returns True if at least one restaurant matches.
    restaurant_exists = any(
        restaurant["id"] == restaurant_id
        for restaurant in restaurants
    )

    if not restaurant_exists:
        raise ValueError("Restaurant not found")

    # The repository generates the item ID and saves the record.
    return create_menu_item(
        restaurant_id=restaurant_id,
        item_data=item_data,
        path=menu_items_path,
    )


# ============================================================
# Menu Item Editing
# ============================================================

def edit_menu_item(
    restaurant_id: int,
    item_id: str,
    updates: dict,
    restaurants_path: Path = RESTAURANTS_FILE,
    menu_items_path: Path = MENU_ITEMS_FILE,
) -> dict:
    """
    Update an existing menu item.

    Args:
        restaurant_id: ID of the restaurant associated with the item.
        item_id: Unique identifier of the menu item.
        updates: Dictionary containing fields to update.
        restaurants_path: Location of the restaurant JSON file.
        menu_items_path: Location of the menu items JSON file.

    Returns:
        The updated menu item dictionary.

    Raises:
        ValueError:
            "Restaurant not found" if the restaurant does not exist.
            "Menu item not found" if the item does not exist
            or belongs to a different restaurant.

    The restaurant and item IDs must both match an existing
    record before the menu item can be modified.
    """

    restaurants = load_restaurants(restaurants_path)

    # Verify that the requested restaurant exists.
    if not any(r["id"] == restaurant_id for r in restaurants):
        raise ValueError("Restaurant not found")

    # The repository finds the item and applies the requested changes.
    updated_item = update_menu_item(
        restaurant_id=restaurant_id,
        item_id=item_id,
        updates=updates,
        path=menu_items_path,
    )

    if updated_item is None:
        raise ValueError("Menu item not found")

    return updated_item


# ============================================================
# Restaurant Menu Retrieval
# ============================================================

def get_menu_for_restaurant(
    restaurant_id: int,
    restaurants_path: Path = RESTAURANTS_FILE,
    menu_items_path: Path = MENU_ITEMS_FILE,
) -> list[dict]:
    """
    Retrieve all menu items associated with a restaurant.

    Args:
        restaurant_id: ID of the requested restaurant.
        restaurants_path: Location of the restaurant JSON file.
        menu_items_path: Location of the menu items JSON file.

    Returns:
        A list of menu item dictionaries.
        An empty list if the restaurant exists but has no items.

    Raises:
        ValueError: If the restaurant does not exist.
    """

    # An unknown restaurant is different from an existing
    # restaurant with an empty menu.
    if load_restaurant_by_id(restaurant_id, restaurants_path) is None:
        raise ValueError("Restaurant not found")

    return load_menu_items_by_restaurant(
        restaurant_id,
        menu_items_path,
    )


# ============================================================
# Individual Menu Item Retrieval
# ============================================================

def get_menu_item_for_restaurant(
    restaurant_id: int,
    item_id: str,
    restaurants_path: Path = RESTAURANTS_FILE,
    menu_items_path: Path = MENU_ITEMS_FILE,
) -> dict:
    """
    Retrieve an individual menu item associated with a restaurant.

    Args:
        restaurant_id: ID of the requested restaurant.
        item_id: Unique ID of the requested menu item.
        restaurants_path: Location of the restaurant JSON file.
        menu_items_path: Location of the menu items JSON file.

    Returns:
        The matching menu item dictionary.

    Raises:
        ValueError:
            "Restaurant not found" if the restaurant does not exist.
            "Menu item not found" if the item is missing or
            belongs to a different restaurant.
    """

    # Check the restaurant before looking up its menu item.
    if load_restaurant_by_id(restaurant_id, restaurants_path) is None:
        raise ValueError("Restaurant not found")

    # The repository checks both the item ID and restaurant ID.
    item = load_menu_item_by_id(
        restaurant_id,
        item_id,
        menu_items_path,
    )

    if item is None:
        raise ValueError("Menu item not found")

    return item