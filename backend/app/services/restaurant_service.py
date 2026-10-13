from importlib.resources import path
from pathlib import Path
from zipfile import Path

from app.api.routes import restaurants
from app.core.config import RESTAURANTS_FILE
from app.core.identifiers import generate_restaurant_id
from app.repositories.restaurant_repository import load_restaurants, save_restaurants
from app.schemas.restaurant import Restaurant, RestaurantCreate


def get_all_restaurants() -> list[Restaurant]:
    raw_data = load_restaurants()
    return [Restaurant(**item) for item in raw_data]


def create_restaurant(restaurant_data: RestaurantCreate, owner_id: str, path: Path = RESTAURANTS_FILE) -> Restaurant:
    raw_data = load_restaurants(path)
    new_id = generate_restaurant_id(raw_data)
    new_restaurant = Restaurant(
        id=new_id,
        owner_id=owner_id,
        name=restaurant_data.name,
        cuisine=restaurant_data.cuisine,
        rating=0.0,
        address=restaurant_data.address
    )
    raw_data.append(new_restaurant.model_dump())
    save_restaurants(raw_data, path)
    return new_restaurant