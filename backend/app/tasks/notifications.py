from app.celery_app import celery


@celery.task(name="app.tasks.notifications.send_email")
def send_email(to: str, subject: str, body: str):
    """Send email notification."""
    # TODO: Phase 4 - Customer Dashboard notifications
    pass
