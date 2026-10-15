import json
import pytest
from fastapi import HTTPException
from app.schemas.restaurant import RestaurantUpdate
from app.services.restaurant_service import update_restaurant
from app.repositories.restaurant_repository import load_restaurants


@pytest.fixture
def restaurant_file(tmp_path):
    path = tmp_path / "restaurants.json"
    path.write_text(json.dumps([
        {
            "id": 1,
            "owner_id": "owner_001",
            "name": "Original Cafe",
            "cuisine": "Italian",
            "rating": 4.5,
            "address": "100 Main Street"
        }
    ]))
    return path


def test_owner_can_update_restaurant(restaurant_file):
    update = RestaurantUpdate(name="Updated Cafe")
    restaurant = update_restaurant(
        restaurant_id=1,
        owner_id="owner_001",
        update_data=update,
        path=restaurant_file
    )
    assert restaurant.name == "Updated Cafe"
    assert restaurant.cuisine == "Italian"


def test_restaurant_update_is_saved(restaurant_file):
    update_restaurant(
        restaurant_id=1,
        owner_id="owner_001",
        update_data=RestaurantUpdate(address="200 Main Street"),
        path=restaurant_file
    )
    saved = load_restaurants(restaurant_file)
    assert saved[0]["address"] == "200 Main Street"


def test_non_owner_cannot_update(restaurant_file):
    with pytest.raises(HTTPException) as error:
        update_restaurant(
            restaurant_id=1,
            owner_id="owner_999",
            update_data=RestaurantUpdate(name="Stolen Cafe"),
            path=restaurant_file
        )
    assert error.value.status_code == 403
    assert load_restaurants(restaurant_file)[0]["name"] == "Original Cafe"


def test_update_nonexistent_restaurant(restaurant_file):
    with pytest.raises(HTTPException) as error:
        update_restaurant(
            restaurant_id=999,
            owner_id="owner_001",
            update_data=RestaurantUpdate(name="New Name"),
            path=restaurant_file
        )
    assert error.value.status_code == 404
