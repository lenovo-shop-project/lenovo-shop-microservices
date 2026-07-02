from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import Unicode
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.product import Product


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        Unicode(100),
        unique=True,
        nullable=False,
    )

    products: Mapped[list[Product]] = relationship(
        back_populates="category",
    )