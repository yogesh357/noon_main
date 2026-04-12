from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import current_active_user
from app.dependencies import get_db
from app.models.user import Address, User
from app.services.notification import get_unread_count, mark_all_read, mark_read
from app.templating import templates

router = APIRouter(prefix="/api/dashboard", tags=["dashboard-api"])


# --- Addresses ---
@router.post("/addresses")
async def create_address(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Create new address from form data."""
    form = await request.form()
    address = Address(
        user_id=user.id,
        label=form.get("label", "Home"),
        full_name=form.get("full_name", ""),
        phone=form.get("phone", ""),
        street=form.get("street", ""),
        city=form.get("city", ""),
        province=form.get("province", ""),
        postal_code=form.get("postal_code", ""),
        is_default=form.get("is_default") == "on",
    )

    # If setting as default, unset other defaults
    if address.is_default:
        existing = await db.execute(
            select(Address).where(
                Address.user_id == user.id, Address.is_default.is_(True)
            )
        )
        for addr in existing.scalars().all():
            addr.is_default = False

    db.add(address)
    await db.flush()

    # Return updated address list
    return await _render_address_list(request, db, user)


@router.patch("/addresses/{address_id}")
async def update_address(
    address_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Update an existing address."""
    address = await db.get(Address, address_id)
    if not address or str(address.user_id) != str(user.id):
        return JSONResponse(status_code=404, content={"error": "Not found"})

    form = await request.form()
    if "full_name" in form:
        address.full_name = form["full_name"]
    if "phone" in form:
        address.phone = form["phone"]
    if "street" in form:
        address.street = form["street"]
    if "city" in form:
        address.city = form["city"]
    if "province" in form:
        address.province = form["province"]
    if "postal_code" in form:
        address.postal_code = form["postal_code"]
    if "label" in form:
        address.label = form["label"]

    await db.flush()
    return await _render_address_list(request, db, user)


@router.delete("/addresses/{address_id}")
async def delete_address(
    address_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Delete an address."""
    address = await db.get(Address, address_id)
    if not address or str(address.user_id) != str(user.id):
        return JSONResponse(status_code=404, content={"error": "Not found"})

    await db.delete(address)
    await db.flush()
    return await _render_address_list(request, db, user)


@router.post("/addresses/{address_id}/default")
async def set_default_address(
    address_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Set an address as default."""
    # Unset all defaults
    existing = await db.execute(
        select(Address).where(
            Address.user_id == user.id, Address.is_default.is_(True)
        )
    )
    for addr in existing.scalars().all():
        addr.is_default = False

    # Set new default
    address = await db.get(Address, address_id)
    if address and str(address.user_id) == str(user.id):
        address.is_default = True

    await db.flush()
    return await _render_address_list(request, db, user)


async def _render_address_list(request: Request, db: AsyncSession, user: User):
    result = await db.execute(
        select(Address)
        .where(Address.user_id == user.id)
        .order_by(Address.is_default.desc(), Address.id)
    )
    addresses = list(result.scalars().all())
    return templates.TemplateResponse(
        "dashboard/_address_list.html",
        {"request": request, "addresses": addresses},
    )


# --- Profile ---
@router.post("/profile")
async def update_profile(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Update user profile."""
    form = await request.form()
    if "full_name" in form:
        user.full_name = form["full_name"]
    if "phone" in form:
        user.phone = form["phone"]
    if "language_pref" in form and form["language_pref"] in ("id", "en"):
        user.language_pref = form["language_pref"]

    await db.flush()

    return templates.TemplateResponse(
        "dashboard/_profile_form.html",
        {"request": request, "user": user, "saved": True},
    )


# --- Notifications ---
@router.get("/notifications/count")
async def notification_count(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Get unread notification count for header badge."""
    count = await get_unread_count(db, str(user.id))
    return templates.TemplateResponse(
        "partials/_notification_badge.html",
        {"request": request, "notification_count": count},
    )


@router.post("/notifications/read-all")
async def mark_all_notifications_read(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Mark all notifications as read."""
    await mark_all_read(db, str(user.id))
    return JSONResponse(status_code=200, content={"status": "ok"})


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Mark a single notification as read."""
    await mark_read(db, notification_id, str(user.id))
    return JSONResponse(status_code=200, content={"status": "ok"})
