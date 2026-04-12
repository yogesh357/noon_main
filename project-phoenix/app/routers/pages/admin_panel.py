"""Custom admin panel views for operational workflows.

Separate from SQLAdmin CRUD — these handle order management, bulk operations,
label generation, and dashboard stats.
"""

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import current_active_user
from app.dependencies import get_db
from app.models.order import Order, OrderSource, OrderStatus
from app.models.user import User, UserRole
from app.services.admin import bulk_process_orders, get_admin_dashboard_stats, get_admin_order_queue
from app.services.order import get_order_by_number, update_order_status
from app.templating import templates
from app.utils.pdf import generate_labels_pdf

router = APIRouter(prefix="/admin-panel", tags=["admin-panel"])


def _require_admin(user: User) -> None:
    if user.role not in (UserRole.ADMIN,):
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Admin access required")


@router.get("")
async def admin_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    _require_admin(user)
    stats = await get_admin_dashboard_stats(db)

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "page_title": "Admin Dashboard",
            "section": "dashboard",
            "user": user,
            "stats": stats,
        },
    )


@router.get("/orders")
async def admin_orders(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
    status: str | None = Query(None),
    source: str | None = Query(None),
    page: int = Query(1, ge=1),
):
    _require_admin(user)

    status_enum = None
    source_enum = None
    if status:
        try:
            status_enum = OrderStatus(status)
        except ValueError:
            pass
    if source:
        try:
            source_enum = OrderSource(source)
        except ValueError:
            pass

    orders, total = await get_admin_order_queue(
        db, status=status_enum, source=source_enum, page=page
    )
    total_pages = (total + 19) // 20

    ctx = {
        "request": request,
        "page_title": "Order Management",
        "section": "orders",
        "user": user,
        "orders": orders,
        "total": total,
        "total_pages": total_pages,
        "current_page": page,
        "current_status": status,
        "current_source": source,
    }

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse("admin/_order_queue.html", ctx)

    return templates.TemplateResponse("admin/orders.html", ctx)


@router.get("/orders/{order_number}")
async def admin_order_detail(
    order_number: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    _require_admin(user)
    order = await get_order_by_number(db, order_number)
    if not order:
        return templates.TemplateResponse(
            "pages/404.html", {"request": request, "page_title": "Not Found"}, status_code=404
        )

    return templates.TemplateResponse(
        "admin/order_detail.html",
        {
            "request": request,
            "page_title": f"Order {order.order_number}",
            "section": "orders",
            "user": user,
            "order": order,
        },
    )


@router.post("/orders/bulk-process")
async def admin_bulk_process(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Move accepted (paid) orders to PROCESSING status to begin fulfillment."""
    _require_admin(user)
    form = await request.form()
    order_ids = [int(id) for id in form.getlist("order_ids")]

    if order_ids:
        await bulk_process_orders(db, order_ids)

    # Refresh the order queue
    orders, total = await get_admin_order_queue(db)
    return templates.TemplateResponse(
        "admin/_order_queue.html",
        {
            "request": request,
            "orders": orders,
            "total": total,
            "total_pages": (total + 19) // 20,
            "current_page": 1,
            "current_status": None,
            "current_source": None,
        },
    )


@router.post("/orders/{order_number}/status")
async def admin_update_status(
    order_number: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Update a single order's status."""
    _require_admin(user)
    form = await request.form()
    new_status_str = form.get("status", "")

    order = await get_order_by_number(db, order_number)
    if not order:
        return Response(status_code=404)

    try:
        new_status = OrderStatus(new_status_str)
        await update_order_status(db, order.id, new_status)
    except ValueError:
        pass

    # Return updated order detail
    order = await get_order_by_number(db, order_number)
    return templates.TemplateResponse(
        "admin/order_detail.html",
        {
            "request": request,
            "page_title": f"Order {order.order_number}",
            "section": "orders",
            "user": user,
            "order": order,
        },
    )


@router.post("/orders/print-labels")
async def admin_print_labels(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Generate shipping label PDF for selected orders."""
    _require_admin(user)
    form = await request.form()
    order_ids = [int(id) for id in form.getlist("order_ids")]

    if not order_ids:
        return Response(status_code=400, content="No orders selected")

    from sqlalchemy import select

    stmt = (
        select(Order)
        .where(Order.id.in_(order_ids))
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )
    result = await db.execute(stmt)
    orders = list(result.scalars().all())

    if not orders:
        return Response(status_code=404, content="No orders found")

    # WeasyPrint is CPU-intensive — run in thread to avoid blocking event loop
    import asyncio

    try:
        pdf_bytes = await asyncio.to_thread(generate_labels_pdf, orders)
    except Exception as e:
        return Response(
            status_code=500,
            content=f"Label generation failed: {e}",
        )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename=labels-{len(orders)}-orders.pdf",
        },
    )


@router.get("/marketplace-orders")
async def admin_marketplace_orders(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
    source: str | None = Query(None),
    page: int = Query(1, ge=1),
):
    """View marketplace orders (non-website sources)."""
    _require_admin(user)

    source_enum = None
    if source:
        try:
            source_enum = OrderSource(source)
        except ValueError:
            pass

    # Default to showing all marketplace orders (exclude website)
    from sqlalchemy import func, select

    per_page = 20
    count_stmt = (
        select(func.count())
        .select_from(Order)
        .where(Order.source != OrderSource.WEBSITE)
    )
    data_stmt = (
        select(Order)
        .where(Order.source != OrderSource.WEBSITE)
        .options(selectinload(Order.items), selectinload(Order.payment))
        .order_by(Order.created_at.desc())
    )
    if source_enum:
        count_stmt = count_stmt.where(Order.source == source_enum)
        data_stmt = data_stmt.where(Order.source == source_enum)

    total = (await db.execute(count_stmt)).scalar_one()
    offset = (page - 1) * per_page
    data_stmt = data_stmt.offset(offset).limit(per_page)

    result = await db.execute(data_stmt)
    orders = list(result.scalars().all())

    return templates.TemplateResponse(
        "admin/marketplace_orders.html",
        {
            "request": request,
            "page_title": "Marketplace Orders",
            "section": "marketplace",
            "user": user,
            "orders": orders,
            "current_source": source,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page,
            "current_page": page,
        },
    )


@router.get("/disputes")
async def admin_disputes(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
    status: str | None = Query(None),
):
    """Admin dispute queue with SLA tracking."""
    _require_admin(user)

    from app.services.dispute import get_admin_dispute_queue, get_dispute_stats

    disputes = await get_admin_dispute_queue(db, status=status)
    stats = await get_dispute_stats(db)

    return templates.TemplateResponse(
        "admin/disputes.html",
        {
            "request": request,
            "page_title": "Disputes",
            "section": "disputes",
            "user": user,
            "disputes": disputes,
            "stats": stats,
            "current_status": status,
        },
    )


@router.get("/disputes/{dispute_id}")
async def admin_dispute_detail(
    dispute_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    _require_admin(user)

    from app.services.dispute import get_dispute

    dispute = await get_dispute(db, dispute_id)
    if not dispute:
        return templates.TemplateResponse(
            "pages/404.html", {"request": request, "page_title": "Not Found"},
            status_code=404,
        )

    return templates.TemplateResponse(
        "admin/dispute_detail.html",
        {
            "request": request,
            "page_title": f"Dispute #{dispute.id}",
            "section": "disputes",
            "user": user,
            "dispute": dispute,
        },
    )
