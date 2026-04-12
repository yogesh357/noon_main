from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import current_active_user
from app.dependencies import get_db
from app.models.order import Order
from app.models.user import Address, User
from app.services.catalog import get_user_wishlist_products
from app.services.notification import get_unread_count, get_user_notifications
from app.services.order import get_user_orders
from app.templating import templates

router = APIRouter(prefix="/dashboard", tags=["dashboard-pages"])


@router.get("")
async def dashboard_overview(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Dashboard overview — recent orders, stats, pending actions."""
    orders = await get_user_orders(db, str(user.id))
    recent_orders = orders[:5]
    unread_count = await get_unread_count(db, str(user.id))
    wishlist_products = await get_user_wishlist_products(db, str(user.id))

    language = getattr(request.state, "language", "id")

    return templates.TemplateResponse(
        "dashboard/overview.html",
        {
            "request": request,
            "page_title": "Dashboard",
            "section": "overview",
            "user": user,
            "recent_orders": recent_orders,
            "total_orders": len(orders),
            "unread_notifications": unread_count,
            "wishlist_count": len(wishlist_products),
            "language": language,
        },
    )


@router.get("/orders")
async def dashboard_orders(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
    status: str | None = Query(None),
):
    orders = await get_user_orders(db, str(user.id), status=status)
    language = getattr(request.state, "language", "id")

    ctx = {
        "request": request,
        "page_title": "My Orders",
        "section": "orders",
        "user": user,
        "orders": orders,
        "current_status": status,
        "language": language,
    }

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse("dashboard/_order_list.html", ctx)

    return templates.TemplateResponse("dashboard/orders.html", ctx)


@router.get("/orders/{order_number}")
async def dashboard_order_detail(
    order_number: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    from app.services.order import get_order_by_number

    order = await get_order_by_number(db, order_number)
    if not order or str(order.user_id) != str(user.id):
        return templates.TemplateResponse(
            "pages/404.html",
            {"request": request, "page_title": "Not Found"},
            status_code=404,
        )

    language = getattr(request.state, "language", "id")

    return templates.TemplateResponse(
        "dashboard/order_detail.html",
        {
            "request": request,
            "page_title": f"Order {order.order_number}",
            "section": "orders",
            "user": user,
            "order": order,
            "language": language,
        },
    )


@router.get("/tracking")
async def dashboard_tracking(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Active shipments tracking."""
    from sqlalchemy.orm import selectinload

    from app.models.logistics import Shipment
    from app.models.order import OrderStatus

    active_statuses = [
        OrderStatus.PROCESSING, OrderStatus.PICKING, OrderStatus.PACKING,
        OrderStatus.READY_TO_SHIP, OrderStatus.SHIPPED,
    ]
    stmt = (
        select(Order)
        .where(Order.user_id == user.id, Order.status.in_(active_statuses))
        .options(selectinload(Order.shipment).selectinload(Shipment.tracking_events))
        .order_by(Order.created_at.desc())
    )
    result = await db.execute(stmt)
    active_orders = list(result.scalars().all())
    language = getattr(request.state, "language", "id")

    return templates.TemplateResponse(
        "dashboard/tracking.html",
        {
            "request": request,
            "page_title": "Track Shipment",
            "section": "tracking",
            "user": user,
            "active_orders": active_orders,
            "language": language,
        },
    )


@router.get("/disputes")
async def dashboard_disputes(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    from app.services.dispute import get_user_disputes

    disputes = await get_user_disputes(db, str(user.id))
    language = getattr(request.state, "language", "id")

    return templates.TemplateResponse(
        "dashboard/disputes.html",
        {
            "request": request,
            "page_title": "Disputes",
            "section": "disputes",
            "user": user,
            "disputes": disputes,
            "language": language,
        },
    )


@router.get("/disputes/raise/{order_id}")
async def dashboard_raise_dispute(
    order_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    from app.services.dispute import can_raise_dispute

    order = await db.get(Order, order_id)
    if not order or str(order.user_id) != str(user.id):
        return templates.TemplateResponse(
            "pages/404.html", {"request": request, "page_title": "Not Found"},
            status_code=404,
        )

    check = await can_raise_dispute(db, order_id, str(user.id))
    language = getattr(request.state, "language", "id")

    return templates.TemplateResponse(
        "dashboard/raise_dispute.html",
        {
            "request": request,
            "page_title": "Raise Dispute",
            "section": "disputes",
            "user": user,
            "order": order,
            "can_dispute": check,
            "language": language,
        },
    )


@router.get("/disputes/{dispute_id}")
async def dashboard_dispute_detail(
    dispute_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    from app.services.dispute import get_dispute

    dispute = await get_dispute(db, dispute_id)
    if not dispute or str(dispute.user_id) != str(user.id):
        return templates.TemplateResponse(
            "pages/404.html", {"request": request, "page_title": "Not Found"},
            status_code=404,
        )

    language = getattr(request.state, "language", "id")

    return templates.TemplateResponse(
        "dashboard/dispute_detail.html",
        {
            "request": request,
            "page_title": f"Dispute #{dispute.id}",
            "section": "disputes",
            "user": user,
            "dispute": dispute,
            "language": language,
        },
    )


@router.get("/addresses")
async def dashboard_addresses(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    result = await db.execute(
        select(Address)
        .where(Address.user_id == user.id)
        .order_by(Address.is_default.desc(), Address.id)
    )
    addresses = list(result.scalars().all())

    return templates.TemplateResponse(
        "dashboard/addresses.html",
        {
            "request": request,
            "page_title": "Addresses",
            "section": "addresses",
            "user": user,
            "addresses": addresses,
            "language": getattr(request.state, "language", "id"),
        },
    )


@router.get("/payments")
async def dashboard_payments(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    orders = await get_user_orders(db, str(user.id))
    payments = [o for o in orders if o.payment]
    language = getattr(request.state, "language", "id")

    return templates.TemplateResponse(
        "dashboard/payments.html",
        {
            "request": request,
            "page_title": "Payments",
            "section": "payments",
            "user": user,
            "payments": payments,
            "language": language,
        },
    )


@router.get("/wishlist")
async def dashboard_wishlist(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    products = await get_user_wishlist_products(db, str(user.id))
    language = getattr(request.state, "language", "id")

    return templates.TemplateResponse(
        "dashboard/wishlist.html",
        {
            "request": request,
            "page_title": "Wishlist",
            "section": "wishlist",
            "user": user,
            "products": products,
            "language": language,
        },
    )


@router.get("/profile")
async def dashboard_profile(
    request: Request,
    user: User = Depends(current_active_user),
):
    return templates.TemplateResponse(
        "dashboard/profile.html",
        {
            "request": request,
            "page_title": "Profile",
            "section": "profile",
            "user": user,
            "language": getattr(request.state, "language", "id"),
        },
    )


@router.get("/notifications")
async def dashboard_notifications(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    notifications = await get_user_notifications(db, str(user.id))
    language = getattr(request.state, "language", "id")

    return templates.TemplateResponse(
        "dashboard/notifications.html",
        {
            "request": request,
            "page_title": "Notifications",
            "section": "notifications",
            "user": user,
            "notifications": notifications,
            "language": language,
        },
    )
