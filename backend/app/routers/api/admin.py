from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from io import BytesIO
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import current_active_user
from app.dependencies import get_db
from app.models.catalog import Category, Product, ProductCategory, ProductImage, ProductVariant
from app.models.dispute import Dispute, DisputeStatus
from app.models.marketplace import MarketplaceOrder
from app.models.order import Order, OrderSource, OrderStatus, Payment, PaymentStatus
from app.models.user import User, UserRole
from app.services.admin import bulk_process_orders, get_admin_dashboard_stats, get_admin_order_queue
from app.services.dispute import get_admin_dispute_queue, get_dispute
from app.services.order import update_order_status
from app.utils.pdf import generate_labels_pdf
from app.routers.api.helpers import (
    _decimal,
    _enum_name,
    _iso,
    _serialize_order,
    _serialize_dispute,
    _serialize_product,
    _require_role,
    _get_order_for_admin,
    _slugify,
)

router = APIRouter(tags=["admin"])


@router.get("/api/admin-panel/stats")
async def api_admin_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    _require_role(user, UserRole.ADMIN)
    base_stats = await get_admin_dashboard_stats(db)
    disputes = await get_admin_dispute_queue(db)
    today = datetime.now(UTC).date()
    revenue_last_7_days = []
    for day_offset in range(6, -1, -1):
        target_day = today - timedelta(days=day_offset)
        revenue = (
            await db.execute(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(
                    func.date(Payment.paid_at) == target_day,
                    Payment.status == PaymentStatus.PAID,
                )
            )
        ).scalar_one()
        revenue_last_7_days.append({"date": target_day.isoformat(), "revenue": float(revenue or 0)})

    pending_orders = (
        await db.execute(
            select(func.count()).select_from(Order).where(Order.status.in_([OrderStatus.PENDING_PAYMENT, OrderStatus.ACCEPTED]))
        )
    ).scalar_one()

    return {
        "total_orders_today": base_stats["orders_today"],
        "revenue_today": base_stats["revenue_today"],
        "pending_orders": pending_orders,
        "active_disputes": len(disputes),
        "orders_by_status": {_enum_name(OrderStatus(status_key)): count for status_key, count in base_stats["status_counts"].items()},
        "revenue_last_7_days": revenue_last_7_days,
    }


@router.get("/api/admin-panel/orders")
async def api_admin_orders(
    status: str | None = None,
    source: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    _require_role(user, UserRole.ADMIN)
    try:
        status_enum = OrderStatus(status.lower()) if status else None
        source_enum = OrderSource(source.lower()) if source else None
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid filter") from exc
    orders, total = await get_admin_order_queue(db, status=status_enum, source=source_enum, page=page, per_page=per_page)
    return {
        "items": [_serialize_order(order) for order in orders],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, ceil(total / per_page)),
    }


@router.get("/api/admin-panel/orders/{order_id}")
async def api_admin_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    _require_role(user, UserRole.ADMIN)
    order = await _get_order_for_admin(db, order_id)
    return _serialize_order(order)


@router.post("/api/admin-panel/orders/bulk-process")
async def api_admin_bulk_process(
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    _require_role(user, UserRole.ADMIN)
    order_ids = [int(order_id) for order_id in body.get("order_ids", [])]
    orders = await bulk_process_orders(db, order_ids)
    return {"processed": len(orders), "items": [_serialize_order(order) for order in orders]}


@router.patch("/api/admin-panel/orders/{order_id}/status")
async def api_admin_update_order_status(
    order_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    _require_role(user, UserRole.ADMIN)
    try:
        new_status = OrderStatus(str(body.get("status", "")).lower())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid order status") from exc

    await update_order_status(db, order_id, new_status)
    order = await _get_order_for_admin(db, order_id)
    return _serialize_order(order)


@router.get("/api/admin-panel/orders/{order_id}/label")
async def api_admin_order_label(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    _require_role(user, UserRole.ADMIN)
    order = await _get_order_for_admin(db, order_id)
    try:
        pdf_bytes = generate_labels_pdf([order], tracking_numbers={order.id: order.order_number})
    except Exception:
        fallback = BytesIO()
        fallback.write(b"%PDF-1.4\n% Phoenix label placeholder\n")
        pdf_bytes = fallback.getvalue()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="label-{order.order_number}.pdf"'},
    )


@router.get("/api/admin-panel/marketplace-orders")
async def api_admin_marketplace_orders(
    channel: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    _require_role(user, UserRole.ADMIN)
    stmt = select(MarketplaceOrder).order_by(MarketplaceOrder.created_at.desc())
    count_stmt = select(func.count()).select_from(MarketplaceOrder)
    if channel:
        stmt = stmt.where(func.lower(MarketplaceOrder.marketplace) == channel.lower())
        count_stmt = count_stmt.where(func.lower(MarketplaceOrder.marketplace) == channel.lower())
    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(stmt.offset((page - 1) * per_page).limit(per_page))
    items = result.scalars().all()
    return {
        "items": [
            {
                "id": item.id,
                "order_id": item.linked_order_id or 0,
                "channel": str(item.marketplace).upper(),
                "external_order_id": item.external_order_id,
                "sync_status": item.status,
                "raw_data": item.raw_data or {},
                "created_at": _iso(item.created_at),
            }
            for item in items
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, ceil(total / per_page)),
    }


@router.get("/api/admin-panel/disputes")
async def api_admin_disputes(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    _require_role(user, UserRole.ADMIN)
    disputes = await get_admin_dispute_queue(db, status=status.lower() if status else None)
    return {
        "items": [_serialize_dispute(dispute) for dispute in disputes],
        "total": len(disputes),
        "page": 1,
        "per_page": len(disputes) or 1,
        "pages": 1,
    }


@router.patch("/api/admin-panel/disputes/{dispute_id}")
async def api_admin_dispute_update(
    dispute_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    _require_role(user, UserRole.ADMIN)
    dispute = await db.get(Dispute, dispute_id)
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
    response_text = str(body.get("admin_response") or "").strip()
    if not response_text:
        raise HTTPException(status_code=400, detail="admin_response is required")
    dispute.admin_notes = response_text
    dispute.responded_at = datetime.now(UTC)
    if dispute.status == DisputeStatus.OPEN:
        dispute.status = DisputeStatus.UNDER_REVIEW
    await db.flush()
    refreshed = await get_dispute(db, dispute_id)
    return _serialize_dispute(refreshed or dispute)


@router.get("/api/admin-panel/products")
async def api_admin_list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    _require_role(user, UserRole.ADMIN)
    stmt = (
        select(Product)
        .options(selectinload(Product.images), selectinload(Product.variants), selectinload(Product.categories))
        .order_by(Product.created_at.desc())
    )
    if search:
        stmt = stmt.where(
            Product.name_id.ilike(f"%{search}%") | Product.name_en.ilike(f"%{search}%")
        )
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    products = list((await db.execute(stmt)).scalars().unique().all())
    return {
        "items": [_serialize_product(p) for p in products],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, ceil(total / per_page)),
    }


@router.post("/api/admin-panel/products", status_code=status.HTTP_201_CREATED)
async def api_admin_create_product(
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Admin: create a product with variants and images."""
    _require_role(user, UserRole.ADMIN)

    # Validate required fields
    name_id = (body.get("name_id") or "").strip()
    name_en = (body.get("name_en") or "").strip()
    base_price = body.get("base_price")
    if not name_id or not name_en:
        raise HTTPException(status_code=400, detail="name_id and name_en are required")
    try:
        base_price = float(base_price)
        if base_price < 0:
            raise ValueError
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="base_price must be a positive number")

    # Pre-validate all variants before touching the DB
    variants_data = body.get("variants") or []
    if not variants_data:
        raise HTTPException(status_code=400, detail="At least one variant with a SKU is required")

    seen_skus: set[str] = set()
    seen_barcodes: set[str] = set()
    for v in variants_data:
        sku = (v.get("sku") or "").strip()
        if not sku:
            raise HTTPException(status_code=400, detail="Each variant must have a SKU")
        if sku in seen_skus:
            raise HTTPException(status_code=400, detail=f"Duplicate SKU '{sku}' in the same request")
        seen_skus.add(sku)
        if (await db.execute(select(ProductVariant).where(ProductVariant.sku == sku))).scalar_one_or_none():
            raise HTTPException(status_code=409, detail=f"SKU '{sku}' sudah digunakan / already exists")

        barcode = (v.get("barcode") or "").strip() or None
        if barcode:
            if barcode in seen_barcodes:
                raise HTTPException(status_code=400, detail=f"Duplicate barcode '{barcode}' in the same request")
            seen_barcodes.add(barcode)
            if (await db.execute(select(ProductVariant).where(ProductVariant.barcode == barcode))).scalar_one_or_none():
                raise HTTPException(status_code=409, detail=f"Barcode '{barcode}' sudah digunakan oleh produk lain / already used by another variant")

    # Auto-generate slug from English name; ensure uniqueness
    base_slug = _slugify(name_en)
    slug = base_slug
    counter = 1
    while (await db.execute(select(Product).where(Product.slug == slug))).scalar_one_or_none():
        slug = f"{base_slug}-{counter}"
        counter += 1

    product = Product(
        name_id=name_id,
        name_en=name_en,
        slug=slug,
        description_id=body.get("description_id") or None,
        description_en=body.get("description_en") or None,
        brand=body.get("brand") or None,
        base_price=base_price,
        is_active=bool(body.get("is_active", True)),
    )
    db.add(product)
    await db.flush()  # get product.id

    # Attach categories
    for cat_id in (body.get("category_ids") or []):
        cat = await db.get(Category, int(cat_id))
        if cat:
            db.add(ProductCategory(product_id=product.id, category_id=cat.id))

    # Create variants (already validated above)
    for v in variants_data:
        sku = (v.get("sku") or "").strip()
        barcode = (v.get("barcode") or "").strip() or None
        variant = ProductVariant(
            product_id=product.id,
            sku=sku,
            barcode=barcode,
            color=v.get("color") or None,
            size=v.get("size") or None,
            variant_type=v.get("variant_type") or None,
            price_override=float(v["price_override"]) if v.get("price_override") is not None else None,
            stock_quantity=int(v.get("stock_quantity") or 0),
            weight_grams=int(v["weight_grams"]) if v.get("weight_grams") else None,
            is_active=True,
        )
        db.add(variant)

    # Create images
    for idx, img in enumerate(body.get("images") or []):
        image_url = (img.get("image_url") or "").strip()
        if not image_url:
            continue
        db.add(ProductImage(
            product_id=product.id,
            image_url=image_url,
            alt_text=img.get("alt_text") or name_en,
            sort_order=idx,
            is_primary=idx == 0,
        ))

    await db.commit()

    # Reload with eager-loaded relationships via select (db.get uses identity map and skips selectinload)
    product_id = product.id
    result = await db.execute(
        select(Product)
        .where(Product.id == product_id)
        .options(
            selectinload(Product.images),
            selectinload(Product.variants),
            selectinload(Product.categories),
        )
    )
    return _serialize_product(result.scalar_one())


@router.patch("/api/admin-panel/products/{product_id}")
async def api_admin_update_product(
    product_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    _require_role(user, UserRole.ADMIN)
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if "name_id" in body and body["name_id"]:
        product.name_id = body["name_id"]
    if "name_en" in body and body["name_en"]:
        product.name_en = body["name_en"]
    if "description_id" in body:
        product.description_id = body["description_id"] or None
    if "description_en" in body:
        product.description_en = body["description_en"] or None
    if "brand" in body:
        product.brand = body["brand"] or None
    if "base_price" in body:
        product.base_price = float(body["base_price"])
    if "is_active" in body:
        product.is_active = bool(body["is_active"])

    await db.commit()
    result = await db.execute(
        select(Product)
        .where(Product.id == product_id)
        .options(
            selectinload(Product.images),
            selectinload(Product.variants),
            selectinload(Product.categories),
        )
    )
    return _serialize_product(result.scalar_one())


@router.delete("/api/admin-panel/products/{product_id}", status_code=status.HTTP_200_OK)
async def api_admin_delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    _require_role(user, UserRole.ADMIN)
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    await db.delete(product)
    await db.commit()
    return {"success": True, "id": product_id}
