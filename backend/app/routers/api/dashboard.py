from __future__ import annotations

from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import current_active_user
from app.dependencies import get_db
from app.models.logistics import Shipment
from app.models.order import Order, Payment, PaymentStatus
from app.models.user import Address, User
from app.services.catalog import get_user_wishlist_products
from app.services.dispute import add_evidence, create_dispute, get_dispute, get_user_disputes
from app.services.notification import get_unread_count, get_user_notifications, mark_all_read, mark_read
from app.services.order import get_user_orders
from app.routers.api.helpers import (
    _decimal,
    _enum_name,
    _iso,
    _snapshot_address,
    _serialize_address,
    _serialize_user,
    _serialize_product,
    _serialize_order,
    _serialize_shipment,
    _serialize_dispute,
    _serialize_payment,
    _get_order_for_user,
)

router = APIRouter(tags=["dashboard"])


@router.get("/api/dashboard/overview")
async def api_dashboard_overview(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    orders = await get_user_orders(db, str(user.id))
    open_count = sum(1 for order in orders if _enum_name(order.status) not in {"DELIVERED", "CANCELLED"})
    paid_total = sum(_decimal(order.payment.amount) for order in orders if order.payment and order.payment.status == PaymentStatus.PAID)
    return {
        "total_orders": len(orders),
        "open_orders": open_count,
        "total_spent": paid_total,
        "wishlist_count": len(await get_user_wishlist_products(db, str(user.id))),
    }


@router.get("/api/dashboard/addresses")
async def api_get_addresses(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    stmt = select(Address).where(Address.user_id == user.id).order_by(Address.is_default.desc(), Address.id.asc())
    result = await db.execute(stmt)
    return [_serialize_address(address) for address in result.scalars().all()]


@router.post("/api/dashboard/addresses")
async def api_create_address(
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    if body.get("is_default"):
        result = await db.execute(select(Address).where(Address.user_id == user.id))
        for address in result.scalars().all():
            address.is_default = False

    address = Address(
        user_id=user.id,
        label=body.get("label") or "Home",
        full_name=body.get("name") or body.get("full_name") or "",
        phone=body.get("phone") or "",
        street=body.get("street") or "",
        city=body.get("city") or "",
        province=body.get("province") or "",
        postal_code=body.get("postal_code") or "",
        is_default=bool(body.get("is_default")),
    )
    db.add(address)
    await db.flush()
    return _serialize_address(address)


@router.patch("/api/dashboard/addresses/{address_id}")
async def api_update_address(
    address_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    address = await db.get(Address, address_id)
    if not address or str(address.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Address not found")

    if body.get("is_default"):
        result = await db.execute(select(Address).where(Address.user_id == user.id))
        for item in result.scalars().all():
            item.is_default = False

    address.label = body.get("label", address.label)
    address.full_name = body.get("name", body.get("full_name", address.full_name))
    address.phone = body.get("phone", address.phone)
    address.street = body.get("street", address.street)
    address.city = body.get("city", address.city)
    address.province = body.get("province", address.province)
    address.postal_code = body.get("postal_code", address.postal_code)
    if "is_default" in body:
        address.is_default = bool(body["is_default"])

    await db.flush()
    return _serialize_address(address)


@router.delete("/api/dashboard/addresses/{address_id}")
async def api_delete_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    address = await db.get(Address, address_id)
    if not address or str(address.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Address not found")
    await db.delete(address)
    await db.flush()
    return {"success": True}


@router.post("/api/dashboard/addresses/{address_id}/default")
async def api_default_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    result = await db.execute(select(Address).where(Address.user_id == user.id))
    selected_address = None
    for address in result.scalars().all():
        address.is_default = address.id == address_id
        if address.id == address_id:
            selected_address = address
    await db.flush()
    if not selected_address:
        raise HTTPException(status_code=404, detail="Address not found")
    return _serialize_address(selected_address)


@router.get("/api/dashboard/orders")
async def api_dashboard_orders(
    status: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    orders = await get_user_orders(db, str(user.id), status=status.lower() if status else None)
    total = len(orders)
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "items": [_serialize_order(order) for order in orders[start:end]],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, ceil(total / per_page)),
    }


@router.get("/api/dashboard/orders/{order_number}")
async def api_dashboard_order(
    order_number: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    order = await _get_order_for_user(db, order_number, user)
    return _serialize_order(order)


@router.get("/api/dashboard/tracking/{order_number}")
async def api_dashboard_tracking(
    order_number: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    stmt = (
        select(Order)
        .where(Order.order_number == order_number, Order.user_id == user.id)
        .options(selectinload(Order.shipment).selectinload(Shipment.tracking_events))
    )
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    if not order or not order.shipment:
        raise HTTPException(status_code=404, detail="Order not found or not shipped yet")
    return _serialize_shipment(order.shipment)


@router.get("/api/dashboard/disputes")
async def api_dashboard_disputes(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    disputes = await get_user_disputes(db, str(user.id))
    return [_serialize_dispute(dispute) for dispute in disputes]


@router.get("/api/dashboard/disputes/{dispute_id}")
async def api_dashboard_dispute(
    dispute_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    dispute = await get_dispute(db, dispute_id)
    if not dispute or str(dispute.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Dispute not found")
    return _serialize_dispute(dispute)


@router.post("/api/dashboard/disputes/raise/{order_id}")
async def api_dashboard_raise_dispute(
    order_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    form = await request.form()
    dispute_type = str(form.get("type") or "refund").lower()
    reason = str(form.get("reason") or "other").lower()
    description = str(form.get("description") or form.get("reason") or "Dispute submitted from React frontend")

    dispute = await create_dispute(
        db,
        order_id=order_id,
        user_id=str(user.id),
        dispute_type=dispute_type,
        reason=reason,
        description=description,
    )
    if not dispute:
        raise HTTPException(status_code=400, detail="Unable to create dispute")

    for uploaded in form.getlist("evidence"):
        filename = getattr(uploaded, "filename", "") or ""
        if not filename:
            continue
        await add_evidence(
            db,
            dispute_id=dispute.id,
            user_id=str(user.id),
            file_url=f"/uploads/disputes/{filename}",
            description=f"Uploaded evidence: {filename}",
        )

    refreshed = await get_dispute(db, dispute.id)
    return _serialize_dispute(refreshed or dispute)


@router.post("/api/dashboard/profile")
async def api_dashboard_profile(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    form = await request.form()
    user.full_name = str(form.get("full_name") or user.full_name or "")
    user.phone = str(form.get("phone") or user.phone or "")
    await db.flush()
    return _serialize_user(user)


@router.get("/api/dashboard/payments")
async def api_dashboard_payments(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    stmt = select(Payment).join(Order).where(Order.user_id == user.id).order_by(Payment.created_at.desc())
    result = await db.execute(stmt)
    return [_serialize_payment(payment) for payment in result.scalars().all() if payment]


@router.get("/api/dashboard/notifications/count")
async def api_notification_count(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    return {"count": await get_unread_count(db, str(user.id))}


@router.get("/api/dashboard/notifications")
async def api_notifications(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    notifications = await get_user_notifications(db, str(user.id), limit=100)
    return [
        {
            "id": notification.id,
            "type": _enum_name(notification.type),
            "title_id": notification.title_id,
            "title_en": notification.title_en,
            "message_id": notification.message_id,
            "message_en": notification.message_en,
            "is_read": notification.is_read,
            "created_at": _iso(notification.created_at),
        }
        for notification in notifications
    ]


@router.post("/api/dashboard/notifications/read-all")
async def api_notifications_read_all(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    await mark_all_read(db, str(user.id))
    return {"success": True}


@router.post("/api/dashboard/notifications/{notification_id}/read")
async def api_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    await mark_read(db, notification_id, str(user.id))
    return {"success": True}
