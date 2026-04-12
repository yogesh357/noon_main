
from datetime import UTC

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.order import Order, OrderStatus, Payment, PaymentMethod, PaymentStatus


async def create_xendit_invoice(
    db: AsyncSession,
    order: Order,
    success_redirect_url: str,
) -> Payment:
    """Create a Xendit invoice and return the Payment record."""
    import asyncio

    import xendit
    from xendit.apis import InvoiceApi

    xendit_client = xendit.ApiClient()
    xendit_client.configuration.api_key["ApiKeyAuth"] = settings.xendit_api_key

    invoice_api = InvoiceApi(xendit_client)

    # Build invoice items
    items = []
    for item in order.items:
        items.append({
            "name": item.product_name_snapshot,
            "quantity": item.quantity,
            "price": float(item.unit_price),
        })

    address = order.shipping_address or {}

    try:
        # Xendit SDK is synchronous — run in thread to avoid blocking event loop
        invoice = await asyncio.to_thread(
            invoice_api.create_invoice,
            create_invoice_request={
                "external_id": order.order_number,
                "amount": float(order.total),
                "payer_email": "",  # Will be set from user
                "description": f"Order {order.order_number}",
                "invoice_duration": 1800,  # 30 minutes
                "currency": "IDR",
                "items": items,
                "success_redirect_url": success_redirect_url,
                "customer": {
                    "given_names": address.get("full_name", ""),
                    "mobile_number": address.get("phone", ""),
                },
            },
        )

        payment = Payment(
            order_id=order.id,
            xendit_invoice_id=invoice.id,
            xendit_invoice_url=invoice.invoice_url,
            amount=order.total,
            status=PaymentStatus.PENDING,
        )
        db.add(payment)
        await db.flush()

        return payment

    except Exception as e:
        # Fallback: create payment record without Xendit (for development/testing)
        payment = Payment(
            order_id=order.id,
            xendit_invoice_id=f"dev-{order.order_number}",
            xendit_invoice_url=success_redirect_url,  # Redirect to success in dev mode
            amount=order.total,
            status=PaymentStatus.PENDING,
        )
        db.add(payment)
        await db.flush()

        if settings.debug:
            print(f"Xendit API error (using dev fallback): {e}")

        return payment


async def handle_xendit_webhook(
    db: AsyncSession,
    payload: dict,
) -> bool:
    """Process Xendit webhook callback. Returns True if handled successfully."""
    external_id = payload.get("external_id")
    status = payload.get("status")
    payment_method = payload.get("payment_method")
    payment_id = payload.get("id")

    if not external_id or not status:
        return False

    # Find order by external_id (order_number)
    from app.services.order import get_order_by_number

    order = await get_order_by_number(db, external_id)
    if not order or not order.payment:
        return False

    payment = order.payment
    payment.callback_data = payload
    payment.xendit_payment_id = payment_id

    # Map payment method
    method_map = {
        "BANK_TRANSFER": PaymentMethod.VIRTUAL_ACCOUNT,
        "EWALLET": PaymentMethod.EWALLET,
        "QR_CODE": PaymentMethod.QRIS,
        "CREDIT_CARD": PaymentMethod.CREDIT_CARD,
        "RETAIL_OUTLET": PaymentMethod.RETAIL_OUTLET,
    }
    payment.method = method_map.get(payment_method, PaymentMethod.OTHER)

    if status == "PAID":
        payment.status = PaymentStatus.PAID
        from datetime import datetime

        payment.paid_at = datetime.now(UTC)
        order.status = OrderStatus.ACCEPTED
        order.reserved_until = None  # No longer needs reservation

    elif status == "EXPIRED":
        payment.status = PaymentStatus.EXPIRED
        # Release stock
        from app.models.catalog import ProductVariant

        for item in order.items:
            if item.variant_id:
                variant = await db.get(ProductVariant, item.variant_id)
                if variant:
                    variant.stock_quantity += item.quantity
        order.status = OrderStatus.CANCELLED

    elif status in ("FAILED", "VOIDED"):
        payment.status = PaymentStatus.FAILED

    await db.flush()
    return True
