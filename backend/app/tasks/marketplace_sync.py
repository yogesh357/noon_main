"""Celery tasks for marketplace order polling and stock sync."""

import asyncio

from app.celery_app import celery


@celery.task(name="app.tasks.marketplace_sync.poll_all_marketplace_orders")
def poll_all_marketplace_orders():
    """Poll all connected marketplaces for new orders."""
    asyncio.run(_poll_orders())


async def _poll_orders():
    from app.database import async_session_factory
    from app.models.marketplace import MarketplaceCode
    from app.services.marketplace.sync import import_marketplace_orders

    async with async_session_factory() as db:
        try:
            total = 0
            for marketplace in MarketplaceCode:
                count = await import_marketplace_orders(db, marketplace.value)
                total += count
            await db.commit()
            return f"Imported {total} new marketplace orders"
        except Exception:
            await db.rollback()
            raise


@celery.task(name="app.tasks.marketplace_sync.sync_variant_stock")
def sync_variant_stock(variant_id: int):
    """Push stock update for a variant to all linked marketplaces."""
    asyncio.run(_sync_stock(variant_id))


async def _sync_stock(variant_id: int):
    from app.database import async_session_factory
    from app.services.marketplace.sync import sync_stock_to_all_marketplaces

    async with async_session_factory() as db:
        try:
            count = await sync_stock_to_all_marketplaces(db, variant_id)
            await db.commit()
            return f"Stock synced to {count} marketplaces"
        except Exception:
            await db.rollback()
            raise
