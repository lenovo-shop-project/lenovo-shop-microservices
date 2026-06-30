from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import UserRole
from app.schemas.user import AdminUserResponse
from app.security import require_role
from app.services.user_service import UserService


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[
        Depends(require_role(UserRole.ADMIN)),
    ],
)


@router.get("/users", response_model=list[AdminUserResponse])
async def get_users_without_admins(db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    return await service.get_users_without_admins()