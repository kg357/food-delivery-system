from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, computed_field

MAX_QUANTITY = 2_147_483_647
Quantity = Annotated[int, Field(strict=True, gt=0, le=MAX_QUANTITY)]
Money = Annotated[Decimal, Field(ge=0, allow_inf_nan=False)]

class CartItemCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    restaurant_id: int = Field(strict=True, gt=0)
    item_id: str = Field(min_length=1)
    quantity: Quantity = 1

class CartQuantityUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quantity: Quantity

class CartItem(BaseModel):
    item_id: str
    name: str
    unit_price: Money
    quantity: Quantity

    @computed_field
    @property
    def total_price(self) -> Decimal:
        return self.unit_price * self.quantity

class Cart(BaseModel):
    id: str
    customer_id: str
    restaurant_id: int | None = None
    items: list[CartItem] = Field(default_factory=list)

    @computed_field
    @property
    def subtotal(self) -> Decimal:
        return sum((item.total_price for item in self.items), Decimal("0.00"))

    @computed_field
    @property
    def total(self) -> Decimal:
        return self.subtotal
