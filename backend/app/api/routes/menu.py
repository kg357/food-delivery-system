
"""
FastAPI routes for restaurant menu operations.

This module defines HTTP endpoints for:
    - Creating menu items.
    - Editing existing menu items.
    - Retrieving a restaurant's complete menu.
    - Retrieving individual menu items.

The route layer handles HTTP requests, validates input using
Pydantic schemas, and converts service errors into HTTP responses.

The service layer handles menu business logic, while
the repository layer handles JSON persistence.
"""


from fastapi import APIRouter, HTTPException, status

from app.schemas.menu_item import (
    MenuItem,
    MenuItemCreate,
    MenuItemUpdate,
)
from app.services.menu_service import (
    add_menu_item,
    edit_menu_item,
    get_menu_for_restaurant,
    get_menu_item_for_restaurant,
)


router = APIRouter()


# ============================================================
# Menu Item Creation
# ============================================================

@router.post(
    "/restaurants/{restaurant_id}/menu",
    response_model=MenuItem,
    status_code=status.HTTP_201_CREATED,
    summary="Create a menu item",
    description=(
        "Create a menu item for an existing restaurant. "
        "The backend generates the item's unique identifier."
    ),
    responses={
        404: {"description": "Restaurant not found"},
        422: {"description": "Invalid request body or restaurant_id"},
    },
)
def create_menu_item_endpoint(
    restaurant_id: int,
    item: MenuItemCreate,
):
    """
    Create a menu item associated with a restaurant.

    FastAPI validates the request body against MenuItemCreate.

    The service checks whether the restaurant exists,
    then creates and saves the menu item.

    Returns HTTP 201 when the item is created successfully.
    Returns HTTP 404 when the restaurant does not exist.
    """
    try:
        # model_dump() converts the validated Pydantic model
        # into a dictionary for the service layer.
        return add_menu_item(
            restaurant_id=restaurant_id,
            item_data=item.model_dump(),
        )

    except ValueError as error:
        # Translate a business-level error into an HTTP response.
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


# ============================================================
# Menu Item Editing
# ============================================================

@router.patch(
    "/restaurants/{restaurant_id}/menu/{item_id}",
    response_model=MenuItem,
    summary="Update a menu item",
    description=(
        "Partially update an existing menu item. "
        "Only supplied, non-null fields are applied."
    ),
    responses={
        404: {"description": "Restaurant not found or menu item not found"},
        422: {"description": "Invalid request body or restaurant_id"},
    },
)
def edit_menu_item_endpoint(
    restaurant_id: int,
    item_id: str,
    item: MenuItemUpdate,
):
    """
    Update a menu item belonging to a restaurant.

    FastAPI validates the request body against MenuItemUpdate.

    The service verifies that the restaurant and menu item exist,
    then applies the requested changes.

    Returns HTTP 200 for successful updates.
    Returns HTTP 404 when the restaurant or item is not found.
    """
    try:
        # exclude_unset=True ignores omitted fields.
        # exclude_none=True ignores fields explicitly set to null.
        # This prevents unspecified or null values from replacing
        # existing menu item information.
        return edit_menu_item(
            restaurant_id=restaurant_id,
            item_id=item_id,
            updates=item.model_dump(
                exclude_unset=True,
                exclude_none=True,
            ),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


# ============================================================
# Restaurant Menu Browsing
# ============================================================

@router.get(
    "/restaurants/{restaurant_id}/menu",
    response_model=list[MenuItem],
    summary="List restaurant menu items",
    description=(
        "Retrieve all menu items belonging to a restaurant. "
        "An existing restaurant without menu items returns an empty list."
    ),
    responses={
        404: {"description": "Restaurant not found"},
        422: {"description": "restaurant_id is not an integer"},
    },
)
def list_menu_items_endpoint(restaurant_id: int):
    """
    Retrieve all menu items associated with a restaurant.

    The service checks that the restaurant exists before
    retrieving its menu.

    Returns HTTP 200 with a list of menu items.
    Returns HTTP 200 with an empty list for an empty menu.
    Returns HTTP 404 when the restaurant does not exist.
    """
    try:
        return get_menu_for_restaurant(restaurant_id)

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


# ============================================================
# Individual Menu Item Retrieval
# ============================================================

@router.get(
    "/restaurants/{restaurant_id}/menu/{item_id}",
    response_model=MenuItem,
    summary="Get menu item details",
    description=(
        "Retrieve a specific menu item belonging to a restaurant "
        "using its unique item identifier."
    ),
    responses={
        404: {"description": "Restaurant not found or menu item not found"},
        422: {"description": "restaurant_id is not an integer"},
    },
)
def get_menu_item_endpoint(
    restaurant_id: int,
    item_id: str,
):
    """
    Retrieve an individual menu item.

    Both restaurant_id and item_id must match an existing record.

    Returns HTTP 200 when the item is found.
    Returns HTTP 404 when the restaurant or item does not exist.
    """
    try:
        return get_menu_item_for_restaurant(
            restaurant_id,
            item_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
