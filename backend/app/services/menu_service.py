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


def add_menu_item(
    restaurant_id: int,
    item_data: dict,
    restaurants_path: Path | None = None,
    menu_items_path: Path | None = None,
) -> dict:

    if restaurants_path is None:
        restaurants_path = RESTAURANTS_FILE

    if menu_items_path is None:
        menu_items_path = MENU_ITEMS_FILE

    restaurants = load_restaurants(restaurants_path)

    restaurant_exists = any(
        restaurant["id"] == restaurant_id
        for restaurant in restaurants
    )

    if not restaurant_exists:
        raise ValueError("Restaurant not found")

    return create_menu_item(
        restaurant_id=restaurant_id,
        item_data=item_data,
        path=menu_items_path,
    )


def edit_menu_item(
    restaurant_id: int,
    item_id: str,
    updates: dict,
    restaurants_path: Path = RESTAURANTS_FILE,
    menu_items_path: Path = MENU_ITEMS_FILE,
) -> dict:
    restaurants = load_restaurants(restaurants_path)

    if not any(r["id"] == restaurant_id for r in restaurants):
        raise ValueError("Restaurant not found")

    updated_item = update_menu_item(
        restaurant_id=restaurant_id,
        item_id=item_id,
        updates=updates,
        path=menu_items_path,
    )

    if updated_item is None:
        raise ValueError("Menu item not found")

    return updated_item


def get_menu_for_restaurant(
    restaurant_id: int,
    restaurants_path: Path = RESTAURANTS_FILE,
    menu_items_path: Path = MENU_ITEMS_FILE,
) -> list[dict]:
    if load_restaurant_by_id(restaurant_id, restaurants_path) is None:
        raise ValueError("Restaurant not found")

    return load_menu_items_by_restaurant(restaurant_id, menu_items_path)


def get_menu_item_for_restaurant(
    restaurant_id: int,
    item_id: str,
    restaurants_path: Path = RESTAURANTS_FILE,
    menu_items_path: Path = MENU_ITEMS_FILE,
) -> dict:
    if load_restaurant_by_id(restaurant_id, restaurants_path) is None:
        raise ValueError("Restaurant not found")

    item = load_menu_item_by_id(restaurant_id, item_id, menu_items_path)

    if item is None:
        raise ValueError("Menu item not found")

    return item
