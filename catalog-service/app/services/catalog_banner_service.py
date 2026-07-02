from fastapi import HTTPException, status
from sqlalchemy import select, true
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.catalog_banner import CatalogBanner
from app.schemas.catalog_banner import CatalogBannerCreate


class CatalogBannerService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_catalog_banner(
        self,
        data: CatalogBannerCreate,
    ) -> CatalogBanner:
        old_banners = await self.db.scalars(
            select(CatalogBanner).where(
                CatalogBanner.is_active == true(),
            )
        )

        for banner in old_banners:
            banner.is_active = False

        title = data.title.strip() if data.title else None

        banner = CatalogBanner(
            title=title,
            image_url=data.image_url,
            is_active=True,
        )
        self.db.add(banner)
        await self.db.commit()
        await self.db.refresh(banner)
        return banner

    async def get_active_catalog_banner(
        self,
    ) -> CatalogBanner:
        banner = await self.db.scalar(
            select(CatalogBanner)
            .where(
                CatalogBanner.is_active == true(),
            )
            .order_by(
                CatalogBanner.id.desc(),
            )
        )

        if banner is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Банер каталогу не знайдено",
            )
        return banner