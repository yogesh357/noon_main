"""Marketplace sync orchestration — product push, stock sync, order import."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog import Product, ProductVariant
from app.models.marketplace import (
    MarketplaceCode,
    MarketplaceListing,
    MarketplaceOrder,
    SyncLog,
    SyncStatus,
)
from app.services.marketplace.base import BaseMarketplaceService
from app.services.marketplace.lazada import LazadaService
from app.services.marketplace.shopee import ShopeeService
from app.services.marketplace.tiktok import TikTokService
from app.services.marketplace.tokopedia import TokopediaService


def get_marketplace_service(marketplace: str) -> BaseMarketplaceService:
    """Factory — returns the correct service for a marketplace code."""
    services = {
        MarketplaceCode.SHOPEE: ShopeeService,
        MarketplaceCode.TOKOPEDIA: TokopediaService,
        MarketplaceCode.TIKTOK: TikTokService,
        MarketplaceCode.LAZADA: LazadaService,
    }
    try:
        code = MarketplaceCode(marketplace.lower())
        return services[code]()
    except (ValueError, KeyError) as e:
        raise ValueError(f"Unknown marketplace: {marketplace}") from e


async def sync_product_to_marketplace(
    db: AsyncSession,
    product_id: int,
    marketplace: str,
) -> bool:
    """Push a product to a specific marketplace."""
    from sqlalchemy.orm import selectinload

    product = await db.get(
        Product, product_id,
        options=[selectinload(Product.variants), selectinload(Product.images)],
    )
    if not product:
        return False

    service = get_marketplace_service(marketplace)

    # Check for existing listing
    listing_stmt = select(MarketplaceListing).where(
        MarketplaceListing.product_id == product_id,
        MarketplaceListing.marketplace == marketplace,
    )
    result = await db.execute(listing_stmt)
    listing = result.scalar_one_or_none()

    external_id = listing.external_product_id if listing else None

    # Build variant data
    variant_data = [
        {
            "sku": v.sku,
            "size": v.size,
            "color": v.color,
            "type": v.variant_type,
            "price": float(v.price_override or product.base_price),
            "stock": v.stock_quantity,
        }
        for v in product.variants
        if v.is_active
    ]

    image_urls = [img.image_url for img in product.images]

    try:
        auth_ok = await service.authenticate()
        if not auth_ok:
            _log_sync(db, marketplace, "push_product", "failed", {
                "product_id": product_id,
                "error": "Authentication failed",
            })
            await db.flush()
            return False

        new_external_id = await service.push_product(
            title=product.name_en,
            description=product.description_en or "",
            price=float(product.base_price),
            stock=sum(v.stock_quantity for v in product.variants),
            images=image_urls,
            variants=variant_data,
            external_id=external_id,
        )

        if not listing:
            listing = MarketplaceListing(
                product_id=product_id,
                marketplace=marketplace,
                external_product_id=new_external_id,
                sync_status=SyncStatus.SYNCED,
                last_synced_at=datetime.now(UTC),
            )
            db.add(listing)
        else:
            listing.external_product_id = new_external_id or listing.external_product_id
            listing.sync_status = SyncStatus.SYNCED
            listing.last_synced_at = datetime.now(UTC)

        _log_sync(db, marketplace, "push_product", "success", {
            "product_id": product_id,
            "external_id": new_external_id,
        })
        await db.flush()
        return True

    except Exception as e:
        if listing:
            listing.sync_status = SyncStatus.FAILED
        _log_sync(db, marketplace, "push_product", "failed", {
            "product_id": product_id,
            "error": str(e),
        })
        await db.flush()
        return False


async def sync_stock_to_all_marketplaces(
    db: AsyncSession,
    variant_id: int,
) -> int:
    """Push updated stock for a variant to all linked marketplaces. Returns success count."""
    variant = await db.get(ProductVariant, variant_id)
    if not variant:
        return 0

    listings_stmt = select(MarketplaceListing).where(
        MarketplaceListing.product_id == variant.product_id,
        MarketplaceListing.sync_status == SyncStatus.SYNCED,
        MarketplaceListing.external_product_id.isnot(None),
    )
    result = await db.execute(listings_stmt)
    listings = list(result.scalars().all())

    success_count = 0
    for listing in listings:
        try:
            service = get_marketplace_service(listing.marketplace)
            if not await service.authenticate():
                continue
            ok = await service.update_stock(
                listing.external_product_id,
                None,  # Variant-level external ID not tracked yet
                variant.stock_quantity,
            )
            if ok:
                success_count += 1
                listing.last_synced_at = datetime.now(UTC)
        except Exception as e:
            _log_sync(db, listing.marketplace, "stock_sync", "failed", {
                "variant_id": variant_id,
                "error": str(e),
            })

    await db.flush()
    return success_count


async def import_marketplace_orders(
    db: AsyncSession,
    marketplace: str,
) -> int:
    """Pull new orders from a marketplace and import them. Returns count."""
    service = get_marketplace_service(marketplace)

    try:
        if not await service.authenticate():
            _log_sync(db, marketplace, "pull_orders", "failed", {
                "error": "Authentication failed",
            })
            await db.flush()
            return 0
        orders = await service.pull_orders(since_minutes=5)
    except Exception as e:
        _log_sync(db, marketplace, "pull_orders", "failed", {"error": str(e)})
        await db.flush()
        return 0

    imported = 0
    for order_data in orders:
        # Check if already imported
        existing = await db.execute(
            select(MarketplaceOrder).where(
                MarketplaceOrder.external_order_id == order_data.external_order_id,
                MarketplaceOrder.marketplace == marketplace,
            )
        )
        if existing.scalar_one_or_none():
            continue

        # Create internal Order record from marketplace data
        from app.models.order import Order, OrderItem, OrderSource, OrderStatus
        from app.services.order import generate_order_number

        source_map = {
            "shopee": OrderSource.SHOPEE,
            "tokopedia": OrderSource.TOKOPEDIA,
            "tiktok": OrderSource.TIKTOK,
            "lazada": OrderSource.LAZADA,
        }

        internal_order = Order(
            order_number=generate_order_number(),
            status=OrderStatus.ACCEPTED,
            source=source_map.get(marketplace, OrderSource.SHOPEE),
            shipping_address=order_data.shipping_address,
            subtotal=order_data.total,
            shipping_cost=0,
            total=order_data.total,
            items=[
                OrderItem(
                    quantity=item.get("quantity", 1),
                    unit_price=item.get("price", 0),
                    product_name_snapshot=item.get("name", ""),
                    sku_snapshot=item.get("sku", ""),
                )
                for item in order_data.items
            ],
        )
        db.add(internal_order)
        await db.flush()

        # Create marketplace order record linked to internal order
        mp_order = MarketplaceOrder(
            external_order_id=order_data.external_order_id,
            marketplace=marketplace,
            raw_data=order_data.raw_data,
            linked_order_id=internal_order.id,
            status="imported",
        )
        db.add(mp_order)
        imported += 1

    if imported > 0:
        _log_sync(db, marketplace, "pull_orders", "success", {"imported": imported})

    await db.flush()
    return imported


async def get_sync_logs(
    db: AsyncSession,
    marketplace: str | None = None,
    limit: int = 50,
) -> list[SyncLog]:
    """Get recent sync logs."""
    stmt = select(SyncLog).order_by(SyncLog.created_at.desc()).limit(limit)
    if marketplace:
        stmt = stmt.where(SyncLog.marketplace == marketplace)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_product_listings(
    db: AsyncSession,
    product_id: int,
) -> list[MarketplaceListing]:
    """Get all marketplace listings for a product."""
    stmt = select(MarketplaceListing).where(
        MarketplaceListing.product_id == product_id
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


def _log_sync(
    db: AsyncSession,
    marketplace: str,
    action: str,
    status: str,
    details: dict | None = None,
) -> None:
    """Add a sync log entry (synchronous add, flushed by caller)."""
    log = SyncLog(
        marketplace=marketplace,
        action=action,
        status=status,
        details=details,
    )
    db.add(log)
