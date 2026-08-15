from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, CompatJSON


class MarketplaceCode(StrEnum):
    SHOPEE = "shopee"
    TOKOPEDIA = "tokopedia"
    TIKTOK = "tiktok"
    LAZADA = "lazada"


class SyncStatus(StrEnum):
    PENDING = "pending"
    SYNCED = "synced"
    FAILED = "failed"
    PARTIAL = "partial"


class MarketplaceListing(Base):
    """Links an internal product to its listing on an external marketplace."""

    __tablename__ = "marketplace_listings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    marketplace: Mapped[str] = mapped_column(String(20), nullable=False)
    external_product_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    external_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sync_status: Mapped[SyncStatus] = mapped_column(
        String(20), default=SyncStatus.PENDING
    )
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("product_id", "marketplace", name="uq_listing_product_marketplace"),
    )


class MarketplaceOrder(Base):
    """Imported order from a marketplace, linked to internal order once processed."""

    __tablename__ = "marketplace_orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    external_order_id: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    marketplace: Mapped[str] = mapped_column(String(20), nullable=False)
    raw_data: Mapped[dict | None] = mapped_column(CompatJSON(), nullable=True)
    linked_order_id: Mapped[int | None] = mapped_column(
        ForeignKey("orders.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(30), default="imported"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "external_order_id", "marketplace",
            name="uq_marketplace_order_external",
        ),
    )


class SyncLog(Base):
    """Audit trail for marketplace sync operations."""

    __tablename__ = "sync_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    marketplace: Mapped[str] = mapped_column(String(20), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    details: Mapped[dict | None] = mapped_column(CompatJSON(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
