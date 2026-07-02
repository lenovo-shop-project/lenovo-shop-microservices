from __future__ import annotations
from datetime import UTC, datetime
from sqlalchemy import Boolean, DateTime, String, Unicode
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class CatalogBanner(Base):
    __tablename__ = "catalog_banners"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str | None] = mapped_column(
        Unicode(255),
        nullable=True,
    )

    image_url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )