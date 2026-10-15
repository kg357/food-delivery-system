from app.repositories.menu_repository import (
    create_menu_item,
    load_menu_items,
    save_menu_items,
    update_menu_item,
)


def test_create_menu_item(tmp_path):
    test_file = tmp_path / "menu_items.json"

    save_menu_items([], test_file)

    new_item = create_menu_item(
        restaurant_id=1,
        item_data={
            "name": "Burger",
            "description": "Beef burger",
            "price": 12.99,
            "available": True,
        },
        path=test_file,
    )

    saved_items = load_menu_items(test_file)

    assert len(saved_items) == 1
    assert saved_items[0]["id"] == new_item["id"]
    assert saved_items[0]["name"] == "Burger"
    assert saved_items[0]["restaurant_id"] == 1


def test_update_menu_item(tmp_path):
    test_file = tmp_path / "menu_items.json"

    original_item = {
        "id": "item-123",
        "restaurant_id": 1,
        "name": "Burger",
        "description": "Beef burger",
        "price": 12.99,
        "available": True,
    }

    save_menu_items([original_item], test_file)

    updated_item = update_menu_item(
        restaurant_id=1,
        item_id="item-123",
        updates={"price": 14.99},
        path=test_file,
    )

    saved_items = load_menu_items(test_file)

    assert updated_item["price"] == 14.99
    assert saved_items[0]["price"] == 14.99
    assert saved_items[0]["name"] == "Burger"
    assert saved_items[0]["id"] == "item-123"



def test_update_menu_item_wrong_restaurant(tmp_path):
    test_file = tmp_path / "menu_items.json"

    original_item = {
        "id": "item-456",
        "restaurant_id": 1,
        "name": "Burger",
        "description": "Beef burger",
        "price": 12.99,
        "available": True,
    }

    save_menu_items([original_item], test_file)

    updated_item = update_menu_item(
        restaurant_id=2,
        item_id="item-456",
        updates={"price": 14.99},
        path=test_file,
    )

    assert updated_item is None
    assert load_menu_items(test_file)[0]["price"] == 12.99