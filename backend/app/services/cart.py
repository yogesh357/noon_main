from decimal import Decimal

from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart import Cart, CartItem
from app.models.catalog import Product, ProductVariant


async def _ensure_items_loaded(db: AsyncSession, cart: Cart) -> None:
    """Ensure cart items are loaded into the object to prevent lazy-load errors."""
    if "items" in inspect(cart).unloaded:
        await db.refresh(cart, ["items"])


async def get_or_create_cart(
    db: AsyncSession,
    user_id: str | None = None,
    session_key: str | None = None,
) -> Cart:
    """Get existing cart or create a new one."""
    if user_id:
        stmt = (
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(selectinload(Cart.items))
        )
        result = await db.execute(stmt)
        cart = result.scalar_one_or_none()
        if cart:
            return cart

    if session_key:
        stmt = (
            select(Cart)
            .where(Cart.session_key == session_key)
            .options(selectinload(Cart.items))
        )
        result = await db.execute(stmt)
        cart = result.scalar_one_or_none()
        if cart:
            return cart

    cart = Cart(user_id=user_id, session_key=session_key)
    db.add(cart)
    await db.flush()
    return cart


async def merge_carts(
    db: AsyncSession,
    user_id: str,
    session_key: str,
) -> Cart:
    """Merge anonymous session cart into user's cart on login."""
    # Get session cart
    session_stmt = (
        select(Cart)
        .where(Cart.session_key == session_key, Cart.user_id.is_(None))
        .options(selectinload(Cart.items))
    )
    result = await db.execute(session_stmt)
    session_cart = result.scalar_one_or_none()

    # Get or create user cart
    user_cart = await get_or_create_cart(db, user_id=user_id)

    if not session_cart or not session_cart.items:
        return user_cart

    # Merge items
    existing_variants = {item.variant_id: item for item in user_cart.items}
    for session_item in session_cart.items:
        if session_item.variant_id in existing_variants:
            existing_variants[session_item.variant_id].quantity += session_item.quantity
        else:
            new_item = CartItem(
                cart_id=user_cart.id,
                variant_id=session_item.variant_id,
                quantity=session_item.quantity,
            )
            db.add(new_item)

    # Delete session cart
    await db.delete(session_cart)
    await db.flush()

    return user_cart


async def add_to_cart(
    db: AsyncSession,
    cart: Cart,
    variant_id: int,
    quantity: int = 1,
) -> CartItem | None:
    """Add item to cart. Returns None if variant not found or insufficient stock."""
    # Validate variant exists and has stock
    variant = await db.get(ProductVariant, variant_id)
    if not variant or not variant.is_active:
        return None

    if variant.stock_quantity < quantity:
        return None

    # Check if already in cart
    await _ensure_items_loaded(db, cart)
    for item in cart.items:
        if item.variant_id == variant_id:
            new_qty = item.quantity + quantity
            if new_qty > variant.stock_quantity:
                return None
            item.quantity = new_qty
            await db.flush()
            return item

    # Add new item
    item = CartItem(cart_id=cart.id, variant_id=variant_id, quantity=quantity)
    db.add(item)
    await db.flush()
    cart.items.append(item)
    return item


async def update_cart_item(
    db: AsyncSession,
    cart: Cart,
    item_id: int,
    quantity: int,
) -> bool:
    """Update cart item quantity. Quantity 0 removes the item."""
    await _ensure_items_loaded(db, cart)
    for item in cart.items:
        if item.id == item_id:
            if quantity <= 0:
                await db.delete(item)
                cart.items.remove(item)
            else:
                variant = await db.get(ProductVariant, item.variant_id)
                if variant and quantity <= variant.stock_quantity:
                    item.quantity = quantity
                else:
                    return False
            await db.flush()
            return True
    return False


async def remove_cart_item(db: AsyncSession, cart: Cart, item_id: int) -> bool:
    """Remove an item from cart."""
    return await update_cart_item(db, cart, item_id, 0)


async def get_cart_details(db: AsyncSession, cart: Cart) -> dict:
    """Get cart with full item details (product info, images, prices)."""
    items_detail = []
    subtotal = Decimal("0")

    await _ensure_items_loaded(db, cart)
    for item in cart.items:
        variant_stmt = (
            select(ProductVariant)
            .where(ProductVariant.id == item.variant_id)
            .options(selectinload(ProductVariant.product).selectinload(Product.images))
        )
        result = await db.execute(variant_stmt)
        variant = result.scalar_one_or_none()

        if not variant:
            continue

        product = variant.product
        primary_image = next(
            (img for img in product.images if img.is_primary),
            product.images[0] if product.images else None,
        )
        unit_price = variant.price_override if variant.price_override else product.base_price
        line_total = unit_price * item.quantity
        subtotal += line_total

        items_detail.append({
            "id": item.id,
            "variant_id": variant.id,
            "sku": variant.sku,
            "product_name": product.name_en,
            "product_name_id": product.name_id,
            "product_slug": product.slug,
            "image_url": primary_image.image_url if primary_image else None,
            "size": variant.size,
            "color": variant.color,
            "variant_type": variant.variant_type,
            "unit_price": unit_price,
            "quantity": item.quantity,
            "line_total": line_total,
            "stock_available": variant.stock_quantity,
        })

    return {
        "items": items_detail,
        "item_count": sum(i["quantity"] for i in items_detail),
        "subtotal": subtotal,
    }


def get_cart_item_count(cart: Cart) -> int:
    """Quick count of items in cart. Defensive against unloaded items."""
    try:
        # Check if items attribute is initialized and not uninitialized
        if "items" in inspect(cart).unloaded:
            return 0
        return sum(item.quantity for item in cart.items)
    except Exception:
        return 0
