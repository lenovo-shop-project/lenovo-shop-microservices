from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.security import CurrentUser, UserRole, require_role
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import OrderService
from app.schemas.contact import (
    ContactMessageCreate,
    ContactMessageResponse,
    PhoneRequestCreate,
    PhoneRequestResponse,
)
from app.services.contact_service import ContactService
from typing import Optional
import logging

logger = logging.getLogger("uvicorn.error")

router = APIRouter(
    prefix="/client",
    tags=["Client"],
)


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(data: OrderCreate, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(require_role(UserRole.CLIENT))):
    service = OrderService(db)
    return await service.create_order(
        data=data,
        current_user=current_user,
    )


@router.get("/orders", response_model=list[OrderResponse])
async def get_my_orders(db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(require_role(UserRole.CLIENT))):
    service = OrderService(db)
    return await service.get_my_orders(current_user)


@router.patch("/orders/{order_id}/cancel", response_model=OrderResponse)
async def cancel_my_order(order_id: int, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(require_role(UserRole.CLIENT))):
    service = OrderService(db)
    return await service.cancel_my_order(
        order_id=order_id,
        current_user=current_user,
    )


@router.post("/contact-messages", response_model=ContactMessageResponse, status_code=status.HTTP_201_CREATED)
async def create_contact_message(data: ContactMessageCreate, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(require_role(UserRole.CLIENT))):
    service = ContactService(db)
    return await service.create_contact_message(
        data=data,
        current_user=current_user,
    )


@router.post("/phone-requests", response_model=PhoneRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_phone_request(data: PhoneRequestCreate, source: Optional[str] = "unknown", db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(require_role(UserRole.CLIENT))):
    service = ContactService(db)
    logger.info(f"!!! [LOG] Новая заявка на звонок. Источник: {source}. Номер: {data.phone_number}")
    return await service.create_phone_request(
        data=data,
        current_user=current_user,
    )
