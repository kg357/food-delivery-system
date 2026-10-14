from pydantic import BaseModel, Field


class MenuItemCreate(BaseModel):
    name: str = Field(min_length=1)
    description: str
    price: float = Field(ge=0)
    available: bool = True

class MenuItem(MenuItemCreate):
    id: str
    restaurant_id: int