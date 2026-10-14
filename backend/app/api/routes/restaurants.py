from app.schemas.restaurant import Restaurant
from app.services.restaurant_service import get_all_restaurants
from fastapi import APIRouter

router = APIRouter()

@router.get("/restaurants", response_model=list[Restaurant])
def list_restaurants():
    return get_all_restaurants()