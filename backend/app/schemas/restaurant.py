
"""
Pydantic schemas for restaurant data.

Schemas define the structure and validation rules for
restaurant information handled by the API.

Three models are provided:
    Restaurant:
        Represents a complete restaurant record.

    RestaurantCreate:
        Validates data submitted when creating a restaurant.

    RestaurantUpdate:
        Validates partial updates to existing restaurants.

Separate creation and update schemas prevent clients from
modifying server-managed fields such as IDs and ratings.
"""


from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


# ============================================================
# Complete Restaurant Model
# ============================================================

class Restaurant(BaseModel):
    """
    Represent a complete restaurant record.

    This model includes information supplied by users as well
    as fields managed by the backend, such as the restaurant ID,
    owner ID, and rating.
    """

    id: int
    owner_id: str
    name: str
    cuisine: str
    rating: float
    address: str


# ============================================================
# Restaurant Creation Model
# ============================================================

class RestaurantCreate(BaseModel):
    """
    Validate information submitted when creating a restaurant.

    Required fields:
        name: Restaurant name, between 1 and 100 characters.
        cuisine: Cuisine type, between 1 and 100 characters.
        address: Restaurant address, between 1 and 200 characters.

    Restaurant IDs, owner IDs, and ratings are managed by the
    backend rather than supplied by the client.
    """

    # Remove surrounding whitespace from strings.
    # Reject unexpected fields instead of silently ignoring them.
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    # Field() enforces minimum and maximum string lengths.
    name: str = Field(min_length=1, max_length=100)
    cuisine: str = Field(min_length=1, max_length=100)
    address: str = Field(min_length=1, max_length=200)


# ============================================================
# Restaurant Update Model
# ============================================================

class RestaurantUpdate(BaseModel):
    """
    Validate partial updates to an existing restaurant.

    All fields may be omitted because PATCH requests only
    need to contain the information being changed.

    Explicit null values are rejected, preventing clients
    from replacing required restaurant information with None.

    Protected fields such as id, owner_id, and rating cannot
    be changed through this schema.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    # None defaults allow fields to be omitted from PATCH requests.
    # Non-null values must still satisfy the specified lengths.
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    cuisine: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    address: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    @model_validator(mode="before")
    @classmethod
    def reject_null_values(cls, data):
        """
        Reject fields explicitly set to null in an update request.

        A missing field means "leave this value unchanged."
        A field supplied as null is rejected.

        mode="before" runs this validator on the raw input
        before Pydantic processes individual field values.
        """
        if isinstance(data, dict):
            for field in ("name", "cuisine", "address"):
                if field in data and data[field] is None:
                    raise ValueError(
                        f"{field} cannot be null"
                    )

        return data
