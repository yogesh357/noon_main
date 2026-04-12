from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import current_active_user, optional_current_user
from app.dependencies import get_db
from app.models.catalog import Product, ProductVariant, Review
from app.models.notification import Notification
from app.models.order import Order, Payment
from app.models.user import Address, User
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
    get_categories,
    get_category_tree,
    get_product_by_slug,
    get_products,
    get_user_wishlist_products,
    search_products,
    toggle_wishlist,
)
from app.services.notification import (
    get_unread_count,
    get_user_notifications,
    mark_all_read,
    mark_read,
)
from app.services.order import create_order_from_cart, get_order_by_number, get_user_orders
from app.services.payment import create_xendit_invoice

router = APIRouter(tags=["react-frontend"])


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
    categories = product.categories if categories_loaded else []
    avg_rating = None
    reviews_loaded = "reviews" not in product_state.unloaded
    reviews = product.reviews if reviews_loaded else []
    review_count = len(reviews)
    if reviews:
        avg_rating = sum(review.rating for review in product.reviews) / review_count

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


def _serialize_order(order: Order) -> dict:
    return {
        "id": order.id,
        "order_number": order.order_number,
        "status": _enum_name(order.status),
        "source": _enum_name(order.source),
        "items": [
            {
                "id": item.id,
                "product_name": item.product_name_snapshot,
                "variant_label": item.sku_snapshot,
                "image_url": None,
                "price": _decimal(item.unit_price),
                "quantity": item.quantity,
                "subtotal": _decimal(item.unit_price * item.quantity),
            }
            for item in order.items
        ],
        "payment": _serialize_payment(order.payment),
        "shipping_address": order.shipping_address,
        "courier": order.courier,
        "tracking_number": getattr(order.shipment, "tracking_number", None) if getattr(order, "shipment", None) else None,
        "subtotal": _decimal(order.subtotal),
        "shipping_cost": _decimal(order.shipping_cost),
        "total": _decimal(order.total),
        "notes": order.notes,
        "created_at": _iso(order.created_at),
        "updated_at": _iso(order.updated_at),
    }


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
async def api_search_suggestions(
    q: str = Query("", min_length=0),
    db: AsyncSession = Depends(get_db),
):
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
async def api_get_wishlist(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    products = await get_user_wishlist_products(db, str(user.id))
    return {
        "product_ids": [product.id for product in products],
        "products": [_serialize_product(product) for product in products],
    }


@router.post("/api/wishlist/toggle/{product_id}")
async def api_toggle_wishlist(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    return {"is_wishlisted": await toggle_wishlist(db, str(user.id), product_id)}


@router.get("/api/stock/{product_id}")
async def api_stock_status(product_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(ProductVariant).where(
        ProductVariant.product_id == product_id,
        ProductVariant.is_active.is_(True),
    )
    result = await db.execute(stmt)
    variants = list(result.scalars().all())
    total_stock = sum(variant.stock_quantity for variant in variants)
    return {"in_stock": total_stock > 0, "total_stock": total_stock}


@router.post("/api/language")
async def api_set_language(request: Request, body: dict):
    language = body.get("language", "id")
    if language not in {"id", "en"}:
        language = "id"
    request.session["language"] = language
    return {"language": language}


@router.get("/api/dashboard/addresses")
async def api_get_addresses(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    stmt = (
        select(Address)
        .where(Address.user_id == user.id)
        .order_by(Address.is_default.desc(), Address.id.asc())
    )
    result = await db.execute(stmt)
    return [_serialize_address(address) for address in result.scalars().all()]


@router.post("/api/dashboard/addresses")
async def api_create_address(
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
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
async def api_delete_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    address = await db.get(Address, address_id)
    if not address or str(address.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Address not found")
    await db.delete(address)
    await db.flush()
    return {"success": True}


@router.post("/api/dashboard/addresses/{address_id}/default")
async def api_default_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
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
async def api_dashboard_order(
    order_number: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    order = await get_order_by_number(db, order_number)
    if not order or str(order.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Order not found")
    return _serialize_order(order)


@router.get("/api/dashboard/notifications/count")
async def api_notification_count(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    return {"count": await get_unread_count(db, str(user.id))}


@router.get("/api/dashboard/notifications")
async def api_notifications(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
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
async def api_notifications_read_all(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    await mark_all_read(db, str(user.id))
    return {"success": True}


@router.post("/api/dashboard/notifications/{notification_id}/read")
async def api_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    await mark_read(db, notification_id, str(user.id))
    return {"success": True}


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

    base_url = str(request.base_url).rstrip("/")
    success_url = f"{base_url}/order/success/{order.order_number}"
    payment = await create_xendit_invoice(db, order, success_url)
    order.payment = payment
    return {"order": _serialize_order(order), "payment_url": payment.xendit_invoice_url}


@router.get("/api/order/success/{order_number}")
async def api_order_success(
    order_number: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    order = await get_order_by_number(db, order_number)
    if not order or str(order.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Order not found")
    return _serialize_order(order)
