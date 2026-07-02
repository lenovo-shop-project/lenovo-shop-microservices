from __future__ import annotations
from typing import TYPE_CHECKING
import enum
from datetime import UTC, datetime
from decimal import Decimal
from sqlalchemy import DateTime, Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.order_item import OrderItem


class OrderStatus(str, enum.Enum):
    CREATED = "created"       # заказ создан
    PAID = "paid"             # оплачен
    SHIPPED = "shipped"       # отправлен
    COMPLETED = "completed"   # завершён
    CANCELLED = "cancelled"   # отменён


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        nullable=False,
        index=True,
    )

    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus),
        default=OrderStatus.CREATED,
        nullable=False,
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )


    items: Mapped[list[OrderItem]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )