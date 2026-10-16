import json

import pytest
from app.api.routes import menu as menu_routes
from app.main import app
from app.repositories.menu_repository import load_menu_item_by_id
from app.services.menu_service import get_menu_item_for_restaurant
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
        ]),
        encoding="utf-8",
    )
    menu_items_file.write_text(
        json.dumps([
            make_item("item-a", 1, "Burger"),
            make_item("item-b", 2, "Pizza"),
        ]),
        encoding="utf-8",
    )

    return restaurants_file, menu_items_file


# ---------- repository ----------

def test_repository_finds_item_by_id(data_files):
    _, menu_items_file = data_files

    item = load_menu_item_by_id(1, "item-a", menu_items_file)

    assert item["name"] == "Burger"


def test_repository_returns_none_for_unknown_item_id(data_files):
    _, menu_items_file = data_files

    assert load_menu_item_by_id(1, "does-not-exist", menu_items_file) is None


def test_repository_returns_none_for_item_of_another_restaurant(data_files):
    _, menu_items_file = data_files

    assert load_menu_item_by_id(2, "item-a", menu_items_file) is None


# ---------- service ----------

def test_service_returns_requested_item(data_files):
    restaurants_file, menu_items_file = data_files

    item = get_menu_item_for_restaurant(
        1, "item-a", restaurants_file, menu_items_file
    )

    assert item["id"] == "item-a"
    assert item["restaurant_id"] == 1


def test_service_unknown_restaurant_raises_error(data_files):
    restaurants_file, menu_items_file = data_files

    with pytest.raises(ValueError, match="Restaurant not found"):
        get_menu_item_for_restaurant(
            99, "item-a", restaurants_file, menu_items_file
        )


def test_service_unknown_item_raises_error(data_files):
    restaurants_file, menu_items_file = data_files

    with pytest.raises(ValueError, match="Menu item not found"):
        get_menu_item_for_restaurant(
            1, "does-not-exist", restaurants_file, menu_items_file
        )


def test_service_item_of_another_restaurant_raises_error(data_files):
    restaurants_file, menu_items_file = data_files

    with pytest.raises(ValueError, match="Menu item not found"):
        get_menu_item_for_restaurant(
            2, "item-a", restaurants_file, menu_items_file
        )


# ---------- route ----------

@pytest.fixture
def client(data_files, monkeypatch):
    restaurants_file, menu_items_file = data_files

    def isolated_get_item(restaurant_id, item_id):
        return get_menu_item_for_restaurant(
            restaurant_id,
            item_id,
            restaurants_path=restaurants_file,
            menu_items_path=menu_items_file,
        )

    monkeypatch.setattr(
        menu_routes, "get_menu_item_for_restaurant", isolated_get_item
    )

    return TestClient(app)


def test_route_returns_item_with_status_200(client):
    response = client.get("/restaurants/1/menu/item-a")

    assert response.status_code == 200
    assert response.json()["id"] == "item-a"
    assert response.json()["name"] == "Burger"


def test_route_unknown_restaurant_returns_404(client):
    response = client.get("/restaurants/99/menu/item-a")

    assert response.status_code == 404
    assert response.json() == {"detail": "Restaurant not found"}


def test_route_unknown_item_returns_404(client):
    response = client.get("/restaurants/1/menu/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {"detail": "Menu item not found"}


def test_route_item_of_another_restaurant_returns_404(client):
    response = client.get("/restaurants/2/menu/item-a")

    assert response.status_code == 404
    assert response.json() == {"detail": "Menu item not found"}
