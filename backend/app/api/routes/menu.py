from app.schemas.menu_item import MenuItem, MenuItemCreate
from app.services.menu_service import add_menu_item
from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.post(
    "/restaurants/{restaurant_id}/menu",
    response_model=MenuItem,
    status_code=status.HTTP_201_CREATED,
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