from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from io import BytesIO
from math import ceil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import func, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import current_active_user, optional_current_user
from app.config import settings
from app.dependencies import get_db
from app.models.catalog import Category, Product, ProductCategory, ProductImage, ProductVariant, Review
from app.models.dispute import Dispute, DisputeStatus, DisputeType
from app.models.logistics import Shipment, TrackingEvent
from app.models.marketplace import MarketplaceOrder
from app.models.order import Order, OrderItem, OrderSource, OrderStatus, Payment, PaymentStatus
from app.models.user import Address, User, UserRole
from app.models.warehouse import HandoverBatch, HandoverItem, PackingTask, PickingTask
from app.services.admin import bulk_process_orders, get_admin_dashboard_stats, get_admin_order_queue
from app.services.cart import (
    add_to_cart,
    get_cart_details,
    get_cart_item_count,
    get_or_create_cart,
    remove_cart_item,
    update_cart_item,
)
from app.services.catalog import (
    get_available_filters,
    get_category_tree,
    get_product_by_slug,
    get_products,
    get_user_wishlist_products,
    search_products,
    toggle_wishlist,
)
from app.services.dispute import add_evidence, create_dispute, get_admin_dispute_queue, get_dispute, get_user_disputes
from app.services.notification import get_unread_count, get_user_notifications, mark_all_read, mark_read
from app.services.order import create_order_from_cart, get_user_orders, update_order_status
from app.services.payment import create_xendit_invoice
from app.services.warehouse import (
    complete_handover,
    complete_packing,
    complete_picking,
    get_handover_orders,
    get_or_create_handover_batch,
    get_packing_progress,
    get_packing_queue,
    get_picking_queue,
    return_to_picker,
    scan_handover_order,
    scan_product,
    start_packing,
    start_picking,
)
from app.utils.pdf import generate_labels_pdf

router = APIRouter(tags=["react-frontend"])

# Reusable eager-load chain: order items → variant → product → images
_ORDER_ITEM_IMAGE_OPTS = [
    selectinload(Order.items)
    .selectinload(OrderItem.variant)
    .selectinload(ProductVariant.product)
    .selectinload(Product.images),
]


def _get_session_key(request: Request) -> str:
    session = request.session
    if "cart_session" not in session:
        import uuid

        session["cart_session"] = str(uuid.uuid4())
    return session["cart_session"]


def _decimal(value: Decimal | int | float | None) -> float:
    return float(value or 0)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _enum_name(value) -> str | None:
    if value is None:
        return None
    return getattr(value, "name", str(value)).upper()


def _dispute_status_name(value: str | None) -> str:
    mapping = {
        "open": "OPEN",
        "under_review": "IN_REVIEW",
        "resolved": "RESOLVED",
        "rejected": "REJECTED",
        "closed": "RESOLVED",
    }
    return mapping.get((value or "").lower(), (value or "").upper())


def _snapshot_address(payload: dict | None) -> dict | None:
    if not payload:
        return None
    return {
        "id": payload.get("id", 0),
        "name": payload.get("name") or payload.get("full_name") or "",
        "phone": payload.get("phone") or "",
        "street": payload.get("street") or "",
        "city": payload.get("city") or "",
        "province": payload.get("province") or "",
        "postal_code": payload.get("postal_code") or "",
        "country": payload.get("country") or "Indonesia",
        "is_default": bool(payload.get("is_default", False)),
    }


def _serialize_user(user: User) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name or "",
        "phone": user.phone,
        "avatar_url": user.avatar_url,
        "language": user.language_pref or "id",
        "role": _enum_name(user.role) or "CUSTOMER",
        "is_verified": user.is_verified,
        "is_active": user.is_active,
        "created_at": _iso(user.created_at),
    }


def _serialize_address(address: Address) -> dict:
    return {
        "id": address.id,
        "name": address.full_name,
        "label": address.label,
        "phone": address.phone,
        "street": address.street,
        "city": address.city,
        "province": address.province,
        "postal_code": address.postal_code,
        "country": "Indonesia",
        "is_default": address.is_default,
    }


def _serialize_category(category) -> dict:
    category_state = inspect(category)
    children_loaded = "children" not in category_state.unloaded
    return {
        "id": category.id,
        "name_id": category.name_id,
        "name_en": category.name_en,
        "slug": category.slug,
        "description_id": None,
        "description_en": None,
        "parent_id": category.parent_id,
        "children": [_serialize_category(child) for child in (category.children if children_loaded else [])],
    }


def _serialize_variant(variant: ProductVariant, product: Product) -> dict:
    return {
        "id": variant.id,
        "sku": variant.sku,
        "color": variant.color,
        "size": variant.size,
        "variant_type": variant.variant_type,
        "price": _decimal(variant.effective_price if hasattr(variant, "effective_price") else product.base_price),
        "stock_quantity": variant.stock_quantity,
        "weight": variant.weight_grams,
        "barcode": variant.barcode,
    }


def _serialize_product(product: Product) -> dict:
    primary_image = next((img for img in product.images if img.is_primary), None)
    primary_image = primary_image or (product.images[0] if product.images else None)
    product_state = inspect(product)
    categories_loaded = "categories" not in product_state.unloaded
    reviews_loaded = "reviews" not in product_state.unloaded
    categories = product.categories if categories_loaded else []
    reviews = product.reviews if reviews_loaded else []
    review_count = len(reviews)
    avg_rating = None
    if reviews:
        avg_rating = sum(review.rating for review in reviews) / review_count

    return {
        "id": product.id,
        "name_id": product.name_id,
        "name_en": product.name_en,
        "slug": product.slug,
        "description_id": product.description_id,
        "description_en": product.description_en,
        "brand": product.brand,
        "base_price": _decimal(product.base_price),
        "status": "ACTIVE" if product.is_active else "ARCHIVED",
        "category_id": categories[0].id if categories else None,
        "category": _serialize_category(categories[0]) if categories else None,
        "images": [
            {
                "id": image.id,
                "image_url": image.image_url,
                "alt_text": image.alt_text,
                "is_primary": image.is_primary,
                "sort_order": image.sort_order,
            }
            for image in product.images
        ],
        "variants": [_serialize_variant(variant, product) for variant in product.variants if variant.is_active],
        "avg_rating": avg_rating,
        "review_count": review_count,
        "primary_image_url": primary_image.image_url if primary_image else None,
    }


def _serialize_cart(cart_data: dict) -> dict:
    items = [
        {
            "id": item["id"],
            "product_id": None,
            "variant_id": item["variant_id"],
            "product_name": item["product_name"],
            "product_slug": item["product_slug"],
            "variant_label": " / ".join(filter(None, [item.get("size"), item.get("color"), item.get("variant_type")])),
            "image_url": item["image_url"],
            "price": _decimal(item["unit_price"]),
            "quantity": item["quantity"],
            "stock_quantity": item["stock_available"],
        }
        for item in cart_data["items"]
    ]
    return {
        "items": items,
        "total_items": cart_data["item_count"],
        "subtotal": _decimal(cart_data["subtotal"]),
    }


def _serialize_payment(payment: Payment | None) -> dict | None:
    if not payment:
        return None
    return {
        "id": payment.id,
        "xendit_invoice_id": payment.xendit_invoice_id,
        "payment_url": payment.xendit_invoice_url,
        "method": _enum_name(payment.method),
        "status": _enum_name(payment.status),
        "amount": _decimal(payment.amount),
        "paid_at": _iso(payment.paid_at),
    }


def _serialize_order_item(item) -> dict:
    # Resolve primary image from the eagerly-loaded variant → product → images chain
    image_url = None
    try:
        images = item.variant.product.images if item.variant and item.variant.product else []
        if images:
            primary = next((img for img in images if img.is_primary), images[0])
            image_url = primary.image_url
    except Exception:
        pass
    return {
        "id": item.id,
        "product_name": item.product_name_snapshot,
        "variant_label": item.sku_snapshot,
        "image_url": image_url,
        "price": _decimal(item.unit_price),
        "quantity": item.quantity,
        "subtotal": _decimal(item.unit_price * item.quantity),
    }


def _serialize_order(order: Order) -> dict:
    order_state = inspect(order)
    shipment_loaded = "shipment" not in order_state.unloaded
    shipment = order.shipment if shipment_loaded else None
    return {
        "id": order.id,
        "order_number": order.order_number,
        "status": _enum_name(order.status),
        "source": _enum_name(order.source),
        "items": [_serialize_order_item(item) for item in order.items],
        "payment": _serialize_payment(order.payment),
        "shipping_address": _snapshot_address(order.shipping_address),
        "courier": order.courier,
        "tracking_number": shipment.tracking_number if shipment else None,
        "subtotal": _decimal(order.subtotal),
        "shipping_cost": _decimal(order.shipping_cost),
        "total": _decimal(order.total),
        "notes": order.notes,
        "created_at": _iso(order.created_at),
        "updated_at": _iso(order.updated_at),
    }


def _serialize_tracking_event(event: TrackingEvent) -> dict:
    return {
        "id": event.id,
        "status": event.status,
        "description": event.description or "",
        "location": event.location,
        "timestamp": _iso(event.timestamp),
    }


def _serialize_shipment(shipment: Shipment) -> dict:
    return {
        "id": shipment.id,
        "courier": _enum_name(shipment.courier) or str(shipment.courier),
        "tracking_number": shipment.tracking_number or "",
        "status": _enum_name(shipment.status) or str(shipment.status),
        "estimated_delivery": _iso(shipment.estimated_delivery),
        "events": [_serialize_tracking_event(event) for event in shipment.tracking_events],
    }


def _serialize_dispute(dispute: Dispute) -> dict:
    order = getattr(dispute, "order", None)
    return {
        "id": dispute.id,
        "order_id": dispute.order_id,
        "order_number": order.order_number if order else "",
        "type": _enum_name(DisputeType(dispute.type)) if dispute.type else "REFUND",
        "status": _dispute_status_name(dispute.status),
        "reason": dispute.description or str(dispute.reason).replace("_", " ").title(),
        "admin_response": dispute.resolution_notes or dispute.admin_notes,
        "sla_deadline": _iso(dispute.sla_deadline),
        "evidence": [
            {
                "id": evidence.id,
                "file_url": evidence.file_url,
                "file_name": Path(evidence.file_url).name or f"evidence-{evidence.id}",
                "uploaded_at": _iso(evidence.uploaded_at),
            }
            for evidence in getattr(dispute, "evidence", [])
        ],
        "created_at": _iso(dispute.opened_at),
        "updated_at": _iso(dispute.resolved_at or dispute.responded_at or dispute.opened_at),
    }


def _serialize_picking_task(task: PickingTask, order: Order) -> dict:
    return {
        "id": task.id,
        "order_id": task.order_id,
        "order_number": order.order_number,
        "assigned_to": str(task.picker_user_id) if task.picker_user_id else None,
        "started_at": _iso(task.started_at),
        "completed_at": _iso(task.completed_at),
    }


def _serialize_packing_task(task: PackingTask, order: Order) -> dict:
    scan_log = [entry.get("barcode") or entry.get("sku") or "" for entry in (task.scan_log or [])]
    return {
        "id": task.id,
        "order_id": task.order_id,
        "order_number": order.order_number,
        "items": [_serialize_order_item(item) for item in order.items],
        "scan_log": scan_log,
        "started_at": _iso(task.started_at),
        "completed_at": _iso(task.completed_at),
    }


def _serialize_handover_batch(batch: HandoverBatch) -> dict:
    return {
        "id": batch.id,
        "courier": batch.courier or "",
        "sender_name": "Warehouse",
        "items": [
            {
                "order_number": item.order.order_number if getattr(item, "order", None) else "",
                "order_id": item.order_id,
            }
            for item in getattr(batch, "items", [])
        ],
        "is_completed": _enum_name(batch.status) == "COMPLETED",
        "created_at": _iso(batch.created_at),
    }


def _require_role(user: User, *roles: UserRole) -> None:
    if user.role not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


async def _get_order_for_user(db: AsyncSession, order_number: str, user: User) -> Order:
    stmt = (
        select(Order)
        .where(Order.order_number == order_number, Order.user_id == user.id)
        .options(
            *_ORDER_ITEM_IMAGE_OPTS,
            selectinload(Order.payment),
            selectinload(Order.shipment),
        )
    )
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


async def _get_order_for_admin(db: AsyncSession, order_id: int) -> Order:
    stmt = (
        select(Order)
        .where(Order.id == order_id)
        .options(
            *_ORDER_ITEM_IMAGE_OPTS,
            selectinload(Order.payment),
            selectinload(Order.shipment),
        )
    )
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/api/catalog/categories")
async def api_catalog_categories(db: AsyncSession = Depends(get_db)):
    categories = await get_category_tree(db)
    return [_serialize_category(category) for category in categories]


@router.get("/api/catalog/products")
async def api_catalog_products(
    db: AsyncSession = Depends(get_db),
    category: str | None = None,
    brand: str | None = None,
    color: str | None = None,
    size: str | None = None,
    price_min: Decimal | None = None,
    price_max: Decimal | None = None,
    in_stock: bool | None = None,
    sort: str = Query("newest", pattern="^(newest|price_asc|price_desc|popular|rating)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=48),
    q: str | None = None,
):
    from app.schemas.catalog import ProductFilter

    filters = ProductFilter(
        category_slug=category,
        brand=brand,
        color=color,
        size=size,
        price_min=price_min,
        price_max=price_max,
        in_stock=in_stock,
        sort=sort,
        page=page,
        per_page=per_page,
        search=q,
    )
    products, total = await get_products(db, filters)
    categories = await get_category_tree(db)
    available_filters = await get_available_filters(db, category_slug=category)

    product_payload = [_serialize_product(product) for product in products]
    price_values = [product["base_price"] for product in product_payload]

    return {
        "products": product_payload,
        "total": total,
        "page": page,
        "pages": max(1, ceil(total / per_page)) if per_page else 1,
        "per_page": per_page,
        "filters": {
            "brands": available_filters.get("brands", []),
            "colors": available_filters.get("colors", []),
            "sizes": available_filters.get("sizes", []),
            "price_min": min(price_values) if price_values else 0,
            "price_max": max(price_values) if price_values else 0,
        },
        "categories": [_serialize_category(item) for item in categories],
    }


@router.get("/api/catalog/products/{product_id}/reviews")
async def api_product_reviews(product_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Review).where(Review.product_id == product_id).order_by(Review.created_at.desc())
    result = await db.execute(stmt)
    reviews = list(result.scalars().all())
    return [
        {
            "id": review.id,
            "user_id": str(review.user_id),
            "user_name": "Verified Customer" if review.is_verified_purchase else "Customer",
            "rating": review.rating,
            "comment": review.comment,
            "is_verified": review.is_verified_purchase,
            "created_at": _iso(review.created_at),
        }
        for review in reviews
    ]


@router.get("/api/catalog/products/{slug}")
async def api_catalog_product(slug: str, db: AsyncSession = Depends(get_db)):
    product = await get_product_by_slug(db, slug)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return _serialize_product(product)


@router.get("/api/search/suggestions")
async def api_search_suggestions(q: str = Query("", min_length=0), db: AsyncSession = Depends(get_db)):
    if len(q.strip()) < 2:
        return {"suggestions": []}

    products = await search_products(db, q.strip(), limit=6)
    suggestions = [product.name_en for product in products]
    return {"suggestions": suggestions}


@router.get("/api/cart")
async def api_get_cart(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_current_user),
):
    user_id = str(user.id) if user else None
    session_key = _get_session_key(request) if not user else None
    cart = await get_or_create_cart(db, user_id=user_id, session_key=session_key)
    return _serialize_cart(await get_cart_details(db, cart))


@router.post("/api/cart/add")
async def api_cart_add(
    request: Request,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_current_user),
):
    user_id = str(user.id) if user else None
    session_key = _get_session_key(request) if not user else None
    cart = await get_or_create_cart(db, user_id=user_id, session_key=session_key)
    item = await add_to_cart(db, cart, int(body["variant_id"]), int(body.get("quantity", 1)))
    if not item:
        raise HTTPException(status_code=400, detail="Unable to add item to cart")
    cart_data = await get_cart_details(db, cart)
    matching = next((entry for entry in _serialize_cart(cart_data)["items"] if entry["id"] == item.id), None)
    return matching or {"id": item.id}


@router.patch("/api/cart/item/{item_id}")
async def api_cart_update(
    item_id: int,
    request: Request,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_current_user),
):
    user_id = str(user.id) if user else None
    session_key = _get_session_key(request) if not user else None
    cart = await get_or_create_cart(db, user_id=user_id, session_key=session_key)
    success = await update_cart_item(db, cart, item_id, int(body.get("quantity", 1)))
    if not success:
        raise HTTPException(status_code=400, detail="Unable to update cart item")
    cart_data = await get_cart_details(db, cart)
    matching = next((entry for entry in _serialize_cart(cart_data)["items"] if entry["id"] == item_id), None)
    return matching or {"id": item_id}


@router.delete("/api/cart/item/{item_id}")
async def api_cart_remove(
    item_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_current_user),
):
    user_id = str(user.id) if user else None
    session_key = _get_session_key(request) if not user else None
    cart = await get_or_create_cart(db, user_id=user_id, session_key=session_key)
    await remove_cart_item(db, cart, item_id)
    return {"success": True}


@router.get("/api/cart/count")
async def api_cart_count(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_current_user),
):
    user_id = str(user.id) if user else None
    session_key = _get_session_key(request) if not user else None
    cart = await get_or_create_cart(db, user_id=user_id, session_key=session_key)
    return {"count": get_cart_item_count(cart)}


@router.get("/api/cart/shipping-rates")
async def api_cart_shipping_rates(address_id: int, db: AsyncSession = Depends(get_db)):
    address = await db.get(Address, address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return [
        {"courier": "JNE", "service": "REG", "cost": 18000, "estimated_days": "2-3 days"},
        {"courier": "J&T", "service": "EZ", "cost": 15000, "estimated_days": "2-4 days"},
        {"courier": "SiCepat", "service": "BEST", "cost": 22000, "estimated_days": "1-2 days"},
    ]


@router.get("/api/wishlist")
async def api_get_wishlist(db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    products = await get_user_wishlist_products(db, str(user.id))
    return {
        "product_ids": [product.id for product in products],
        "products": [_serialize_product(product) for product in products],
    }


@router.post("/api/wishlist/toggle/{product_id}")
async def api_toggle_wishlist(product_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    return {"is_wishlisted": await toggle_wishlist(db, str(user.id), product_id)}


@router.get("/api/stock/{product_id}")
async def api_stock_status(product_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(ProductVariant).where(ProductVariant.product_id == product_id, ProductVariant.is_active.is_(True))
    result = await db.execute(stmt)
    variants = list(result.scalars().all())
    total_stock = sum(variant.stock_quantity for variant in variants)
    return {"in_stock": total_stock > 0, "total_stock": total_stock}



@router.get("/api/dashboard/overview")
async def api_dashboard_overview(db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    orders = await get_user_orders(db, str(user.id))
    open_count = sum(1 for order in orders if _enum_name(order.status) not in {"DELIVERED", "CANCELLED"})
    paid_total = sum(_decimal(order.payment.amount) for order in orders if order.payment and order.payment.status == PaymentStatus.PAID)
    return {
        "total_orders": len(orders),
        "open_orders": open_count,
        "total_spent": paid_total,
        "wishlist_count": len(await get_user_wishlist_products(db, str(user.id))),
    }


@router.get("/api/dashboard/addresses")
async def api_get_addresses(db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    stmt = select(Address).where(Address.user_id == user.id).order_by(Address.is_default.desc(), Address.id.asc())
    result = await db.execute(stmt)
    return [_serialize_address(address) for address in result.scalars().all()]


@router.post("/api/dashboard/addresses")
async def api_create_address(body: dict, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    if body.get("is_default"):
        result = await db.execute(select(Address).where(Address.user_id == user.id))
        for address in result.scalars().all():
            address.is_default = False

    address = Address(
        user_id=user.id,
        label=body.get("label") or "Home",
        full_name=body.get("name") or body.get("full_name") or "",
        phone=body.get("phone") or "",
        street=body.get("street") or "",
        city=body.get("city") or "",
        province=body.get("province") or "",
        postal_code=body.get("postal_code") or "",
        is_default=bool(body.get("is_default")),
    )
    db.add(address)
    await db.flush()
    return _serialize_address(address)


@router.patch("/api/dashboard/addresses/{address_id}")
async def api_update_address(
    address_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    address = await db.get(Address, address_id)
    if not address or str(address.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Address not found")

    if body.get("is_default"):
        result = await db.execute(select(Address).where(Address.user_id == user.id))
        for item in result.scalars().all():
            item.is_default = False

    address.label = body.get("label", address.label)
    address.full_name = body.get("name", body.get("full_name", address.full_name))
    address.phone = body.get("phone", address.phone)
    address.street = body.get("street", address.street)
    address.city = body.get("city", address.city)
    address.province = body.get("province", address.province)
    address.postal_code = body.get("postal_code", address.postal_code)
    if "is_default" in body:
        address.is_default = bool(body["is_default"])

    await db.flush()
    return _serialize_address(address)


@router.delete("/api/dashboard/addresses/{address_id}")
async def api_delete_address(address_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    address = await db.get(Address, address_id)
    if not address or str(address.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Address not found")
    await db.delete(address)
    await db.flush()
    return {"success": True}


@router.post("/api/dashboard/addresses/{address_id}/default")
async def api_default_address(address_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    result = await db.execute(select(Address).where(Address.user_id == user.id))
    selected_address = None
    for address in result.scalars().all():
        address.is_default = address.id == address_id
        if address.id == address_id:
            selected_address = address
    await db.flush()
    if not selected_address:
        raise HTTPException(status_code=404, detail="Address not found")
    return _serialize_address(selected_address)


@router.get("/api/dashboard/orders")
async def api_dashboard_orders(
    status: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    orders = await get_user_orders(db, str(user.id), status=status.lower() if status else None)
    total = len(orders)
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "items": [_serialize_order(order) for order in orders[start:end]],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, ceil(total / per_page)),
    }


@router.get("/api/dashboard/orders/{order_number}")
async def api_dashboard_order(order_number: str, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    order = await _get_order_for_user(db, order_number, user)
    return _serialize_order(order)


@router.get("/api/dashboard/tracking/{order_number}")
async def api_dashboard_tracking(order_number: str, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    stmt = (
        select(Order)
        .where(Order.order_number == order_number, Order.user_id == user.id)
        .options(selectinload(Order.shipment).selectinload(Shipment.tracking_events))
    )
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    if not order or not order.shipment:
        raise HTTPException(status_code=404, detail="Order not found or not shipped yet")
    return _serialize_shipment(order.shipment)


@router.get("/api/dashboard/disputes")
async def api_dashboard_disputes(db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    disputes = await get_user_disputes(db, str(user.id))
    return [_serialize_dispute(dispute) for dispute in disputes]


@router.get("/api/dashboard/disputes/{dispute_id}")
async def api_dashboard_dispute(dispute_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    dispute = await get_dispute(db, dispute_id)
    if not dispute or str(dispute.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Dispute not found")
    return _serialize_dispute(dispute)


@router.post("/api/dashboard/disputes/raise/{order_id}")
async def api_dashboard_raise_dispute(order_id: int, request: Request, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    form = await request.form()
    dispute_type = str(form.get("type") or "refund").lower()
    reason = str(form.get("reason") or "other").lower()
    description = str(form.get("description") or form.get("reason") or "Dispute submitted from React frontend")

    dispute = await create_dispute(
        db,
        order_id=order_id,
        user_id=str(user.id),
        dispute_type=dispute_type,
        reason=reason,
        description=description,
    )
    if not dispute:
        raise HTTPException(status_code=400, detail="Unable to create dispute")

    for uploaded in form.getlist("evidence"):
        filename = getattr(uploaded, "filename", "") or ""
        if not filename:
            continue
        await add_evidence(
            db,
            dispute_id=dispute.id,
            user_id=str(user.id),
            file_url=f"/uploads/disputes/{filename}",
            description=f"Uploaded evidence: {filename}",
        )

    refreshed = await get_dispute(db, dispute.id)
    return _serialize_dispute(refreshed or dispute)


@router.post("/api/dashboard/profile")
async def api_dashboard_profile(request: Request, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    form = await request.form()
    user.full_name = str(form.get("full_name") or user.full_name or "")
    user.phone = str(form.get("phone") or user.phone or "")
    await db.flush()
    return _serialize_user(user)


@router.get("/api/dashboard/payments")
async def api_dashboard_payments(db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    stmt = select(Payment).join(Order).where(Order.user_id == user.id).order_by(Payment.created_at.desc())
    result = await db.execute(stmt)
    return [_serialize_payment(payment) for payment in result.scalars().all() if payment]


@router.get("/api/dashboard/notifications/count")
async def api_notification_count(db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    return {"count": await get_unread_count(db, str(user.id))}


@router.get("/api/dashboard/notifications")
async def api_notifications(db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    notifications = await get_user_notifications(db, str(user.id), limit=100)
    return [
        {
            "id": notification.id,
            "type": _enum_name(notification.type),
            "title_id": notification.title_id,
            "title_en": notification.title_en,
            "message_id": notification.message_id,
            "message_en": notification.message_en,
            "is_read": notification.is_read,
            "created_at": _iso(notification.created_at),
        }
        for notification in notifications
    ]


@router.post("/api/dashboard/notifications/read-all")
async def api_notifications_read_all(db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    await mark_all_read(db, str(user.id))
    return {"success": True}


@router.post("/api/dashboard/notifications/{notification_id}/read")
async def api_notification_read(notification_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    await mark_read(db, notification_id, str(user.id))
    return {"success": True}


@router.post("/api/checkout")
async def api_checkout(request: Request, body: dict, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
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
    from sqlalchemy.orm import selectinload as _sl
    from sqlalchemy import select as _select
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
async def api_order_success(order_number: str, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    order = await _get_order_for_user(db, order_number, user)
    return _serialize_order(order)


@router.get("/api/admin-panel/stats")
async def api_admin_stats(db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
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
async def api_admin_order(order_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    _require_role(user, UserRole.ADMIN)
    order = await _get_order_for_admin(db, order_id)
    return _serialize_order(order)


@router.post("/api/admin-panel/orders/bulk-process")
async def api_admin_bulk_process(body: dict, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
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
async def api_admin_order_label(order_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
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
async def api_admin_disputes(status: str | None = None, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
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


@router.get("/api/warehouse")
async def api_warehouse_home(db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    _require_role(user, UserRole.WAREHOUSE, UserRole.ADMIN)
    picking = await get_picking_queue(db)
    packing = await get_packing_queue(db)
    handover = await get_handover_orders(db)
    return {
        "pending_picking": len(picking),
        "pending_packing": len(packing),
        "pending_handover": len(handover),
    }


@router.post("/api/warehouse/picking/start/{order_id}")
async def api_warehouse_start_picking(order_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    _require_role(user, UserRole.WAREHOUSE, UserRole.ADMIN)
    task = await start_picking(db, order_id, str(user.id))
    if not task:
        raise HTTPException(status_code=400, detail="Unable to start picking task")
    order = await db.get(Order, task.order_id)
    return _serialize_picking_task(task, order)


@router.post("/api/warehouse/picking/complete/{task_id}")
async def api_warehouse_complete_picking(task_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    _require_role(user, UserRole.WAREHOUSE, UserRole.ADMIN)
    task = await db.get(PickingTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Picking task not found")
    success = await complete_picking(db, task_id)
    if not success:
        raise HTTPException(status_code=400, detail="Unable to complete picking task")
    refreshed = await db.get(PickingTask, task_id)
    order = await db.get(Order, refreshed.order_id)
    return _serialize_picking_task(refreshed, order)


@router.post("/api/warehouse/packing/start/{order_id}")
async def api_warehouse_start_packing(order_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    _require_role(user, UserRole.WAREHOUSE, UserRole.ADMIN)
    task = await start_packing(db, order_id, str(user.id))
    if not task:
        raise HTTPException(status_code=400, detail="Unable to start packing task")
    order = await db.get(Order, task.order_id, options=[selectinload(Order.items)])
    return _serialize_packing_task(task, order)


@router.post("/api/warehouse/packing/scan/{task_id}")
async def api_warehouse_scan_packing(
    task_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    _require_role(user, UserRole.WAREHOUSE, UserRole.ADMIN)
    barcode = str(body.get("barcode") or "").strip()
    if not barcode:
        raise HTTPException(status_code=400, detail="barcode is required")
    result = await scan_product(db, task_id, barcode)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    progress = await get_packing_progress(db, task_id)
    return {"success": True, "message": result["message"], "progress": progress}


@router.post("/api/warehouse/packing/complete/{task_id}")
async def api_warehouse_complete_packing(task_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    _require_role(user, UserRole.WAREHOUSE, UserRole.ADMIN)
    task = await db.get(PackingTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Packing task not found")
    success = await complete_packing(db, task_id)
    if not success:
        raise HTTPException(status_code=400, detail="All items must be scanned before completing packing")
    refreshed = await db.get(PackingTask, task_id)
    order = await db.get(Order, refreshed.order_id, options=[selectinload(Order.items)])
    return _serialize_packing_task(refreshed, order)


@router.post("/api/warehouse/packing/return/{task_id}")
async def api_warehouse_return_packing(task_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    _require_role(user, UserRole.WAREHOUSE, UserRole.ADMIN)
    success = await return_to_picker(db, task_id)
    if not success:
        raise HTTPException(status_code=400, detail="Unable to return order to picker")
    return {"success": True}


@router.post("/api/warehouse/handover/scan")
async def api_warehouse_handover_scan(body: dict, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    _require_role(user, UserRole.WAREHOUSE, UserRole.ADMIN)
    batch_id = body.get("batch_id")
    order_number = str(body.get("order_number") or "").strip()
    if not order_number:
        raise HTTPException(status_code=400, detail="order_number is required")
    batch = await db.get(HandoverBatch, int(batch_id)) if batch_id else None
    if not batch:
        batch = await get_or_create_handover_batch(db, str(user.id))
    result = await scan_handover_order(db, batch.id, order_number)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    refreshed = await db.get(
        HandoverBatch,
        batch.id,
        options=[selectinload(HandoverBatch.items).selectinload(HandoverItem.order)],
    )
    return {
        "success": True,
        "batch_id": batch.id,
        "order_number": result["order_number"],
        "batch": _serialize_handover_batch(refreshed or batch),
    }


@router.post("/api/warehouse/handover/complete/{batch_id}")
async def api_warehouse_handover_complete(batch_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    _require_role(user, UserRole.WAREHOUSE, UserRole.ADMIN)
    success = await complete_handover(db, batch_id)
    if not success:
        raise HTTPException(status_code=400, detail="Unable to complete handover batch")
    batch = await db.get(
        HandoverBatch,
        batch_id,
        options=[selectinload(HandoverBatch.items).selectinload(HandoverItem.order)],
    )
    return _serialize_handover_batch(batch)


# ─── Admin: Product Management ───────────────────────────────────────────────

def _slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    import re
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text


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
