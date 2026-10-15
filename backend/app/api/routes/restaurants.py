from app.schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate
from app.services.restaurant_service import (
    create_restaurant,
    get_all_restaurants,
    get_restaurant_by_id,
    update_restaurant,
)
from fastapi import APIRouter, Query, status

router = APIRouter()

@router.get(
        "/restaurants", 
        response_model=list[Restaurant])
def list_restaurants(
    cuisine: str | None=None,
    min_rating: float | None = Query(
        default=None,
        ge=0,
        le=5,
        description="Minimum restaurant rating"
        )
):
    return get_all_restaurants(cuisine = cuisine, min_rating=min_rating)

@router.get("/restaurants/{restaurant_id}",
            response_model=Restaurant)
def restaurant_details(restaurant_id: int):
    return get_restaurant_by_id(restaurant_id)
 
@router.post("/restaurants", response_model=Restaurant, status_code=status.HTTP_201_CREATED
)
def add_restaurant(restaurant_data: RestaurantCreate):
    owner_id = "development_owner"
    return create_restaurant(restaurant_data, owner_id)

@router.patch("/restaurants/{restaurant_id}", response_model=Restaurant, status_code=status.HTTP_200_OK)
def edit_restaurant(restaurant_id: int, update_data: RestaurantUpdate):
    owner_id = "development_owner"
    return update_restaurant(restaurant_id, owner_id, update_data)
