import json
from pathlib import Path
from uuid import uuid4

from app.core.config import MENU_ITEMS_FILE


def load_menu_items(path: Path = MENU_ITEMS_FILE) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_menu_items(
    items: list[dict],
    path: Path = MENU_ITEMS_FILE
) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(items, file, indent=4)


def create_menu_item(
    restaurant_id: int,
    item_data: dict,
    path: Path = MENU_ITEMS_FILE
) -> dict:
    items = load_menu_items(path)

    new_item = {
        **item_data,
        "id": str(uuid4()),
        "restaurant_id": restaurant_id,
    }

    items.append(new_item)
    save_menu_items(items, path)

    return new_item


def update_menu_item(
    restaurant_id: int,
    item_id: str,
    updates: dict,
    path: Path = MENU_ITEMS_FILE,
) -> dict | None:

    items = load_menu_items(path)

    for item in items:
        if (
            item["id"] == item_id
            and item["restaurant_id"] == restaurant_id
        ):
            item.update(updates)
            save_menu_items(items, path)
            return item

    return None


def get_menu_items_by_restaurant(
    restaurant_id: int,
    path: Path = MENU_ITEMS_FILE,
) -> list[dict]:
    items = load_menu_items(path)

    return [
        item for item in items
        if item["restaurant_id"] == restaurant_id
    ]