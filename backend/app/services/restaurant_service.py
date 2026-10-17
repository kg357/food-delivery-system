
"""
Business logic for restaurant operations.

The restaurant service layer sits between FastAPI routes
and the restaurant repository.

Its responsibilities include:
    - Retrieving and filtering restaurants.
    - Finding individual restaurants.
    - Creating new restaurants.
    - Verifying restaurant ownership.
    - Updating existing restaurant information.

The repository handles JSON persistence, while this
service handles business rules and missing-resource errors.
"""


from pathlib import Path

from fastapi import HTTPException

from app.core.config import RESTAURANTS_FILE
from app.core.identifiers import generate_restaurant_id
from app.repositories.restaurant_repository import (
    load_restaurant_by_id,
    load_restaurants,
    save_restaurants,
)
from app.schemas.restaurant import (
    Restaurant,
    RestaurantCreate,
    RestaurantUpdate,
)


# ============================================================
# Restaurant Retrieval and Filtering
# ============================================================

def get_all_restaurants(
    cuisine: str | None = None,
    min_rating: float | None = None,
) -> list[Restaurant]:
    """
    Retrieve restaurants, optionally filtering by cuisine and rating.

    Args:
        cuisine: Optional cuisine type. Matching is case-insensitive.
        min_rating: Optional minimum restaurant rating (inclusive).

    Returns:
        A list of Restaurant models matching all supplied filters.
        An empty list if no restaurants match.
    """

    restaurants = load_restaurants()

    # Only include restaurants matching the requested cuisine.
    # Case-insensitive comparison allows "italian" and "Italian"
    # to produce the same results.
    if cuisine:
        restaurants = [
            restaurant
            for restaurant in restaurants
            if restaurant["cuisine"].lower() == cuisine.lower()
        ]

    # Include restaurants with ratings equal to or above the
    # supplied minimum. The explicit None check allows 0.0.
    if min_rating is not None:
        restaurants = [
            restaurant
            for restaurant in restaurants
            if restaurant["rating"] >= min_rating
        ]

    # Convert stored dictionaries to validated Pydantic models.
    # **restaurant unpacks dictionary keys into model arguments.
    return [
        Restaurant(**restaurant)
        for restaurant in restaurants
    ]


def get_restaurant_by_id(restaurant_id: int) -> Restaurant:
    """
    Retrieve one restaurant by its ID.

    Args:
        restaurant_id: Identifier of the requested restaurant.

    Returns:
        The matching Restaurant model.

    Raises:
        HTTPException: Status 404 if the restaurant does not exist.
    """

    restaurant = load_restaurant_by_id(restaurant_id)

    if restaurant is None:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found",
        )

    return Restaurant(**restaurant)


# ============================================================
# Restaurant Creation
# ============================================================

def create_restaurant(
    restaurant_data: RestaurantCreate,
    owner_id: str,
    path: Path = RESTAURANTS_FILE,
) -> Restaurant:
    """
    Create and persist a new restaurant.

    Args:
        restaurant_data: Validated restaurant creation information.
        owner_id: Identifier of the restaurant's owner.
        path: Location of the restaurant JSON file.

    Returns:
        The newly created Restaurant model.

    New restaurants receive:
        - A unique integer ID.
        - The supplied owner ID.
        - An initial rating of 0.0.
    """

    # Load existing records so creating a restaurant preserves them.
    raw_data = load_restaurants(path)

    # Find the smallest unused positive restaurant ID.
    new_id = generate_restaurant_id(raw_data)

    new_restaurant = Restaurant(
        id=new_id,
        owner_id=owner_id,
        name=restaurant_data.name,
        cuisine=restaurant_data.cuisine,
        rating=0.0,
        address=restaurant_data.address,
    )

    # model_dump() converts the Pydantic model to a dictionary
    # suitable for JSON serialization.
    raw_data.append(new_restaurant.model_dump())

    save_restaurants(raw_data, path)

    return new_restaurant


# ============================================================
# Restaurant Ownership
# ============================================================

def verify_restaurant_ownership(
    restaurant_id: int,
    owner_id: str,
    path: Path = RESTAURANTS_FILE,
) -> Restaurant:
    """
    Verify that a restaurant exists and belongs to the supplied owner.

    Args:
        restaurant_id: Identifier of the requested restaurant.
        owner_id: Expected owner identifier.
        path: Location of the restaurant JSON file.

    Returns:
        The Restaurant model when ownership matches.

    Raises:
        HTTPException:
            403 if the restaurant belongs to another owner.
            404 if the restaurant does not exist.

    This verifies the supplied owner ID against stored data.
    It does not authenticate the identity of an API caller.
    """

    restaurants = load_restaurants(path)

    for restaurant in restaurants:
        if restaurant["id"] == restaurant_id:
            if restaurant["owner_id"] != owner_id:
                raise HTTPException(
                    status_code=403,
                    detail=(
                        "You do not have permission to modify "
                        "this restaurant."
                    ),
                )

            return Restaurant(**restaurant)

    raise HTTPException(
        status_code=404,
        detail="Restaurant not found.",
    )


# ============================================================
# Restaurant Updates
# ============================================================

def update_restaurant(
    restaurant_id: int,
    owner_id: str,
    update_data: RestaurantUpdate,
    path: Path = RESTAURANTS_FILE,
) -> Restaurant:
    """
    Update an existing restaurant's editable fields.

    Args:
        restaurant_id: Identifier of the restaurant to update.
        owner_id: Expected owner identifier.
        update_data: Validated partial update information.
        path: Location of the restaurant JSON file.

    Returns:
        The updated Restaurant model.

    Raises:
        HTTPException:
            403 if the supplied owner ID does not match.
            404 if the restaurant does not exist.
    """

    # Reject unauthorized or nonexistent restaurant updates
    # before making changes to stored data.
    verify_restaurant_ownership(restaurant_id, owner_id, path)

    restaurants = load_restaurants(path)

    # exclude_unset=True includes only fields explicitly supplied
    # in the PATCH request, preserving all omitted fields.
    changes = update_data.model_dump(exclude_unset=True)

    for restaurant in restaurants:
        if restaurant["id"] == restaurant_id:
            # Update only the requested fields.
            restaurant.update(changes)

            updated_restaurant = Restaurant(**restaurant)

            save_restaurants(restaurants, path)

            return updated_restaurant

    # Defensive fallback if the restaurant is no longer present
    # between the ownership check and the repository read.
    raise HTTPException(
        status_code=404,
        detail="Restaurant not found.",
    )
