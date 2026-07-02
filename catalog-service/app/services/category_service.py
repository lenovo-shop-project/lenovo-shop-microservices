from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.category import Category
from app.schemas.category import CategoryCreate

class CategoryService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_category(
        self,
        data: CategoryCreate,
    ) -> Category:
        name = data.name.strip()

        existing_category = await self.db.scalar(
            select(Category).where(
                Category.name == name,
            )
        )

        if existing_category is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Категория с таким названием уже существует",
            )

        category = Category(
            name=name,
        )

        self.db.add(category)

        try:
            await self.db.commit()
            await self.db.refresh(category)

        except IntegrityError as error:
            await self.db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Категория с таким названием уже существует",
            ) from error

        return category

    async def get_all_categories(
        self,
    ) -> list[Category]:
        result = await self.db.scalars(
            select(Category).order_by(
                Category.name,
            )
        )

        return list(result.all())
