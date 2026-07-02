from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.security import UserRole, require_role
from app.schemas.order import OrderResponse, OrderStatusUpdate
from app.services.order_service import OrderService
from app.schemas.contact import ContactMessageResponse, PhoneRequestResponse
from app.services.contact_service import ContactService


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[
        Depends(require_role(UserRole.ADMIN)),
    ],
)


@router.get("/orders", response_model=list[OrderResponse])
async def get_all_orders(db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    return await service.get_all_orders_admin()


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order_by_id(order_id: int, db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    return await service.get_order_by_id_admin(order_id)


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
async def change_order_status(order_id: int, data: OrderStatusUpdate, db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    return await service.change_order_status_admin(
        order_id=order_id,
        new_status=data.status,
    )


@router.get("/contact-messages", response_model=list[ContactMessageResponse])
async def get_all_contact_messages(db: AsyncSession = Depends(get_db)):
    service = ContactService(db)
    return await service.get_all_contact_messages_admin()


@router.get("/phone-requests", response_model=list[PhoneRequestResponse])
async def get_all_phone_requests(db: AsyncSession = Depends(get_db)):
    service = ContactService(db)
    return await service.get_all_phone_requests_admin()