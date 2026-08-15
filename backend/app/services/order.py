import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart import Cart
from app.models.catalog import Product, ProductImage, ProductVariant
from app.models.order import Order, OrderItem, OrderSource, OrderStatus
from app.models.user import Address


def generate_order_number() -> str:
    """Generate unique order number: PX-YYYYMMDD-XXXX."""
    now = datetime.now(UTC)
    date_part = now.strftime("%Y%m%d")
    random_part = uuid.uuid4().hex[:6].upper()
    return f"PX-{date_part}-{random_part}"


async def create_order_from_cart(
    db: AsyncSession,
    user_id: str,
    cart: Cart,
    address_id: int,
    courier: str | None = None,
    shipping_cost: Decimal = Decimal("0"),
    notes: str | None = None,
) -> Order | None:
    """Create an order from cart items. Reserves stock for 30 minutes."""
    if not cart.items:
        return None

    # Get shipping address
    address = await db.get(Address, address_id)
    if not address or str(address.user_id) != user_id:
        return None

    address_snapshot = {
        "full_name": address.full_name,
        "phone": address.phone,
        "street": address.street,
        "city": address.city,
        "province": address.province,
        "postal_code": address.postal_code,
    }

    # Build order items and calculate subtotal
    order_items = []
    subtotal = Decimal("0")

    for cart_item in cart.items:
        variant = await db.get(ProductVariant, cart_item.variant_id)
        if not variant or not variant.is_active:
            continue

        # Check stock
        if variant.stock_quantity < cart_item.quantity:
            return None  # Insufficient stock

        # Reserve stock (decrement)
        variant.stock_quantity -= cart_item.quantity

        product_stmt = select(Product).where(Product.id == variant.product_id)
        result = await db.execute(product_stmt)
        product = result.scalar_one_or_none()

        unit_price = variant.price_override if variant.price_override else product.base_price
        line_total = unit_price * cart_item.quantity
        subtotal += line_total

        order_items.append(
            OrderItem(
                variant_id=variant.id,
                quantity=cart_item.quantity,
                unit_price=unit_price,
                product_name_snapshot=product.name_en,
                sku_snapshot=variant.sku,
            )
        )

    if not order_items:
        return None

    total = subtotal + shipping_cost

    order = Order(
        user_id=user_id,
        order_number=generate_order_number(),
        status=OrderStatus.PENDING_PAYMENT,
        source=OrderSource.WEBSITE,
        shipping_address=address_snapshot,
        courier=courier,
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        total=total,
        notes=notes,
        reserved_until=datetime.now(UTC) + timedelta(minutes=30),
        items=order_items,
    )
    db.add(order)
    await db.flush()

    # Clear cart
    for item in cart.items[:]:
        await db.delete(item)
    cart.items.clear()
    await db.flush()

    return order


_ITEM_IMAGE_OPTS = (
    selectinload(Order.items)
    .selectinload(OrderItem.variant)
    .selectinload(ProductVariant.product)
    .selectinload(Product.images),
)


async def get_order_by_number(db: AsyncSession, order_number: str) -> Order | None:
    stmt = (
        select(Order)
        .where(Order.order_number == order_number)
        .options(*_ITEM_IMAGE_OPTS, selectinload(Order.payment))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_orders(
    db: AsyncSession,
    user_id: str,
    status: str | None = None,
) -> list[Order]:
    stmt = (
        select(Order)
        .where(Order.user_id == user_id)
        .options(*_ITEM_IMAGE_OPTS, selectinload(Order.payment))
        .order_by(Order.created_at.desc())
    )
    if status:
        try:
            status_enum = OrderStatus(status)
            stmt = stmt.where(Order.status == status_enum)
        except ValueError:
            pass  # Invalid status string, ignore filter
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_order_status(
    db: AsyncSession,
    order_id: int,
    new_status: OrderStatus,
) -> bool:
    stmt = update(Order).where(Order.id == order_id).values(status=new_status)
    await db.execute(stmt)
    await db.flush()
    return True


async def release_expired_reservations(db: AsyncSession) -> int:
    """Release stock for orders that were never paid within the reservation window."""
    now = datetime.now(UTC)
    expired_stmt = (
        select(Order)
        .where(
            Order.status == OrderStatus.PENDING_PAYMENT,
            Order.reserved_until < now,
        )
        .options(selectinload(Order.items))
    )
    result = await db.execute(expired_stmt)
    expired_orders = result.scalars().all()

    count = 0
    for order in expired_orders:
        # Restore stock
        for item in order.items:
            if item.variant_id:
                variant = await db.get(ProductVariant, item.variant_id)
                if variant:
                    variant.stock_quantity += item.quantity

        order.status = OrderStatus.CANCELLED
        count += 1

    await db.flush()
    return count
