from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.security import CurrentUser, UserRole, require_role
from app.schemas.product import ProductResponse
from app.services.product_service import ProductService
from app.schemas.category import CategoryResponse
from app.services.category_service import CategoryService
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewUpdate
from app.services.review_service import ReviewService
from app.schemas.catalog_banner import CatalogBannerResponse
from app.services.catalog_banner_service import CatalogBannerService
from app.services.favorite_product_service import FavoriteProductService

router = APIRouter(
    prefix="/client",
    tags=["Client"],
)


@router.get("/products", response_model=list[ProductResponse])
async def get_active_products(db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    return await service.get_active_products()


@router.get("/categories", response_model=list[CategoryResponse])
async def get_all_categories(db: AsyncSession = Depends(get_db)):
    service = CategoryService(db)
    return await service.get_all_categories()


@router.get("/products/{product_id}", response_model=ProductResponse, dependencies=[Depends(require_role(UserRole.CLIENT))])
async def get_active_product_by_id(product_id: int, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    return await service.get_active_product_by_id(product_id)


@router.get("/products/{product_id}/reviews", response_model=list[ReviewResponse])
async def get_product_reviews(product_id: int, db: AsyncSession = Depends(get_db)):
    service = ReviewService(db)
    return await service.get_product_reviews(product_id)


@router.post("/products/{product_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(product_id: int, data: ReviewCreate, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(require_role(UserRole.CLIENT))):
    service = ReviewService(db)
    return await service.create_review(
        product_id=product_id,
        data=data,
        current_user=current_user,
    )


@router.patch("/reviews/{review_id}", response_model=ReviewResponse)
async def update_own_review(review_id: int, data: ReviewUpdate, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(require_role(UserRole.CLIENT))):
    service = ReviewService(db)
    return await service.update_own_review(
        review_id=review_id,
        data=data,
        current_user=current_user,
    )


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_own_review(review_id: int, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(require_role(UserRole.CLIENT))):
    service = ReviewService(db)
    await service.delete_own_review(
        review_id=review_id,
        current_user=current_user,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/catalog-banner", response_model=CatalogBannerResponse)
async def get_catalog_banner(db: AsyncSession = Depends(get_db)):
    service = CatalogBannerService(db)
    return await service.get_active_catalog_banner()


@router.post("/favorites/{product_id}", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite_product(product_id: int, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(require_role(UserRole.CLIENT))):
    service = FavoriteProductService(db)
    return await service.add_favorite_product(
        product_id=product_id,
        current_user=current_user,
    )


@router.delete("/favorites/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite_product(product_id: int, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(require_role(UserRole.CLIENT))):
    service = FavoriteProductService(db)
    await service.remove_favorite_product(
        product_id=product_id,
        current_user=current_user,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/favorites", response_model=list[ProductResponse])
async def get_my_favorite_products(db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(require_role(UserRole.CLIENT))):
    service = FavoriteProductService(db)
    return await service.get_my_favorite_products(current_user=current_user)