from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CatalogBannerCreate(BaseModel):
    title: str | None = Field(
        default=None,
        max_length=255,
    )
    image_url: str = Field(max_length=1000)


class CatalogBannerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str | None
    image_url: str
    is_active: bool
    created_at: datetime