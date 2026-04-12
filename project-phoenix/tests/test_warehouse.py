"""Tests for warehouse barcode scanning logic."""

from decimal import Decimal

import pytest

from app.models.catalog import Product, ProductVariant
from app.models.order import Order, OrderItem, OrderStatus
from app.models.user import User
from app.services.warehouse import (
    complete_packing,
    get_packing_progress,
    scan_product,
    start_packing,
)


@pytest.fixture
async def warehouse_order(db):
    """Create an order in PACKING status with 2 items."""
    from uuid import uuid4

    user = User(id=uuid4(), email="wh@example.com", hashed_password="fake", role="warehouse")
    db.add(user)
    await db.flush()

    product = Product(
        name_id="Produk WH", name_en="WH Product",
        slug="wh-product", base_price=Decimal("50000"),
    )
    db.add(product)
    await db.flush()

    variant1 = ProductVariant(
        product_id=product.id, sku="WH-001", barcode="BC001",
        stock_quantity=10, color="Red",
    )
    variant2 = ProductVariant(
        product_id=product.id, sku="WH-002", barcode="BC002",
        stock_quantity=5, color="Blue",
    )
    db.add_all([variant1, variant2])
    await db.flush()

    order = Order(
        user_id=str(user.id),
        order_number="PX-TEST-WH001",
        status=OrderStatus.PACKING,
        source="website",
        subtotal=Decimal("150000"),
        shipping_cost=Decimal("0"),
        total=Decimal("150000"),
        items=[
            OrderItem(
                variant_id=variant1.id, quantity=2,
                unit_price=Decimal("50000"),
                product_name_snapshot="WH Product Red",
                sku_snapshot="WH-001",
            ),
            OrderItem(
                variant_id=variant2.id, quantity=1,
                unit_price=Decimal("50000"),
                product_name_snapshot="WH Product Blue",
                sku_snapshot="WH-002",
            ),
        ],
    )
    db.add(order)
    await db.flush()

    return order, user, variant1, variant2


async def test_scan_correct_barcode(db, warehouse_order):
    """Test scanning a correct barcode."""
    order, user, v1, v2 = warehouse_order

    task = await start_packing(db, order.id, str(user.id))
    assert task is not None

    # Scan first item by barcode
    result = await scan_product(db, task.id, "BC001")
    assert result["success"] is True
    assert result["item_name"] == "WH Product Red"


async def test_scan_wrong_barcode(db, warehouse_order):
    """Test scanning a barcode not in the order."""
    order, user, _, _ = warehouse_order

    task = await start_packing(db, order.id, str(user.id))

    result = await scan_product(db, task.id, "WRONG_BARCODE")
    assert result["success"] is False
    assert "not in this order" in result["message"]


async def test_scan_over_quantity(db, warehouse_order):
    """Test that scanning more than required quantity fails."""
    order, user, v1, v2 = warehouse_order

    task = await start_packing(db, order.id, str(user.id))

    # v2 has quantity=1, scan twice
    result1 = await scan_product(db, task.id, "BC002")
    assert result1["success"] is True

    result2 = await scan_product(db, task.id, "BC002")
    assert result2["success"] is False
    assert "Already scanned" in result2["message"]


async def test_packing_progress(db, warehouse_order):
    """Test progress tracking during packing."""
    order, user, v1, v2 = warehouse_order

    task = await start_packing(db, order.id, str(user.id))

    # Before any scans
    progress = await get_packing_progress(db, task.id)
    assert progress["total_items"] == 3  # 2 + 1
    assert progress["scanned_items"] == 0
    assert progress["complete"] is False

    # Scan all items
    await scan_product(db, task.id, "BC001")
    await scan_product(db, task.id, "BC001")
    await scan_product(db, task.id, "BC002")

    progress = await get_packing_progress(db, task.id)
    assert progress["scanned_items"] == 3
    assert progress["complete"] is True


async def test_complete_packing_blocks_incomplete(db, warehouse_order):
    """Test that packing cannot complete with missing scans."""
    order, user, _, _ = warehouse_order

    task = await start_packing(db, order.id, str(user.id))

    # Try to complete without scanning
    success = await complete_packing(db, task.id)
    assert success is False


async def test_complete_packing_success(db, warehouse_order):
    """Test successful packing completion."""
    order, user, _, _ = warehouse_order

    task = await start_packing(db, order.id, str(user.id))

    # Scan all items
    await scan_product(db, task.id, "BC001")
    await scan_product(db, task.id, "BC001")
    await scan_product(db, task.id, "BC002")

    success = await complete_packing(db, task.id)
    assert success is True

    await db.refresh(order)
    assert order.status == OrderStatus.READY_TO_SHIP
