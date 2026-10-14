from fastapi import APIRouter, status
from app.services.restaurant_service import get_all_restaurants, create_restaurant
from app.schemas.restaurant import Restaurant, RestaurantCreate

router = APIRouter()

@router.get("/restaurants", response_model=list[Restaurant])
def list_restaurants():
    return get_all_restaurants()

@router.post("/restaurants", response_model=Restaurant, status_code=status.HTTP_201_CREATED
)
def add_restaurant(restaurant_data: RestaurantCreate):
    owner_id = "development_owner"
    return create_restaurant(restaurant_data, owner_id)