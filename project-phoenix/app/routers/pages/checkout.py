from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import current_active_user
from app.dependencies import get_db
from app.models.user import Address, User
from app.services.cart import get_cart_details, get_or_create_cart
from app.services.order import create_order_from_cart, get_order_by_number
from app.services.payment import create_xendit_invoice
from app.templating import templates

router = APIRouter(tags=["checkout-pages"])


@router.get("/checkout")
async def checkout_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    cart = await get_or_create_cart(db, user_id=str(user.id))
    cart_data = await get_cart_details(db, cart)

    if not cart_data["items"]:
        return RedirectResponse("/cart", status_code=303)

    # Get user addresses
    addr_stmt = (
        select(Address)
        .where(Address.user_id == user.id)
        .order_by(Address.is_default.desc())
    )
    result = await db.execute(addr_stmt)
    addresses = list(result.scalars().all())

    language = getattr(request.state, "language", "id")

    return templates.TemplateResponse(
        "pages/checkout.html",
        {
            "request": request,
            "page_title": "Checkout",
            "cart": cart_data,
            "addresses": addresses,
            "language": language,
        },
    )


@router.post("/checkout")
async def process_checkout(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    form = await request.form()
    address_id = int(form.get("address_id", 0))
    courier = form.get("courier", "")
    shipping_cost_str = form.get("shipping_cost", "0")
    notes = form.get("notes", "")

    from decimal import Decimal

    shipping_cost = Decimal(shipping_cost_str) if shipping_cost_str else Decimal("0")

    cart = await get_or_create_cart(db, user_id=str(user.id))

    order = await create_order_from_cart(
        db,
        user_id=str(user.id),
        cart=cart,
        address_id=address_id,
        courier=courier,
        shipping_cost=shipping_cost,
        notes=notes,
    )

    if not order:
        return RedirectResponse("/cart?error=checkout_failed", status_code=303)

    # Create Xendit invoice
    base_url = str(request.base_url).rstrip("/")
    success_url = f"{base_url}/order/success/{order.order_number}"

    payment = await create_xendit_invoice(db, order, success_url)

    # Redirect to Xendit payment page
    if payment.xendit_invoice_url:
        return RedirectResponse(payment.xendit_invoice_url, status_code=303)

    return RedirectResponse(success_url, status_code=303)


@router.get("/order/success/{order_number}")
async def order_success(
    order_number: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    order = await get_order_by_number(db, order_number)
    if not order or str(order.user_id) != str(user.id):
        return RedirectResponse("/", status_code=303)

    language = getattr(request.state, "language", "id")

    return templates.TemplateResponse(
        "pages/order_success.html",
        {
            "request": request,
            "page_title": "Order Confirmed",
            "order": order,
            "language": language,
        },
    )
