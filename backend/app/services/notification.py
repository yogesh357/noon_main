from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationType


async def get_user_notifications(
    db: AsyncSession,
    user_id: str,
    unread_only: bool = False,
    limit: int = 20,
) -> list[Notification]:
    stmt = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
    )
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_unread_count(db: AsyncSession, user_id: str) -> int:
    stmt = (
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == user_id, Notification.is_read.is_(False))
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def mark_all_read(db: AsyncSession, user_id: str) -> int:
    stmt = (
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        .values(is_read=True)
    )
    result = await db.execute(stmt)
    await db.flush()
    return result.rowcount


async def mark_read(db: AsyncSession, notification_id: int, user_id: str) -> bool:
    stmt = (
        update(Notification)
        .where(Notification.id == notification_id, Notification.user_id == user_id)
        .values(is_read=True)
    )
    result = await db.execute(stmt)
    await db.flush()
    return result.rowcount > 0


async def create_notification(
    db: AsyncSession,
    user_id: str,
    type: NotificationType,
    title_id: str,
    title_en: str,
    message_id: str,
    message_en: str,
    related_object_type: str | None = None,
    related_object_id: int | None = None,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        type=type,
        title_id=title_id,
        title_en=title_en,
        message_id=message_id,
        message_en=message_en,
        related_object_type=related_object_type,
        related_object_id=related_object_id,
    )
    db.add(notification)
    await db.flush()
    return notification
