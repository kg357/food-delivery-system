
"""
Tests for the restaurant API routes.

These tests verify how the FastAPI application handles HTTP
requests for restaurant browsing, filtering, details,
creation, and updates.

The tests cover:
    - Successful GET requests.
    - Restaurant filtering through query parameters.
    - HTTP 404 responses for missing restaurants.
    - HTTP 422 responses for invalid request data.
    - Successful POST and PATCH requests.
    - Correct communication between routes and services.

Repository and service dependencies are mocked where needed
so tests do not modify the application's development data.
"""


import pytest
from fastapi.testclient import TestClient

import app.services.restaurant_service as restaurant_service
from app.api.routes import restaurants as restaurant_routes
from app.main import app
from app.schemas.restaurant import (
    Restaurant,
    RestaurantCreate,
    RestaurantUpdate,
)


# ============================================================
# Test Fixtures
# ============================================================

@pytest.fixture
def restaurant_routes_client(monkeypatch, restaurant_data):
    """
    Provide a FastAPI test client using isolated restaurant data.

    TestClient sends simulated HTTP requests directly to FastAPI
    without requiring a running backend server.

    monkeypatch.setattr() temporarily replaces the restaurant
    repository functions used by the service layer.

    The original functions are automatically restored by pytest
    after each test.
    """

    def isolated_load_by_id(restaurant_id):
        """
        Find a restaurant in the sample data by its ID.

        next() returns the first matching record, or None
        when no restaurant has the requested ID.
        """
        return next(
            (
                restaurant
                for restaurant in restaurant_data
                if restaurant["id"] == restaurant_id
            ),
            None,
        )

    # Replace loading all restaurants with the shared sample data.
    monkeypatch.setattr(
        restaurant_service,
        "load_restaurants",
        lambda: restaurant_data,
    )

    # Replace individual restaurant lookup with an isolated version.
    monkeypatch.setattr(
        restaurant_service,
        "load_restaurant_by_id",
        isolated_load_by_id,
    )

    return TestClient(app)


# ============================================================
# Restaurant Browsing
# ============================================================

def test_restaurants_endpoint_returns_200(restaurant_routes_client):
    """
    Verify that the restaurant listing endpoint is accessible.

    HTTP 200 indicates that the request was processed
    successfully.
    """
    response = restaurant_routes_client.get("/restaurants")

    assert response.status_code == 200


def test_restaurants_endpoint_returns_correct_data(
    restaurant_routes_client,
):
    """
    Verify that the restaurant listing returns the expected data.

    The shared test fixture contains three restaurants.
    """
    response = restaurant_routes_client.get("/restaurants")

    # response.json() converts the HTTP JSON response into Python data.
    data = response.json()

    assert len(data) == 3
    assert data[0]["name"] == "Restaurant One"


# ============================================================
# Restaurant Filtering
# ============================================================

def test_filter_restaurants_by_cuisine(restaurant_routes_client):
    """
    Verify that the API filters restaurants by cuisine.

    The params argument supplies URL query parameters,
    equivalent to /restaurants?cuisine=Italian.
    """
    response = restaurant_routes_client.get(
        "/restaurants",
        params={"cuisine": "Italian"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Restaurant One"


def test_filter_restaurants_by_min_rating(restaurant_routes_client):
    """
    Verify that restaurants can be filtered by minimum rating.

    Only restaurants meeting or exceeding 4.5 stars
    should appear in the response.
    """
    response = restaurant_routes_client.get(
        "/restaurants",
        params={"min_rating": 4.5},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Restaurant One"


def test_filter_returns_empty_list(restaurant_routes_client):
    """
    Verify that filtering with no matches returns an empty list.

    An empty search result is valid, so the endpoint
    should return HTTP 200 rather than HTTP 404.
    """
    response = restaurant_routes_client.get(
        "/restaurants",
        params={"cuisine": "Mexican"},
    )

    assert response.status_code == 200
    assert response.json() == []


# ============================================================
# Restaurant Details
# ============================================================

def test_get_restaurant_by_id(restaurant_routes_client):
    """
    Verify that an existing restaurant can be retrieved by ID.

    The API should return HTTP 200 and the requested
    restaurant's information.
    """
    response = restaurant_routes_client.get("/restaurants/1")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Restaurant One"


def test_get_second_restaurant(restaurant_routes_client):
    """
    Verify that restaurant retrieval works for another valid ID.

    This confirms that the endpoint does not always
    return the first restaurant in storage.
    """
    response = restaurant_routes_client.get("/restaurants/2")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Restaurant Two"


def test_get_invalid_restaurant_returns_404(restaurant_routes_client):
    """
    Verify that requesting an unknown restaurant returns HTTP 404.

    HTTP 404 indicates that the requested resource does not
    exist. The API should also return a descriptive error.
    """
    response = restaurant_routes_client.get("/restaurants/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Restaurant not found"
    }


# ============================================================
# Restaurant Creation — Invalid Requests
# ============================================================

@pytest.mark.parametrize(
    "invalid_data",
    [
        # Missing required name.
        {
            "cuisine": "American",
            "address": "123 Main Street",
        },

        # Empty or whitespace-only name.
        {
            "name": "",
            "cuisine": "American",
            "address": "123 Main Street",
        },
        {
            "name": "   ",
            "cuisine": "American",
            "address": "123 Main Street",
        },

        # Empty required fields.
        {
            "name": "New Cafe",
            "cuisine": "",
            "address": "123 Main Street",
        },
        {
            "name": "New Cafe",
            "cuisine": "American",
            "address": "",
        },

        # Name exceeds the permitted length.
        {
            "name": "A" * 101,
            "cuisine": "American",
            "address": "123 Main Street",
        },

        # Fields that clients are not permitted to supply.
        {
            "name": "New Cafe",
            "cuisine": "American",
            "address": "123 Main Street",
            "rating": 5.0,
        },
        {
            "name": "New Cafe",
            "cuisine": "American",
            "address": "123 Main Street",
            "owner_id": "fake_owner",
        },

        # Invalid data type for the name.
        {
            "name": 123,
            "cuisine": "American",
            "address": "123 Main Street",
        },
    ],
)
def test_invalid_restaurant_creation(
    invalid_data,
    restaurant_routes_client,
):
    """
    Verify that invalid restaurant creation requests return HTTP 422.

    @pytest.mark.parametrize runs this test once for each
    invalid_data dictionary above, creating nine test cases.

    HTTP 422 means FastAPI understood the request but rejected
    its contents because they failed validation.
    """
    response = restaurant_routes_client.post(
        "/restaurants",
        json=invalid_data,
    )

    assert response.status_code == 422


# ============================================================
# Restaurant Creation — Successful Requests
# ============================================================

def test_create_restaurant_returns_201(
    monkeypatch,
    restaurant_routes_client,
):
    """
    Verify that a valid POST request returns the created restaurant.

    The service is replaced with a mock to prevent writing
    to the application's restaurant JSON file.

    HTTP 201 indicates that a new resource was created.
    """

    def mock_create_restaurant(restaurant_data, owner_id):
        # Verify that FastAPI passed a validated Pydantic model.
        assert isinstance(restaurant_data, RestaurantCreate)

        # The application currently uses a fixed demo owner.
        assert owner_id == "development_owner"

        return Restaurant(
            id=4,
            owner_id=owner_id,
            name=restaurant_data.name,
            cuisine=restaurant_data.cuisine,
            rating=0.0,
            address=restaurant_data.address,
        )

    monkeypatch.setattr(
        restaurant_routes,
        "create_restaurant",
        mock_create_restaurant,
    )

    response = restaurant_routes_client.post(
        "/restaurants",
        json={
            "name": "New Cafe",
            "cuisine": "Canadian",
            "address": "100 Main Street",
        },
    )

    assert response.status_code == 201
    assert response.json()["name"] == "New Cafe"
    assert response.json()["owner_id"] == "development_owner"
    assert response.json()["rating"] == 0.0


def test_create_restaurant_passes_correct_data(
    monkeypatch,
    restaurant_routes_client,
):
    """
    Verify that the creation route forwards request data correctly.

    A mock service records the arguments supplied by the route.
    The test then checks that the expected values were received.
    """
    received = {}

    def mock_create_restaurant(restaurant_data, owner_id):
        received["name"] = restaurant_data.name
        received["cuisine"] = restaurant_data.cuisine
        received["address"] = restaurant_data.address
        received["owner_id"] = owner_id

        return Restaurant(
            id=4,
            owner_id=owner_id,
            name=restaurant_data.name,
            cuisine=restaurant_data.cuisine,
            rating=0.0,
            address=restaurant_data.address,
        )

    monkeypatch.setattr(
        restaurant_routes,
        "create_restaurant",
        mock_create_restaurant,
    )

    response = restaurant_routes_client.post(
        "/restaurants",
        json={
            "name": "Test Bistro",
            "cuisine": "French",
            "address": "200 Oak Avenue",
        },
    )

    assert response.status_code == 201
    assert received == {
        "name": "Test Bistro",
        "cuisine": "French",
        "address": "200 Oak Avenue",
        "owner_id": "development_owner",
    }


# ============================================================
# Restaurant Updates — Invalid Requests
# ============================================================

@pytest.mark.parametrize(
    "invalid_data",
    [
        # Empty, missing-value, or excessively long names.
        {"name": ""},
        {"name": "   "},
        {"name": None},
        {"name": "A" * 101},

        # Invalid cuisine or address values.
        {"cuisine": ""},
        {"cuisine": None},
        {"address": ""},
        {"address": None},

        # Protected fields cannot be modified through PATCH.
        {"rating": 5.0},
        {"owner_id": "fake_owner"},
        {"id": 999},

        # Invalid data type.
        {"name": 123},
    ],
)
def test_invalid_restaurant_update(
    invalid_data,
    restaurant_routes_client,
):
    """
    Verify that invalid PATCH requests return HTTP 422.

    Parametrization runs the same test against twelve
    different invalid update payloads.
    """
    response = restaurant_routes_client.patch(
        "/restaurants/1",
        json=invalid_data,
    )

    assert response.status_code == 422


def test_invalid_update_does_not_call_service(
    monkeypatch,
    restaurant_routes_client,
):
    """
    Verify that invalid input is rejected before reaching the service.

    The update service is replaced by a function that immediately
    fails the test if called.

    Since the request contains invalid data, FastAPI validation
    should reject it without invoking the update service.
    """

    def fail_if_called(*args, **kwargs):
        pytest.fail("Update service should not be called")

    monkeypatch.setattr(
        restaurant_routes,
        "update_restaurant",
        fail_if_called,
    )

    response = restaurant_routes_client.patch(
        "/restaurants/1",
        json={"name": None},
    )

    assert response.status_code == 422


# ============================================================
# Restaurant Updates — Successful Requests
# ============================================================

def test_update_restaurant_returns_200(
    monkeypatch,
    restaurant_routes_client,
):
    """
    Verify that a valid PATCH request returns the updated restaurant.

    The service is mocked so this route test checks the HTTP
    response without modifying JSON storage.

    HTTP 200 indicates successful processing of the update.
    """

    def mock_update_restaurant(restaurant_id, owner_id, update_data):
        assert restaurant_id == 1
        assert owner_id == "development_owner"
        assert isinstance(update_data, RestaurantUpdate)

        return Restaurant(
            id=1,
            owner_id=owner_id,
            name=update_data.name,
            cuisine="Italian",
            rating=4.5,
            address="100 Main Street",
        )

    monkeypatch.setattr(
        restaurant_routes,
        "update_restaurant",
        mock_update_restaurant,
    )

    response = restaurant_routes_client.patch(
        "/restaurants/1",
        json={"name": "Updated Cafe"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Updated Cafe"
    assert data["cuisine"] == "Italian"


def test_update_restaurant_passes_only_requested_fields(
    monkeypatch,
    restaurant_routes_client,
):
    """
    Verify that partial updates preserve which fields were supplied.

    model_dump(exclude_unset=True) returns only fields explicitly
    provided to the Pydantic update model.

    This allows the service to distinguish a requested change
    from a field that the client did not include.
    """
    received = {}

    def mock_update_restaurant(restaurant_id, owner_id, update_data):
        received["restaurant_id"] = restaurant_id
        received["owner_id"] = owner_id

        received["changes"] = update_data.model_dump(
            exclude_unset=True
        )

        return Restaurant(
            id=restaurant_id,
            owner_id=owner_id,
            name="Original Cafe",
            cuisine="Italian",
            rating=4.5,
            address=update_data.address,
        )

    monkeypatch.setattr(
        restaurant_routes,
        "update_restaurant",
        mock_update_restaurant,
    )

    response = restaurant_routes_client.patch(
        "/restaurants/1",
        json={"address": "500 New Street"},
    )

    assert response.status_code == 200

    assert received == {
        "restaurant_id": 1,
        "owner_id": "development_owner",
        "changes": {"address": "500 New Street"},
    }

    assert response.json()["address"] == "500 New Street"
