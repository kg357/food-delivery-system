from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_restaurant_by_id():
    response = client.get("/restaurants/1")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Wasabi Ramen"


def test_get_second_restaurant():
    response = client.get("/restaurants/2")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Bella Pasta"


def test_get_invalid_restaurant_returns_404():
    response = client.get("/restaurants/999")

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Restaurant not found"
    }