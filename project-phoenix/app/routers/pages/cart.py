from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import optional_current_user
from app.dependencies import get_db
from app.models.user import User
from app.services.cart import get_cart_details, get_or_create_cart
from app.templating import templates

router = APIRouter(tags=["cart-pages"])


@router.get("/cart")
async def cart_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_current_user),
):
    user_id = str(user.id) if user else None
    session_key = request.session.get("cart_session") if not user else None

    cart_data = {"items": [], "item_count": 0, "subtotal": 0}

    if user_id or session_key:
        cart = await get_or_create_cart(db, user_id=user_id, session_key=session_key)
        cart_data = await get_cart_details(db, cart)

    language = getattr(request.state, "language", "id")

    return templates.TemplateResponse(
        "pages/cart.html",
        {
            "request": request,
            "page_title": "Cart",
            "cart": cart_data,
            "language": language,
        },
    )
