from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery = Celery(
    "project_phoenix",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Jakarta",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Auto-discover tasks from all task modules
celery.autodiscover_tasks(["app.tasks"])

# Celery Beat schedule
celery.conf.beat_schedule = {
    # Stock sync — runs every 5 seconds for near real-time
    "sync-stock-levels": {
        "task": "app.tasks.stock_sync.sync_stock_levels",
        "schedule": 5.0,
    },
    # Tracking updates — poll every 15 minutes
    "update-shipment-tracking": {
        "task": "app.tasks.tracking.update_all_tracking",
        "schedule": 900.0,  # 15 minutes
    },
    # Marketplace order polling — every 60 seconds
    "poll-marketplace-orders": {
        "task": "app.tasks.marketplace_sync.poll_all_marketplace_orders",
        "schedule": 60.0,
    },
    # Cleanup expired carts/payments — every 30 minutes
    "cleanup-expired": {
        "task": "app.tasks.cleanup.cleanup_expired_reservations",
        "schedule": 1800.0,  # 30 minutes
    },
    # Daily backup reminder (placeholder)
    "daily-maintenance": {
        "task": "app.tasks.cleanup.daily_maintenance",
        "schedule": crontab(hour=2, minute=0),  # 2 AM Jakarta time
    },
}
