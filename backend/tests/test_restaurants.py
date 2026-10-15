import json

import pytest
from app.main import app
from app.repositories.restaurant_repository import load_restaurants
from app.schemas.restaurant import Restaurant, RestaurantCreate
from app.services.restaurant_service import create_restaurant, get_all_restaurants
from fastapi.testclient import TestClient
from pydantic import ValidationError

client = TestClient(app)


def test_load_restaurants_reads_isolated_test_data(tmp_path):
    test_data = [
        {"id": 1, "owner_id": "owner01", "name": "Test Diner", "cuisine": "American", "rating": 4.0, "address": "1 Test St"},
        {"id": 2, "owner_id": "owner02", "name": "Test Bistro", "cuisine": "French", "rating": 4.8, "address": "2 Test Ave"},
    ]
    test_file = tmp_path / "restaurants.json"
    test_file.write_text(json.dumps(test_data))

    data = load_restaurants(path=test_file)

    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["name"] == "Test Diner"


def test_get_all_restaurants_returns_restaurant_objects():
    restaurants = get_all_restaurants()
    assert len(restaurants) == 3
    assert restaurants[0].name == "Wasabi Ramen"


def test_restaurants_endpoint_returns_200():
    response = client.get("/restaurants")
    assert response.status_code == 200


def test_restaurants_endpoint_returns_correct_data():
    response = client.get("/restaurants")
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "Wasabi Ramen"


def test_invalid_restaurant_data_raises_validation_error():
    bad_item = {
        "id": "not-a-number",
        "owner_id": "ownerX",
        "name": "Broken Place",
        "cuisine": "Unknown",
        "rating": 3.0,
        "address": "3 Test Rd",
    }

    with pytest.raises(ValidationError):
        Restaurant(**bad_item)

def test_filter_restaurants_by_cuisine():
    response = client.get("/restaurants?cuisine=Italian")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Bella Pasta"

def test_filter_restaurants_by_min_rating():
    response = client.get("/restaurants?min_rating=4.5")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    names = [restaurant["name"] for restaurant in data]

    assert "Wasabi Ramen" in names
    assert "Spice Route" in names


def test_filter_returns_empty_list():
    response = client.get("/restaurants?cuisine=Mexican")

    assert response.status_code == 200
    assert response.json() == []

def test_restaurant_creation_schema():
    restaurant = RestaurantCreate(
        name="Test Cafe",
        cuisine="Cafe",
        address="4 Test Ln",
    )
    assert restaurant.name == "Test Cafe"
    assert restaurant.cuisine == "Cafe"


def test_restaurant_creation_schema_requires_name():
    with pytest.raises(ValidationError):
        RestaurantCreate(
            cuisine="Cafe",
            address="4 Test Ln",
        )


def test_restaurant_creation_schema_forbids_extra_fields():
    with pytest.raises(ValidationError):
        RestaurantCreate(
            name="Test Cafe",
            cuisine="Cafe",
            address="4 Test Ln",
            extra_field="not allowed",
        )

def test_restaurant_has_owner():
    restaurant = Restaurant(
        id=1,
        owner_id="owner11",
        name="Wasabi Ramen",
        cuisine="Japanese",
        rating=4.5,
        address="123 Main St"
    )
    assert restaurant.owner_id == "owner11"


def test_restaurant_requires_owner():
    with pytest.raises(ValidationError):
        Restaurant(
            id=1,
            name="Wasabi Ramen",
            cuisine="Japanese",
            rating=4.5,
            address="123 Main St"
        )

@pytest.fixture
def test_file(tmp_path):
    path = tmp_path / "restaurants.json"
    initial_data = [
        {
            "id": 1,
            "owner_id": "owner_001",
            "name": "Existing Restaurant",
            "cuisine": "Italian",
            "rating": 4.5,
            "address": "100 Main Street"
        }
    ]
    path.write_text(json.dumps(initial_data))
    return path


def test_create_restaurant(test_file):
    restaurant_data = RestaurantCreate(
        name="New Cafe",
        cuisine="American",
        address="200 Main Street"
    )
    restaurant = create_restaurant(
        restaurant_data,
        owner_id="owner_002",
        path=test_file,
    )
    assert restaurant.id == 2
    assert restaurant.owner_id == "owner_002"
    assert restaurant.name == "New Cafe"
    assert restaurant.rating == 0.0


def test_created_restaurant_is_saved(test_file):
    restaurant_data = RestaurantCreate(
        name="New Cafe",
        cuisine="American",
        address="200 Main Street"
    )
    create_restaurant(
        restaurant_data,
        owner_id="owner_002",
        path=test_file,
    )
    saved_restaurants = load_restaurants(test_file)
    assert len(saved_restaurants) == 2
    assert saved_restaurants[1]["name"] == "New Cafe"


def test_creation_preserves_existing_restaurants(test_file):
    restaurant_data = RestaurantCreate(
        name="New Cafe",
        cuisine="American",
        address="200 Main Street"
    )
    create_restaurant(
        restaurant_data,
        owner_id="owner_002",
        path=test_file,
    )
    saved_restaurants = load_restaurants(test_file)
    assert saved_restaurants[0]["name"] == "Existing Restaurant"
    assert saved_restaurants[0]["id"] == 1
