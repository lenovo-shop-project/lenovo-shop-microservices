from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    rating: int = Field(
        ge=1,
        le=5,
    )
    comment: str = Field(
        min_length=2,
        max_length=2000,
    )


class ReviewUpdate(BaseModel):
    rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )
    comment: str | None = Field(
        default=None,
        min_length=2,
        max_length=2000,
    )


class ReviewAdminResponseUpdate(BaseModel):
    admin_response: str = Field(
        min_length=2,
        max_length=2000,
    )


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    product_id: int
    rating: int
    comment: str
    created_at: datetime
    updated_at: datetime
    admin_response: str | None
    admin_response_created_at: datetime | None