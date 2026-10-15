import json
from pathlib import Path

from app.core.config import RESTAURANTS_FILE


def load_restaurants(path: Path = RESTAURANTS_FILE) -> list[dict]:
    with path.open() as f:
        return json.load(f)

def load_restaurant_by_id(restaurant_id: int, path: Path = RESTAURANTS_FILE) -> dict | None:
    restaurants = load_restaurants(path)

    for restaurant in restaurants:
        if restaurant["id"] == restaurant_id:
            return restaurant
    return None

def save_restaurants(restaurants: list[dict], path: Path = RESTAURANTS_FILE) -> None:
    with path.open("w") as f:
        json.dump(restaurants, f, indent=2)
