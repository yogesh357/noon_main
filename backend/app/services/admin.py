"""Admin-specific business logic for order management."""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderSource, OrderStatus


async def get_admin_order_queue(
    db: AsyncSession,
    status: OrderStatus | None = None,
    source: OrderSource | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Order], int]:
    """Get paginated orders for admin queue."""
    count_stmt = select(func.count()).select_from(Order)
    data_stmt = (
        select(Order)
        .options(selectinload(Order.items), selectinload(Order.payment))
        .order_by(Order.created_at.desc())
    )

    if status:
        count_stmt = count_stmt.where(Order.status == status)
        data_stmt = data_stmt.where(Order.status == status)
    if source:
        count_stmt = count_stmt.where(Order.source == source)
        data_stmt = data_stmt.where(Order.source == source)

    total = (await db.execute(count_stmt)).scalar_one()

    offset = (page - 1) * per_page
    data_stmt = data_stmt.offset(offset).limit(per_page)
    result = await db.execute(data_stmt)
    orders = list(result.scalars().all())

    return orders, total


async def bulk_process_orders(
    db: AsyncSession,
    order_ids: list[int],
) -> list[Order]:
    """Move accepted orders to PROCESSING status (begin fulfillment).

    Only orders with ACCEPTED status (paid via Xendit webhook) can be processed.
    """
    stmt = (
        select(Order)
        .where(
            Order.id.in_(order_ids),
            Order.status == OrderStatus.ACCEPTED,
        )
        .options(selectinload(Order.items))
    )
    result = await db.execute(stmt)
    orders = list(result.scalars().all())

    for order in orders:
        order.status = OrderStatus.PROCESSING

    await db.flush()
    return orders


async def get_admin_dashboard_stats(db: AsyncSession) -> dict:
    """Get order statistics for admin dashboard."""
    today = datetime.now(UTC).date()

    # Total orders today
    today_count = (
        await db.execute(
            select(func.count())
            .select_from(Order)
            .where(func.date(Order.created_at) == today)
        )
    ).scalar_one()

    # Orders by status
    status_counts = {}
    for status in OrderStatus:
        count = (
            await db.execute(
                select(func.count())
                .select_from(Order)
                .where(Order.status == status)
            )
        ).scalar_one()
        if count > 0:
            status_counts[status.value] = count

    # Revenue today
    from app.models.order import Payment, PaymentStatus

    revenue_today = (
        await db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0))
            .join(Order)
            .where(
                func.date(Payment.paid_at) == today,
                Payment.status == PaymentStatus.PAID,
            )
        )
    ).scalar_one()

    # Orders by source
    source_counts = {}
    for source in OrderSource:
        count = (
            await db.execute(
                select(func.count())
                .select_from(Order)
                .where(Order.source == source)
            )
        ).scalar_one()
        if count > 0:
            source_counts[source.value] = count

    return {
        "orders_today": today_count,
        "status_counts": status_counts,
        "revenue_today": float(revenue_today),
        "source_counts": source_counts,
    }
