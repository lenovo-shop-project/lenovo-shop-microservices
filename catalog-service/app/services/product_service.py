from fastapi import HTTPException, status
from sqlalchemy import select, true
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.category import Category
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

class ProductService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _get_category_or_404(
        self,
        category_id: int,
    ) -> Category:
        category = await self.db.get(
            Category,
            category_id,
        )

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена",
            )
        return category

    async def _get_product_or_404(
        self,
        product_id: int,
        include_inactive: bool,
    ) -> Product:
        statement = select(Product).where(
            Product.id == product_id,
        )

        if not include_inactive:
            statement = statement.where(
                Product.is_available == true(),
            )

        product = await self.db.scalar(statement)

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Товар не найден",
            )
        return product

    async def _save_product(
        self,
        product: Product,
    ) -> Product:
        try:
            await self.db.commit()
            await self.db.refresh(product)

        except IntegrityError as error:
            await self.db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Не удалось сохранить товар",
            ) from error
        return product

    async def create_product(
        self,
        data: ProductCreate,
    ) -> Product:
        await self._get_category_or_404(
            data.category_id,
        )

        product = Product(
            name=data.name.strip(),
            description=data.description,
            price=data.price,
            stock=data.stock,
            image_url=data.image_url,
            category_id=data.category_id,
            is_available=True,
        )

        self.db.add(product)
        return await self._save_product(product)

    async def update_product(
        self,
        product_id: int,
        data: ProductUpdate,
    ) -> Product:
        product = await self._get_product_or_404(
            product_id=product_id,
            include_inactive=True,
        )

        update_data = data.model_dump(
            exclude_unset=True,
        )

        if "category_id" in update_data:
            category_id = update_data["category_id"]

            if category_id is not None:
                await self._get_category_or_404(
                    category_id,
                )

        if "name" in update_data:
            name = update_data["name"]

            if name is not None:
                update_data["name"] = name.strip()

        for field_name, value in update_data.items():
            setattr(
                product,
                field_name,
                value,
            )
        return await self._save_product(product)

    async def deactivate_product(
        self,
        product_id: int,
    ) -> Product:
        product = await self._get_product_or_404(
            product_id=product_id,
            include_inactive=True,
        )

        product.is_available = False
        return await self._save_product(product)

    async def activate_product(
        self,
        product_id: int,
    ) -> Product:
        product = await self._get_product_or_404(
            product_id=product_id,
            include_inactive=True,
        )

        product.is_available = True
        return await self._save_product(product)

    async def get_active_products(
        self,
    ) -> list[Product]:
        result = await self.db.scalars(
            select(Product)
            .where(
                Product.is_available == true(),
            )
            .order_by(Product.id)
        )
        return list(result.all())

    async def get_active_product_by_id(
        self,
        product_id: int,
    ) -> Product:
        return await self._get_product_or_404(
            product_id=product_id,
            include_inactive=False,
        )

    async def get_all_products_admin(
        self,
    ) -> list[Product]:
        result = await self.db.scalars(
            select(Product).order_by(
                Product.id,
            )
        )
        return list(result.all())

    async def get_product_by_id_admin(
        self,
        product_id: int,
    ) -> Product:
        return await self._get_product_or_404(
            product_id=product_id,
            include_inactive=True,
        )

    async def reserve_stock(
        self,
        product_id: int,
        quantity: int,
    ) -> Product:
        product = await self._get_product_or_404(
            product_id=product_id,
            include_inactive=False,
        )

        if product.stock < quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Недостатньо товару на складі",
            )
        product.stock -= quantity
        return await self._save_product(product)

    async def restore_stock(
        self,
        product_id: int,
        quantity: int,
    ) -> Product:
        product = await self._get_product_or_404(
            product_id=product_id,
            include_inactive=True,
        )
        product.stock += quantity
        return await self._save_product(product)