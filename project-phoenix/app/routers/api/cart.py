from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import optional_current_user
from app.dependencies import get_db
from app.models.user import User
from app.schemas.cart import CartAddItem, CartUpdateItem
from app.services.cart import (
    add_to_cart,
    get_cart_details,
    get_cart_item_count,
    get_or_create_cart,
    remove_cart_item,
    update_cart_item,
)
from app.templating import templates

router = APIRouter(prefix="/api/cart", tags=["cart"])


def _get_session_key(request: Request) -> str:
    """Get or create a session key for anonymous cart."""
    session = request.session
    if "cart_session" not in session:
        import uuid

        session["cart_session"] = str(uuid.uuid4())
    return session["cart_session"]


@router.post("/add")
async def cart_add(
    request: Request,
    body: CartAddItem,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_current_user),
):
    """Add item to cart. Returns updated cart badge."""
    user_id = str(user.id) if user else None
    session_key = _get_session_key(request) if not user else None

    cart = await get_or_create_cart(db, user_id=user_id, session_key=session_key)
    item = await add_to_cart(db, cart, body.variant_id, body.quantity)

    count = get_cart_item_count(cart)
    return templates.TemplateResponse(
        "partials/_cart_badge.html",
        {"request": request, "cart_count": count, "success": item is not None},
    )


@router.patch("/item/{item_id}")
async def cart_update(
    item_id: int,
    body: CartUpdateItem,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_current_user),
):
    """Update cart item quantity. Returns updated cart summary."""
    user_id = str(user.id) if user else None
    session_key = _get_session_key(request) if not user else None

    cart = await get_or_create_cart(db, user_id=user_id, session_key=session_key)
    await update_cart_item(db, cart, item_id, body.quantity)

    cart_data = await get_cart_details(db, cart)
    language = getattr(request.state, "language", "id")

    return templates.TemplateResponse(
        "partials/_cart_summary.html",
        {"request": request, "cart": cart_data, "language": language},
    )


@router.delete("/item/{item_id}")
async def cart_remove(
    item_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_current_user),
):
    """Remove item from cart. Returns updated cart summary."""
    user_id = str(user.id) if user else None
    session_key = _get_session_key(request) if not user else None

    cart = await get_or_create_cart(db, user_id=user_id, session_key=session_key)
    await remove_cart_item(db, cart, item_id)

    cart_data = await get_cart_details(db, cart)
    language = getattr(request.state, "language", "id")

    return templates.TemplateResponse(
        "partials/_cart_summary.html",
        {"request": request, "cart": cart_data, "language": language},
    )


@router.get("/count")
async def cart_count(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_current_user),
):
    """Get cart item count for badge."""
    user_id = str(user.id) if user else None
    session_key = request.session.get("cart_session") if not user else None

    if not user_id and not session_key:
        return templates.TemplateResponse(
            "partials/_cart_badge.html",
            {"request": request, "cart_count": 0},
        )

    cart = await get_or_create_cart(db, user_id=user_id, session_key=session_key)
    count = get_cart_item_count(cart)

    return templates.TemplateResponse(
        "partials/_cart_badge.html",
        {"request": request, "cart_count": count},
    )
