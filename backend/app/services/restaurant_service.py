from app.repositories.restaurant_repository import load_restaurants
from app.schemas.restaurant import Restaurant

def get_all_restaurants() -> list[Restaurant]:
    raw_data = load_restaurants()
    return [Restaurant(**item) for item in raw_data]
