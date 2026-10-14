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