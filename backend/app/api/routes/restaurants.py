
"""
FastAPI routes for restaurant operations.

This module defines HTTP endpoints for:
    - Listing restaurants with optional filters.
    - Retrieving an individual restaurant.
    - Creating a new restaurant.
    - Updating an existing restaurant.

Routes handle HTTP requests and responses, while restaurant
business logic is delegated to the service layer.

Creating and editing a restaurant require a signed-in restaurant
owner. The owner's ID comes from the login token, never from the
request body.
"""


from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import RESTAURANT_OWNER, require_role

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
def add_restaurant(
    restaurant_data: RestaurantCreate,
    user: dict = Depends(require_role(RESTAURANT_OWNER)),
):
    """
    Create a restaurant using validated request data.

    RestaurantCreate prevents clients from supplying
    server-managed fields such as rating or owner_id.

    The owner is the signed-in restaurant owner. Other roles get
    403 and callers without a valid token get 401.

    HTTP 201 indicates that the restaurant was created.
    """
    return create_restaurant(
        restaurant_data,
        user["id"],
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
    user: dict = Depends(require_role(RESTAURANT_OWNER)),
):
    """
    Update an existing restaurant using a partial request body.

    RestaurantUpdate validates editable fields and rejects
    protected fields such as ID, owner ID, and rating.

    Only a signed-in restaurant owner may call this, and the
    service checks that they own this restaurant (403 otherwise).
    """
    return update_restaurant(
        restaurant_id,
        user["id"],
        update_data,
    )
