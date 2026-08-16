from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import current_active_user, optional_current_user
from app.dependencies import get_db
from app.models.user import Address, User
from app.services.cart import (
    add_to_cart,
    get_cart_details,
    get_cart_item_count,
    get_or_create_cart,
    remove_cart_item,
    update_cart_item,
)
from app.services.catalog import get_user_wishlist_products, toggle_wishlist
from app.routers.api.helpers import (
    _get_session_key,
    _serialize_cart,
    _serialize_product,
)

router = APIRouter(tags=["cart"])


@router.get("/api/cart")
async def api_get_cart(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_current_user),
):
    user_id = str(user.id) if user else None
    session_key = _get_session_key(request) if not user else None
    cart = await get_or_create_cart(db, user_id=user_id, session_key=session_key)
    return _serialize_cart(await get_cart_details(db, cart))


@router.post("/api/cart/add")
async def api_cart_add(
    request: Request,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_current_user),
):
    user_id = str(user.id) if user else None
    session_key = _get_session_key(request) if not user else None
    cart = await get_or_create_cart(db, user_id=user_id, session_key=session_key)
    item = await add_to_cart(db, cart, int(body["variant_id"]), int(body.get("quantity", 1)))
    if not item:
        raise HTTPException(status_code=400, detail="Unable to add item to cart")
    cart_data = await get_cart_details(db, cart)
    matching = next((entry for entry in _serialize_cart(cart_data)["items"] if entry["id"] == item.id), None)
    return matching or {"id": item.id}


@router.patch("/api/cart/item/{item_id}")
async def api_cart_update(
    item_id: int,
    request: Request,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_current_user),
):
    user_id = str(user.id) if user else None
    session_key = _get_session_key(request) if not user else None
    cart = await get_or_create_cart(db, user_id=user_id, session_key=session_key)
    success = await update_cart_item(db, cart, item_id, int(body.get("quantity", 1)))
    if not success:
        raise HTTPException(status_code=400, detail="Unable to update cart item")
    cart_data = await get_cart_details(db, cart)
    matching = next((entry for entry in _serialize_cart(cart_data)["items"] if entry["id"] == item_id), None)
    return matching or {"id": item_id}


@router.delete("/api/cart/item/{item_id}")
async def api_cart_remove(
    item_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_current_user),
):
    user_id = str(user.id) if user else None
    session_key = _get_session_key(request) if not user else None
    cart = await get_or_create_cart(db, user_id=user_id, session_key=session_key)
    await remove_cart_item(db, cart, item_id)
    return {"success": True}


@router.get("/api/cart/count")
async def api_cart_count(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_current_user),
):
    user_id = str(user.id) if user else None
    session_key = _get_session_key(request) if not user else None
    cart = await get_or_create_cart(db, user_id=user_id, session_key=session_key)
    return {"count": get_cart_item_count(cart)}


@router.get("/api/cart/shipping-rates")
async def api_cart_shipping_rates(address_id: int, db: AsyncSession = Depends(get_db)):
    address = await db.get(Address, address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return [
        {"courier": "JNE", "service": "REG", "cost": 18000, "estimated_days": "2-3 days"},
        {"courier": "J&T", "service": "EZ", "cost": 15000, "estimated_days": "2-4 days"},
        {"courier": "SiCepat", "service": "BEST", "cost": 22000, "estimated_days": "1-2 days"},
    ]


@router.get("/api/wishlist")
async def api_get_wishlist(db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    products = await get_user_wishlist_products(db, str(user.id))
    return {
        "product_ids": [product.id for product in products],
        "products": [_serialize_product(product) for product in products],
    }


@router.post("/api/wishlist/toggle/{product_id}")
async def api_toggle_wishlist(product_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    return {"is_wishlisted": await toggle_wishlist(db, str(user.id), product_id)}
