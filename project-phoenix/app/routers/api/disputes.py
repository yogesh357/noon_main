"""Dispute API — customer raises disputes, admin reviews and resolves."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import current_active_user
from app.dependencies import get_db
from app.models.user import User, UserRole
from app.services.dispute import (
    add_evidence,
    can_raise_dispute,
    create_dispute,
    resolve_dispute,
)

router = APIRouter(prefix="/api/disputes", tags=["disputes"])


# --- Customer ---

@router.post("/raise/{order_id}")
async def raise_dispute(
    order_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Customer raises a dispute from order detail page."""
    form = await request.form()
    dispute_type = form.get("type", "refund")
    reason = form.get("reason", "other")
    description = form.get("description", "")

    if not description.strip():
        return JSONResponse(status_code=400, content={"error": "Description required"})

    dispute = await create_dispute(
        db, order_id, str(user.id), dispute_type, reason, description
    )

    if not dispute:
        check = await can_raise_dispute(db, order_id, str(user.id))
        return JSONResponse(status_code=400, content={"error": check["reason"]})

    # Handle file uploads if present
    files = await request.form()
    for key in files:
        if key.startswith("evidence_"):
            upload = files[key]
            if hasattr(upload, "filename") and upload.filename:
                # In production: upload to R2, get URL
                # For now: store filename as placeholder
                await add_evidence(
                    db, dispute.id, str(user.id),
                    file_url=f"/uploads/disputes/{dispute.id}/{upload.filename}",
                    description=f"Evidence: {upload.filename}",
                )

    return RedirectResponse(
        f"/dashboard/disputes/{dispute.id}", status_code=303
    )


# --- Admin ---

@router.post("/{dispute_id}/resolve")
async def admin_resolve_dispute(
    dispute_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Admin resolves a dispute."""
    if user.role != UserRole.ADMIN:
        return JSONResponse(status_code=403, content={"error": "Admin only"})

    form = await request.form()
    resolution_type = form.get("resolution_type", "")
    resolution_notes = form.get("resolution_notes", "")
    admin_notes = form.get("admin_notes", "")

    success = await resolve_dispute(
        db, dispute_id, resolution_type, resolution_notes, admin_notes
    )

    if not success:
        return JSONResponse(status_code=400, content={"error": "Resolution failed"})

    return RedirectResponse(
        f"/admin-panel/disputes/{dispute_id}", status_code=303
    )
