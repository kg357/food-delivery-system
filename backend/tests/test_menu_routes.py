import json

import pytest
from app.api.routes import menu as menu_routes
from app.main import app
from app.services.menu_service import edit_menu_item
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    restaurants_file = tmp_path / "restaurants.json"
    menu_items_file = tmp_path / "menu_items.json"

    restaurants_file.write_text(
        json.dumps([{"id": 1, "name": "Test Restaurant"}]),
        encoding="utf-8",
    )
    menu_items_file.write_text("[]", encoding="utf-8")

    original_add = menu_routes.add_menu_item

    def isolated_add(restaurant_id, item_data):
        return original_add(
            restaurant_id=restaurant_id,
            item_data=item_data,
            restaurants_path=restaurants_file,
            menu_items_path=menu_items_file,
        )

    monkeypatch.setattr(menu_routes, "add_menu_item", isolated_add)

    return TestClient(app)


def test_create_menu_item_success(client):
    response = client.post(
        "/restaurants/1/menu",
        json={
            "name": "Burger",
            "description": "Beef burger",
            "price": 12.99,
            "available": True,
        },
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Burger"
    assert response.json()["restaurant_id"] == 1
    assert "id" in response.json()


def test_create_menu_item_restaurant_not_found(client):
    response = client.post(
        "/restaurants/99/menu",
        json={
            "name": "Burger",
            "description": "Beef burger",
            "price": 12.99,
            "available": True,
        },
    )

    assert response.status_code == 404


def test_create_menu_item_invalid_price(client):
    response = client.post(
        "/restaurants/1/menu",
        json={
            "name": "Burger",
            "description": "Beef burger",
            "price": -5,
            "available": True,
        },
    )

    assert response.status_code == 422


def test_patch_menu_item(tmp_path, monkeypatch):
    restaurants_file = tmp_path / "restaurants.json"
    menu_items_file = tmp_path / "menu_items.json"

    restaurants_file.write_text(
        json.dumps([{"id": 1, "name": "Burger Place"}])
    )

    menu_items_file.write_text(
        json.dumps([{
            "id": "item-123",
            "restaurant_id": 1,
            "name": "Burger",
            "description": "Beef burger",
            "price": 12.99,
            "available": True
        }])
    )

    def isolated_edit(restaurant_id, item_id, updates):
        return edit_menu_item(
            restaurant_id=restaurant_id,
            item_id=item_id,
            updates=updates,
            restaurants_path=restaurants_file,
            menu_items_path=menu_items_file,
        )

    monkeypatch.setattr(menu_routes, "edit_menu_item", isolated_edit)

    client = TestClient(app)

    response = client.patch(
        "/restaurants/1/menu/item-123",
        json={"price": 14.99},
    )

    assert response.status_code == 200
    assert response.json()["price"] == 14.99
    assert response.json()["name"] == "Burger"
    assert response.json()["id"] == "item-123"

    saved_items = json.loads(menu_items_file.read_text())
    assert saved_items[0]["price"] == 14.99


def test_patch_menu_item_negative_price():
    client = TestClient(app)

    response = client.patch(
        "/restaurants/1/menu/item-123",
        json={"price": -6},
    )

    assert response.status_code == 422


def test_patch_menu_item_not_found(tmp_path, monkeypatch):
    restaurants_file = tmp_path / "restaurants.json"
    menu_items_file = tmp_path / "menu_items.json"

    restaurants_file.write_text(
        json.dumps([{"id": 1, "name": "Burger Place"}])
    )
    menu_items_file.write_text("[]")

    def isolated_edit(restaurant_id, item_id, updates):
        return edit_menu_item(
            restaurant_id=restaurant_id,
            item_id=item_id,
            updates=updates,
            restaurants_path=restaurants_file,
            menu_items_path=menu_items_file,
        )

    monkeypatch.setattr(menu_routes, "edit_menu_item", isolated_edit)

    client = TestClient(app)

    response = client.patch(
        "/restaurants/1/menu/nonexistent",
        json={"price": 14.99},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Menu item not found"