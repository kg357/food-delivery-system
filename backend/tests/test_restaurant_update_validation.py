import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.routes import restaurants as restaurant_routes
from app.schemas.restaurant import RestaurantUpdate


client = TestClient(app)


@pytest.mark.parametrize("invalid_data", [
    {"name": ""},
    {"name": "   "},
    {"name": None},
    {"name": "A" * 101},
    {"cuisine": ""},
    {"cuisine": None},
    {"address": ""},
    {"address": None},
    {"rating": 5.0},
    {"owner_id": "fake_owner"},
    {"id": 999},
    {"name": 123}
])


def test_invalid_restaurant_update(invalid_data):
    response = client.patch(
        "/restaurants/1",
        json=invalid_data
    )
    assert response.status_code == 422


def test_invalid_update_does_not_call_service(monkeypatch):
    def fail_if_called(restaurant_id, owner_id, update_data):
        pytest.fail(
            "Update service should not be called"
        )
    monkeypatch.setattr(
        restaurant_routes,
        "update_restaurant",
        fail_if_called
    )
    response = client.patch(
        "/restaurants/1",
        json={"name": None}
    )
    assert response.status_code == 422


def test_valid_partial_update():
    update = RestaurantUpdate(name="Updated Cafe")
    assert update.name == "Updated Cafe"
    assert update.model_dump(exclude_unset=True) == {
        "name": "Updated Cafe"
    }


def test_update_strips_whitespace():
    update = RestaurantUpdate(
        name="   Updated Cafe   "
    )
    assert update.name == "Updated Cafe"


def test_update_allows_omitted_fields():
    update = RestaurantUpdate()
    assert update.model_dump(exclude_unset=True) == {}
