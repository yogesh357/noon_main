"""Celery task to poll courier APIs for tracking updates."""

import asyncio

from app.celery_app import celery


@celery.task(name="app.tasks.tracking.update_all_tracking")
def update_all_tracking():
    """Poll courier APIs for tracking updates on all active shipments."""
    asyncio.run(_poll_all())


async def _poll_all():
    from app.database import async_session_factory
    from app.services.logistics.shipment import get_active_shipments, poll_tracking_updates

    async with async_session_factory() as db:
        try:
            shipments = await get_active_shipments(db)
            total_new = 0
            for shipment in shipments:
                new_events = await poll_tracking_updates(db, shipment.id)
                total_new += new_events
            await db.commit()
            return f"Polled {len(shipments)} shipments, {total_new} new events"
        except Exception:
            await db.rollback()
            raise
