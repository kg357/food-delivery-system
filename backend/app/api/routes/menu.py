from app.schemas.menu_item import MenuItem, MenuItemCreate, MenuItemUpdate
from app.services.menu_service import (
    add_menu_item,
    edit_menu_item,
    get_menu_for_restaurant,
    get_menu_item_for_restaurant,
)
from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.post(
    "/restaurants/{restaurant_id}/menu",
    response_model=MenuItem,
    status_code=status.HTTP_201_CREATED,
    summary="Add a menu item",
    description=(
        "Creates a new menu item for the given restaurant and returns it "
        "with its generated id. The name must not be empty and the price "
        "must not be negative."
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
    try:
        return add_menu_item(
            restaurant_id=restaurant_id,
            item_data=item.model_dump(),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


@router.patch(
    "/restaurants/{restaurant_id}/menu/{item_id}",
    response_model=MenuItem,
    summary="Update a menu item",
    description=(
        "Updates only the fields provided for an existing menu item of the "
        "given restaurant and returns the updated item. Omitted fields are "
        "left unchanged."
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
    try:
        return edit_menu_item(
            restaurant_id=restaurant_id,
            item_id=item_id,
            updates=item.model_dump(exclude_unset=True, exclude_none=True),
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
            ) from error


@router.get(
    "/restaurants/{restaurant_id}/menu",
    response_model=list[MenuItem],
    summary="List a restaurant's menu",
    description=(
        "Returns every menu item that belongs to the given restaurant, "
        "including items marked as unavailable. Returns an empty list if "
        "the restaurant has no menu items."
    ),
    responses={
        404: {"description": "Restaurant not found"},
        422: {"description": "restaurant_id is not an integer"},
    },
)
def list_menu_items_endpoint(restaurant_id: int):
    try:
        return get_menu_for_restaurant(restaurant_id)
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


@router.get(
    "/restaurants/{restaurant_id}/menu/{item_id}",
    response_model=MenuItem,
    summary="Get one menu item",
    description=(
        "Returns a single menu item of the given restaurant. The item must "
        "belong to that restaurant; an item id from a different restaurant "
        "is treated as not found."
    ),
    responses={
        404: {"description": "Restaurant not found or menu item not found"},
        422: {"description": "restaurant_id is not an integer"},
    },
)
def get_menu_item_endpoint(restaurant_id: int, item_id: str):
    try:
        return get_menu_item_for_restaurant(restaurant_id, item_id)
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
