import asyncio

from app.celery_app import celery


@celery.task(name="app.tasks.cleanup.cleanup_expired_reservations")
def cleanup_expired_reservations():
    """Release stock reservations for unpaid orders older than 30 minutes."""
    asyncio.run(_cleanup_expired())


async def _cleanup_expired():
    from app.database import async_session_factory
    from app.services.order import release_expired_reservations

    async with async_session_factory() as db:
        try:
            count = await release_expired_reservations(db)
            await db.commit()
            return f"Released {count} expired reservations"
        except Exception:
            await db.rollback()
            raise


@celery.task(name="app.tasks.cleanup.daily_maintenance")
def daily_maintenance():
    """Daily maintenance: cleanup old sessions, expired carts, etc."""
    # TODO: Phase 10 - Polish
    pass
