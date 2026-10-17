
"""
Repository functions for restaurant JSON persistence.

The repository layer is responsible for reading and writing
restaurant records stored in backend/data/restaurants.json.

It does not perform HTTP request handling or business logic.
Those responsibilities belong to the route and service layers.

An optional file path allows tests to use temporary JSON files
without modifying the application's development data.
"""


import json
from pathlib import Path

from app.core.config import RESTAURANTS_FILE


# ============================================================
# Loading Restaurants
# ============================================================

def load_restaurants(path: Path = RESTAURANTS_FILE) -> list[dict]:
    """
    Load all restaurant records from a JSON file.

    Args:
        path: Location of the restaurant JSON file.
            Defaults to the configured restaurants file.

    Returns:
        A list of dictionaries containing restaurant records.
        An empty JSON array produces an empty list.

    Raises:
        FileNotFoundError: If the requested file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """

    # The with statement automatically closes the file.
    # json.load() converts JSON file contents into Python data.
    with path.open(encoding="utf-8") as file:
        return json.load(file)


# ============================================================
# Retrieving Individual Restaurants
# ============================================================

def load_restaurant_by_id(
    restaurant_id: int,
    path: Path = RESTAURANTS_FILE,
) -> dict | None:
    """
    Retrieve a restaurant using its unique ID.

    Args:
        restaurant_id: Identifier of the requested restaurant.
        path: Location of the restaurant JSON file.

    Returns:
        The matching restaurant dictionary if found.
        None if no restaurant has the requested ID.

    The repository returns None rather than raising an HTTP
    exception. The service layer decides how missing
    restaurants should be handled.
    """

    restaurants = load_restaurants(path)

    for restaurant in restaurants:
        if restaurant["id"] == restaurant_id:
            return restaurant

    return None


# ============================================================
# Saving Restaurants
# ============================================================

def save_restaurants(
    restaurants: list[dict],
    path: Path = RESTAURANTS_FILE,
) -> None:
    """
    Save a complete collection of restaurants to JSON.

    Args:
        restaurants: Restaurant records to persist.
        path: Destination JSON file.

    The existing file is overwritten with the supplied
    restaurant collection.

    indent=2 makes the JSON readable when inspecting
    stored records during development.
    """

    # Opening with "w" replaces the file's existing contents.
    # json.dump() writes Python data as JSON.
    with path.open("w", encoding="utf-8") as file:
        json.dump(restaurants, file, indent=2)
