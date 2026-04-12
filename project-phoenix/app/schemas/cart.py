from decimal import Decimal

from pydantic import BaseModel, Field


class CartAddItem(BaseModel):
    variant_id: int
    quantity: int = Field(default=1, ge=1)


class CartUpdateItem(BaseModel):
    quantity: int = Field(ge=0)  # 0 = remove


class CartItemRead(BaseModel):
    id: int
    variant_id: int
    sku: str
    product_name: str
    product_slug: str
    image_url: str | None = None
    size: str | None = None
    color: str | None = None
    variant_type: str | None = None
    unit_price: Decimal
    quantity: int
    line_total: Decimal
    stock_available: int

    model_config = {"from_attributes": True}


class CartRead(BaseModel):
    items: list[CartItemRead] = []
    item_count: int = 0
    subtotal: Decimal = Decimal("0")
