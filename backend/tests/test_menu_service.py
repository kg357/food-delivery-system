import json

import pytest
from app.repositories.menu_repository import load_menu_items
from app.services.menu_service import add_menu_item, edit_menu_item


def test_add_menu_item_existing_restaurant(tmp_path):
    restaurants_file = tmp_path / "restaurants.json"
    menu_items_file = tmp_path / "menu_items.json"

    restaurants_file.write_text(
        json.dumps([
            {"id": 1, "name": "Test Restaurant"}
        ]),
        encoding="utf-8",
    )

    menu_items_file.write_text("[]", encoding="utf-8")

    new_item = add_menu_item(
        restaurant_id=1,
        item_data={
            "name": "Burger",
            "description": "Beef burger",
            "price": 12.99,
            "available": True,
        },
        restaurants_path=restaurants_file,
        menu_items_path=menu_items_file,
    )

    assert new_item["name"] == "Burger"
    assert new_item["restaurant_id"] == 1
    assert len(load_menu_items(menu_items_file)) == 1


def test_add_menu_item_nonexistent_restaurant(tmp_path):
    restaurants_file = tmp_path / "restaurants.json"
    menu_items_file = tmp_path / "menu_items.json"

    restaurants_file.write_text("[]", encoding="utf-8")
    menu_items_file.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="Restaurant not found"):
        add_menu_item(
            restaurant_id=99,
            item_data={
                "name": "Burger",
                "description": "Beef burger",
                "price": 12.99,
                "available": True,
            },
            restaurants_path=restaurants_file,
            menu_items_path=menu_items_file,
        )

    assert load_menu_items(menu_items_file) == []


def test_edit_menu_item(tmp_path):
    restaurants_file = tmp_path / "restaurants.json"
    menu_items_file = tmp_path / "menu_items.json"

    restaurants_file.write_text('[{"id": 1, "name": "Burger Place"}]')

    menu_items_file.write_text("""
    [{
        "id": "item-123",
        "restaurant_id": 1,
        "name": "Burger",
        "description": "Beef burger",
        "price": 12.99,
        "available": true
    }]
    """)

    result = edit_menu_item(
        restaurant_id=1,
        item_id="item-123",
        updates={"price": 14.99},
        restaurants_path=restaurants_file,
        menu_items_path=menu_items_file,
    )

    assert result["price"] == 14.99
    assert result["name"] == "Burger"
    assert result["id"] == "item-123"


def test_edit_menu_item_wrong_restaurant(tmp_path):
    restaurants_file = tmp_path / "restaurants.json"
    menu_items_file = tmp_path / "menu_items.json"

    restaurants_file.write_text("""
    [
        {"id": 1, "name": "Burger Place"},
        {"id": 2, "name": "Pizza Place"}
    ]
    """)

    menu_items_file.write_text("""
    [{
        "id": "item-123",
        "restaurant_id": 1,
        "name": "Burger",
        "description": "Beef burger",
        "price": 12.99,
        "available": true
    }]
    """)

    with pytest.raises(ValueError, match="Menu item not found"):
        edit_menu_item(
            restaurant_id=2,
            item_id="item-123",
            updates={"price": 14.99},
            restaurants_path=restaurants_file,
            menu_items_path=menu_items_file,
        )