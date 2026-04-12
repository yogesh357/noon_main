"""Warehouse scan API endpoints — used by HTMX + barcode scanner JS."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import current_active_user
from app.dependencies import get_db
from app.models.user import User, UserRole
from app.services.warehouse import (
    complete_handover,
    complete_packing,
    complete_picking,
    get_handover_progress,
    get_or_create_handover_batch,
    get_order_product_checklist,
    get_packing_progress,
    return_to_picker,
    scan_handover_order,
    scan_product,
    start_packing,
    start_picking,
)
from app.templating import templates

router = APIRouter(prefix="/api/warehouse", tags=["warehouse-api"])


def _require_warehouse(user: User) -> None:
    if user.role not in (UserRole.ADMIN, UserRole.WAREHOUSE):
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Warehouse access required")


# --- Picking ---

@router.post("/picking/start/{order_id}")
async def api_start_picking(
    order_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Start picking for an order."""
    _require_warehouse(user)
    task = await start_picking(db, order_id, str(user.id))

    if not task:
        return JSONResponse(
            status_code=409,
            content={"error": "Order not available for picking"},
        )

    checklist = await get_order_product_checklist(db, order_id)

    return templates.TemplateResponse(
        "warehouse/_picking_active.html",
        {
            "request": request,
            "task": task,
            "checklist": checklist,
            "order_id": order_id,
        },
    )


@router.post("/picking/complete/{task_id}")
async def api_complete_picking(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Complete picking for an order."""
    _require_warehouse(user)
    success = await complete_picking(db, task_id)
    return JSONResponse(
        content={"success": success},
        headers={"HX-Refresh": "true"} if success else {},
    )


# --- Packing ---

@router.post("/packing/start/{order_id}")
async def api_start_packing(
    order_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Start packing for an order — shows product checklist."""
    _require_warehouse(user)
    task = await start_packing(db, order_id, str(user.id))

    if not task:
        return JSONResponse(
            status_code=409,
            content={"error": "Order not available for packing"},
        )

    progress = await get_packing_progress(db, task.id)

    return templates.TemplateResponse(
        "warehouse/_packing_active.html",
        {
            "request": request,
            "task": task,
            "progress": progress,
            "order_id": order_id,
        },
    )


@router.post("/packing/scan/{task_id}")
async def api_scan_product(
    task_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Scan a product barcode during packing."""
    _require_warehouse(user)
    form = await request.form()
    barcode = form.get("barcode", "").strip()

    if not barcode:
        return templates.TemplateResponse(
            "warehouse/_scan_result.html",
            {"request": request, "result": {"success": False, "message": "Empty scan"}},
        )

    result = await scan_product(db, task_id, barcode)
    progress = await get_packing_progress(db, task_id)

    return templates.TemplateResponse(
        "warehouse/_packing_active.html",
        {
            "request": request,
            "task": {"id": task_id},
            "progress": progress,
            "order_id": None,
            "last_scan": result,
        },
    )


@router.post("/packing/complete/{task_id}")
async def api_complete_packing(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Complete packing — only succeeds if all items scanned."""
    _require_warehouse(user)
    success = await complete_packing(db, task_id)
    msg = "Packing complete" if success else "Not all items scanned"
    return JSONResponse(
        content={"success": success, "message": msg},
        headers={"HX-Refresh": "true"} if success else {},
    )


@router.post("/packing/return/{task_id}")
async def api_return_to_picker(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Return order to picker (wrong/incomplete products)."""
    _require_warehouse(user)
    await return_to_picker(db, task_id)
    return JSONResponse(
        content={"success": True},
        headers={"HX-Refresh": "true"},
    )


# --- Handover ---

@router.post("/handover/scan")
async def api_scan_handover(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Scan a packed order for courier handover."""
    _require_warehouse(user)
    form = await request.form()
    order_number = form.get("order_number", "").strip()

    batch = await get_or_create_handover_batch(db, str(user.id))
    result = await scan_handover_order(db, batch.id, order_number)
    progress = await get_handover_progress(db, batch.id)

    return templates.TemplateResponse(
        "warehouse/_handover_status.html",
        {
            "request": request,
            "result": result,
            "progress": progress,
            "batch": batch,
        },
    )


@router.post("/handover/complete/{batch_id}")
async def api_complete_handover(
    batch_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Complete handover batch."""
    _require_warehouse(user)
    await complete_handover(db, batch_id)
    return JSONResponse(
        content={"success": True},
        headers={"HX-Refresh": "true"},
    )
