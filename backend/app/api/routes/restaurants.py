from app.schemas.restaurant import Restaurant
from app.services.restaurant_service import get_all_restaurants
from fastapi import APIRouter, Query

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
