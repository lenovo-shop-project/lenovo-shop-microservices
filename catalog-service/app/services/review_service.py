from datetime import UTC, datetime
from fastapi import HTTPException, status
from sqlalchemy import select, true
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product
from app.models.review import Review
from app.security import CurrentUser
from app.schemas.review import (
    ReviewAdminResponseUpdate,
    ReviewCreate,
    ReviewUpdate,
)


class ReviewService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _get_active_product_or_404(self, product_id: int) -> Product:
        product = await self.db.scalar(
            select(Product).where(
                Product.id == product_id,
                Product.is_available == true(),
            )
        )
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Товар не найден",
            )
        return product

    async def _get_any_product_or_404(self, product_id: int) -> Product:
        product = await self.db.get(Product, product_id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Товар не найден",
            )
        return product

    async def _get_review_or_404(self, review_id: int) -> Review:
        review = await self.db.get(Review, review_id)
        if review is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Отзыв не найден",
            )
        return review

    async def get_product_reviews(self, product_id: int) -> list[Review]:
        await self._get_active_product_or_404(product_id)
        result = await self.db.scalars(
            select(Review)
            .where(Review.product_id == product_id)
            .order_by(Review.created_at.desc())
        )
        return list(result.all())

    async def create_review(
        self,
        product_id: int,
        data: ReviewCreate,
        current_user: CurrentUser,
    ) -> Review:
        await self._get_active_product_or_404(product_id)

        existing_review = await self.db.scalar(
            select(Review).where(
                Review.product_id == product_id,
                Review.user_id == current_user.id,
            )
        )

        if existing_review is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Вы уже оставили отзыв на этот товар",
            )

        review = Review(
            user_id=current_user.id,
            product_id=product_id,
            rating=data.rating,
            comment=data.comment.strip(),
        )

        self.db.add(review)

        try:
            await self.db.commit()
            await self.db.refresh(review)
        except IntegrityError as error:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Отзыв на этот товар уже существует",
            ) from error
        return review

    async def update_own_review(
        self,
        review_id: int,
        data: ReviewUpdate,
        current_user: CurrentUser,
    ) -> Review:
        review = await self._get_review_or_404(review_id)

        if review.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нельзя изменять чужой отзыв",
            )

        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нет данных для обновления",
            )

        if "rating" in update_data:
            if update_data["rating"] is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Оценка не может быть null",
                )

            review.rating = update_data["rating"]

        if "comment" in update_data:
            if update_data["comment"] is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Комментарий не может быть null",
                )

            review.comment = update_data["comment"].strip()

        review.updated_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def delete_own_review(
        self,
        review_id: int,
        current_user: CurrentUser,
    ) -> None:
        review = await self._get_review_or_404(review_id)
        if review.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нельзя удалять чужой отзыв",
            )
        await self.db.delete(review)
        await self.db.commit()

    async def get_all_reviews_admin(self) -> list[Review]:
        result = await self.db.scalars(
            select(Review).order_by(
                Review.created_at.desc(),
            )
        )
        return list(result.all())

    async def get_review_by_id_admin(self, review_id: int) -> Review:
        return await self._get_review_or_404(review_id)

    async def get_product_reviews_admin(self, product_id: int) -> list[Review]:
        await self._get_any_product_or_404(product_id)
        result = await self.db.scalars(
            select(Review)
            .where(Review.product_id == product_id)
            .order_by(Review.created_at.desc())
        )
        return list(result.all())

    async def delete_review_admin(self, review_id: int) -> None:
        review = await self._get_review_or_404(review_id)
        await self.db.delete(review)
        await self.db.commit()

    async def add_admin_response(self, review_id: int, data: ReviewAdminResponseUpdate) -> Review:
        review = await self._get_review_or_404(review_id)
        admin_response = data.admin_response.strip()
        if not admin_response:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Відповідь адміністратора не може бути порожньою",
            )
        review.admin_response = admin_response
        review.admin_response_created_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(review)
        return review