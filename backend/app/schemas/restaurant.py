from pydantic import BaseModel, ConfigDict

class Restaurant(BaseModel):
    id: int
    owner_id: str
    name: str
    cuisine: str
    rating: float
    address: str

class RestaurantCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str
    cuisine: str
    address: str