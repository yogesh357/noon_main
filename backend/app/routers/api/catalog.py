from __future__ import annotations

from decimal import Decimal
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.catalog import Product, ProductVariant, Review
from app.services.catalog import (
    get_available_filters,
    get_category_tree,
    get_product_by_slug,
    get_products,
    search_products,
)
from app.routers.api.helpers import _serialize_category, _serialize_product, _iso

router = APIRouter(tags=["catalog"])


@router.get("/api/catalog/categories")
async def api_catalog_categories(db: AsyncSession = Depends(get_db)):
    categories = await get_category_tree(db)
    return [_serialize_category(category) for category in categories]


@router.get("/api/catalog/products")
async def api_catalog_products(
    db: AsyncSession = Depends(get_db),
    category: str | None = None,
    brand: str | None = None,
    color: str | None = None,
    size: str | None = None,
    price_min: Decimal | None = None,
    price_max: Decimal | None = None,
    in_stock: bool | None = None,
    sort: str = Query("newest", pattern="^(newest|price_asc|price_desc|popular|rating)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=48),
    q: str | None = None,
):
    from app.schemas.catalog import ProductFilter

    filters = ProductFilter(
        category_slug=category,
        brand=brand,
        color=color,
        size=size,
        price_min=price_min,
        price_max=price_max,
        in_stock=in_stock,
        sort=sort,
        page=page,
        per_page=per_page,
        search=q,
    )
    products, total = await get_products(db, filters)
    categories = await get_category_tree(db)
    available_filters = await get_available_filters(db, category_slug=category)

    product_payload = [_serialize_product(product) for product in products]
    price_values = [product["base_price"] for product in product_payload]

    return {
        "products": product_payload,
        "total": total,
        "page": page,
        "pages": max(1, ceil(total / per_page)) if per_page else 1,
        "per_page": per_page,
        "filters": {
            "brands": available_filters.get("brands", []),
            "colors": available_filters.get("colors", []),
            "sizes": available_filters.get("sizes", []),
            "price_min": min(price_values) if price_values else 0,
            "price_max": max(price_values) if price_values else 0,
        },
        "categories": [_serialize_category(item) for item in categories],
    }


@router.get("/api/catalog/products/{product_id}/reviews")
async def api_product_reviews(product_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Review).where(Review.product_id == product_id).order_by(Review.created_at.desc())
    result = await db.execute(stmt)
    reviews = list(result.scalars().all())
    return [
        {
            "id": review.id,
            "user_id": str(review.user_id),
            "user_name": "Verified Customer" if review.is_verified_purchase else "Customer",
            "rating": review.rating,
            "comment": review.comment,
            "is_verified": review.is_verified_purchase,
            "created_at": _iso(review.created_at),
        }
        for review in reviews
    ]


@router.get("/api/catalog/products/{slug}")
async def api_catalog_product(slug: str, db: AsyncSession = Depends(get_db)):
    product = await get_product_by_slug(db, slug)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return _serialize_product(product)


@router.get("/api/search/suggestions")
async def api_search_suggestions(q: str = Query("", min_length=0), db: AsyncSession = Depends(get_db)):
    if len(q.strip()) < 2:
        return {"suggestions": []}

    products = await search_products(db, q.strip(), limit=6)
    suggestions = [product.name_en for product in products]
    return {"suggestions": suggestions}


@router.get("/api/stock/{product_id}")
async def api_stock_status(product_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(ProductVariant).where(ProductVariant.product_id == product_id, ProductVariant.is_active.is_(True))
    result = await db.execute(stmt)
    variants = list(result.scalars().all())
    total_stock = sum(variant.stock_quantity for variant in variants)
    return {"in_stock": total_stock > 0, "total_stock": total_stock}
