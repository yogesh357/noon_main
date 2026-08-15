"""Shipment management — create, track, update shipments."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.logistics import CourierCode, Shipment, ShipmentStatus, TrackingEvent
from app.models.order import Order, OrderStatus
from app.services.logistics.rajaongkir import get_waybill_tracking


async def create_shipment(
    db: AsyncSession,
    order_id: int,
    courier: str,
    tracking_number: str | None = None,
) -> Shipment:
    """Create a shipment record for an order."""
    try:
        courier_enum = CourierCode(courier.lower())
    except ValueError:
        courier_enum = CourierCode.JNE  # fallback

    shipment = Shipment(
        order_id=order_id,
        courier=courier_enum,
        tracking_number=tracking_number,
        status=ShipmentStatus.LABEL_CREATED,
    )
    db.add(shipment)
    await db.flush()
    return shipment


async def get_shipment_by_order(db: AsyncSession, order_id: int) -> Shipment | None:
    stmt = (
        select(Shipment)
        .where(Shipment.order_id == order_id)
        .options(selectinload(Shipment.tracking_events))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_shipment_by_tracking(
    db: AsyncSession, tracking_number: str
) -> Shipment | None:
    stmt = (
        select(Shipment)
        .where(Shipment.tracking_number == tracking_number)
        .options(selectinload(Shipment.tracking_events))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_tracking_number(
    db: AsyncSession,
    shipment_id: int,
    tracking_number: str,
) -> bool:
    shipment = await db.get(Shipment, shipment_id)
    if not shipment:
        return False
    shipment.tracking_number = tracking_number
    await db.flush()
    return True


async def poll_tracking_updates(db: AsyncSession, shipment_id: int) -> int:
    """Poll courier API for tracking updates. Returns number of new events added."""
    shipment = await db.get(
        Shipment, shipment_id,
        options=[selectinload(Shipment.tracking_events)],
    )
    if not shipment or not shipment.tracking_number:
        return 0

    # Skip if already delivered
    if shipment.status == ShipmentStatus.DELIVERED:
        return 0

    # Fetch from RajaOngkir
    events = await get_waybill_tracking(
        shipment.tracking_number,
        shipment.courier.value,
    )

    if not events:
        return 0

    # Get existing event descriptions to avoid duplicates (normalize to raw string)
    existing_descs = {
        (e.description, e.timestamp.strftime("%Y-%m-%d %H:%M:%S") if e.timestamp else "")
        for e in shipment.tracking_events
    }

    new_count = 0
    latest_status = shipment.status

    for event_data in events:
        # Parse timestamp first so we can use consistent format for dedup
        try:
            ts = datetime.fromisoformat(event_data.timestamp.strip())
        except (ValueError, AttributeError):
            ts = datetime.now(UTC)

        event_key = (event_data.description, ts.strftime("%Y-%m-%d %H:%M:%S"))
        if event_key in existing_descs:
            continue

        tracking_event = TrackingEvent(
            shipment_id=shipment.id,
            status=event_data.status,
            description=event_data.description,
            location=event_data.location,
            timestamp=ts,
            raw_data=event_data.raw_data,
        )
        db.add(tracking_event)
        new_count += 1

        # Update shipment status to latest
        try:
            latest_status = ShipmentStatus(event_data.status)
        except ValueError:
            pass

    if new_count > 0:
        shipment.status = latest_status

        # If delivered, update order and set actual delivery time
        if latest_status == ShipmentStatus.DELIVERED:
            now = datetime.now(UTC)
            shipment.actual_delivery = now
            order = await db.get(Order, shipment.order_id)
            if order:
                order.status = OrderStatus.DELIVERED
                order.delivered_at = now

        await db.flush()

    return new_count


async def get_active_shipments(db: AsyncSession) -> list[Shipment]:
    """Get all shipments that need tracking updates (not delivered/returned)."""
    terminal_statuses = [ShipmentStatus.DELIVERED, ShipmentStatus.RETURNED]
    stmt = (
        select(Shipment)
        .where(
            Shipment.tracking_number.isnot(None),
            Shipment.status.notin_(terminal_statuses),
        )
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
