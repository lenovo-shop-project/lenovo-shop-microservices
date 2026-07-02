from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ContactMessageCreate(BaseModel):
    message: str = Field(
        min_length=2,
        max_length=3000,
    )


class ContactMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    email: str
    message: str
    is_processed: bool
    created_at: datetime


class PhoneRequestCreate(BaseModel):
    phone_number: str = Field(
        min_length=5,
        max_length=30,
    )


class PhoneRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    email: str
    phone_number: str
    is_processed: bool
    created_at: datetime