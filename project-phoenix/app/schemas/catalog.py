from decimal import Decimal

from pydantic import BaseModel, Field


# --- Category Schemas ---
class CategoryRead(BaseModel):
    id: int
    name_id: str
    name_en: str
    slug: str
    parent_id: int | None = None
    image_url: str | None = None
    sort_order: int = 0
    is_active: bool = True

    model_config = {"from_attributes": True}


class CategoryTree(CategoryRead):
    children: list["CategoryTree"] = []


# --- Product Schemas ---
class ProductImageRead(BaseModel):
    id: int
    image_url: str
    alt_text: str | None = None
    sort_order: int = 0
    is_primary: bool = False

    model_config = {"from_attributes": True}


class ProductVariantRead(BaseModel):
    id: int
    sku: str
    barcode: str | None = None
    size: str | None = None
    color: str | None = None
    variant_type: str | None = None
    price_override: Decimal | None = None
    stock_quantity: int = 0
    weight_grams: int | None = None
    is_active: bool = True

    model_config = {"from_attributes": True}


class ReviewRead(BaseModel):
    id: int
    rating: int
    comment: str | None = None
    is_verified_purchase: bool = False
    created_at: str | None = None

    model_config = {"from_attributes": True}


class ProductCard(BaseModel):
    """Lightweight product for listing pages."""

    id: int
    name_id: str
    name_en: str
    slug: str
    brand: str | None = None
    base_price: Decimal
    primary_image_url: str | None = None
    colors: list[str] = []
    in_stock: bool = True
    avg_rating: float | None = None
    review_count: int = 0

    model_config = {"from_attributes": True}


class ProductDetail(BaseModel):
    """Full product detail."""

    id: int
    name_id: str
    name_en: str
    slug: str
    description_id: str | None = None
    description_en: str | None = None
    brand: str | None = None
    base_price: Decimal
    is_active: bool = True
    categories: list[CategoryRead] = []
    variants: list[ProductVariantRead] = []
    images: list[ProductImageRead] = []
    reviews: list[ReviewRead] = []
    avg_rating: float | None = None
    review_count: int = 0

    model_config = {"from_attributes": True}


# --- Filter/Sort Schemas ---
class ProductFilter(BaseModel):
    category_id: int | None = None
    category_slug: str | None = None
    brand: str | None = None
    color: str | None = None
    size: str | None = None
    price_min: Decimal | None = None
    price_max: Decimal | None = None
    in_stock: bool | None = None
    search: str | None = None
    sort: str = Field(default="newest", pattern="^(newest|price_asc|price_desc|popular|rating)$")
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=12, ge=1, le=48)
