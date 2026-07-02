from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class ProductCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
    )
    description: str | None = Field(
        default=None,
        max_length=5000,
    )
    price: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2,
    )
    stock: int = Field(
        default=0,
        ge=0,
    )
    image_url: str | None = Field(
        default=None,
        max_length=500,
    )
    category_id: int = Field(gt=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(
    default=None,
    min_length=1,
    max_length=255,
    )
    description: str | None = Field(
        default=None,
        max_length=5000,
    )
    price: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=10,
        decimal_places=2,
    )
    stock: int | None = Field(
        default=None,
        ge=0,
    )
    image_url: str | None = Field(
        default=None,
        max_length=500,
    )
    category_id: int | None = Field(
        default=None,
        gt=0,
    )


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None
    price: Decimal
    stock: int
    is_available: bool
    image_url: str | None
    category_id: int