from pydantic import BaseModel, ConfigDict, EmailStr


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    image_url: str | None