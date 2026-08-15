"""Warehouse operations: picking, packing, handover with barcode scanning."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.catalog import ProductVariant
from app.models.order import Order, OrderStatus
from app.models.warehouse import (
    HandoverBatch,
    HandoverItem,
    HandoverStatus,
    PackingTask,
    PickingTask,
    TaskStatus,
)

# --- Picking ---

async def get_picking_queue(db: AsyncSession) -> list[Order]:
    """Get orders ready for picking (status = PROCESSING)."""
    stmt = (
        select(Order)
        .where(Order.status == OrderStatus.PROCESSING)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def start_picking(
    db: AsyncSession,
    order_id: int,
    picker_user_id: str,
) -> PickingTask | None:
    """Start picking for an order. Returns None if order is not in PROCESSING status."""
    order = await db.get(Order, order_id)
    if not order or order.status != OrderStatus.PROCESSING:
        return None

    # Check no active picking task already exists for this order
    existing = await db.execute(
        select(PickingTask).where(
            PickingTask.order_id == order_id,
            PickingTask.status.in_([TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]),
        )
    )
    if existing.scalar_one_or_none():
        return None

    task = PickingTask(
        order_id=order_id,
        picker_user_id=picker_user_id,
        status=TaskStatus.IN_PROGRESS,
        started_at=datetime.now(UTC),
    )
    db.add(task)
    order.status = OrderStatus.PICKING

    await db.flush()
    return task


async def complete_picking(db: AsyncSession, task_id: int) -> bool:
    """Mark picking as complete, move order to PACKING."""
    task = await db.get(PickingTask, task_id)
    if not task:
        return False

    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.now(UTC)

    order = await db.get(Order, task.order_id)
    if order:
        order.status = OrderStatus.PACKING

    await db.flush()
    return True


# --- Packing ---

async def get_packing_queue(db: AsyncSession) -> list[Order]:
    """Get orders ready for packing (status = PACKING)."""
    stmt = (
        select(Order)
        .where(Order.status == OrderStatus.PACKING)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def start_packing(
    db: AsyncSession,
    order_id: int,
    packer_user_id: str,
) -> PackingTask | None:
    """Start packing for an order. Returns None if order is not in PACKING status."""
    order = await db.get(Order, order_id)
    if not order or order.status != OrderStatus.PACKING:
        return None

    # Check no active packing task already exists
    existing = await db.execute(
        select(PackingTask).where(
            PackingTask.order_id == order_id,
            PackingTask.status.in_([TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]),
        )
    )
    if existing.scalar_one_or_none():
        return None

    task = PackingTask(
        order_id=order_id,
        packer_user_id=packer_user_id,
        status=TaskStatus.IN_PROGRESS,
        started_at=datetime.now(UTC),
        scan_log=[],
    )
    db.add(task)
    await db.flush()
    return task


async def get_order_product_checklist(
    db: AsyncSession,
    order_id: int,
) -> list[dict]:
    """Get the product checklist for packing verification."""
    order = await db.get(Order, order_id, options=[selectinload(Order.items)])
    if not order:
        return []

    checklist = []
    for item in order.items:
        variant = None
        if item.variant_id:
            variant = await db.get(ProductVariant, item.variant_id)

        checklist.append({
            "order_item_id": item.id,
            "product_name": item.product_name_snapshot,
            "sku": item.sku_snapshot,
            "barcode": variant.barcode if variant else None,
            "quantity": item.quantity,
            "scanned": 0,
        })

    return checklist


async def scan_product(
    db: AsyncSession,
    task_id: int,
    scanned_barcode: str,
) -> dict:
    """Process a barcode scan during packing.

    Returns: {"success": bool, "message": str, "item_name": str|None}
    """
    task = await db.get(PackingTask, task_id)
    if not task:
        return {"success": False, "message": "Task not found", "item_name": None}

    order = await db.get(Order, task.order_id, options=[selectinload(Order.items)])
    if not order:
        return {"success": False, "message": "Order not found", "item_name": None}

    # Find matching variant by barcode or SKU
    matched_item = None
    for item in order.items:
        if item.variant_id:
            variant = await db.get(ProductVariant, item.variant_id)
            if variant and (
                variant.barcode == scanned_barcode or variant.sku == scanned_barcode
            ):
                matched_item = item
                break

    if not matched_item:
        return {
            "success": False,
            "message": "Product not in this order",
            "item_name": None,
        }

    # Count how many times this item has been scanned (track by order_item_id)
    scan_log = list(task.scan_log or [])  # Copy to ensure SQLAlchemy detects mutation
    scanned_count = sum(
        1 for s in scan_log if s.get("order_item_id") == matched_item.id
    )

    if scanned_count >= matched_item.quantity:
        return {
            "success": False,
            "message": f"Already scanned all {matched_item.quantity} of this item",
            "item_name": matched_item.product_name_snapshot,
        }

    # Record the scan (track by order_item_id for uniqueness)
    scan_log.append({
        "order_item_id": matched_item.id,
        "sku": matched_item.sku_snapshot,
        "barcode": scanned_barcode,
        "timestamp": datetime.now(UTC).isoformat(),
    })
    task.scan_log = scan_log  # Reassign copy so SQLAlchemy detects change
    await db.flush()

    return {
        "success": True,
        "message": "Scanned successfully",
        "item_name": matched_item.product_name_snapshot,
    }


async def get_packing_progress(
    db: AsyncSession,
    task_id: int,
) -> dict:
    """Get scan progress for a packing task."""
    task = await db.get(PackingTask, task_id)
    if not task:
        return {"total_items": 0, "scanned_items": 0, "complete": False, "items": []}

    order = await db.get(Order, task.order_id, options=[selectinload(Order.items)])
    scan_log = task.scan_log or []

    items = []
    total_required = 0
    total_scanned = 0

    for item in order.items:
        scanned = sum(1 for s in scan_log if s.get("order_item_id") == item.id)
        total_required += item.quantity
        total_scanned += min(scanned, item.quantity)

        variant = None
        if item.variant_id:
            variant = await db.get(ProductVariant, item.variant_id)

        items.append({
            "product_name": item.product_name_snapshot,
            "sku": item.sku_snapshot,
            "barcode": variant.barcode if variant else None,
            "required": item.quantity,
            "scanned": min(scanned, item.quantity),
            "complete": scanned >= item.quantity,
        })

    return {
        "total_items": total_required,
        "scanned_items": total_scanned,
        "complete": total_scanned >= total_required,
        "items": items,
    }


async def complete_packing(db: AsyncSession, task_id: int) -> bool:
    """Complete packing — verify all items scanned, move to READY_TO_SHIP."""
    progress = await get_packing_progress(db, task_id)
    if not progress["complete"]:
        return False

    task = await db.get(PackingTask, task_id)
    if not task:
        return False

    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.now(UTC)

    order = await db.get(Order, task.order_id)
    if order:
        order.status = OrderStatus.READY_TO_SHIP

    await db.flush()
    return True


async def return_to_picker(db: AsyncSession, task_id: int) -> bool:
    """Return order to picker (wrong/incomplete products)."""
    task = await db.get(PackingTask, task_id)
    if not task:
        return False

    task.status = TaskStatus.RETURNED
    task.scan_log = []

    order = await db.get(Order, task.order_id)
    if order:
        order.status = OrderStatus.PROCESSING

    await db.flush()
    return True


# --- Handover ---

async def get_handover_orders(db: AsyncSession) -> list[Order]:
    """Get orders ready for handover (status = READY_TO_SHIP)."""
    stmt = (
        select(Order)
        .where(Order.status == OrderStatus.READY_TO_SHIP)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_or_create_handover_batch(
    db: AsyncSession,
    sender_user_id: str,
) -> HandoverBatch:
    """Get open batch or create new one for this sender."""
    stmt = select(HandoverBatch).where(
        HandoverBatch.sender_user_id == sender_user_id,
        HandoverBatch.status == HandoverStatus.OPEN,
    )
    result = await db.execute(stmt)
    batch = result.scalar_one_or_none()

    if batch:
        return batch

    batch = HandoverBatch(
        sender_user_id=sender_user_id,
        status=HandoverStatus.OPEN,
    )
    db.add(batch)
    await db.flush()
    return batch


async def scan_handover_order(
    db: AsyncSession,
    batch_id: int,
    order_number: str,
) -> dict:
    """Scan an order for handover. Returns result dict."""
    # Find order by number or tracking number
    stmt = select(Order).where(
        Order.order_number == order_number,
        Order.status == OrderStatus.READY_TO_SHIP,
    )
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        return {"success": False, "message": "Order not found or not ready to ship"}

    # Check not already in this batch
    existing = await db.execute(
        select(HandoverItem).where(
            HandoverItem.batch_id == batch_id,
            HandoverItem.order_id == order.id,
        )
    )
    if existing.scalar_one_or_none():
        return {"success": False, "message": "Already scanned in this batch"}

    # Add to batch and update status
    item = HandoverItem(batch_id=batch_id, order_id=order.id)
    db.add(item)

    order.status = OrderStatus.SHIPPED

    await db.flush()

    return {
        "success": True,
        "message": f"Order {order.order_number} shipped",
        "order_number": order.order_number,
    }


async def get_handover_progress(
    db: AsyncSession,
    batch_id: int,
) -> dict:
    """Get progress of a handover batch."""
    batch = await db.get(
        HandoverBatch, batch_id, options=[selectinload(HandoverBatch.items)]
    )
    if not batch:
        return {"scanned": 0, "items": []}

    ready_count_result = await db.execute(
        select(Order)
        .where(Order.status == OrderStatus.READY_TO_SHIP)
    )
    ready_orders = list(ready_count_result.scalars().all())

    scanned_items = []
    for hi in batch.items:
        order = await db.get(Order, hi.order_id)
        if order:
            scanned_items.append({
                "order_number": order.order_number,
                "courier": order.courier or "N/A",
                "scanned_at": hi.scanned_at,
            })

    return {
        "scanned": len(batch.items),
        "remaining": len(ready_orders),
        "items": scanned_items,
    }


async def complete_handover(db: AsyncSession, batch_id: int) -> bool:
    """Complete a handover batch."""
    batch = await db.get(HandoverBatch, batch_id)
    if not batch:
        return False

    batch.status = HandoverStatus.COMPLETED
    batch.completed_at = datetime.now(UTC)
    await db.flush()
    return True
