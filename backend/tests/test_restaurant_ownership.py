import json
import pytest
from fastapi import HTTPException

from app.services.restaurant_service import verify_restaurant_ownership


@pytest.fixture
def restaurant_file(tmp_path):
    path = tmp_path / "restaurants.json"
    restaurants = [
        {
            "id": 1,
            "owner_id": "owner_001",
            "name": "First Restaurant",
            "cuisine": "Italian",
            "rating": 4.5,
            "address": "100 Main Street"
        },
        {
            "id": 2,
            "owner_id": "owner_002",
            "name": "Second Restaurant",
            "cuisine": "Japanese",
            "rating": 4.2,
            "address": "200 Main Street"
        }
    ]
    path.write_text(json.dumps(restaurants))
    return path


def test_owner_can_access_own_restaurant(restaurant_file):
    restaurant = verify_restaurant_ownership(
        restaurant_id=1,
        owner_id="owner_001",
        path=restaurant_file
    )
    assert restaurant.id == 1
    assert restaurant.owner_id == "owner_001"


def test_owner_cannot_access_another_restaurant(restaurant_file):
    with pytest.raises(HTTPException) as error:
        verify_restaurant_ownership(
            restaurant_id=1,
            owner_id="owner_002",
            path=restaurant_file
        )
    assert error.value.status_code == 403


def test_nonexistent_restaurant_returns_404(restaurant_file):
    with pytest.raises(HTTPException) as error:
        verify_restaurant_ownership(
            restaurant_id=999,
            owner_id="owner_001",
            path=restaurant_file
        )
    assert error.value.status_code == 404