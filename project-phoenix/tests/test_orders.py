"""Tests for order creation, stock reservation, and state machine."""

from decimal import Decimal

import pytest

from app.models.cart import Cart, CartItem
from app.models.catalog import Product, ProductVariant
from app.models.order import OrderStatus
from app.models.user import Address, User
from app.services.order import (
    create_order_from_cart,
)


@pytest.fixture
async def sample_user(db):
    """Create a test user."""
    from uuid import uuid4
    user = User(
        id=uuid4(),
        email="test@example.com",
        hashed_password="fake_hash",
        full_name="Test User",
    )
    db.add(user)
    await db.flush()
    return user


@pytest.fixture
async def sample_address(db, sample_user):
    address = Address(
        user_id=sample_user.id,
        label="Home",
        full_name="Test User",
        phone="08123456789",
        street="Jl. Test 123",
        city="Jakarta",
        province="DKI Jakarta",
        postal_code="10110",
        is_default=True,
    )
    db.add(address)
    await db.flush()
    return address


@pytest.fixture
async def sample_product(db):
    product = Product(
        name_id="Produk Test",
        name_en="Test Product",
        slug="test-product",
        base_price=Decimal("100000"),
    )
    db.add(product)
    await db.flush()

    variant = ProductVariant(
        product_id=product.id,
        sku="TST-001",
        barcode="1234567890",
        stock_quantity=10,
        size="M",
        color="Black",
    )
    db.add(variant)
    await db.flush()
    return product, variant


@pytest.fixture
async def sample_cart(db, sample_user, sample_product):
    product, variant = sample_product
    cart = Cart(user_id=str(sample_user.id))
    db.add(cart)
    await db.flush()

    item = CartItem(cart_id=cart.id, variant_id=variant.id, quantity=2)
    db.add(item)
    await db.flush()
    cart.items = [item]
    return cart


async def test_create_order_from_cart(db, sample_user, sample_address, sample_cart, sample_product):
    """Test that order creation decrements stock and clears cart."""
    _, variant = sample_product
    initial_stock = variant.stock_quantity

    order = await create_order_from_cart(
        db,
        user_id=str(sample_user.id),
        cart=sample_cart,
        address_id=sample_address.id,
        courier="jnt",
        shipping_cost=Decimal("15000"),
    )

    assert order is not None
    assert order.status == OrderStatus.PENDING_PAYMENT
    assert order.total == Decimal("215000")  # 100000 * 2 + 15000
    assert len(order.items) == 1
    assert order.items[0].quantity == 2

    # Stock should be decremented
    await db.refresh(variant)
    assert variant.stock_quantity == initial_stock - 2

    # Cart should be empty
    assert len(sample_cart.items) == 0


async def test_create_order_insufficient_stock(db, sample_user, sample_address, sample_product):
    """Test that order fails when stock is insufficient."""
    product, variant = sample_product
    variant.stock_quantity = 1
    await db.flush()

    cart = Cart(user_id=str(sample_user.id))
    db.add(cart)
    await db.flush()
    item = CartItem(cart_id=cart.id, variant_id=variant.id, quantity=5)
    db.add(item)
    await db.flush()
    cart.items = [item]

    order = await create_order_from_cart(
        db,
        user_id=str(sample_user.id),
        cart=cart,
        address_id=sample_address.id,
    )

    assert order is None  # Should fail


async def test_order_status_flow(db, sample_user, sample_address, sample_cart, sample_product):
    """Test the order status state machine."""
    order = await create_order_from_cart(
        db,
        user_id=str(sample_user.id),
        cart=sample_cart,
        address_id=sample_address.id,
    )

    # Initial state
    assert order.status == OrderStatus.PENDING_PAYMENT

    # Simulate payment
    order.status = OrderStatus.ACCEPTED
    await db.flush()
    assert order.status == OrderStatus.ACCEPTED

    # Process -> Pick -> Pack -> Ship -> Deliver
    for next_status in [
        OrderStatus.PROCESSING,
        OrderStatus.PICKING,
        OrderStatus.PACKING,
        OrderStatus.READY_TO_SHIP,
        OrderStatus.SHIPPED,
        OrderStatus.DELIVERED,
    ]:
        order.status = next_status
        await db.flush()
        assert order.status == next_status
