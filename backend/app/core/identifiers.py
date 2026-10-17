
"""
Utilities for generating restaurant and owner identifiers.

Restaurant IDs are positive integers that do not conflict
with IDs already present in the restaurant data.

Owner IDs are generated as UUID strings, providing identifiers
that are extremely unlikely to collide.
"""


from uuid import uuid4


# ============================================================
# Restaurant ID Generation
# ============================================================

def generate_restaurant_id(restaurants: list[dict]) -> int:
    """
    Generate an unused restaurant ID.

    Args:
        restaurants: Existing restaurant records, each containing
            an integer 'id' field.

    Returns:
        An integer ID that does not occur in the existing records.

    The algorithm starts at 1 and finds the smallest positive
    integer that is not already in use.
    """

    # A set comprehension collects existing IDs for efficient lookup.
    existing_ids = {
        restaurant["id"]
        for restaurant in restaurants
    }

    new_id = 1

    # Skip IDs that are already assigned to restaurants.
    while new_id in existing_ids:
        new_id += 1

    return new_id


# ============================================================
# Owner ID Generation
# ============================================================

def generate_owner_id() -> str:
    """
    Generate a new owner identifier.

    Returns:
        A UUID version 4 represented as a string.

    uuid4() produces a random UUID. Converting it to a string
    makes it suitable for JSON storage and API responses.
    """
    return str(uuid4())