from fastapi import APIRouter, Depends, status, Response, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.security import UserRole, require_role
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.services.product_service import ProductService
from app.schemas.category import CategoryCreate, CategoryResponse
from app.services.category_service import CategoryService
from app.schemas.review import ReviewAdminResponseUpdate, ReviewResponse
from app.services.review_service import ReviewService
from app.schemas.upload import UploadImageResponse
from app.services.cloudinary_service import upload_image_to_cloudinary
from app.schemas.catalog_banner import CatalogBannerCreate, CatalogBannerResponse
from app.services.catalog_banner_service import CatalogBannerService



router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[
        Depends(require_role(UserRole.ADMIN)),
    ],
)


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    return await service.create_product(data)


@router.patch("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, data: ProductUpdate, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    return await service.update_product(
        product_id=product_id,
        data=data,
    )


@router.patch("/products/{product_id}/deactivate", response_model=ProductResponse)
async def deactivate_product(product_id: int, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    return await service.deactivate_product(product_id)


@router.patch("/products/{product_id}/activate", response_model=ProductResponse)
async def activate_product(product_id: int, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    return await service.activate_product(product_id)


@router.get("/products", response_model=list[ProductResponse])
async def get_all_products(db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    return await service.get_all_products_admin()


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product_by_id(product_id: int, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    return await service.get_product_by_id_admin(product_id)


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    service = CategoryService(db)
    return await service.create_category(data)


@router.get("/categories", response_model=list[CategoryResponse])
async def get_all_categories(db: AsyncSession = Depends(get_db)):
    service = CategoryService(db)
    return await service.get_all_categories()


@router.get("/reviews", response_model=list[ReviewResponse])
async def get_all_reviews(db: AsyncSession = Depends(get_db)):
    service = ReviewService(db)
    return await service.get_all_reviews_admin()


@router.get("/reviews/{review_id}", response_model=ReviewResponse)
async def get_review_by_id(review_id: int, db: AsyncSession = Depends(get_db)):
    service = ReviewService(db)
    return await service.get_review_by_id_admin(review_id)


@router.get("/products/{product_id}/reviews", response_model=list[ReviewResponse])
async def get_product_reviews_admin(product_id: int, db: AsyncSession = Depends(get_db)):
    service = ReviewService(db)
    return await service.get_product_reviews_admin(product_id)


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review_admin(review_id: int, db: AsyncSession = Depends(get_db)):
    service = ReviewService(db)
    await service.delete_review_admin(review_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/reviews/{review_id}/response", response_model=ReviewResponse)
async def add_admin_response_to_review(review_id: int, data: ReviewAdminResponseUpdate, db: AsyncSession = Depends(get_db)):
    service = ReviewService(db)
    return await service.add_admin_response(
        review_id=review_id,
        data=data,
    )


@router.post("/uploads/products", response_model=UploadImageResponse)
async def upload_product_image(file: UploadFile = File(...)):
    image_url = await upload_image_to_cloudinary(
        file=file,
        folder="products",
    )
    return {"image_url": image_url}


@router.post("/uploads/banners", response_model=UploadImageResponse)
async def upload_banner_image(file: UploadFile = File(...)):
    image_url = await upload_image_to_cloudinary(
        file=file,
        folder="banners",
    )
    return {"image_url": image_url}


@router.post("/catalog-banner", response_model=CatalogBannerResponse)
async def create_catalog_banner(data: CatalogBannerCreate, db: AsyncSession = Depends(get_db)):
    service = CatalogBannerService(db)
    return await service.create_catalog_banner(data)
