from decimal import Decimal

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import optional_current_user
from app.dependencies import get_db
from app.models.user import User
from app.schemas.catalog import ProductFilter
from app.services.catalog import (
    get_available_filters,
    get_categories,
    get_product_by_slug,
    get_products,
    get_related_products,
    get_user_wishlist_product_ids,
)
from app.templating import templates

router = APIRouter(tags=["catalog-pages"])


@router.get("/products")
async def product_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_current_user),
    category: str | None = Query(None),
    brand: str | None = Query(None),
    color: str | None = Query(None),
    size: str | None = Query(None),
    price_min: Decimal | None = Query(None),
    price_max: Decimal | None = Query(None),
    in_stock: bool | None = Query(None),
    search: str | None = Query(None, alias="q"),
    sort: str = Query("newest"),
    page: int = Query(1, ge=1),
):
    filters = ProductFilter(
        category_slug=category,
        brand=brand,
        color=color,
        size=size,
        price_min=price_min,
        price_max=price_max,
        in_stock=in_stock,
        search=search,
        sort=sort,
        page=page,
    )

    products, total_count = await get_products(db, filters)
    categories = await get_categories(db, parent_id=None)
    available_filters = await get_available_filters(db, category_slug=category)
    wishlist_ids = set()
    if user:
        wishlist_ids = await get_user_wishlist_product_ids(db, str(user.id))

    total_pages = (total_count + filters.per_page - 1) // filters.per_page
    language = getattr(request.state, "language", "id")

    context = {
        "request": request,
        "page_title": "Products",
        "products": products,
        "categories": categories,
        "filters": filters,
        "available_filters": available_filters,
        "wishlist_ids": wishlist_ids,
        "total_count": total_count,
        "total_pages": total_pages,
        "language": language,
    }

    # If HTMX request, return only the product grid partial
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse("partials/_product_grid.html", context)

    return templates.TemplateResponse("pages/product_list.html", context)


@router.get("/products/{slug}")
async def product_detail(
    slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_current_user),
):
    product = await get_product_by_slug(db, slug)
    if not product:
        return templates.TemplateResponse(
            "pages/404.html",
            {"request": request, "page_title": "Not Found"},
            status_code=404,
        )

    related = await get_related_products(db, product)
    is_wishlisted = False
    if user:
        wishlist_ids = await get_user_wishlist_product_ids(db, str(user.id))
        is_wishlisted = product.id in wishlist_ids

    language = getattr(request.state, "language", "id")

    # Calculate avg rating
    avg_rating = None
    review_count = len(product.reviews)
    if review_count > 0:
        avg_rating = sum(r.rating for r in product.reviews) / review_count

    return templates.TemplateResponse(
        "pages/product_detail.html",
        {
            "request": request,
            "page_title": product.name_en if language == "en" else product.name_id,
            "product": product,
            "related_products": related,
            "is_wishlisted": is_wishlisted,
            "avg_rating": avg_rating,
            "review_count": review_count,
            "language": language,
        },
    )


@router.get("/search")
async def search_results(
    request: Request,
    q: str = Query(""),
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_current_user),
    sort: str = Query("newest"),
    page: int = Query(1, ge=1),
):
    filters = ProductFilter(search=q, sort=sort, page=page)
    products, total_count = await get_products(db, filters)
    wishlist_ids = set()
    if user:
        wishlist_ids = await get_user_wishlist_product_ids(db, str(user.id))

    total_pages = (total_count + filters.per_page - 1) // filters.per_page
    language = getattr(request.state, "language", "id")

    return templates.TemplateResponse(
        "pages/search_results.html",
        {
            "request": request,
            "page_title": f"Search: {q}",
            "query": q,
            "products": products,
            "wishlist_ids": wishlist_ids,
            "total_count": total_count,
            "total_pages": total_pages,
            "filters": filters,
            "language": language,
        },
    )
