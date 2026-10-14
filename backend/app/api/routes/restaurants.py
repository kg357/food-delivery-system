from app.schemas.restaurant import Restaurant, RestaurantCreate
from app.services.restaurant_service import get_all_restaurants, create_restaurant
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
 
@router.post("/restaurants", response_model=Restaurant, status_code=status.HTTP_201_CREATED
)
def add_restaurant(restaurant_data: RestaurantCreate):
    owner_id = "development_owner"
    return create_restaurant(restaurant_data, owner_id)