from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class CheckoutAddress(BaseModel):
    address_id: int | None = None
    # Or inline new address
    full_name: str | None = None
    phone: str | None = None
    street: str | None = None
    city: str | None = None
    province: str | None = None
    postal_code: str | None = None


class CheckoutCourier(BaseModel):
    courier: str
    service: str
    cost: Decimal
    estimated_days: str | None = None


class CheckoutCreate(BaseModel):
    address_id: int | None = None
    courier: str | None = None
    shipping_cost: Decimal = Decimal("0")
    notes: str | None = None


class OrderItemRead(BaseModel):
    id: int
    product_name_snapshot: str
    sku_snapshot: str
    quantity: int
    unit_price: Decimal

    model_config = {"from_attributes": True}


class OrderRead(BaseModel):
    id: int
    order_number: str
    status: str
    source: str
    subtotal: Decimal
    shipping_cost: Decimal
    total: Decimal
    courier: str | None = None
    notes: str | None = None
    created_at: datetime | None = None
    items: list[OrderItemRead] = []

    model_config = {"from_attributes": True}
