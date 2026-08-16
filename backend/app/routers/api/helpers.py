from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from fastapi import HTTPException, Request, status
from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.catalog import Category, Product, ProductVariant, Review
from app.models.dispute import Dispute, DisputeStatus, DisputeType
from app.models.logistics import Shipment, TrackingEvent
from app.models.order import Order, OrderItem, Payment
from app.models.user import Address, User, UserRole
from app.models.warehouse import HandoverBatch, PackingTask, PickingTask

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


def _enum_name(value: Any) -> str | None:
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


def _serialize_category(category: Category) -> dict:
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
        "image_url": category.image_url,
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


def _serialize_order_item(item: OrderItem) -> dict:
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


def _slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text
