
"""
FastAPI routes for restaurant operations.

This module defines HTTP endpoints for:
    - Listing restaurants with optional filters.
    - Retrieving an individual restaurant.
    - Creating a new restaurant.
    - Updating an existing restaurant.

Routes handle HTTP requests and responses, while restaurant
business logic is delegated to the service layer.

For Milestone 1, restaurant creation and editing use a fixed
development owner ID rather than real authentication.
"""


from fastapi import APIRouter, Query, status

from app.schemas.restaurant import (
    Restaurant,
    RestaurantCreate,
    RestaurantUpdate,
)
from app.services.restaurant_service import (
    create_restaurant,
    get_all_restaurants,
    get_restaurant_by_id,
    update_restaurant,
)


router = APIRouter()


# ============================================================
# Restaurant Browsing
# ============================================================

@router.get(
    "/restaurants",
    response_model=list[Restaurant],
    summary="List restaurants",
    description=(
        "Retrieve all restaurants, optionally filtering by "
        "cuisine and minimum rating."
    ),
)
def list_restaurants(
    cuisine: str | None = None,
    min_rating: float | None = Query(
        default=None,
        ge=0,
        le=5,
        description="Minimum restaurant rating, from 0 to 5.",
    ),
):
    """
    Return restaurants matching the supplied filters.

    cuisine:
        Optional cuisine filter, matched case-insensitively.

    min_rating:
        Optional minimum rating between 0 and 5, inclusive.

    Both filters can be supplied in the same request.
    """
    return get_all_restaurants(
        cuisine=cuisine,
        min_rating=min_rating,
    )


# ============================================================
# Restaurant Details
# ============================================================

@router.get(
    "/restaurants/{restaurant_id}",
    response_model=Restaurant,
    summary="Get restaurant details",
    description="Retrieve a restaurant by its unique integer ID.",
)
def restaurant_details(restaurant_id: int):
    """
    Return a single restaurant.

    FastAPI converts the restaurant_id URL parameter to an integer.

    A missing restaurant produces HTTP 404, raised by the service.
    """
    return get_restaurant_by_id(restaurant_id)


# ============================================================
# Restaurant Creation
# ============================================================

@router.post(
    "/restaurants",
    response_model=Restaurant,
    status_code=status.HTTP_201_CREATED,
    summary="Create a restaurant",
    description=(
        "Create a restaurant using its name, cuisine, and address. "
        "The backend assigns its ID, owner ID, and initial rating."
    ),
)
def add_restaurant(restaurant_data: RestaurantCreate):
    """
    Create a restaurant using validated request data.

    RestaurantCreate prevents clients from supplying
    server-managed fields such as rating or owner_id.

    HTTP 201 indicates that the restaurant was created.
    """

    # Milestone 1 uses a fixed owner identity for demonstration.
    # This is not a real authentication or authorization system.
    owner_id = "development_owner"

    return create_restaurant(
        restaurant_data,
        owner_id,
    )


# ============================================================
# Restaurant Updates
# ============================================================

@router.patch(
    "/restaurants/{restaurant_id}",
    response_model=Restaurant,
    status_code=status.HTTP_200_OK,
    summary="Update a restaurant",
    description=(
        "Partially update a restaurant's name, cuisine, or address. "
        "Only fields supplied in the request are modified."
    ),
)
def edit_restaurant(
    restaurant_id: int,
    update_data: RestaurantUpdate,
):
    """
    Update an existing restaurant using a partial request body.

    RestaurantUpdate validates editable fields and rejects
    protected fields such as ID, owner ID, and rating.

    The service checks ownership before applying changes.
    """

    # The demo owner must match the restaurant's stored owner ID.
    owner_id = "development_owner"

    return update_restaurant(
        restaurant_id,
        owner_id,
        update_data,
    )
