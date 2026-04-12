
from sqlalchemy import Select, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.catalog import (
    Category,
    Product,
    ProductVariant,
)
from app.models.wishlist import Wishlist
from app.schemas.catalog import ProductFilter


async def get_categories(
    db: AsyncSession,
    parent_id: int | None = None,
    active_only: bool = True,
) -> list[Category]:
    """Get categories, optionally filtered by parent."""
    stmt = select(Category).order_by(Category.sort_order, Category.name_en)
    if parent_id is not None:
        stmt = stmt.where(Category.parent_id == parent_id)
    elif parent_id is None:
        # Top-level categories
        stmt = stmt.where(Category.parent_id.is_(None))
    if active_only:
        stmt = stmt.where(Category.is_active.is_(True))
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_category_by_slug(db: AsyncSession, slug: str) -> Category | None:
    stmt = select(Category).where(Category.slug == slug)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_category_tree(db: AsyncSession) -> list[Category]:
    """Get full category tree with children loaded."""
    stmt = (
        select(Category)
        .where(Category.parent_id.is_(None), Category.is_active.is_(True))
        .options(selectinload(Category.children))
        .order_by(Category.sort_order)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


def _apply_product_filters(stmt: Select, filters: ProductFilter) -> Select:
    """Apply filter conditions to a product query."""
    stmt = stmt.where(Product.is_active.is_(True))

    if filters.category_id:
        stmt = stmt.join(Product.categories).where(Category.id == filters.category_id)
    elif filters.category_slug:
        stmt = stmt.join(Product.categories).where(Category.slug == filters.category_slug)

    if filters.brand:
        stmt = stmt.where(Product.brand == filters.brand)

    if filters.price_min is not None:
        stmt = stmt.where(Product.base_price >= filters.price_min)
    if filters.price_max is not None:
        stmt = stmt.where(Product.base_price <= filters.price_max)

    # Variant-level filters (color, size, in_stock)
    if filters.color or filters.size or filters.in_stock is not None:
        stmt = stmt.join(Product.variants)
        if filters.color:
            stmt = stmt.where(ProductVariant.color == filters.color)
        if filters.size:
            stmt = stmt.where(ProductVariant.size == filters.size)
        if filters.in_stock is True:
            stmt = stmt.where(ProductVariant.stock_quantity > 0)

    # Full-text search
    if filters.search:
        search_query = func.plainto_tsquery("simple", filters.search)
        stmt = stmt.where(Product.search_vector.op("@@")(search_query))

    return stmt


def _apply_product_sort(stmt: Select, sort: str) -> Select:
    """Apply sort order to a product query."""
    match sort:
        case "price_asc":
            stmt = stmt.order_by(Product.base_price.asc())
        case "price_desc":
            stmt = stmt.order_by(Product.base_price.desc())
        case "popular":
            # Sort by review count descending
            stmt = stmt.order_by(desc(Product.id))  # Placeholder until order count exists
        case "rating":
            stmt = stmt.order_by(desc(Product.id))  # Placeholder
        case _:  # newest
            stmt = stmt.order_by(Product.created_at.desc())
    return stmt


async def get_products(
    db: AsyncSession,
    filters: ProductFilter,
) -> tuple[list[Product], int]:
    """Get paginated, filtered, sorted products. Returns (products, total_count)."""
    # Count query
    count_stmt = select(func.count(func.distinct(Product.id))).select_from(Product)
    count_stmt = _apply_product_filters(count_stmt, filters)
    total = await db.execute(count_stmt)
    total_count = total.scalar_one()

    # Data query
    stmt = (
        select(Product)
        .distinct()
        .options(
            selectinload(Product.images),
            selectinload(Product.variants),
        )
    )
    stmt = _apply_product_filters(stmt, filters)
    stmt = _apply_product_sort(stmt, filters.sort)

    # Pagination
    offset = (filters.page - 1) * filters.per_page
    stmt = stmt.offset(offset).limit(filters.per_page)

    result = await db.execute(stmt)
    products = list(result.scalars().unique().all())

    return products, total_count


async def get_product_by_slug(db: AsyncSession, slug: str) -> Product | None:
    """Get full product detail by slug."""
    stmt = (
        select(Product)
        .where(Product.slug == slug, Product.is_active.is_(True))
        .options(
            selectinload(Product.images),
            selectinload(Product.variants),
            selectinload(Product.reviews),
            selectinload(Product.categories),
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_product_by_id(db: AsyncSession, product_id: int) -> Product | None:
    stmt = (
        select(Product)
        .where(Product.id == product_id)
        .options(
            selectinload(Product.images),
            selectinload(Product.variants),
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def search_products(
    db: AsyncSession,
    query: str,
    limit: int = 10,
) -> list[Product]:
    """Full-text search with ranking for live search suggestions."""
    search_query = func.plainto_tsquery("simple", query)
    rank = func.ts_rank(Product.search_vector, search_query)

    stmt = (
        select(Product)
        .where(Product.is_active.is_(True), Product.search_vector.op("@@")(search_query))
        .options(selectinload(Product.images))
        .order_by(rank.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_featured_products(db: AsyncSession, limit: int = 8) -> list[Product]:
    """Get featured/newest products for homepage."""
    stmt = (
        select(Product)
        .where(Product.is_active.is_(True))
        .options(selectinload(Product.images), selectinload(Product.variants))
        .order_by(Product.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_related_products(
    db: AsyncSession, product: Product, limit: int = 4
) -> list[Product]:
    """Get related products from same categories."""
    category_ids = [c.id for c in product.categories]
    if not category_ids:
        return []

    stmt = (
        select(Product)
        .join(Product.categories)
        .where(
            Product.is_active.is_(True),
            Product.id != product.id,
            Category.id.in_(category_ids),
        )
        .options(selectinload(Product.images))
        .distinct()
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().unique().all())


async def get_available_filters(db: AsyncSession, category_slug: str | None = None) -> dict:
    """Get available filter options (brands, colors, sizes) scoped to category."""
    # Brands
    brand_stmt = (
        select(Product.brand)
        .where(Product.is_active.is_(True), Product.brand.isnot(None))
        .distinct()
        .order_by(Product.brand)
    )
    if category_slug:
        brand_stmt = brand_stmt.join(Product.categories).where(
            Category.slug == category_slug
        )
    brands_result = await db.execute(brand_stmt)
    brands = [r[0] for r in brands_result.all()]

    # Colors from variants
    color_stmt = (
        select(ProductVariant.color)
        .join(Product)
        .where(Product.is_active.is_(True), ProductVariant.color.isnot(None))
        .distinct()
        .order_by(ProductVariant.color)
    )
    if category_slug:
        color_stmt = color_stmt.join(Product.categories).where(
            Category.slug == category_slug
        )
    colors_result = await db.execute(color_stmt)
    colors = [r[0] for r in colors_result.all()]

    # Sizes from variants
    size_stmt = (
        select(ProductVariant.size)
        .join(Product)
        .where(Product.is_active.is_(True), ProductVariant.size.isnot(None))
        .distinct()
        .order_by(ProductVariant.size)
    )
    if category_slug:
        size_stmt = size_stmt.join(Product.categories).where(
            Category.slug == category_slug
        )
    sizes_result = await db.execute(size_stmt)
    sizes = [r[0] for r in sizes_result.all()]

    return {"brands": brands, "colors": colors, "sizes": sizes}


# --- Wishlist ---
async def get_user_wishlist_product_ids(
    db: AsyncSession, user_id: str
) -> set[int]:
    """Get set of product IDs in user's wishlist."""
    stmt = select(Wishlist.product_id).where(Wishlist.user_id == user_id)
    result = await db.execute(stmt)
    return {r[0] for r in result.all()}


async def toggle_wishlist(
    db: AsyncSession, user_id: str, product_id: int
) -> bool:
    """Toggle product in wishlist. Returns True if added, False if removed."""
    stmt = select(Wishlist).where(
        Wishlist.user_id == user_id, Wishlist.product_id == product_id
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        await db.delete(existing)
        await db.flush()
        return False
    else:
        wishlist_item = Wishlist(user_id=user_id, product_id=product_id)
        db.add(wishlist_item)
        await db.flush()
        return True


async def get_user_wishlist_products(
    db: AsyncSession, user_id: str
) -> list[Product]:
    """Get full product details for user's wishlist."""
    stmt = (
        select(Product)
        .join(Wishlist, Wishlist.product_id == Product.id)
        .where(Wishlist.user_id == user_id)
        .options(selectinload(Product.images), selectinload(Product.variants))
        .order_by(Wishlist.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
