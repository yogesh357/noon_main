"""Tests for Xendit webhook handling."""

from decimal import Decimal

import pytest

from app.models.order import Order, OrderItem, OrderStatus, Payment, PaymentStatus
from app.services.payment import handle_xendit_webhook


@pytest.fixture
async def sample_order_with_payment(db):
    """Create an order with pending payment."""
    from uuid import uuid4

    from app.models.user import User

    user = User(
        id=uuid4(),
        email="pay@example.com",
        hashed_password="fake",
    )
    db.add(user)
    await db.flush()

    order = Order(
        user_id=str(user.id),
        order_number="PX-TEST-PAY001",
        status=OrderStatus.PENDING_PAYMENT,
        source="website",
        subtotal=Decimal("200000"),
        shipping_cost=Decimal("15000"),
        total=Decimal("215000"),
        items=[
            OrderItem(
                quantity=1,
                unit_price=Decimal("200000"),
                product_name_snapshot="Test Product",
                sku_snapshot="TST-PAY",
            )
        ],
    )
    db.add(order)
    await db.flush()

    payment = Payment(
        order_id=order.id,
        xendit_invoice_id="inv_test_123",
        amount=Decimal("215000"),
        status=PaymentStatus.PENDING,
    )
    db.add(payment)
    await db.flush()

    return order, payment


async def test_webhook_paid(db, sample_order_with_payment):
    """Test that PAID webhook updates order to ACCEPTED."""
    order, payment = sample_order_with_payment

    result = await handle_xendit_webhook(db, {
        "external_id": "PX-TEST-PAY001",
        "status": "PAID",
        "payment_method": "BANK_TRANSFER",
        "id": "xendit_pay_123",
    })

    assert result is True

    await db.refresh(order)
    await db.refresh(payment)

    assert order.status == OrderStatus.ACCEPTED
    assert payment.status == PaymentStatus.PAID
    assert payment.paid_at is not None
    assert payment.method is not None


async def test_webhook_expired(db, sample_order_with_payment):
    """Test that EXPIRED webhook cancels order."""
    order, payment = sample_order_with_payment

    result = await handle_xendit_webhook(db, {
        "external_id": "PX-TEST-PAY001",
        "status": "EXPIRED",
        "id": "xendit_pay_expired",
    })

    assert result is True

    await db.refresh(order)
    await db.refresh(payment)

    assert order.status == OrderStatus.CANCELLED
    assert payment.status == PaymentStatus.EXPIRED


async def test_webhook_unknown_order(db):
    """Test that webhook for unknown order returns False."""
    result = await handle_xendit_webhook(db, {
        "external_id": "PX-NONEXISTENT",
        "status": "PAID",
    })

    assert result is False


async def test_webhook_missing_fields(db):
    """Test that webhook with missing fields returns False."""
    result = await handle_xendit_webhook(db, {})
    assert result is False

    result = await handle_xendit_webhook(db, {"external_id": "PX-TEST"})
    assert result is False
