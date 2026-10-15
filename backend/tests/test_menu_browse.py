import json

import pytest
from app.api.routes import menu as menu_routes
from app.main import app
from app.repositories.menu_repository import load_menu_items_by_restaurant
from app.services.menu_service import get_menu_for_restaurant
from fastapi.testclient import TestClient


def make_item(item_id, restaurant_id, name):
    return {
        "id": item_id,
        "restaurant_id": restaurant_id,
        "name": name,
        "description": "Test item",
        "price": 10.0,
        "available": True,
    }


@pytest.fixture
def data_files(tmp_path):
    restaurants_file = tmp_path / "restaurants.json"
    menu_items_file = tmp_path / "menu_items.json"

    restaurants_file.write_text(
        json.dumps([
            {"id": 1, "name": "Restaurant One"},
            {"id": 2, "name": "Restaurant Two"},
            {"id": 3, "name": "Restaurant With No Menu"},
        ]),
        encoding="utf-8",
    )
    menu_items_file.write_text(
        json.dumps([
            make_item("a", 1, "Burger"),
            make_item("b", 1, "Fries"),
            make_item("c", 2, "Pizza"),
        ]),
        encoding="utf-8",
    )

    return restaurants_file, menu_items_file


# ---------- repository ----------

def test_repository_returns_only_items_for_that_restaurant(data_files):
    _, menu_items_file = data_files

    items = load_menu_items_by_restaurant(1, menu_items_file)

    assert [item["name"] for item in items] == ["Burger", "Fries"]


def test_repository_returns_empty_list_when_restaurant_has_no_items(data_files):
    _, menu_items_file = data_files

    assert load_menu_items_by_restaurant(3, menu_items_file) == []


# ---------- service ----------

def test_service_returns_menu_for_existing_restaurant(data_files):
    restaurants_file, menu_items_file = data_files

    menu = get_menu_for_restaurant(1, restaurants_file, menu_items_file)

    assert len(menu) == 2


def test_service_never_returns_items_from_other_restaurants(data_files):
    restaurants_file, menu_items_file = data_files

    menu = get_menu_for_restaurant(2, restaurants_file, menu_items_file)

    assert [item["name"] for item in menu] == ["Pizza"]
    assert all(item["restaurant_id"] == 2 for item in menu)


def test_service_unknown_restaurant_raises_error(data_files):
    restaurants_file, menu_items_file = data_files

    with pytest.raises(ValueError, match="Restaurant not found"):
        get_menu_for_restaurant(99, restaurants_file, menu_items_file)


# ---------- route ----------

@pytest.fixture
def client(data_files, monkeypatch):
    restaurants_file, menu_items_file = data_files

    def isolated_get_menu(restaurant_id):
        return get_menu_for_restaurant(
            restaurant_id,
            restaurants_path=restaurants_file,
            menu_items_path=menu_items_file,
        )

    monkeypatch.setattr(menu_routes, "get_menu_for_restaurant", isolated_get_menu)

    return TestClient(app)


def test_route_returns_menu_with_status_200(client):
    response = client.get("/restaurants/1/menu")

    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == ["Burger", "Fries"]


def test_route_unknown_restaurant_returns_404(client):
    response = client.get("/restaurants/99/menu")

    assert response.status_code == 404
    assert response.json() == {"detail": "Restaurant not found"}


def test_route_restaurant_with_no_menu_returns_empty_list(client):
    response = client.get("/restaurants/3/menu")

    assert response.status_code == 200
    assert response.json() == []


def test_route_non_numeric_restaurant_id_returns_422(client):
    response = client.get("/restaurants/abc/menu")

    assert response.status_code == 422
