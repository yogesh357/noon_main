from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select as _select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload as _sl

from app.auth import current_active_user
from app.config import settings
from app.dependencies import get_db
from app.models.order import Order
from app.models.user import User
from app.services.cart import get_or_create_cart
from app.services.order import create_order_from_cart
from app.services.payment import create_xendit_invoice
from app.routers.api.helpers import _serialize_order, _get_order_for_user

router = APIRouter(tags=["checkout"])


@router.post("/api/checkout")
async def api_checkout(
    request: Request,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    cart = await get_or_create_cart(db, user_id=str(user.id))
    order = await create_order_from_cart(
        db,
        user_id=str(user.id),
        cart=cart,
        address_id=int(body["address_id"]),
        courier=body.get("courier") or body.get("shipping_method"),
        shipping_cost=Decimal("0"),
        notes=body.get("notes"),
    )
    if not order:
        raise HTTPException(status_code=400, detail="Checkout failed")

    # Commit the order BEFORE calling Xendit so the order is persisted
    # even if the external payment API call fails.
    await db.commit()
    await db.refresh(order)

    # Re-load items after refresh (needed for serialisation and Xendit invoice)
    order = (
        await db.execute(
            _select(Order)
            .where(Order.id == order.id)
            .options(_sl(Order.items), _sl(Order.payment))
        )
    ).scalar_one()

    success_url = f"{settings.frontend_url}/order/success/{order.order_number}"
    try:
        payment = await create_xendit_invoice(db, order, success_url, payer_email=user.email)
    except Exception as e:
        # Order is already committed — return its number so the frontend can
        # show the success/pending page even when the payment gateway errors.
        raise HTTPException(status_code=502, detail=f"Payment gateway error: {e}")
    order.payment = payment
    return {"order": _serialize_order(order), "payment_url": payment.xendit_invoice_url}


@router.get("/api/order/success/{order_number}")
async def api_order_success(
    order_number: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    order = await _get_order_for_user(db, order_number, user)
    return _serialize_order(order)
