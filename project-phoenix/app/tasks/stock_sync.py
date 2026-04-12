from app.celery_app import celery


@celery.task(name="app.tasks.stock_sync.sync_stock_levels")
def sync_stock_levels():
    """Sync stock levels to Redis cache for near real-time display."""
    # TODO: Phase 2 - Query product variants, update Redis cache
    pass
