# Business Requirements Document (BRD)
## Project Phoenix — AI-Powered E-commerce Platform with Omnichannel, Logistics, and Competitive Intelligence

**Document Version:** 2.0  
**Date:** 2026-04-08  
**Prepared by:** Madocks  
**Client:** Kevin (Ervin)  
**Status:** Draft — Pending Client Review

---

## 1. Objective

To build a modern, scalable e-commerce platform integrated with:

- Omnichannel system (inventory & order management)
- Payment gateway (Xendit)
- Multi-courier logistics tracking
- Social media marketing automation
- AI-powered competitor analysis and pricing engine

The platform will support English and Bahasa Indonesia (toggle-based multilingual UI) and provide a full customer dashboard experience.

**Budget:** ~USD 4,100  
**Primary Language:** Indonesian (default), English (toggle)

---

## 2. Scope

### 2.1 In Scope

| Area | Deliverables |
|------|-------------|
| E-commerce Website | Customer-facing store + admin panel |
| Customer Dashboard | Orders, shipment tracking, disputes, wishlist, profile, payments, notifications |
| Product Catalog | Filtering, sorting, search |
| Payment Integration | Xendit |
| Logistics & Tracking | Multi-courier integration (JNE, J&T, J&T Cargo, TIKI, SiCepat, Grab, Gojek) |
| Dispute Management | Raise, track, resolve disputes with SLA |
| Design | UI (style, colors, icons), mobile & desktop responsive, UX prototype, micro-animations |
| Front-End | HTML5, CSS framework, bilingual (ID/EN) support |
| Back-End | Python framework, code sanitation |
| Security | Authentication & authorization, data & API protection, input sanitization, validation, rate limiting |

### 2.2 Out of Scope (Phase 2 — Future)

- AI competitor analysis and market scraping
- COGS / pricing calculator tool
- Social media multi-platform post management
- Marketplace data analytics
- Telegram/social media data crawling
- Advanced recommendation engine
- AI chatbot automation
- Multi-vendor marketplace
- International logistics optimization

---

## 3. Stakeholders

| Role | Party |
|------|-------|
| Client / Business Owner | Kevin (Ervin) |
| Development Team | Madocks (Rahul) |
| End Users | Retail customers (Indonesian market) |
| Warehouse Staff | Pickers, Packers, Senders |
| Operations Team | Order fulfillment, logistics, delivery issues |
| Marketing Team | Campaigns, social media, competitor analysis (Phase 2) |

---

## 4. Business Context & Problem Statement

The client currently sells products through Shopee, Tokopedia, TikTok Shop, and Lazada. Key pain points:

1. **No owned storefront** — the business is entirely dependent on third-party marketplaces.
2. **Fragmented stock management** — inventory moves across multiple channels simultaneously; there is no single source of truth visible to the customer-facing website.
3. **Manual product updates** — updating product listings (title, description, variants, images) must be done separately on each marketplace platform.
4. **No unified order management** — orders from different channels are handled in silos.
5. **No direct customer relationship** — no wishlist data, no dispute management, no direct loyalty channel.

---

## 5. User Types

### 1. Customer
- Browse products
- Place orders
- Track shipments
- Manage profile
- Raise disputes
- Access dashboard
- Manage wishlist

### 2. Admin (Seller / Business Admin)
- Monitor operations
- Handle disputes
- Manage integrations
- View analytics
- Manage products, orders, marketplace sync

### 3. Warehouse Admin (Operations Team)
- Fulfill orders (picking, packing, handover)
- Manage logistics
- Resolve delivery issues

---

## 6. Multilingual Requirement

- Language toggle: English ↔ Bahasa Indonesia
- Applies to: Website UI, Customer dashboard, Emails/notifications
- Use i18n-based architecture
- Default language: Indonesian (Bahasa Indonesia)

---

## 7. Website Sitemap

```
HOME
├── Product List
│   └── Product Detail
│       ├── Product Description
│       ├── Variant, Size, Color, Type
│       └── Reviews / Product Rating
├── Static Pages
│   ├── About Us
│   ├── Terms & Conditions
│   ├── Disclaimer
│   ├── Contact Us
│   └── FAQ
└── Other Functions
    └── Payment (via Xendit)
```

Additional pages:
- Search Results
- Cart
- Checkout
- Order Success
- Order Summary
- User Dashboard (orders, tracking, profile, wishlist, disputes)
- Dispute / Return Request

---

## 8. Functional Requirements

### 8.1 E-commerce Core

| ID | Requirement |
|----|-------------|
| FR-01 | Homepage |
| FR-02 | Product listing with category navigation |
| FR-03 | Filter products by: price range, eye color, category, brand, attributes (size, color), availability |
| FR-04 | Sort products (e.g., price low-high, newest) |
| FR-05 | Product detail page showing: description, variants (size, color, type), images, reviews/ratings |
| FR-06 | Search functionality with a dedicated search results page |
| FR-07 | Stock levels must sync in near real-time (every few seconds) via inventory management system |
| FR-08 | Wishlist functionality across platform — persistent wishlist linked to user account |

### 8.2 Cart & Checkout

| ID | Requirement |
|----|-------------|
| FR-09 | Add to cart, update quantity, remove items |
| FR-10 | Cart page showing item summary and total |
| FR-11 | Checkout flow: shipping address → delivery method → payment |
| FR-12 | Payment processed via **Xendit** payment gateway |
| FR-13 | Order success page and order summary page post-payment |

### 8.3 Customer Dashboard (Core Module)

Objective: Provide a central control panel for all customer activities.

**Dashboard Structure:**
```
Dashboard
 ├── Overview
 ├── Orders
 ├── Track Shipment
 ├── Disputes
 ├── Addresses
 ├── Payments
 ├── Wishlist
 ├── Profile
 └── Notifications
```

#### Orders
| ID | Requirement |
|----|-------------|
| FR-14 | View all orders |
| FR-15 | Order status tracking |
| FR-16 | Invoice download |
| FR-17 | Order details |

#### Shipment Tracking
| ID | Requirement |
|----|-------------|
| FR-18 | Real-time tracking via courier APIs |
| FR-19 | Courier details (JNE, J&T, etc.) |
| FR-20 | AWB tracking |
| FR-21 | Delivery timeline |
| FR-22 | Tracking number auto-updated when assigned by system |

#### Disputes
| ID | Requirement |
|----|-------------|
| FR-23 | Raise dispute |
| FR-24 | Upload evidence |
| FR-25 | Track dispute status |
| FR-26 | View resolution |

#### Profile Management
| ID | Requirement |
|----|-------------|
| FR-27 | Update profile |
| FR-28 | Change password |
| FR-29 | Contact details |

#### Address Management
| ID | Requirement |
|----|-------------|
| FR-30 | Add/edit/delete addresses |
| FR-31 | Default shipping address |

#### Payments
| ID | Requirement |
|----|-------------|
| FR-32 | Payment history |
| FR-33 | Retry failed payments |

#### Notifications
| ID | Requirement |
|----|-------------|
| FR-34 | Order updates |
| FR-35 | Delivery updates |
| FR-36 | Dispute updates |

#### Wishlist (Core Feature)
| ID | Requirement |
|----|-------------|
| FR-37 | Add/remove products to wishlist |
| FR-38 | View saved products |
| FR-39 | Move items to cart |
| FR-40 | Mark out-of-stock items |
| FR-41 | Heart icon on product cards and product detail page |
| FR-42 | Dedicated Wishlist page in dashboard |

**Wishlist Flow:** Browse Product → Click ❤ → Saved in Wishlist → Move to Cart → Checkout

**Wishlist Business Value:**
- Increases conversion (users return)
- Captures purchase intent data
- Enables remarketing campaigns
- Useful for retargeting

**Wishlist Database:**
```
wishlist
- id
- user_id
- product_id
- created_at
```

### 8.4 Payment Integration (Xendit)

| ID | Requirement |
|----|-------------|
| FR-43 | Payment link/API integration |
| FR-44 | Webhook-based confirmation |
| FR-45 | Multi-payment methods |
| FR-46 | Status handling (success/failed) |

### 8.5 Logistics & Delivery Tracking

**Supported Couriers:** JNE, J&T, J&T Cargo, TIKI, SiCepat, Grab, Gojek

| ID | Requirement |
|----|-------------|
| FR-47 | Tracking API integration per courier |
| FR-48 | Status normalization across couriers |
| FR-49 | Shipment logs |
| FR-50 | Customer tracking UI |
| FR-51 | Auto-generate tracking number via expedition/courier API |

### 8.6 Dispute Management System

| ID | Requirement |
|----|-------------|
| FR-52 | Customer can raise disputes from dashboard |
| FR-53 | Upload evidence (photos, description) |
| FR-54 | Admin review panel with notification |
| FR-55 | Resolution options: Refund, Replacement, Reject |
| FR-56 | Dispute SOP displayed to customers before submission (to deter frivolous returns) |
| FR-57 | Separate SOP flows for website orders vs. marketplace orders (SOPs to be provided by client) |

**SLA:**
- Dispute window: 48–72 hrs after delivery
- Admin response: 24 hrs

### 8.7 Omni-Channel Product Sync

| ID | Requirement |
|----|-------------|
| FR-58 | Admin can update product details (title, description, variants, images, price) in backend |
| FR-59 | One-click publish syncs product changes to all connected marketplace listings simultaneously (Shopee, Tokopedia, TikTok Shop, Lazada) |
| FR-60 | Product attributes synced: Size, Variant, Color, Type |
| FR-61 | Stock levels sync to website in near real-time (target: every few seconds) |

---

## 9. SOP Requirements

### 9.1 Customer Order Flow

```
Customer → Product List → Product Detail → Add to Cart → Cart → Checkout → Payment → Order Success → Order Summary
```

### 9.2 Website Orders SOP (Backend)

```
Order Received → Accept Order (bulk) → Auto-generate Tracking No. & Shipping Label → System updates tracking for customer → WMS prints Shipping Label (100mm × 150mm) → Order moves to "Process Order" (Picking & Packing) → Package Handover
```

| ID | Requirement |
|----|-------------|
| SOP-01 | Admin can view and bulk-accept incoming website orders |
| SOP-02 | System auto-generates tracking number upon order acceptance |
| SOP-03 | System auto-generates and prints shipping label (100mm × 150mm format) |
| SOP-04 | Tracking number is pushed back to the customer's order dashboard automatically |
| SOP-05 | Order status progresses automatically after shipping label is printed |

### 9.3 Marketplace Orders SOP (Backend)

```
Order Received → Accept Order (bulk) → Auto-generate Tracking No. & Shipping Label → System updates tracking → WMS prints label (sorted Latest → Most Recent) → Picking & Packing → Package Handover
```

| ID | Requirement |
|----|-------------|
| SOP-06 | Receive and display orders from Shopee, Tokopedia, TikTok Shop, Lazada |
| SOP-07 | Bulk order acceptance across marketplace channels |
| SOP-08 | Auto-generate tracking number via expedition/courier API |
| SOP-09 | System generates PDF shipping label (100mm × 150mm); label print order sorted from latest to most recent |
| SOP-10 | Order status automatically progresses after label print |

### 9.4 Picking & Packing SOP

This workflow is part of the warehouse management module.

| Step | Requirement |
|------|-------------|
| 1 | Picker picks products based on the printed shipping label |
| 2 | Each order is compiled into a separate basket (1 order = 1 basket) |
| 3 | Picker scans their User ID once |
| 4 | Picker scans the order's tracking no. / order no. |
| 5 | Basket handed to Packer |
| 6 | Packer scans their User ID once |
| 7 | Packer scans the order's tracking no. / order no. |
| 8 | System displays the product list for that order |
| 9 | Packer scans each product one by one: ✅ correct scan = audio success sound; ❌ wrong product = audio error sound |
| 10 | System blocks progression if order is incomplete |
| 11 | On completion, system auto-refreshes and prompts for next order scan |
| 12 | If wrong products or incomplete — entire basket returned to Picker |

**Screen Reference:** "Proses Packing → Picking" screen with fields: ID Packer, Scan No. Pesanan/Resi/Serial, Order No., Tracking No., Source

### 9.5 Package Handover SOP

| Step | Requirement |
|------|-------------|
| 1 | Courier/Sender gathers all packed orders |
| 2 | System displays list of "Packed" orders in "Ready to be Shipped" column |
| 3 | Sender scans each packed order |
| 4 | Scanned orders move from "Ready to be Shipped" to "Shipped" status |

**Screen Reference:** "Proses Packing → Package Handover" screen with same fields as Picking screen.

### 9.6 Dispute SOP

```
Ticket → Verification → Categorization → Resolution → Closure
```

- Separate SOPs for website orders vs. marketplace orders (to be provided by client)

### 9.7 Social Marketplace SOP

```
Customer DM → Agent → Order → Payment → Fulfillment
```

---

## 10. Non-Functional Requirements

### 10.1 Design & UX

| ID | Requirement |
|----|-------------|
| NFR-01 | Site structure inspired by warbyparker.com |
| NFR-02 | Visual design inspired by uniqlo.com/id |
| NFR-03 | Fully responsive: mobile and desktop versions |
| NFR-04 | UX prototype to be delivered and approved before development |
| NFR-05 | Micro-animations for interactive elements |

### 10.2 Performance

| ID | Requirement |
|----|-------------|
| NFR-06 | Page load time < 3 seconds |
| NFR-07 | Stock levels must refresh at intervals of a few seconds (near real-time) |
| NFR-08 | Shipping label generation must be fast enough to support warehouse throughput |

### 10.3 Security

| ID | Requirement |
|----|-------------|
| NFR-09 | Authentication & authorization for all user roles (customer, warehouse staff, admin) |
| NFR-10 | Encrypted data storage |
| NFR-11 | Secure APIs (HTTPS, API keys secured server-side) |
| NFR-12 | Role-based access control |
| NFR-13 | Input sanitization on all user-facing forms |
| NFR-14 | Input validation (client-side and server-side) |
| NFR-15 | Rate limiting on login, payment, and API endpoints |

### 10.4 Reliability

| ID | Requirement |
|----|-------------|
| NFR-16 | 99.5% uptime target |
| NFR-17 | Retry mechanisms for API integrations |

### 10.5 Scalability

| ID | Requirement |
|----|-------------|
| NFR-18 | Handle traffic spikes |
| NFR-19 | Expand product catalog without performance degradation |

---

## 11. Technical Architecture

### 11.1 Technology Stack

| Layer | Technology |
|-------|-----------|
| Front-End | HTML5, CSS Framework (TBD) |
| Back-End | Python Framework (TBD — e.g., FastAPI / Django) |
| Database | PostgreSQL |
| Payment Gateway | Xendit |
| Marketplace Channels | Shopee, Tokopedia, TikTok Shop, Lazada |
| Courier/Expedition | JNE, J&T, J&T Cargo, TIKI, SiCepat, Grab, Gojek |

### 11.2 Key Integrations

| Integration | Purpose |
|-------------|---------|
| Xendit | Payment processing |
| Shopee API | Order intake + product listing sync |
| Tokopedia API | Order intake + product listing sync |
| TikTok Shop API | Order intake + product listing sync |
| Lazada API | Order intake + product listing sync |
| JNE, J&T, TIKI, SiCepat, Grab, Gojek APIs | Tracking number generation + shipment tracking |

---

## 12. Key Modules

1. Product Catalog
2. Customer Dashboard
3. Order Management
4. Payment System (Xendit)
5. Logistics System (Multi-courier)
6. Dispute System
7. Omni-Channel Product Sync
8. Warehouse Management (Picking/Packing/Handover)

---

## 13. MVP Definition

Include in MVP:
- Product catalog + filters + sorting + search
- Customer dashboard (full module)
- Cart & Checkout (Xendit)
- Wishlist (core feature)
- Shipment tracking
- Dispute system
- Omni-channel product sync
- Warehouse SOPs (picking, packing, handover)
- Bilingual support (ID/EN)

---

## 14. Future Enhancements (Phase 2)

- AI competitor analysis and market scraping
- COGS / pricing calculator tool
- Social media multi-platform post management (Hootsuite-like)
- Marketplace data analytics (TALO-equivalent)
- AI-generated captions and campaign management
- Price drop alerts for wishlist items
- Back-in-stock notifications
- AI-based wishlist recommendations
- Dynamic pricing automation
- Chatbot integration
- Advanced analytics
- Multi-country support

---

## 15. Risks & Dependencies

| # | Risk / Dependency |
|---|-------------------|
| R1 | API limitations (marketplace and logistics) |
| R2 | Marketplace API approval requirements and rate limits |
| R3 | Payment gateway reliability (Xendit) |
| R4 | Courier API availability and consistency |
| R5 | Client-provided SOPs (dispute handling) still pending |

---

## 16. Success Metrics

- Conversion rate
- Order fulfillment time
- Dispute resolution time
- Marketing ROI
- Margin improvement

---

## 17. Assumptions & Constraints

| # | Item |
|---|------|
| A1 | Client will provide the full list of expedition/courier companies for API integration |
| A2 | Client will provide two SOPs (website orders vs. marketplace orders) for dispute handling |
| A3 | Xendit account will be set up and managed by the client |
| A4 | Product data (catalog, images, variants) will be managed via the backend admin panel |
| A5 | Phase 1 budget is ~USD 4,100 |
| A6 | AI/analytics features are deferred to Phase 2 |

---

## 18. Open Items

| # | Item | Owner |
|---|------|-------|
| OI-01 | Website order dispute SOP document | Kevin |
| OI-02 | Marketplace order dispute SOP document | Kevin |
| OI-03 | Confirmation of courier API availability | Madocks |
| OI-04 | Final tech stack selection (CSS framework, Python framework) | Madocks |
| OI-05 | Xendit account details / API credentials | Kevin |
| OI-06 | Confirmation of marketplace API access (rate limits, approval) | Madocks |

---

## 19. Glossary

| Term | Definition |
|------|-----------|
| Xendit | Indonesian payment gateway provider |
| Omni-channel | Unified management of sales and inventory across multiple platforms |
| Expedition | Courier/logistics company that handles physical delivery |
| Picking | Warehouse process of retrieving products for an order |
| Packing | Warehouse process of verifying and packaging picked products |
| Resi | Indonesian term for tracking number / receipt number |
| Proses Pesanan | Indonesian: "Order Processing" |
| Gudang | Indonesian: "Warehouse" |
| AWB | Air Waybill — shipment tracking reference number |
| COGS | Cost of Goods Sold |
| i18n | Internationalization — architecture for multilingual support |

---

*Document prepared based on: client meeting transcripts (March 2026), Project Phoenix Scope of Work document, Project Phoenix Sitemap, and warehouse reference screenshots.*
