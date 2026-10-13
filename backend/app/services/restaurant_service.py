from app.repositories.restaurant_repository import load_restaurants
from app.schemas.restaurant import Restaurant


def get_all_restaurants(
        cuisine: str | None = None,
        min_rating: float | None = None
) -> list[Restaurant]:
    restaurants = load_restaurants()

    # Filter by cuisine
    if cuisine:
        filtered_restaurants = []

        for restaurant in restaurants:
            if restaurant['cuisine'].lower() == cuisine.lower():
                filtered_restaurants.append(restaurant)

        restaurants = filtered_restaurants

    # Filter by rating
    if min_rating is not None:
        filtered_restaurants = []
        
        for restaurant in restaurants:
            if restaurant['rating'] >= min_rating:
                filtered_restaurants.append(restaurant)

        restaurants = filtered_restaurants

    # Convert each raw dictionary into a Restaurant objec using
    # dictionary unpacking (**restaurant), then return the new list of objects
    return [Restaurant(**restaurant) for restaurant in restaurants]
