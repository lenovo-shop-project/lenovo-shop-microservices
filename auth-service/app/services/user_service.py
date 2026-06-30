from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_users_without_admins(self) -> list[User]:
        result = await self.db.scalars(
            select(User)
            .where(
                User.role != UserRole.ADMIN,
            )
            .order_by(
                User.id,
            )
        )
        return list(result.all())

    async def update_avatar(self, user: User, image_url: str) -> User:
        user.image_url = image_url
        await self.db.commit()
        await self.db.refresh(user)
        return user