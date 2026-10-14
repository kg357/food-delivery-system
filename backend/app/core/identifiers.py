from uuid import uuid4

def generate_restaurant_id(restaurants: list[dict]) -> int:
    """Generate a unique restaurant ID based on existing restaurant data."""
    existing_ids = {restaurant["id"] for restaurant in restaurants}
    new_id = 1
    while new_id in existing_ids:
        new_id += 1
    return new_id

def generate_owner_id() -> str:
    """Generate a unique owner ID using UUID."""
    return str(uuid4())