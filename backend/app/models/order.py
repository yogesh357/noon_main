from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, CompatUUID, CompatJSON


class OrderStatus(StrEnum):
    PENDING_PAYMENT = "pending_payment"
    ACCEPTED = "accepted"
    PROCESSING = "processing"
    PICKING = "picking"
    PACKING = "packing"
    READY_TO_SHIP = "ready_to_ship"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderSource(StrEnum):
    WEBSITE = "website"
    SHOPEE = "shopee"
    TOKOPEDIA = "tokopedia"
    TIKTOK = "tiktok"
    LAZADA = "lazada"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        CompatUUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    order_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.PENDING_PAYMENT, nullable=False
    )
    source: Mapped[OrderSource] = mapped_column(
        Enum(OrderSource), default=OrderSource.WEBSITE, nullable=False
    )

    # Shipping address snapshot (JSONB so it's preserved even if user changes address)
    shipping_address: Mapped[dict | None] = mapped_column(CompatJSON(), nullable=True)
    courier: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Pricing
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    shipping_cost: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=Decimal("0"), server_default="0"
    )
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Stock reservation expiry (release stock if not paid within 30 min)
    reserved_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    payment: Mapped["Payment | None"] = relationship(
        back_populates="order", uselist=False, cascade="all, delete-orphan"
    )
    shipment: Mapped["Shipment | None"] = relationship(  # noqa: F821
        "Shipment", back_populates="order", uselist=False
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Snapshots (preserved even if product is deleted/changed)
    product_name_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    sku_snapshot: Mapped[str] = mapped_column(String(50), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    variant: Mapped[Any] = relationship(
        "ProductVariant", foreign_keys=[variant_id], lazy="noload"
    )


class PaymentStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    EXPIRED = "expired"
    REFUNDED = "refunded"


class PaymentMethod(StrEnum):
    VIRTUAL_ACCOUNT = "virtual_account"
    EWALLET = "ewallet"
    QRIS = "qris"
    CREDIT_CARD = "credit_card"
    RETAIL_OUTLET = "retail_outlet"
    OTHER = "other"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    # Xendit fields
    xendit_invoice_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    xendit_payment_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    xendit_invoice_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    method: Mapped[PaymentMethod | None] = mapped_column(Enum(PaymentMethod), nullable=True)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    callback_data: Mapped[dict | None] = mapped_column(CompatJSON(), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    order: Mapped["Order"] = relationship(back_populates="payment")
