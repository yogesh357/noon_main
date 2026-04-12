from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import current_active_user
from app.dependencies import get_db
from app.models.user import User
from app.services.catalog import toggle_wishlist
from app.templating import templates

router = APIRouter(prefix="/api/wishlist", tags=["wishlist"])


@router.post("/toggle/{product_id}")
async def toggle_wishlist_item(
    product_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Toggle product in/out of wishlist. Returns updated heart button partial."""
    is_added = await toggle_wishlist(db, str(user.id), product_id)

    return templates.TemplateResponse(
        "partials/_wishlist_button.html",
        {
            "request": request,
            "product_id": product_id,
            "is_wishlisted": is_added,
        },
    )
