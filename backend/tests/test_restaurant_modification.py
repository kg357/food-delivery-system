import json
import pytest
from app.schemas.restaurant import RestaurantUpdate
from app.services.restaurant_service import update_restaurant
import app.services.restaurant_service as restaurant_service
from app.repositories.restaurant_repository import load_restaurants
from pydantic import ValidationError
from fastapi import HTTPException


@pytest.fixture
def restaurant_file(tmp_path):
    path = tmp_path / "restaurants.json"
    restaurants = [
        {
            "id": 1,
            "owner_id": "owner_001",
            "name": "Original Cafe",
            "cuisine": "Italian",
            "rating": 4.5,
            "address": "100 Main Street"
        },
        {
            "id": 2,
            "owner_id": "owner_002",
            "name": "Second Cafe",
            "cuisine": "French",
            "rating": 4.2,
            "address": "200 Main Street"
        }
    ]
    path.write_text(json.dumps(restaurants))
    return path


def test_partial_update_preserves_other_fields(restaurant_file):
    before = load_restaurants(restaurant_file)[0].copy()
    update_restaurant(
        restaurant_id=1,
        owner_id="owner_001",
        update_data=RestaurantUpdate(name="Renamed Cafe"),
        path=restaurant_file
    )
    after = load_restaurants(restaurant_file)[0]
    assert after["name"] == "Renamed Cafe"
    assert after["cuisine"] == before["cuisine"]
    assert after["address"] == before["address"]
    assert after["rating"] == before["rating"]
    assert after["owner_id"] == before["owner_id"]
    assert after["id"] == before["id"]


def test_update_preserves_other_restaurants(restaurant_file):
    before = load_restaurants(restaurant_file)[1].copy()
    update_restaurant(
        restaurant_id=1,
        owner_id="owner_001",
        update_data=RestaurantUpdate(address="999 New Street"),
        path=restaurant_file
    )
    after = load_restaurants(restaurant_file)[1]
    assert after == before


def test_update_multiple_fields(restaurant_file):
    updated = update_restaurant(
        restaurant_id=1,
        owner_id="owner_001",
        update_data=RestaurantUpdate(
            name="New Restaurant",
            cuisine="Japanese",
            address="500 Updated Avenue"
        ),
        path=restaurant_file
    )
    assert updated.name == "New Restaurant"
    assert updated.cuisine == "Japanese"
    assert updated.address == "500 Updated Avenue"
    saved = load_restaurants(restaurant_file)
    assert saved[0]["name"] == "New Restaurant"
    assert saved[0]["cuisine"] == "Japanese"
    assert saved[0]["address"] == "500 Updated Avenue"


def test_empty_update_changes_nothing(restaurant_file):
    before = load_restaurants(restaurant_file)
    update_restaurant(
        restaurant_id=1,
        owner_id="owner_001",
        update_data=RestaurantUpdate(),
        path=restaurant_file
    )
    after = load_restaurants(restaurant_file)
    assert before == after


@pytest.mark.parametrize("protected_field", [
    {"id": 999},
    {"owner_id": "another_owner"},
    {"rating": 5.0}
])


def test_protected_fields_cannot_be_updated(protected_field):
    with pytest.raises(ValidationError):
        RestaurantUpdate(**protected_field)


def test_unauthorized_update_does_not_save(
    restaurant_file, monkeypatch
):
    def fail_if_called(*args, **kwargs):
        pytest.fail("Unauthorized update attempted to save data")
    monkeypatch.setattr(
        restaurant_service,
        "save_restaurants",
        fail_if_called
    )
    with pytest.raises(HTTPException) as error:
        update_restaurant(
            restaurant_id=1,
            owner_id="owner_999",
            update_data=RestaurantUpdate(name="Stolen Cafe"),
            path=restaurant_file
        )
    assert error.value.status_code == 403


def test_nonexistent_update_does_not_save(
    restaurant_file, monkeypatch
):
    def fail_if_called(*args, **kwargs):
        pytest.fail("Nonexistent restaurant update attempted to save")
    monkeypatch.setattr(
        restaurant_service,
        "save_restaurants",
        fail_if_called
    )
    with pytest.raises(HTTPException) as error:
        update_restaurant(
            restaurant_id=999,
            owner_id="owner_001",
            update_data=RestaurantUpdate(name="Missing Cafe"),
            path=restaurant_file
        )
    assert error.value.status_code == 404
