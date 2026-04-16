
import asyncio
import logging
import traceback
from datetime import UTC

import xendit
from xendit.apis import InvoiceApi
from xendit.invoice.model.create_invoice_request import CreateInvoiceRequest
from xendit.invoice.model.customer_object import CustomerObject
from xendit.invoice.model.invoice_item import InvoiceItem

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.order import Order, OrderStatus, Payment, PaymentMethod, PaymentStatus

logger = logging.getLogger(__name__)


def _build_xendit_client() -> InvoiceApi:
    configuration = xendit.Configuration()
    configuration.api_key = settings.xendit_api_key
    client = xendit.ApiClient(configuration)
    return InvoiceApi(client)


async def create_xendit_invoice(
    db: AsyncSession,
    order: Order,
    success_redirect_url: str,
    payer_email: str = "",
) -> Payment:
    """Create a Xendit invoice and return the Payment record."""
    try:
        return await _do_create_xendit_invoice(db, order, success_redirect_url, payer_email)
    except Exception:
        # Print full traceback unconditionally so it always appears in terminal
        print("=" * 60)
        print("XENDIT ERROR — full traceback:")
        traceback.print_exc()
        print("=" * 60)
        raise


async def _do_create_xendit_invoice(
    db: AsyncSession,
    order: Order,
    success_redirect_url: str,
    payer_email: str = "",
) -> Payment:
    print(f"[Xendit] Starting invoice for order {order.order_number}")
    print(f"[Xendit] API key prefix: {settings.xendit_api_key[:12]}...")
    print(f"[Xendit] Payer email: {payer_email!r}")
    print(f"[Xendit] Order total: {order.total}")
    print(f"[Xendit] Items count: {len(order.items)}")
    print(f"[Xendit] shipping_address type: {type(order.shipping_address)}")
    print(f"[Xendit] shipping_address value: {order.shipping_address!r}")

    if not settings.xendit_api_key:
        raise RuntimeError("XENDIT_API_KEY is not set. Add it to your .env file.")

    address = order.shipping_address
    if isinstance(address, str):
        import json
        address = json.loads(address)
    if not isinstance(address, dict):
        address = {}

    print(f"[Xendit] Resolved address dict: {address}")

    customer = CustomerObject(
        given_names=address.get("full_name", ""),
        mobile_number=address.get("phone", ""),
        email=payer_email or None,
    )

    items = [
        InvoiceItem(
            name=item.product_name_snapshot,
            quantity=float(item.quantity),
            price=float(item.unit_price),
        )
        for item in order.items
    ]

    print(f"[Xendit] Built {len(items)} InvoiceItems")

    create_request = CreateInvoiceRequest(
        external_id=order.order_number,
        amount=float(order.total),
        payer_email=payer_email or None,
        description=f"Order {order.order_number}",
        invoice_duration=float(1800),
        currency="IDR",
        items=items,
        success_redirect_url=success_redirect_url,
        failure_redirect_url=success_redirect_url,
        customer=customer,
    )

    print("[Xendit] CreateInvoiceRequest built. Calling Xendit API...")

    invoice_api = _build_xendit_client()
    invoice = await asyncio.to_thread(invoice_api.create_invoice, create_request)

    print(f"[Xendit] SUCCESS — invoice_id={invoice.id}, url={invoice.invoice_url}")

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

    from app.services.order import get_order_by_number

    order = await get_order_by_number(db, external_id)
    if not order or not order.payment:
        return False

    payment = order.payment
    payment.callback_data = payload
    payment.xendit_payment_id = payment_id

    method_map = {
        "BANK_TRANSFER": PaymentMethod.VIRTUAL_ACCOUNT,
        "EWALLET": PaymentMethod.EWALLET,
        "QR_CODE": PaymentMethod.QRIS,
        "CREDIT_CARD": PaymentMethod.CREDIT_CARD,
        "RETAIL_OUTLET": PaymentMethod.RETAIL_OUTLET,
    }
    payment.method = method_map.get(payment_method, PaymentMethod.OTHER)

    if status == "PAID":
        from datetime import datetime

        payment.status = PaymentStatus.PAID
        payment.paid_at = datetime.now(UTC)
        order.status = OrderStatus.ACCEPTED
        order.reserved_until = None

    elif status == "EXPIRED":
        payment.status = PaymentStatus.EXPIRED
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
