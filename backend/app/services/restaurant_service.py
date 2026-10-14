from pathlib import Path
from fastapi import HTTPException
from app.core.config import RESTAURANTS_FILE
from app.core.identifiers import generate_restaurant_id
from app.repositories.restaurant_repository import load_restaurants, save_restaurants
from app.schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate


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


def verify_restaurant_ownership(restaurant_id: int, owner_id: str, path: Path = RESTAURANTS_FILE) -> Restaurant:
    restaurants = load_restaurants(path)
    for restaurant in restaurants:
        if restaurant["id"] == restaurant_id: 
            if restaurant["owner_id"] != owner_id:
                raise HTTPException(status_code=403, detail="You do not have permission to modify this restaurant.")
            return Restaurant(**restaurant)
    raise HTTPException(status_code=404, detail="Restaurant not found.")


def update_restaurant(restaurant_id: int, owner_id: str, update_data: RestaurantUpdate, path: Path = RESTAURANTS_FILE) -> Restaurant:
    verify_restaurant_ownership(restaurant_id, owner_id, path)
    restaurants = load_restaurants(path)
    changes = update_data.model_dump(exclude_unset=True)
    for restaurant in restaurants:
        if restaurant["id"] == restaurant_id:
            restaurant.update(changes)
            updated_restaurant = Restaurant(**restaurant)
            save_restaurants(restaurants, path)
            return updated_restaurant
