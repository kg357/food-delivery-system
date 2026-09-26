import json
import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.restaurant_repository import load_restaurants
from app.services.restaurant_service import get_all_restaurants
from app.schemas.restaurant import Restaurant

client = TestClient(app)


def test_load_restaurants_reads_isolated_test_data(tmp_path):
    test_data = [
        {"id": 1, "name": "Test Diner", "cuisine": "American", "rating": 4.0, "address": "1 Test St"},
        {"id": 2, "name": "Test Bistro", "cuisine": "French", "rating": 4.8, "address": "2 Test Ave"},
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
        "name": "Broken Place",
        "cuisine": "Unknown",
        "rating": 3.0,
        "address": "3 Test Rd",
    }

    with pytest.raises(ValidationError):
        Restaurant(**bad_item)
