"""Seed the database with dummy data for development/demo."""

import asyncio
from decimal import Decimal
from uuid import uuid4

import app.models  # noqa: F401
from app.database import Base, async_session_factory, engine
# hash of Password1234
SEEDED_PASSWORD_HASH = "$argon2id$v=19$m=65536,t=3,p=4$kza5GX6CX1egedFtW11Yxw$qVjmj39ReD8venqcGkbeTbIPv2rWxzhphs5gHQldg60"


async def seed():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        from app.models.user import User, Address, UserRole
        from app.models.catalog import (
            Category, Product, ProductVariant, ProductImage, ProductCategory, Review,
        )
        from app.models.order import Order, OrderItem, OrderStatus, OrderSource, Payment, PaymentStatus

        # ============ USERS ============
        print("Creating users...")

        admin = User(
            id=uuid4(), email="admin@phoenix.id", hashed_password=SEEDED_PASSWORD_HASH,
            full_name="Admin Phoenix", phone="081200000001", role=UserRole.ADMIN,
            is_active=True, is_superuser=True, is_verified=True,
        )
        warehouse = User(
            id=uuid4(), email="gudang@phoenix.id", hashed_password=SEEDED_PASSWORD_HASH,
            full_name="Staff Gudang", phone="081200000002", role=UserRole.WAREHOUSE,
            is_active=True, is_superuser=False, is_verified=True,
        )
        customer1 = User(
            id=uuid4(), email="budi@example.com", hashed_password=SEEDED_PASSWORD_HASH,
            full_name="Budi Santoso", phone="081234567890", role=UserRole.CUSTOMER,
            is_active=True, is_superuser=False, is_verified=True,
        )
        customer2 = User(
            id=uuid4(), email="siti@example.com", hashed_password=SEEDED_PASSWORD_HASH,
            full_name="Siti Rahayu", phone="081298765432", role=UserRole.CUSTOMER,
            is_active=True, is_superuser=False, is_verified=True,
        )
        db.add_all([admin, warehouse, customer1, customer2])
        await db.flush()

        # Addresses
        addr1 = Address(
            user_id=customer1.id, label="Rumah", full_name="Budi Santoso",
            phone="081234567890", street="Jl. Sudirman No. 45, RT 03/RW 05",
            city="Jakarta Selatan", province="DKI Jakarta", postal_code="12190", is_default=True,
        )
        addr2 = Address(
            user_id=customer1.id, label="Kantor", full_name="Budi Santoso",
            phone="081234567890", street="Gedung Wisma 46, Lt. 12, Jl. Jend. Sudirman Kav. 1",
            city="Jakarta Pusat", province="DKI Jakarta", postal_code="10220", is_default=False,
        )
        addr3 = Address(
            user_id=customer2.id, label="Rumah", full_name="Siti Rahayu",
            phone="081298765432", street="Jl. Raya Darmo No. 78",
            city="Surabaya", province="Jawa Timur", postal_code="60241", is_default=True,
        )
        db.add_all([addr1, addr2, addr3])
        await db.flush()

        # ============ CATEGORIES ============
        print("Creating categories...")

        cat_kacamata = Category(name_id="Kacamata", name_en="Eyeglasses", slug="kacamata", sort_order=1)
        cat_sunglasses = Category(name_id="Kacamata Hitam", name_en="Sunglasses", slug="sunglasses", sort_order=2)
        cat_lensa = Category(name_id="Lensa Kontak", name_en="Contact Lenses", slug="lensa-kontak", sort_order=3)
        cat_aksesoris = Category(name_id="Aksesoris", name_en="Accessories", slug="aksesoris", sort_order=4)
        db.add_all([cat_kacamata, cat_sunglasses, cat_lensa, cat_aksesoris])
        await db.flush()

        # Sub-categories
        cat_pria = Category(name_id="Pria", name_en="Men", slug="pria", parent_id=cat_kacamata.id, sort_order=1)
        cat_wanita = Category(name_id="Wanita", name_en="Women", slug="wanita", parent_id=cat_kacamata.id, sort_order=2)
        db.add_all([cat_pria, cat_wanita])
        await db.flush()

        # ============ PRODUCTS ============
        print("Creating products...")

        products_data = [
            {
                "name_id": "Kacamata Klasik Hitam",
                "name_en": "Classic Black Frame",
                "slug": "classic-black-frame",
                "description_id": "Kacamata klasik dengan bingkai hitam elegan. Cocok untuk segala kesempatan. Bahan titanium ringan dan tahan lama.",
                "description_en": "Classic eyeglasses with elegant black frame. Perfect for any occasion. Lightweight and durable titanium material.",
                "brand": "Phoenix Optics",
                "base_price": Decimal("450000"),
                "categories": [cat_kacamata, cat_pria],
                "variants": [
                    {"sku": "CLB-S", "barcode": "8901001001", "size": "S", "color": "Hitam", "stock": 25},
                    {"sku": "CLB-M", "barcode": "8901001002", "size": "M", "color": "Hitam", "stock": 40},
                    {"sku": "CLB-L", "barcode": "8901001003", "size": "L", "color": "Hitam", "stock": 15},
                ],
                "images": [
                    "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=600",
                    "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=600",
                ],
            },
            {
                "name_id": "Kacamata Hitam Aviator",
                "name_en": "Aviator Sunglasses",
                "slug": "aviator-sunglasses",
                "description_id": "Kacamata hitam bergaya aviator dengan lensa UV400. Perlindungan maksimal dari sinar matahari.",
                "description_en": "Aviator-style sunglasses with UV400 lenses. Maximum protection from sunlight.",
                "brand": "Phoenix Shades",
                "base_price": Decimal("350000"),
                "categories": [cat_sunglasses, cat_pria],
                "variants": [
                    {"sku": "AVT-GLD", "barcode": "8901002001", "size": "One Size", "color": "Gold", "stock": 30},
                    {"sku": "AVT-SLV", "barcode": "8901002002", "size": "One Size", "color": "Silver", "stock": 20},
                    {"sku": "AVT-BLK", "barcode": "8901002003", "size": "One Size", "color": "Hitam", "stock": 35},
                ],
                "images": [
                    "https://images.unsplash.com/photo-1473496169904-658ba7c44d8a?w=600",
                    "https://images.unsplash.com/photo-1577803645773-f96470509666?w=600",
                ],
            },
            {
                "name_id": "Kacamata Wanita Cat Eye",
                "name_en": "Cat Eye Women's Frame",
                "slug": "cat-eye-womens-frame",
                "description_id": "Bingkai cat eye yang modis untuk wanita modern. Desain retro dengan sentuhan kontemporer.",
                "description_en": "Fashionable cat eye frame for modern women. Retro design with contemporary touch.",
                "brand": "Phoenix Optics",
                "base_price": Decimal("520000"),
                "categories": [cat_kacamata, cat_wanita],
                "variants": [
                    {"sku": "CAT-BLK", "barcode": "8901003001", "size": "S", "color": "Hitam", "stock": 18},
                    {"sku": "CAT-RED", "barcode": "8901003002", "size": "S", "color": "Merah", "stock": 12},
                    {"sku": "CAT-TRT", "barcode": "8901003003", "size": "M", "color": "Tortoise", "stock": 22},
                ],
                "images": [
                    "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=600",
                    "https://images.unsplash.com/photo-1608541737042-87a12275d313?w=600",
                ],
            },
            {
                "name_id": "Lensa Kontak Harian",
                "name_en": "Daily Contact Lenses",
                "slug": "daily-contact-lenses",
                "description_id": "Lensa kontak harian yang nyaman. Isi 30 pasang per kotak. Tersedia dalam berbagai ukuran.",
                "description_en": "Comfortable daily contact lenses. 30 pairs per box. Available in various sizes.",
                "brand": "ClearView",
                "base_price": Decimal("275000"),
                "categories": [cat_lensa],
                "variants": [
                    {"sku": "DCL-175", "barcode": "8901004001", "size": "-1.75", "color": "Clear", "stock": 50},
                    {"sku": "DCL-200", "barcode": "8901004002", "size": "-2.00", "color": "Clear", "stock": 45},
                    {"sku": "DCL-250", "barcode": "8901004003", "size": "-2.50", "color": "Clear", "stock": 38},
                    {"sku": "DCL-300", "barcode": "8901004004", "size": "-3.00", "color": "Clear", "stock": 42},
                ],
                "images": [
                    "https://images.unsplash.com/photo-1585314062340-f1a5a7c9328d?w=600",
                ],
            },
            {
                "name_id": "Kacamata Round Vintage",
                "name_en": "Vintage Round Frame",
                "slug": "vintage-round-frame",
                "description_id": "Kacamata bergaya vintage dengan bingkai bulat. Desain timeless yang cocok untuk pria dan wanita.",
                "description_en": "Vintage-style round frame glasses. Timeless design suitable for men and women.",
                "brand": "Phoenix Optics",
                "base_price": Decimal("380000"),
                "categories": [cat_kacamata, cat_pria, cat_wanita],
                "variants": [
                    {"sku": "RND-GLD", "barcode": "8901005001", "size": "M", "color": "Gold", "stock": 20},
                    {"sku": "RND-BLK", "barcode": "8901005002", "size": "M", "color": "Hitam", "stock": 28},
                    {"sku": "RND-SLV", "barcode": "8901005003", "size": "L", "color": "Silver", "stock": 15},
                ],
                "images": [
                    "https://images.unsplash.com/photo-1509281373149-e957c6296406?w=600",
                    "https://images.unsplash.com/photo-1556015048-4d3aa10df74c?w=600",
                ],
            },
            {
                "name_id": "Kacamata Hitam Sport",
                "name_en": "Sport Sunglasses",
                "slug": "sport-sunglasses",
                "description_id": "Kacamata hitam untuk aktivitas olahraga. Anti slip, tahan air, dan lensa polarized.",
                "description_en": "Sports sunglasses. Anti-slip, water resistant, and polarized lenses.",
                "brand": "Phoenix Active",
                "base_price": Decimal("425000"),
                "categories": [cat_sunglasses],
                "variants": [
                    {"sku": "SPT-BLK", "barcode": "8901006001", "size": "One Size", "color": "Hitam", "stock": 33},
                    {"sku": "SPT-BLU", "barcode": "8901006002", "size": "One Size", "color": "Biru", "stock": 25},
                    {"sku": "SPT-RED", "barcode": "8901006003", "size": "One Size", "color": "Merah", "stock": 19},
                ],
                "images": [
                    "https://images.unsplash.com/photo-1614715838608-dd527c46231d?w=600",
                ],
            },
            {
                "name_id": "Tempat Kacamata Kulit",
                "name_en": "Leather Glasses Case",
                "slug": "leather-glasses-case",
                "description_id": "Tempat kacamata dari kulit asli. Dilengkapi kain pembersih microfiber.",
                "description_en": "Genuine leather glasses case. Includes microfiber cleaning cloth.",
                "brand": "Phoenix",
                "base_price": Decimal("150000"),
                "categories": [cat_aksesoris],
                "variants": [
                    {"sku": "CSE-BRN", "barcode": "8901007001", "size": "Standard", "color": "Cokelat", "stock": 60},
                    {"sku": "CSE-BLK", "barcode": "8901007002", "size": "Standard", "color": "Hitam", "stock": 55},
                ],
                "images": [
                    "https://images.unsplash.com/photo-1591076482161-42ce6da69f67?w=600",
                ],
            },
            {
                "name_id": "Lensa Kontak Warna Cokelat",
                "name_en": "Brown Color Contact Lenses",
                "slug": "brown-color-contacts",
                "description_id": "Lensa kontak berwarna cokelat alami. Nyaman dipakai seharian. Isi 2 pasang.",
                "description_en": "Natural brown color contact lenses. Comfortable for all-day wear. 2 pairs included.",
                "brand": "ClearView",
                "base_price": Decimal("185000"),
                "categories": [cat_lensa],
                "variants": [
                    {"sku": "CCL-000", "barcode": "8901008001", "size": "Plano (0.00)", "color": "Cokelat", "stock": 40},
                    {"sku": "CCL-150", "barcode": "8901008002", "size": "-1.50", "color": "Cokelat", "stock": 30},
                    {"sku": "CCL-200", "barcode": "8901008003", "size": "-2.00", "color": "Cokelat", "stock": 28},
                ],
                "images": [
                    "https://images.unsplash.com/photo-1543349689-9a4d426bee8e?w=600",
                ],
            },
        ]

        created_products = []
        for p_data in products_data:
            product = Product(
                name_id=p_data["name_id"],
                name_en=p_data["name_en"],
                slug=p_data["slug"],
                description_id=p_data["description_id"],
                description_en=p_data["description_en"],
                brand=p_data["brand"],
                base_price=p_data["base_price"],
            )
            db.add(product)
            await db.flush()

            # Categories
            for cat in p_data["categories"]:
                db.add(ProductCategory(product_id=product.id, category_id=cat.id))

            # Variants
            for v in p_data["variants"]:
                db.add(ProductVariant(
                    product_id=product.id, sku=v["sku"], barcode=v["barcode"],
                    size=v["size"], color=v["color"], stock_quantity=v["stock"],
                ))

            # Images
            for idx, url in enumerate(p_data["images"]):
                db.add(ProductImage(
                    product_id=product.id, image_url=url,
                    sort_order=idx, is_primary=(idx == 0),
                ))

            created_products.append(product)
            await db.flush()

        # ============ REVIEWS ============
        print("Creating reviews...")

        review_data = [
            (created_products[0].id, customer1.id, 5, "Kacamata sangat nyaman dan ringan. Desain elegan!"),
            (created_products[0].id, customer2.id, 4, "Bagus, tapi pengiriman agak lama."),
            (created_products[1].id, customer1.id, 5, "Keren banget! Lensa UV-nya mantap."),
            (created_products[2].id, customer2.id, 5, "Suka banget desain cat eye-nya. Very chic!"),
            (created_products[3].id, customer1.id, 4, "Nyaman dipakai seharian. Recommended."),
            (created_products[4].id, customer2.id, 5, "Vintage look yang timeless. Love it!"),
            (created_products[5].id, customer1.id, 4, "Bagus untuk olahraga outdoor."),
            (created_products[6].id, customer2.id, 5, "Kulit asli, kualitas premium."),
        ]

        for prod_id, user_id, rating, comment in review_data:
            db.add(Review(
                product_id=prod_id, user_id=user_id,
                rating=rating, comment=comment, is_verified_purchase=True,
            ))
        await db.flush()

        # ============ SAMPLE ORDERS ============
        print("Creating sample orders...")

        order1 = Order(
            user_id=str(customer1.id), order_number="PX-20260408-A1B2C3",
            status=OrderStatus.DELIVERED, source=OrderSource.WEBSITE,
            shipping_address={"full_name": "Budi Santoso", "phone": "081234567890",
                              "street": "Jl. Sudirman No. 45", "city": "Jakarta Selatan",
                              "province": "DKI Jakarta", "postal_code": "12190"},
            courier="jnt", subtotal=Decimal("900000"), shipping_cost=Decimal("15000"),
            total=Decimal("915000"),
        )
        db.add(order1)
        await db.flush()

        db.add(OrderItem(
            order_id=order1.id, variant_id=None, quantity=2,
            unit_price=Decimal("450000"), product_name_snapshot="Kacamata Klasik Hitam",
            sku_snapshot="CLB-M",
        ))
        db.add(Payment(
            order_id=order1.id, xendit_invoice_id="inv_demo_001",
            amount=Decimal("915000"), status=PaymentStatus.PAID,
        ))

        order2 = Order(
            user_id=str(customer2.id), order_number="PX-20260408-D4E5F6",
            status=OrderStatus.PROCESSING, source=OrderSource.WEBSITE,
            shipping_address={"full_name": "Siti Rahayu", "phone": "081298765432",
                              "street": "Jl. Raya Darmo No. 78", "city": "Surabaya",
                              "province": "Jawa Timur", "postal_code": "60241"},
            courier="sicepat", subtotal=Decimal("520000"), shipping_cost=Decimal("18000"),
            total=Decimal("538000"),
        )
        db.add(order2)
        await db.flush()

        db.add(OrderItem(
            order_id=order2.id, variant_id=None, quantity=1,
            unit_price=Decimal("520000"), product_name_snapshot="Kacamata Wanita Cat Eye",
            sku_snapshot="CAT-TRT",
        ))
        db.add(Payment(
            order_id=order2.id, xendit_invoice_id="inv_demo_002",
            amount=Decimal("538000"), status=PaymentStatus.PAID,
        ))

        order3 = Order(
            user_id=str(customer1.id), order_number="PX-20260407-G7H8I9",
            status=OrderStatus.ACCEPTED, source=OrderSource.SHOPEE,
            shipping_address={"full_name": "Budi Santoso", "phone": "081234567890",
                              "street": "Jl. Sudirman No. 45", "city": "Jakarta Selatan",
                              "province": "DKI Jakarta", "postal_code": "12190"},
            courier="jne", subtotal=Decimal("350000"), shipping_cost=Decimal("12000"),
            total=Decimal("362000"),
        )
        db.add(order3)
        await db.flush()

        db.add(OrderItem(
            order_id=order3.id, variant_id=None, quantity=1,
            unit_price=Decimal("350000"), product_name_snapshot="Kacamata Hitam Aviator",
            sku_snapshot="AVT-GLD",
        ))

        await db.flush()

        # ============ NOTIFICATIONS ============
        print("Creating notifications...")

        from app.models.notification import Notification

        db.add(Notification(
            user_id=str(customer1.id), type="order_update",
            title_id="Pesanan Dikirim", title_en="Order Shipped",
            message_id="Pesanan PX-20260408-A1B2C3 telah dikirim melalui J&T Express.",
            message_en="Order PX-20260408-A1B2C3 has been shipped via J&T Express.",
        ))
        db.add(Notification(
            user_id=str(customer1.id), type="delivery_update",
            title_id="Pesanan Terkirim", title_en="Order Delivered",
            message_id="Pesanan PX-20260408-A1B2C3 telah sampai di tujuan.",
            message_en="Order PX-20260408-A1B2C3 has been delivered.",
            is_read=True,
        ))
        db.add(Notification(
            user_id=str(customer2.id), type="order_update",
            title_id="Pesanan Diproses", title_en="Order Processing",
            message_id="Pesanan PX-20260408-D4E5F6 sedang diproses di gudang.",
            message_en="Order PX-20260408-D4E5F6 is being processed in the warehouse.",
        ))

        await db.commit()
        print("\nSeed data created successfully!")
        print(f"  Users: 4 (admin, warehouse, 2 customers)")
        print(f"  Categories: 6 (4 main + 2 sub)")
        print(f"  Products: {len(created_products)} with variants & images")
        print(f"  Reviews: {len(review_data)}")
        print(f"  Orders: 3 (delivered, processing, accepted)")
        print(f"  Notifications: 3")
        print(f"\nLogin emails: admin@phoenix.id, budi@example.com, siti@example.com")
        print(f"(Note: passwords are dummy hashes — use /admin/ to manage or register new accounts)")


if __name__ == "__main__":
    asyncio.run(seed())
