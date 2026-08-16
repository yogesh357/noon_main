from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import current_active_user
from app.dependencies import get_db
from app.models.order import Order
from app.models.user import User, UserRole
from app.models.warehouse import HandoverBatch, HandoverItem, PackingTask, PickingTask
from app.services.warehouse import (
    complete_handover,
    complete_packing,
    complete_picking,
    get_handover_orders,
    get_or_create_handover_batch,
    get_packing_progress,
    get_packing_queue,
    get_picking_queue,
    return_to_picker,
    scan_handover_order,
    scan_product,
    start_packing,
    start_picking,
)
from app.routers.api.helpers import (
    _require_role,
    _serialize_picking_task,
    _serialize_packing_task,
    _serialize_handover_batch,
)

router = APIRouter(tags=["warehouse"])


@router.get("/api/warehouse")
async def api_warehouse_home(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    _require_role(user, UserRole.WAREHOUSE, UserRole.ADMIN)
    picking = await get_picking_queue(db)
    packing = await get_packing_queue(db)
    handover = await get_handover_orders(db)
    return {
        "pending_picking": len(picking),
        "pending_packing": len(packing),
        "pending_handover": len(handover),
    }


@router.post("/api/warehouse/picking/start/{order_id}")
async def api_warehouse_start_picking(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    _require_role(user, UserRole.WAREHOUSE, UserRole.ADMIN)
    task = await start_picking(db, order_id, str(user.id))
    if not task:
        raise HTTPException(status_code=400, detail="Unable to start picking task")
    order = await db.get(Order, task.order_id)
    return _serialize_picking_task(task, order)


@router.post("/api/warehouse/picking/complete/{task_id}")
async def api_warehouse_complete_picking(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    _require_role(user, UserRole.WAREHOUSE, UserRole.ADMIN)
    task = await db.get(PickingTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Picking task not found")
    success = await complete_picking(db, task_id)
    if not success:
        raise HTTPException(status_code=400, detail="Unable to complete picking task")
    refreshed = await db.get(PickingTask, task_id)
    order = await db.get(Order, refreshed.order_id)
    return _serialize_picking_task(refreshed, order)


@router.post("/api/warehouse/packing/start/{order_id}")
async def api_warehouse_start_packing(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    _require_role(user, UserRole.WAREHOUSE, UserRole.ADMIN)
    task = await start_packing(db, order_id, str(user.id))
    if not task:
        raise HTTPException(status_code=400, detail="Unable to start packing task")
    order = await db.get(Order, task.order_id, options=[selectinload(Order.items)])
    return _serialize_packing_task(task, order)


@router.post("/api/warehouse/packing/scan/{task_id}")
async def api_warehouse_scan_packing(
    task_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    _require_role(user, UserRole.WAREHOUSE, UserRole.ADMIN)
    barcode = str(body.get("barcode") or "").strip()
    if not barcode:
        raise HTTPException(status_code=400, detail="barcode is required")
    result = await scan_product(db, task_id, barcode)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    progress = await get_packing_progress(db, task_id)
    return {"success": True, "message": result["message"], "progress": progress}


@router.post("/api/warehouse/packing/complete/{task_id}")
async def api_warehouse_complete_packing(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    _require_role(user, UserRole.WAREHOUSE, UserRole.ADMIN)
    task = await db.get(PackingTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Packing task not found")
    success = await complete_packing(db, task_id)
    if not success:
        raise HTTPException(status_code=400, detail="All items must be scanned before completing packing")
    refreshed = await db.get(PackingTask, task_id)
    order = await db.get(Order, refreshed.order_id, options=[selectinload(Order.items)])
    return _serialize_packing_task(refreshed, order)


@router.post("/api/warehouse/packing/return/{task_id}")
async def api_warehouse_return_packing(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    _require_role(user, UserRole.WAREHOUSE, UserRole.ADMIN)
    success = await return_to_picker(db, task_id)
    if not success:
        raise HTTPException(status_code=400, detail="Unable to return order to picker")
    return {"success": True}


@router.post("/api/warehouse/handover/scan")
async def api_warehouse_handover_scan(
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    _require_role(user, UserRole.WAREHOUSE, UserRole.ADMIN)
    batch_id = body.get("batch_id")
    order_number = str(body.get("order_number") or "").strip()
    if not order_number:
        raise HTTPException(status_code=400, detail="order_number is required")
    batch = await db.get(HandoverBatch, int(batch_id)) if batch_id else None
    if not batch:
        batch = await get_or_create_handover_batch(db, str(user.id))
    result = await scan_handover_order(db, batch.id, order_number)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    refreshed = await db.get(
        HandoverBatch,
        batch.id,
        options=[selectinload(HandoverBatch.items).selectinload(HandoverItem.order)],
    )
    return {
        "success": True,
        "batch_id": batch.id,
        "order_number": result["order_number"],
        "batch": _serialize_handover_batch(refreshed or batch),
    }


@router.post("/api/warehouse/handover/complete/{batch_id}")
async def api_warehouse_handover_complete(
    batch_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    _require_role(user, UserRole.WAREHOUSE, UserRole.ADMIN)
    success = await complete_handover(db, batch_id)
    if not success:
        raise HTTPException(status_code=400, detail="Unable to complete handover batch")
    batch = await db.get(
        HandoverBatch,
        batch_id,
        options=[selectinload(HandoverBatch.items).selectinload(HandoverItem.order)],
    )
    return _serialize_handover_batch(batch)
