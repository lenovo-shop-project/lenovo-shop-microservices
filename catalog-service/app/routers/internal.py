from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.product import ProductResponse
from app.services.product_service import ProductService


router = APIRouter(
    prefix="/internal",
    tags=["Internal"],
)


class StockChangeRequest(BaseModel):
    quantity: int


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product_for_service(product_id: int, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    return await service.get_active_product_by_id(product_id)


@router.post("/products/{product_id}/reserve", response_model=ProductResponse)
async def reserve_product_stock(product_id: int, data: StockChangeRequest, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    return await service.reserve_stock(
        product_id=product_id,
        quantity=data.quantity,
    )


@router.post("/products/{product_id}/restore", response_model=ProductResponse)
async def restore_product_stock(product_id: int, data: StockChangeRequest, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    return await service.restore_stock(
        product_id=product_id,
        quantity=data.quantity,
    )