
"""
Pydantic schemas for restaurant menu items.

These models define the structure and validation rules
for menu item information handled by the API.

Three models are provided:
    MenuItemCreate:
        Validates information supplied when adding a menu item.

    MenuItem:
        Represents a complete menu item, including its identifiers.

    MenuItemUpdate:
        Validates partial updates to an existing menu item.
"""


from pydantic import BaseModel, Field


# ============================================================
# Menu Item Creation
# ============================================================

class MenuItemCreate(BaseModel):
    """
    Validate information submitted when creating a menu item.

    Fields:
        name: Required, nonempty item name.
        description: Required text describing the item.
        price: Required, nonnegative item price.
        available: Whether the item is available, defaulting to True.

    Item and restaurant identifiers are assigned separately
    rather than supplied through this creation schema.
    """

    name: str = Field(min_length=1)
    description: str
    price: float = Field(ge=0)
    available: bool = True


# ============================================================
# Complete Menu Item Model
# ============================================================

class MenuItem(MenuItemCreate):
    """
    Represent a complete menu item record.

    Inheriting from MenuItemCreate provides the name,
    description, price, and availability fields.

    The complete model also includes:
        id: Unique identifier of the menu item.
        restaurant_id: Identifier of its associated restaurant.
    """

    id: str
    restaurant_id: int


# ============================================================
# Menu Item Update
# ============================================================

class MenuItemUpdate(BaseModel):
    """
    Validate partial updates to existing menu items.

    All fields may be omitted, allowing clients to change
    only the information they wish to update.

    The menu item ID and restaurant ID cannot be modified
    through the declared update fields.
    """

    name: str | None = Field(default=None, min_length=1)
    description: str | None = None
    price: float | None = Field(default=None, ge=0)
    available: bool | None = None
