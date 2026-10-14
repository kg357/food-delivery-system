from app.repositories.menu_repository import (
    create_menu_item,
    load_menu_items,
    save_menu_items,
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