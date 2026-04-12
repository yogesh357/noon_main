"""Dispute management — raise, review, resolve with SLA enforcement."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.dispute import (
    Dispute,
    DisputeEvidence,
    DisputeReason,
    DisputeStatus,
    DisputeType,
    ResolutionType,
)
from app.models.order import Order, OrderStatus

# SLA: 48-72hr dispute window, 24hr admin response
DISPUTE_WINDOW_HOURS = 72
ADMIN_RESPONSE_HOURS = 24


async def can_raise_dispute(db: AsyncSession, order_id: int, user_id: str) -> dict:
    """Check if a dispute can be raised for this order.

    Returns: {"allowed": bool, "reason": str}
    """
    order = await db.get(Order, order_id)
    if not order:
        return {"allowed": False, "reason": "Order not found"}

    if str(order.user_id) != user_id:
        return {"allowed": False, "reason": "Not your order"}

    if order.status != OrderStatus.DELIVERED:
        return {"allowed": False, "reason": "Order must be delivered before disputing"}

    # Check dispute window (72 hours after delivery)
    delivery_time = order.delivered_at or order.updated_at
    if delivery_time:
        deadline = delivery_time + timedelta(hours=DISPUTE_WINDOW_HOURS)
        if datetime.now(UTC) > deadline:
            return {"allowed": False, "reason": "Dispute window has expired (72 hours)"}

    # Check no existing open dispute
    existing = await db.execute(
        select(Dispute).where(
            Dispute.order_id == order_id,
            Dispute.status.in_([
                DisputeStatus.OPEN, DisputeStatus.UNDER_REVIEW,
            ]),
        )
    )
    if existing.scalar_one_or_none():
        return {"allowed": False, "reason": "An active dispute already exists for this order"}

    return {"allowed": True, "reason": ""}


async def create_dispute(
    db: AsyncSession,
    order_id: int,
    user_id: str,
    dispute_type: str,
    reason: str,
    description: str,
) -> Dispute | None:
    """Create a new dispute."""
    check = await can_raise_dispute(db, order_id, user_id)
    if not check["allowed"]:
        return None

    try:
        dtype = DisputeType(dispute_type)
        dreason = DisputeReason(reason)
    except ValueError:
        return None

    sla_deadline = datetime.now(UTC) + timedelta(hours=ADMIN_RESPONSE_HOURS)

    dispute = Dispute(
        order_id=order_id,
        user_id=user_id,
        type=dtype.value,
        reason=dreason.value,
        description=description,
        status=DisputeStatus.OPEN,
        sla_deadline=sla_deadline,
    )
    db.add(dispute)
    await db.flush()
    return dispute


async def add_evidence(
    db: AsyncSession,
    dispute_id: int,
    user_id: str,
    file_url: str,
    description: str | None = None,
) -> DisputeEvidence:
    evidence = DisputeEvidence(
        dispute_id=dispute_id,
        file_url=file_url,
        description=description,
        uploaded_by=user_id,
    )
    db.add(evidence)
    await db.flush()
    return evidence


async def get_dispute(db: AsyncSession, dispute_id: int) -> Dispute | None:
    stmt = (
        select(Dispute)
        .where(Dispute.id == dispute_id)
        .options(selectinload(Dispute.evidence), selectinload(Dispute.order))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_disputes(db: AsyncSession, user_id: str) -> list[Dispute]:
    stmt = (
        select(Dispute)
        .where(Dispute.user_id == user_id)
        .options(selectinload(Dispute.order))
        .order_by(Dispute.opened_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_admin_dispute_queue(
    db: AsyncSession,
    status: str | None = None,
) -> list[Dispute]:
    """Get disputes for admin review, sorted by SLA urgency."""
    stmt = (
        select(Dispute)
        .options(selectinload(Dispute.evidence), selectinload(Dispute.order))
        .order_by(Dispute.sla_deadline.asc())
    )
    if status:
        try:
            s = DisputeStatus(status)
            stmt = stmt.where(Dispute.status == s.value)
        except ValueError:
            pass
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def resolve_dispute(
    db: AsyncSession,
    dispute_id: int,
    resolution_type: str,
    resolution_notes: str,
    admin_notes: str | None = None,
) -> bool:
    """Admin resolves a dispute."""
    dispute = await db.get(Dispute, dispute_id)
    if not dispute:
        return False

    try:
        rtype = ResolutionType(resolution_type)
    except ValueError:
        return False

    now = datetime.now(UTC)

    if rtype == ResolutionType.REJECTED:
        dispute.status = DisputeStatus.REJECTED
    else:
        dispute.status = DisputeStatus.RESOLVED

    dispute.resolution_type = rtype.value
    dispute.resolution_notes = resolution_notes
    dispute.admin_notes = admin_notes
    dispute.resolved_at = now

    if not dispute.responded_at:
        dispute.responded_at = now

    await db.flush()
    return True


async def get_dispute_stats(db: AsyncSession) -> dict:
    """Get dispute statistics for admin dashboard."""
    now = datetime.now(UTC)

    total_open = (await db.execute(
        select(func.count()).select_from(Dispute).where(
            Dispute.status.in_([DisputeStatus.OPEN, DisputeStatus.UNDER_REVIEW])
        )
    )).scalar_one()

    approaching_sla = (await db.execute(
        select(func.count()).select_from(Dispute).where(
            Dispute.status.in_([DisputeStatus.OPEN, DisputeStatus.UNDER_REVIEW]),
            Dispute.sla_deadline < now + timedelta(hours=4),
            Dispute.sla_deadline > now,
        )
    )).scalar_one()

    breached_sla = (await db.execute(
        select(func.count()).select_from(Dispute).where(
            Dispute.status.in_([DisputeStatus.OPEN, DisputeStatus.UNDER_REVIEW]),
            Dispute.sla_deadline < now,
        )
    )).scalar_one()

    return {
        "total_open": total_open,
        "approaching_sla": approaching_sla,
        "breached_sla": breached_sla,
    }
