from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class Restaurant(BaseModel):
    id: int
    owner_id: str
    name: str
    cuisine: str
    rating: float
    address: str


class RestaurantCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    cuisine: str = Field(min_length=1, max_length=100)
    address: str = Field(min_length=1, max_length=200)


class RestaurantUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str | None = Field(default=None, min_length=1, max_length=100)
    cuisine: str | None = Field(default=None, min_length=1, max_length=100)
    address: str | None = Field(default=None, min_length=1, max_length=200)
    @model_validator(mode="before")
    @classmethod
    def reject_null_values(cls, data):
        if isinstance(data, dict):
            for field in ("name", "cuisine", "address"):
                if field in data and data[field] is None:
                    raise ValueError(
                        f"{field} cannot be null"
                    )
        return data