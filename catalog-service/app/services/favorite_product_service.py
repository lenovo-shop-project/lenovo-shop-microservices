from fastapi import HTTPException, status
from sqlalchemy import delete, select, true
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.favorite_product import FavoriteProduct
from app.models.product import Product
from app.security import CurrentUser


class FavoriteProductService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _get_active_product_or_404(
        self,
        product_id: int,
    ) -> Product:
        product = await self.db.scalar(
            select(Product).where(
                Product.id == product_id,
                Product.is_available == true(),
            )
        )

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Товар не знайдено",
            )
        return product

    async def add_favorite_product(
        self,
        product_id: int,
        current_user: CurrentUser,
    ) -> Product:
        product = await self._get_active_product_or_404(product_id)

        existing_favorite = await self.db.scalar(
            select(FavoriteProduct).where(
                FavoriteProduct.user_id == current_user.id,
                FavoriteProduct.product_id == product_id,
            )
        )

        if existing_favorite is not None:
            return product

        favorite_product = FavoriteProduct(
            user_id=current_user.id,
            product_id=product_id,
        )
        self.db.add(favorite_product)
        await self.db.commit()
        return product

    async def remove_favorite_product(
        self,
        product_id: int,
        current_user: CurrentUser,
    ) -> None:
        favorite_product = await self.db.scalar(
            select(FavoriteProduct).where(
                FavoriteProduct.user_id == current_user.id,
                FavoriteProduct.product_id == product_id,
            )
        )

        if favorite_product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Товар не знайдено в улюблених",
            )

        await self.db.execute(
            delete(FavoriteProduct).where(
                FavoriteProduct.user_id == current_user.id,
                FavoriteProduct.product_id == product_id,
            )
        )
        await self.db.commit()

    async def get_my_favorite_products(
        self,
        current_user: CurrentUser,
    ) -> list[Product]:
        result = await self.db.scalars(
            select(Product)
            .join(
                FavoriteProduct,
                FavoriteProduct.product_id == Product.id,
            )
            .where(
                FavoriteProduct.user_id == current_user.id,
                Product.is_available == true(),
            )
            .order_by(
                FavoriteProduct.created_at.desc(),
            )
        )
        return list(result.all())