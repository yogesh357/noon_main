from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.services.catalog import search_products
from app.templating import templates

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("/suggestions")
async def search_suggestions(
    request: Request,
    q: str = Query("", min_length=2),
    db: AsyncSession = Depends(get_db),
):
    """Live search suggestions for HTMX type-ahead."""
    if len(q) < 2:
        return templates.TemplateResponse(
            "partials/_search_suggestions.html",
            {"request": request, "products": [], "query": q},
        )

    products = await search_products(db, q, limit=6)
    language = getattr(request.state, "language", "id")

    return templates.TemplateResponse(
        "partials/_search_suggestions.html",
        {
            "request": request,
            "products": products,
            "query": q,
            "language": language,
        },
    )
