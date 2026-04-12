"""Real-time stock check API — used by product detail page HTMX polling."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.catalog import ProductVariant
from app.templating import templates

router = APIRouter(prefix="/api/stock", tags=["stock"])


@router.get("/{product_id}")
async def get_stock_status(
    product_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Get stock status for a product (all variants). Returns HTML partial."""
    stmt = select(ProductVariant).where(
        ProductVariant.product_id == product_id,
        ProductVariant.is_active.is_(True),
    )
    result = await db.execute(stmt)
    variants = list(result.scalars().all())

    total_stock = sum(v.stock_quantity for v in variants)
    in_stock = total_stock > 0

    return templates.TemplateResponse(
        "partials/_stock_badge.html",
        {
            "request": request,
            "in_stock": in_stock,
            "total_stock": total_stock,
        },
    )
