from pathlib import Path

from app.core.config import MENU_ITEMS_FILE, RESTAURANTS_FILE
from app.repositories.menu_repository import create_menu_item
from app.repositories.restaurant_repository import load_restaurants


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