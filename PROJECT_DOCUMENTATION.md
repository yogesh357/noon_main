# Project Phoenix - Codebase Documentation

## Overview

Project Phoenix is a full-stack omnichannel e-commerce platform with an integrated ERP/WMS (Warehouse Management System). It powers a customer-facing storefront, an admin back-office, and warehouse operations — all connected to Indonesian marketplace channels (Shopee, Tokopedia, TikTok Shop, Lazada).

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend Framework | FastAPI (async) |
| Database | PostgreSQL 16 (production) / SQLite (development) |
| ORM | SQLAlchemy 2.0 (async) with asyncpg |
| Migrations | Alembic |
| Cache & Broker | Redis 7 |
| Task Queue | Celery (Redis backend) |
| Authentication | FastAPI-Users (JWT + session cookies) |
| Frontend | Jinja2 templates, HTMX, Alpine.js, Tailwind CSS |
| Admin Panel | SQLAdmin + custom admin views |
| Payment Gateway | Xendit |
| Shipping Rates | RajaOngkir API |
| Monitoring | Sentry |
| Containerization | Docker Compose |
| PDF Generation | WeasyPrint |
| Internationalization | Babel (Indonesian + English) |

---

## Project Structure

```
project-phoenix/
├── app/
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Settings via pydantic-settings
│   ├── database.py              # Async engine, session factory, DB compatibility helpers
│   ├── auth.py                  # FastAPI-Users setup (JWT + cookie backends)
│   ├── dependencies.py          # Shared dependency injection
│   ├── templating.py            # Jinja2 template engine setup
│   ├── celery_app.py            # Celery worker configuration
│   │
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── user.py              # User, Address
│   │   ├── catalog.py           # Product, ProductVariant, Category, ProductImage, Review
│   │   ├── cart.py              # Cart, CartItem
│   │   ├── order.py             # Order, OrderItem, Payment
│   │   ├── marketplace.py       # MarketplaceListing, MarketplaceOrder, SyncLog
│   │   ├── logistics.py         # Shipment, TrackingEvent
│   │   ├── warehouse.py         # PickingTask, PackingTask, HandoverBatch, HandoverItem
│   │   ├── notification.py      # Notification
│   │   ├── dispute.py           # Dispute, DisputeEvidence
│   │   └── wishlist.py          # Wishlist
│   │
│   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── user.py
│   │   ├── catalog.py
│   │   ├── cart.py
│   │   └── order.py
│   │
│   ├── routers/
│   │   ├── pages/               # Server-rendered HTML page routes
│   │   │   ├── home.py          # Homepage
│   │   │   ├── catalog.py       # Product listing, detail, search
│   │   │   ├── cart.py          # Cart page
│   │   │   ├── checkout.py      # Checkout flow + order success
│   │   │   ├── dashboard.py     # Customer dashboard (orders, profile, etc.)
│   │   │   ├── warehouse.py     # Warehouse picking/packing/handover UI
│   │   │   ├── admin_panel.py   # Admin dashboard and order management
│   │   │   ├── auth.py          # Login/register pages
│   │   │   └── static_pages.py  # FAQ, Terms, Disclaimer, Contact, About
│   │   │
│   │   ├── api/                 # JSON/HTMX API endpoints
│   │   │   ├── cart.py          # Add/update/remove cart items
│   │   │   ├── search.py        # Live search suggestions
│   │   │   ├── wishlist.py      # Toggle wishlist
│   │   │   ├── payments.py      # Xendit webhook handler
│   │   │   ├── dashboard.py     # Address CRUD, profile update, notifications
│   │   │   ├── warehouse.py     # Picking/packing/handover scan APIs
│   │   │   ├── disputes.py      # Raise and manage disputes
│   │   │   ├── stock.py         # Stock level queries
│   │   │   └── language.py      # Language toggle
│   │   │
│   │   └── htmx/               # HTMX fragment endpoints
│   │
│   ├── services/                # Business logic layer
│   │   ├── cart.py              # Cart operations, session-to-user merge
│   │   ├── catalog.py           # Product queries, filtering, full-text search
│   │   ├── order.py             # Order creation, stock reservation, status mgmt
│   │   ├── payment.py           # Xendit invoice creation + webhook processing
│   │   ├── warehouse.py         # Picking, packing (barcode scan), handover
│   │   ├── notification.py      # Bilingual notification management
│   │   ├── dispute.py           # Dispute lifecycle with SLA tracking
│   │   ├── admin.py             # Dashboard stats, bulk order processing
│   │   ├── marketplace/
│   │   │   ├── base.py          # Abstract marketplace interface
│   │   │   ├── sync.py          # Sync orchestration (product/stock/order)
│   │   │   ├── shopee.py        # Shopee API integration
│   │   │   ├── tokopedia.py     # Tokopedia API integration
│   │   │   ├── tiktok.py        # TikTok Shop API integration
│   │   │   └── lazada.py        # Lazada API integration
│   │   └── logistics/
│   │       ├── base.py          # Logistics interface
│   │       ├── rajaongkir.py    # RajaOngkir shipping rate + tracking API
│   │       └── shipment.py      # Shipment creation + tracking poll
│   │
│   ├── tasks/                   # Celery background tasks
│   │   ├── marketplace_sync.py  # Poll marketplace orders, sync stock
│   │   ├── stock_sync.py        # Stock level caching to Redis
│   │   ├── tracking.py          # Poll courier for tracking updates
│   │   ├── notifications.py     # Async notification dispatch
│   │   └── cleanup.py           # Release expired stock reservations
│   │
│   ├── middleware/
│   │   ├── security.py          # Security headers (CSP, HSTS, X-Frame-Options)
│   │   ├── i18n.py              # Language detection & locale middleware
│   │   └── rate_limit.py        # Rate limiting via slowapi
│   │
│   └── utils/
│       ├── i18n.py              # Internationalization helpers
│       ├── translations.py      # Translation utilities
│       └── pdf.py               # Shipping label PDF generation (100mm x 150mm)
│
├── templates/                   # Jinja2 HTML templates (59 files)
│   ├── base.html                # Main site layout
│   ├── base_checkout.html       # Checkout flow layout
│   ├── base_warehouse.html      # Warehouse operations layout
│   ├── pages/                   # Customer-facing pages
│   ├── dashboard/               # Customer dashboard pages
│   ├── admin/                   # Admin panel pages
│   ├── warehouse/               # Warehouse operation pages
│   └── partials/                # HTMX reusable fragments
│
├── static/
│   ├── css/input.css            # Tailwind CSS source
│   ├── js/
│   │   ├── htmx.min.js         # HTMX library
│   │   ├── alpine.min.js       # Alpine.js library
│   │   ├── barcode-scanner.js   # Barcode scanning for warehouse
│   │   └── audio-feedback.js    # Audio cues for scan success/failure
│   └── images/
│       └── placeholder.svg      # Placeholder product image
│
├── tests/
│   ├── conftest.py              # Test fixtures (async DB, test client, mock users)
│   ├── test_routes.py           # Page route smoke tests
│   ├── test_orders.py           # Order creation + status flow tests
│   ├── test_payments.py         # Xendit webhook handling tests
│   └── test_warehouse.py        # Picking/packing/handover workflow tests
│
├── alembic/                     # Database migration scripts
│   ├── env.py
│   └── script.py.mako
│
├── translations/                # Babel translation files (ID/EN)
├── seed_data.py                 # Sample data seeder
├── pyproject.toml               # Python dependencies & project config
├── package.json                 # Tailwind CSS build tooling
├── docker-compose.yml           # PostgreSQL + Redis containers
├── deploy.sh                    # Production deployment script
├── nginx.conf.example           # Nginx reverse proxy config
├── babel.cfg                    # Babel extraction config
├── Procfile                     # Process manager config (web + worker)
└── .env.example                 # Environment variable template
```

---

## Database Schema

### User & Authentication
- **User** - UUID-based, roles: `CUSTOMER`, `ADMIN`, `WAREHOUSE`. Fields: email, hashed password, full name, phone, avatar URL, language preference (`id`/`en`), email verification status.
- **Address** - User shipping addresses with name, phone, street, city, province, postal code, country, and default flag.

### Product Catalog
- **Category** - Hierarchical categories with parent-child self-referencing, slug, bilingual name/description.
- **Product** - Base product entity with bilingual name/description, brand, slug, base price, status (`ACTIVE`/`DRAFT`/`ARCHIVED`), full-text search vector.
- **ProductVariant** - SKU-level variants with color, size, type, individual pricing, stock count, weight, barcode. Stock managed at variant level.
- **ProductImage** - Multiple images per product with primary flag and sort order.
- **Review** - Customer product reviews with 1-5 rating and verification badge.

### Shopping & Orders
- **Cart / CartItem** - Session-based cart for anonymous users, user-linked for authenticated. Merges on login.
- **Order** - Status pipeline: `PENDING_PAYMENT` → `ACCEPTED` → `PROCESSING` → `PICKING` → `PACKING` → `READY_TO_SHIP` → `SHIPPED` → `DELIVERED` / `CANCELLED`. Tracks source (`WEBSITE`, `SHOPEE`, `TOKOPEDIA`, `TIKTOK`, `LAZADA`).
- **OrderItem** - Line items with product snapshot (name, price, image preserved even if product deleted).
- **Payment** - Xendit integration: invoice ID, payment URL, method (`VIRTUAL_ACCOUNT`, `EWALLET`, `QRIS`, `CREDIT_CARD`, `RETAIL_OUTLET`), status (`PENDING`, `PAID`, `FAILED`, `EXPIRED`, `REFUNDED`).

### Marketplace Integration
- **MarketplaceListing** - Maps internal products/variants to external marketplace item IDs.
- **MarketplaceOrder** - Imported marketplace orders with raw data snapshot and sync status.
- **SyncLog** - Audit trail for all sync operations (direction, status, error messages).

### Logistics & Shipping
- **Shipment** - Courier name, tracking number, status, estimated delivery date.
- **TrackingEvent** - Individual tracking status updates with timestamp, location, and raw courier data.

### Warehouse Operations
- **PickingTask** - Assigned to warehouse staff, tracks start/complete time.
- **PackingTask** - Tracks barcode scans in a JSON log array, validates all items scanned before completion.
- **HandoverBatch** - Groups packed orders for courier pickup.
- **HandoverItem** - Individual orders within a handover batch.

### Notifications & Disputes
- **Notification** - Bilingual (title/message in ID and EN), types: `ORDER_UPDATE`, `DELIVERY_UPDATE`, `DISPUTE_UPDATE`, `SYSTEM`.
- **Dispute** - Types: `REFUND` / `REPLACEMENT`. Tracks reason, evidence, admin response, SLA deadline.
- **DisputeEvidence** - File attachments for dispute claims.

### Wishlist
- **Wishlist** - User-product relationship with unique constraint.

---

## Implemented Features

### 1. Customer-Facing Storefront

**Product Browsing**
- Product listing with pagination
- Filters: category, brand, color, size, price range, in-stock only
- Sort: newest, price ascending/descending, popular, rating
- Full-text search with PostgreSQL TSVECTOR (SQLite fallback)
- Live search suggestions via HTMX
- Product detail pages with variant selection, image gallery, related products, reviews

**Shopping Cart**
- Anonymous session-based cart (auto-merges into user cart on login)
- Add/update/remove items with real-time stock validation
- HTMX-powered cart badge and summary updates

**Checkout & Payment**
- Address selection with saved addresses
- Shipping method selection
- Payment via Xendit gateway (virtual account, e-wallet, QRIS, credit card, retail outlet)
- Stock reserved for 30 minutes during checkout
- Order confirmation page with summary

**Customer Dashboard**
- Order history with status filtering
- Real-time shipment tracking with timeline
- Dispute management (raise, track, view resolution)
- Address book management (CRUD + set default)
- Payment history
- Wishlist management
- Profile editing
- Notification center with unread count badge

**Static Pages**
- FAQ, Terms & Conditions, Disclaimer, Contact Us, About, 404

**Bilingual Support**
- Indonesian (default) and English
- Language toggle persisted in session/cookie
- Bilingual database fields for products, categories, notifications
- Babel-powered translation extraction

### 2. Admin Panel

- Dashboard with order/revenue statistics
- Order queue with status and source filters
- Bulk order acceptance (move to PROCESSING)
- Individual order status updates
- Shipping label PDF generation (100mm x 150mm format)
- Marketplace order view (non-website orders)
- Dispute queue with SLA tracking

### 3. Warehouse Operations (WMS)

**Picking**
- Start picking task (assigns to warehouse staff)
- Order transitions to PICKING state
- Complete picking moves order to PACKING

**Packing**
- Barcode scanning workflow
- Scan validation against order items (by barcode or SKU)
- Real-time scan progress tracking (JSON scan log)
- Audio feedback for scan success/failure
- All items must be scanned to complete
- Return-to-picker option for incorrect/incomplete orders
- Order transitions to READY_TO_SHIP on completion

**Handover**
- Batch creation per courier/sender
- Scan order numbers to add to handover batch
- Order transitions to SHIPPED on handover scan
- Batch completion tracking

### 4. Marketplace Integration

**Supported Channels**
- Shopee
- Tokopedia
- TikTok Shop
- Lazada

**Capabilities (interface defined, implementations are placeholders)**
- Product sync: push product data to marketplace listings
- Stock sync: broadcast inventory updates across all connected channels
- Order import: pull new orders from marketplaces into internal system
- Order status sync: update marketplace order status from internal pipeline
- Sync audit logging

### 5. Logistics & Shipping

- RajaOngkir integration for shipping rate calculation
- Courier tracking number generation
- Automated tracking status polling via Celery
- Tracking event timeline with location data
- Auto-mark orders as DELIVERED when courier confirms delivery

### 6. Background Tasks (Celery)

- Marketplace order polling (scheduled)
- Stock level sync to Redis cache
- Courier tracking updates polling (scheduled)
- Expired stock reservation cleanup (releases stock if payment not received within 30 minutes)
- Async notification dispatch

### 7. Security & Infrastructure

- Security headers middleware (CSP, HSTS, X-Frame-Options)
- Rate limiting on sensitive endpoints (slowapi)
- Session management (7-day cookies, HTTPS-only in production)
- Dual auth: cookie-based for web, JWT bearer for API
- Sentry error monitoring
- Docker Compose for PostgreSQL + Redis
- Nginx reverse proxy configuration
- Gunicorn production deployment

---

## API Endpoints Summary

### Auth (FastAPI-Users)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/login` | Cookie-based login |
| POST | `/api/auth/bearer/login` | JWT bearer login |
| POST | `/api/auth/register` | User registration |
| POST | `/api/auth/forgot-password` | Request password reset |
| POST | `/api/auth/reset-password` | Confirm password reset |
| POST | `/api/auth/request-verify-email` | Request email verification |
| POST | `/api/auth/verify` | Verify email |
| GET | `/api/users/me` | Get current user |
| PATCH | `/api/users/me` | Update profile |

### Cart API
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/cart/add` | Add item to cart |
| PATCH | `/api/cart/item/{item_id}` | Update item quantity |
| DELETE | `/api/cart/item/{item_id}` | Remove item from cart |
| GET | `/api/cart/count` | Get cart item count |

### Search API
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/search/suggestions` | Live search suggestions |

### Wishlist API
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/wishlist/toggle/{product_id}` | Toggle wishlist item |

### Payment API
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/payments/xendit/webhook` | Xendit payment callback |

### Dashboard API
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/dashboard/addresses` | Create address |
| PATCH | `/api/dashboard/addresses/{id}` | Update address |
| DELETE | `/api/dashboard/addresses/{id}` | Delete address |
| POST | `/api/dashboard/addresses/{id}/default` | Set default address |
| POST | `/api/dashboard/profile` | Update profile |
| GET | `/api/dashboard/notifications/count` | Unread notification count |
| POST | `/api/dashboard/notifications/read-all` | Mark all read |
| POST | `/api/dashboard/notifications/{id}/read` | Mark single read |

### Warehouse API
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/warehouse/picking/start/{order_id}` | Start picking task |
| POST | `/api/warehouse/picking/complete/{task_id}` | Complete picking |
| POST | `/api/warehouse/packing/start/{order_id}` | Start packing task |
| POST | `/api/warehouse/packing/scan/{task_id}` | Scan product barcode |
| POST | `/api/warehouse/packing/complete/{task_id}` | Complete packing |
| POST | `/api/warehouse/packing/return/{task_id}` | Return to picker |
| POST | `/api/warehouse/handover/scan` | Scan order for handover |
| POST | `/api/warehouse/handover/complete/{batch_id}` | Complete handover batch |

### Language API
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/language` | Toggle language (ID/EN) |

### Page Routes
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Homepage |
| GET | `/products` | Product listing |
| GET | `/products/{slug}` | Product detail |
| GET | `/search` | Search results |
| GET | `/cart` | Cart page |
| GET | `/checkout` | Checkout form |
| POST | `/checkout` | Process checkout |
| GET | `/order/success/{order_number}` | Order confirmation |
| GET | `/dashboard` | Customer dashboard |
| GET | `/dashboard/orders` | Order history |
| GET | `/dashboard/orders/{order_number}` | Order detail |
| GET | `/dashboard/tracking` | Shipment tracking |
| GET | `/dashboard/disputes` | Dispute list |
| GET | `/dashboard/disputes/raise/{order_id}` | Raise dispute |
| GET | `/dashboard/disputes/{dispute_id}` | Dispute detail |
| GET | `/dashboard/addresses` | Address book |
| GET | `/dashboard/payments` | Payment history |
| GET | `/dashboard/wishlist` | Wishlist |
| GET | `/dashboard/profile` | Profile settings |
| GET | `/dashboard/notifications` | Notifications |
| GET | `/admin-panel` | Admin dashboard |
| GET | `/admin-panel/orders` | Admin order queue |
| POST | `/admin-panel/orders/bulk-process` | Bulk accept orders |
| GET | `/admin-panel/marketplace-orders` | Marketplace orders |
| GET | `/admin-panel/disputes` | Admin dispute queue |
| GET | `/faq` | FAQ page |
| GET | `/terms` | Terms & Conditions |
| GET | `/disclaimer` | Disclaimer |
| GET | `/contact` | Contact Us |
| GET | `/about` | About page |

---

## Order Flow

### Customer (Website) Order
```
Customer browses → Add to Cart → Checkout → Xendit Payment
    → Payment Success (webhook) → Order ACCEPTED
    → Admin bulk-processes → Order PROCESSING
    → Warehouse picks → Order PICKING
    → Warehouse packs (barcode scan) → Order PACKING → READY_TO_SHIP
    → Handover to courier → Order SHIPPED
    → Courier delivers → Order DELIVERED
```

### Marketplace Order
```
Celery polls marketplace API → Import order as MarketplaceOrder
    → Create internal Order (source: SHOPEE/TOKOPEDIA/etc.)
    → Same fulfillment pipeline as website orders
    → Status synced back to marketplace
```

### Payment Failure
```
Stock reserved for 30 minutes → Payment expires/fails
    → Celery cleanup task releases reserved stock
    → Order marked CANCELLED
```

---

## Tests

| Test File | Coverage |
|-----------|----------|
| `test_routes.py` | Page route smoke tests (homepage, products, static pages) |
| `test_orders.py` | Order creation from cart, status transitions |
| `test_payments.py` | Xendit webhook handling, payment status updates |
| `test_warehouse.py` | Full picking → packing → handover workflow |

Test infrastructure uses async pytest with in-memory SQLite, httpx AsyncClient, and mock user fixtures.

---

## Incomplete / Placeholder Implementations

| Area | Status |
|------|--------|
| Marketplace API integrations (Shopee, Tokopedia, TikTok, Lazada) | Interface defined, method bodies are placeholders |
| Redis stock caching | Marked as Phase 2 TODO |
| AI competitor analysis | Not started (future feature) |
| COGS calculator | Not started (future feature) |
| Social media post management | Not started (future feature) |
| Market data analysis | Not started (future feature) |

---

## Running the Project

```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Install Python dependencies
pip install -e .

# Install frontend dependencies and build CSS
npm install
npm run build:css

# Run database migrations
alembic upgrade head

# Seed sample data
python seed_data.py

# Start the application
uvicorn app.main:app --reload

# Start Celery worker (separate terminal)
celery -A app.celery_app worker --loglevel=info

# Start Celery beat scheduler (separate terminal)
celery -A app.celery_app beat --loglevel=info
```

Environment variables are configured via `.env` (see `.env.example` for the template).
