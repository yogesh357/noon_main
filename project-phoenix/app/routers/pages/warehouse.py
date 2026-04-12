from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import current_active_user
from app.dependencies import get_db
from app.models.user import User, UserRole
from app.services.warehouse import (
    get_handover_orders,
    get_or_create_handover_batch,
    get_packing_queue,
    get_picking_queue,
)
from app.templating import templates

router = APIRouter(prefix="/warehouse", tags=["warehouse-pages"])


def _require_warehouse(user: User) -> None:
    if user.role not in (UserRole.ADMIN, UserRole.WAREHOUSE):
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Warehouse access required")


@router.get("")
async def warehouse_home(request: Request, user: User = Depends(current_active_user)):
    _require_warehouse(user)
    return templates.TemplateResponse(
        "warehouse/home.html",
        {"request": request, "page_title": "Warehouse", "user": user},
    )


@router.get("/picking")
async def picking_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    _require_warehouse(user)
    orders = await get_picking_queue(db)

    return templates.TemplateResponse(
        "warehouse/picking.html",
        {
            "request": request,
            "page_title": "Picking",
            "user": user,
            "orders": orders,
        },
    )


@router.get("/packing")
async def packing_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    _require_warehouse(user)
    orders = await get_packing_queue(db)

    return templates.TemplateResponse(
        "warehouse/packing.html",
        {
            "request": request,
            "page_title": "Packing",
            "user": user,
            "orders": orders,
        },
    )


@router.get("/handover")
async def handover_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    _require_warehouse(user)
    ready_orders = await get_handover_orders(db)
    batch = await get_or_create_handover_batch(db, str(user.id))

    from app.services.warehouse import get_handover_progress

    progress = await get_handover_progress(db, batch.id)

    return templates.TemplateResponse(
        "warehouse/handover.html",
        {
            "request": request,
            "page_title": "Package Handover",
            "user": user,
            "ready_orders": ready_orders,
            "batch": batch,
            "progress": progress,
        },
    )
