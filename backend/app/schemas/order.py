from pydantic import BaseModel, Field

class OrderItem(BaseModel):
    item_id: str
    name: str
    description: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(ge=0)
    total_price: float = Field(ge=0)

class Order(BaseModel):
    id: str
    customer_id: str
    restaurant_id: int
    items: list[OrderItem]
    subtotal: float
    total: float
