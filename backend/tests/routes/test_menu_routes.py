
"""
Tests for the menu API routes.

These tests verify how FastAPI handles HTTP requests for
creating, editing, browsing, and retrieving menu items.

The tests cover:
    - Successful menu item creation and editing.
    - Validation errors for invalid menu item data.
    - Handling nonexistent restaurants and menu items.
    - Retrieving restaurant menus and individual menu items.
    - Preventing access to items under incorrect restaurant IDs.

Temporary JSON files and patched service functions keep
the tests independent of the application's development data.
"""


import json

import pytest
from fastapi.testclient import TestClient

from app.api.routes import menu as menu_routes
from app.main import app
from app.services.menu_service import (
    edit_menu_item,
    get_menu_for_restaurant,
    get_menu_item_for_restaurant,
)


# ============================================================
# Test Fixtures
# ============================================================

@pytest.fixture
def client(tmp_path, monkeypatch):
    """
    Provide an isolated FastAPI client for menu creation tests.

    tmp_path creates temporary JSON files for each test.

    monkeypatch.setattr() temporarily replaces the route's
    add_menu_item function with one that uses these files
    instead of the application's development data.
    """
    restaurants_file = tmp_path / "restaurants.json"
    menu_items_file = tmp_path / "menu_items.json"

    restaurants_file.write_text(
        json.dumps([{"id": 1, "name": "Test Restaurant"}]),
        encoding="utf-8",
    )
    menu_items_file.write_text("[]", encoding="utf-8")

    original_add = menu_routes.add_menu_item

    def isolated_add(restaurant_id, item_data):
        """Call the real service using temporary JSON files."""
        return original_add(
            restaurant_id=restaurant_id,
            item_data=item_data,
            restaurants_path=restaurants_file,
            menu_items_path=menu_items_file,
        )

    monkeypatch.setattr(menu_routes, "add_menu_item", isolated_add)

    return TestClient(app)


@pytest.fixture
def menu_browse_client(data_files, monkeypatch):
    """
    Provide a client for browsing restaurant menus.

    The shared data_files fixture supplies sample restaurants
    and menu items stored in temporary JSON files.
    """
    restaurants_file, menu_items_file = data_files

    def isolated_get_menu(restaurant_id):
        """Retrieve menu items using the isolated test files."""
        return get_menu_for_restaurant(
            restaurant_id,
            restaurants_path=restaurants_file,
            menu_items_path=menu_items_file,
        )

    monkeypatch.setattr(
        menu_routes,
        "get_menu_for_restaurant",
        isolated_get_menu,
    )

    return TestClient(app)


@pytest.fixture
def menu_item_details_client(data_files, monkeypatch):
    """
    Provide a client for retrieving individual menu items.

    The route's service dependency is replaced so requests
    use the shared temporary JSON files.
    """
    restaurants_file, menu_items_file = data_files

    def isolated_get_item(restaurant_id, item_id):
        """Look up a menu item using the isolated test files."""
        return get_menu_item_for_restaurant(
            restaurant_id,
            item_id,
            restaurants_path=restaurants_file,
            menu_items_path=menu_items_file,
        )

    monkeypatch.setattr(
        menu_routes,
        "get_menu_item_for_restaurant",
        isolated_get_item,
    )

    return TestClient(app)


# ============================================================
# Menu Item Creation
# ============================================================

def test_create_menu_item_success(client):
    """
    Verify that a valid POST request creates a menu item.

    HTTP 201 indicates successful resource creation.
    The response must contain the item name, restaurant ID,
    and a generated item identifier.
    """
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
    """
    Verify that menu items cannot be added to nonexistent restaurants.

    Restaurant 99 is absent from the test data, so the API
    should return HTTP 404 Not Found.
    """
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
    """
    Verify that menu creation rejects negative prices.

    Pydantic validation should reject the request before
    the service attempts to create the menu item.

    HTTP 422 indicates invalid request data.
    """
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


# ============================================================
# Menu Item Editing
# ============================================================

def test_patch_menu_item(tmp_path, monkeypatch):
    """
    Verify that a valid PATCH request updates an existing menu item.

    The test uses temporary JSON files and confirms that
    both the response and saved data contain the new price.
    """
    restaurants_file = tmp_path / "restaurants.json"
    menu_items_file = tmp_path / "menu_items.json"

    restaurants_file.write_text(
        json.dumps([{"id": 1, "name": "Burger Place"}]),
        encoding="utf-8",
    )

    menu_items_file.write_text(
        json.dumps([
            {
                "id": "item-123",
                "restaurant_id": 1,
                "name": "Burger",
                "description": "Beef burger",
                "price": 12.99,
                "available": True,
            }
        ]),
        encoding="utf-8",
    )

    def isolated_edit(restaurant_id, item_id, updates):
        """Call the real edit service using temporary JSON files."""
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

    # Read the file directly to verify that the update was persisted.
    saved_items = json.loads(menu_items_file.read_text())
    assert saved_items[0]["price"] == 14.99


def test_patch_menu_item_negative_price(client):
    """
    Verify that a negative price is rejected during menu editing.

    HTTP 422 should be returned during request validation,
    before accessing or modifying any stored menu data.
    """

    response = client.patch(
        "/restaurants/1/menu/item-123",
        json={"price": -6},
    )

    assert response.status_code == 422


def test_patch_menu_item_not_found(tmp_path, monkeypatch):
    """
    Verify that editing a nonexistent menu item returns HTTP 404.

    The restaurant exists, but its temporary menu file is empty,
    so the requested item cannot be found.
    """
    restaurants_file = tmp_path / "restaurants.json"
    menu_items_file = tmp_path / "menu_items.json"

    restaurants_file.write_text(
        json.dumps([{"id": 1, "name": "Burger Place"}]),
        encoding="utf-8",
    )
    menu_items_file.write_text("[]", encoding="utf-8")

    def isolated_edit(restaurant_id, item_id, updates):
        """Call the real edit service using temporary JSON files."""
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


# ============================================================
# Restaurant Menu Browsing
# ============================================================

def test_browse_route_returns_menu_with_status_200(menu_browse_client):
    """
    Verify that a restaurant's menu can be retrieved.

    Restaurant 1 has two menu items in the shared test data.
    The API should return HTTP 200 and both items.
    """
    response = menu_browse_client.get("/restaurants/1/menu")

    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == [
        "Burger",
        "Fries",
    ]


def test_browse_route_unknown_restaurant_returns_404(menu_browse_client):
    """
    Verify that requesting a menu for an unknown restaurant returns 404.

    A nonexistent restaurant is different from an existing
    restaurant whose menu happens to be empty.
    """
    response = menu_browse_client.get("/restaurants/99/menu")

    assert response.status_code == 404
    assert response.json() == {"detail": "Restaurant not found"}


def test_browse_route_restaurant_with_no_menu_returns_empty_list(
    menu_browse_client,
):
    """
    Verify that a restaurant without menu items returns an empty list.

    Restaurant 3 exists but has no associated menu items.
    The correct response is HTTP 200 with an empty JSON array.
    """
    response = menu_browse_client.get("/restaurants/3/menu")

    assert response.status_code == 200
    assert response.json() == []


def test_browse_route_non_numeric_restaurant_id_returns_422(
    menu_browse_client,
):
    """
    Verify that restaurant IDs must be valid integers.

    FastAPI rejects 'abc' because the restaurant_id path
    parameter is defined as an integer.

    The API should return HTTP 422.
    """
    response = menu_browse_client.get("/restaurants/abc/menu")

    assert response.status_code == 422


# ============================================================
# Individual Menu Item Retrieval
# ============================================================

def test_item_details_route_returns_item_with_status_200(
    menu_item_details_client,
):
    """
    Verify that an individual menu item can be retrieved.

    The request identifies Restaurant 1 and item 'item-a'.
    Both identifiers must match the stored record.
    """
    response = menu_item_details_client.get(
        "/restaurants/1/menu/item-a"
    )

    assert response.status_code == 200
    assert response.json()["id"] == "item-a"
    assert response.json()["name"] == "Burger"


def test_item_details_route_unknown_restaurant_returns_404(
    menu_item_details_client,
):
    """
    Verify that an unknown restaurant returns HTTP 404
    when retrieving an individual menu item.
    """
    response = menu_item_details_client.get(
        "/restaurants/99/menu/item-a"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Restaurant not found"}


def test_item_details_route_unknown_item_returns_404(
    menu_item_details_client,
):
    """
    Verify that an unknown menu item returns HTTP 404.

    Restaurant 1 exists, but the requested item ID does not.
    """
    response = menu_item_details_client.get(
        "/restaurants/1/menu/does-not-exist"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Menu item not found"}


def test_item_details_route_item_of_another_restaurant_returns_404(
    menu_item_details_client,
):
    """
    Verify that menu item details respect restaurant association.

    Item 'item-a' belongs to Restaurant 1. Requesting that item
    under Restaurant 2 should return HTTP 404.
    """
    response = menu_item_details_client.get(
        "/restaurants/2/menu/item-a"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Menu item not found"}
