# BUSINESS REQUIREMENTS DOCUMENT (BRD)

**Project Name:** Noon – AI-Powered E-commerce Operating System
**Version:** 1.0
**Date:** 2026-03-19
**Status:** Draft

---

## TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [Project Objective](#2-project-objective)
3. [System Overview](#3-system-overview)
4. [Core Design Decisions](#4-core-design-decisions)
5. [User Types & Roles](#5-user-types--roles)
6. [Functional Requirements](#6-functional-requirements)
   - 6.1 E-commerce Storefront
   - 6.2 Wishlist System
   - 6.3 Customer Dashboard
   - 6.4 Payment System (Xendit)
   - 6.5 Order Management
   - 6.6 Jubelio Integration
   - 6.7 Logistics System
   - 6.8 Dispute System
   - 6.9 Social Media Automation
   - 6.10 AI Competitor & Pricing Engine
   - 6.11 COGS Engine
   - 6.12 Analytics Dashboard
7. [Multilingual Requirements](#7-multilingual-requirements)
8. [SOP Requirements](#8-sop-requirements)
9. [Technical Architecture](#9-technical-architecture)
10. [Deployment](#10-deployment)
11. [Non-Functional Requirements](#11-non-functional-requirements)
12. [Risks & Mitigations](#12-risks--mitigations)
13. [Success Metrics](#13-success-metrics)

---

## 1. EXECUTIVE SUMMARY

Noon is an AI-powered e-commerce operating system built for end-to-end commerce automation. It is not merely a storefront — it is a unified platform combining customer experience, order management, payment processing, logistics, marketing automation, and AI-driven intelligence into a single operating system.

The platform connects to Jubelio (OMS/inventory backbone), Xendit (payments), multiple courier APIs, and social media platforms — while layering AI on top for competitor analysis, dynamic pricing, and demand forecasting.

---

## 2. PROJECT OBJECTIVE

To build a full-stack e-commerce operating system that integrates:

- Online storefront (web) supporting English and Bahasa Indonesia
- Customer self-service dashboard
- Omnichannel backend via Jubelio
- Payment processing via Xendit
- Multi-courier logistics tracking
- Social media marketing automation
- AI-based competitor analysis and pricing engine

The system must support end-to-end automation of commerce, operations, and decision-making.

---

## 3. SYSTEM OVERVIEW

```
Frontend (Store + Customer Dashboard)
              ↓
        Backend APIs
              ↓
        Core Systems
    ┌─────────────────────────────────┐
    │ Order Management                │
    │ Payment System (Xendit)         │
    │ Inventory Sync (Jubelio)        │
    │ Logistics Tracking              │
    │ Dispute System                  │
    │ Social Automation               │
    │ AI Pricing Engine               │
    │ COGS Engine                     │
    │ Analytics Dashboard             │
    └─────────────────────────────────┘
```

---

## 4. CORE DESIGN DECISIONS

### Source of Truth Split

| System   | Is Source of Truth For |
|----------|----------------------|
| **Jubelio** | Products, Inventory, Order Fulfillment |
| **Noon**    | Customer Experience, Pre-sync Orders, Payments, AI Analytics, Marketing Automation |

This split is **critical** — all product/inventory data flows from Jubelio into Noon. Orders originate in Noon and are pushed to Jubelio after payment confirmation.

---

## 5. USER TYPES & ROLES

### 5.1 Customer
| Capability | Description |
|-----------|-------------|
| Browse products | View listings, search, filter |
| Wishlist | Save items for later |
| Place orders | Cart → Checkout → Payment |
| Track shipments | Real-time courier updates |
| Raise disputes | Initiate and monitor dispute tickets |

### 5.2 Admin
| Capability | Description |
|-----------|-------------|
| Monitor system | Platform health, integrations status |
| Handle disputes | Review evidence, resolve tickets |
| View analytics | Sales, logistics, pricing insights |
| Manage integrations | Jubelio, Xendit, courier, social APIs |

### 5.3 Operations
| Capability | Description |
|-----------|-------------|
| Fulfill orders | Pick, pack, ship |
| Manage logistics | Courier assignment, AWB creation |
| Sync with Jubelio | Inventory reconciliation |

### 5.4 Marketing
| Capability | Description |
|-----------|-------------|
| Run campaigns | Product promotions, discount events |
| Social media posting | One-click or scheduled publishing |
| Analyze competitors | Pricing and market position data |

---

## 6. FUNCTIONAL REQUIREMENTS

### 6.1 E-Commerce Storefront

#### Product Listing
- Grid/list view of products pulled from Jubelio
- Pagination and infinite scroll support
- Quick-add to cart and wishlist from listing

#### Product Detail Page
- Full product images, description, attributes
- Stock availability (real-time from Jubelio)
- Price, promotions, shipping estimate
- Add to Cart / Add to Wishlist buttons

#### Search & Filters
| Filter Type | Options |
|------------|---------|
| Category | Product category hierarchy |
| Price Range | Min / Max slider |
| Brand | Brand list |
| Attributes | Size, color, material, etc. |
| Availability | In stock / Pre-order |
| Sort By | Price ↑↓, Newest, Best Selling, Relevance |

#### Cart
- Add, remove, update quantity
- Price summary with taxes and shipping estimate
- Proceed to checkout

#### Checkout
- Address selection or new address entry
- Courier selection with rate lookup
- Payment method selection (Xendit)
- Order summary and confirmation

---

### 6.2 Wishlist System (Core Feature)

The wishlist is a mandatory feature with both UX and business intelligence value.

| Feature | Detail |
|--------|--------|
| Add / Remove items | Toggle from PDP or listing |
| View saved items | Dedicated wishlist page |
| Move to Cart | One-click conversion |
| Persist per user | Stored in database, available across devices |

**Business Use Cases:**
- Demand tracking: identify high-wishlist, low-purchase items
- Retargeting: trigger emails/notifications when wishlisted items go on sale
- AI signals: feed wishlist data into pricing and stock planning engine

---

### 6.3 Customer Dashboard

#### Module Overview
| Module | Description |
|-------|-------------|
| Orders | Full order history with status |
| Shipment Tracking | Live courier updates per order |
| Disputes | Active and closed dispute tickets |
| Wishlist | Saved items |
| Profile | Personal info, preferences |
| Addresses | Saved delivery addresses |
| Payments | Payment method management |
| Notifications | System alerts, promotions, status updates |

#### Order View
- Order ID, date, items, quantities
- Payment status (paid / pending / failed)
- Order status (per lifecycle stage)
- Invoice download

#### Shipment Tracking
- Courier name and service type
- AWB (Air Waybill) number
- Live status timeline from courier API
- Estimated delivery date

---

### 6.4 Payment System (Xendit)

#### Payment Flow
```
Checkout
   ↓
Create Payment Request (Noon Backend)
   ↓
Redirect to Xendit Payment Page
   ↓
Customer Completes Payment
   ↓
Xendit Webhook → Noon Backend
   ↓
Verify Webhook Signature
   ↓
Confirm Order → Push to Jubelio
```

#### Requirements
| Requirement | Detail |
|------------|--------|
| Webhook verification | Validate Xendit signature on every callback |
| Retry handling | Retry failed webhook processing with backoff |
| Idempotency | Prevent duplicate order creation on multiple webhook calls |
| Failure states | Handle expired, failed, and cancelled payments gracefully |
| Supported methods | VA, QRIS, Cards, E-wallets (per Xendit capability) |

---

### 6.5 Order Management

#### Order Lifecycle
```
Created → Paid → Processing → Packed → Shipped → Delivered → Closed
```

With exception paths:
```
Created → Payment Failed → Cancelled
Shipped → Dispute Raised → Under Review → Resolved / Closed
```

#### Order States Description
| State | Trigger |
|-------|---------|
| Created | Customer completes checkout |
| Paid | Xendit confirms payment |
| Processing | Order pushed to Jubelio |
| Packed | Jubelio confirms packing |
| Shipped | AWB received from courier |
| Delivered | Courier confirms delivery |
| Closed | Post-delivery review window passed |

---

### 6.6 Jubelio Integration

#### Integration Functions
| Function | Direction | Trigger |
|---------|-----------|---------|
| Pull products | Jubelio → Noon | Scheduled sync / manual |
| Pull inventory | Jubelio → Noon | Real-time / scheduled |
| Push orders | Noon → Jubelio | After payment confirmed |
| Receive order updates | Jubelio → Noon | Webhook / polling |

#### Sync Rules
- Product data in Noon is always overwritten by Jubelio data on sync
- Inventory levels are never manually edited in Noon
- Orders pushed to Jubelio include full customer, item, and payment data
- Sync failures must be logged, alerted, and retried

---

### 6.7 Logistics System

#### Supported Couriers
| Courier | Type |
|--------|------|
| JNE | Regular |
| J&T | Regular |
| J&T Cargo | Cargo |
| TIKI | Regular |
| SiCepat | Regular |
| Grab | Same-day |
| Gojek | Same-day |

#### Features
| Feature | Detail |
|--------|--------|
| Tracking API | Per-courier API integration or aggregator |
| Status normalization | Map courier-specific statuses to a standard set |
| Shipment logs | Full audit trail of tracking events per order |
| Estimated delivery | Show ETA based on courier data |

#### Normalized Status Set
`Picked Up → In Transit → Out for Delivery → Delivered → Failed Delivery → Returned`

---

### 6.8 Dispute System

#### Dispute Types
| Type | Description |
|-----|-------------|
| Not Delivered | Order marked delivered but not received |
| Damaged | Item received in damaged condition |
| Wrong Item | Different item delivered |
| Missing Item | Item(s) missing from package |

#### Dispute Flow
```
Customer Raises Dispute
       ↓
Upload Evidence (photos, description)
       ↓
Admin Reviews Ticket
       ↓
Resolution Decision
       ↓
Execute Resolution → Close Ticket
```

#### Resolution Options
| Resolution | Action |
|-----------|--------|
| Refund | Payment reversed via Xendit |
| Replacement | New item dispatched |
| Reject | Ticket closed with reason |

#### SLA Requirements
| Stage | SLA |
|-------|-----|
| Raise Window | 48–72 hours after delivery |
| Admin Response | Within 24 hours of ticket creation |
| Resolution | Within 3–5 business days |

---

### 6.9 Social Media Automation

#### Supported Platforms
Instagram, Facebook, Twitter/X, LinkedIn, Pinterest

#### Features
| Feature | Detail |
|--------|--------|
| One-click post | Publish a product or promotion to all platforms instantly |
| Scheduling | Queue posts for a future date/time |
| AI captions | Generate captions based on product data using AI |
| Media management | Upload images/videos per platform |

#### Caption AI Inputs
- Product name
- Key attributes
- Target audience
- Promotion or discount
- Brand tone (formal / casual)

---

### 6.10 AI Competitor & Pricing Engine

#### Inputs
| Input | Source |
|-------|--------|
| Marketplace competitor pricing | Shopee via Kalodata or equivalent scraper |
| Internal COGS | COGS Engine |
| Ads spend | Marketing dashboard |
| Platform fees | Configuration |

#### Outputs
| Output | Description |
|--------|-------------|
| Competitor pricing overview | Price positioning vs. competitors |
| Market classification | Price leader / mid-market / premium |
| Strategy recommendations | Suggested price adjustments with rationale |

#### Engine Behavior
- Runs on configurable schedule (e.g., daily)
- Stores historical price data for trend analysis
- Alerts admin when competitor price drops below Noon's price

---

### 6.11 COGS Engine

#### Inputs
| Cost Component | Description |
|---------------|-------------|
| Product cost | Purchase / import cost |
| Import cost | Duties, shipping from supplier |
| Warehouse | Storage cost allocation |
| Staff | Operational headcount cost |
| Ads | Advertising spend allocation |
| Platform fees | Marketplace/Xendit fees |
| Delivery | Last-mile cost |

#### Selling Price Formula
```
Selling Price = COGS / (1 - Target Margin - Platform Fees)
```

#### Output
- Recommended selling price per product
- Minimum viable price (break-even)
- Margin at any given price point

---

### 6.12 Analytics Dashboard

#### Modules
| Module | Key Metrics |
|-------|------------|
| Orders | Total orders, GMV, AOV, conversion rate |
| Shipments | Fulfillment rate, avg. delivery time, courier performance |
| Disputes | Dispute rate, resolution time, resolution type breakdown |
| Pricing Insights | Price vs. COGS, margin trend |
| Competitor Analysis | Price gap, market position, historical trends |

#### Role-Based Access
| Role | Visible Modules |
|------|----------------|
| Admin | All modules |
| Operations | Orders, Shipments |
| Marketing | Pricing Insights, Competitor Analysis |

---

## 7. MULTILINGUAL REQUIREMENTS

| Aspect | Requirement |
|--------|------------|
| Languages | English and Bahasa Indonesia |
| Toggle | Persistent language switcher in header |
| Scope | UI labels, product descriptions, emails, push notifications |
| Implementation | i18n library (next-intl or equivalent) |
| Default | English (Bahasa as secondary) |

---

## 8. SOP REQUIREMENTS

### 8.1 Website Order SOP
```
Customer places order
       ↓
Payment via Xendit confirmed
       ↓
Order pushed to Jubelio (Processing)
       ↓
Operations fulfills (Packing → AWB assigned)
       ↓
Shipped → Courier tracking active
       ↓
Delivered → Order closed
```

### 8.2 Social/DM Order SOP
```
Customer DMs on social platform
       ↓
Agent responds, captures order details
       ↓
Manual order created in Noon
       ↓
Payment link sent (Xendit)
       ↓
Payment confirmed → Fulfillment via Jubelio
```

### 8.3 Dispute SOP
```
Customer raises ticket (within 48–72 hrs of delivery)
       ↓
Evidence uploaded
       ↓
Admin verifies within 24 hrs
       ↓
Resolve: Refund / Replacement / Reject
       ↓
Ticket closed
```

---

## 9. TECHNICAL ARCHITECTURE

### Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js (React) |
| Backend | Node.js (Express) or FastAPI (Python) |
| Database | PostgreSQL |
| Cache | Redis (sessions, rate limiting) |
| Queue | Bull / Celery (webhook processing, sync jobs) |

### External Integrations

| System | Purpose |
|--------|---------|
| Xendit | Payment processing |
| Jubelio | Product, inventory, order fulfillment |
| JNE / J&T / SiCepat / etc. | Courier tracking APIs |
| Kalodata or equivalent | Competitor pricing data |
| Instagram / Facebook / Twitter / LinkedIn / Pinterest | Social posting APIs |

### Architecture Principles
- Jubelio sync is always async (queue-based, not real-time blocking)
- Xendit webhooks are verified before any order state change
- All external API failures must be logged and retried
- Frontend communicates only with Noon's backend — no direct third-party calls from browser

---

## 10. DEPLOYMENT

### Infrastructure (Hostinger VPS)

| Component | Detail |
|-----------|--------|
| Server | Ubuntu VPS on Hostinger |
| Containerization | Docker (per service) |
| Web server | Nginx (reverse proxy) |
| Process management | PM2 (Node.js services) |
| SSL | Let's Encrypt (auto-renew) |

### Environment Strategy
- Development → Staging → Production
- Staging mirrors production environment

---

## 11. NON-FUNCTIONAL REQUIREMENTS

| Category | Requirement |
|---------|------------|
| Performance | Page load < 3 seconds (P95) |
| Security | All data encrypted at rest and in transit (HTTPS, AES) |
| API Security | API keys stored in environment variables, never in code |
| Uptime | 99.5% availability SLA |
| Scalability | Stateless backend to support horizontal scaling |
| Data Privacy | Customer PII handled per applicable data protection laws |
| Audit Logging | All admin actions logged with user, timestamp, and action |

---

## 12. RISKS & MITIGATIONS

| Risk | Impact | Mitigation |
|------|--------|-----------|
| API limitations (Jubelio/courier) | High | Rate limiting + queue-based sync with retry |
| Data inconsistency (Noon vs Jubelio) | High | Reconciliation job + alert on mismatch |
| Sync failures | Medium | Dead-letter queue + admin alert |
| Payment webhook issues | High | Idempotency keys + manual reconciliation tool |
| Competitor data unavailability | Medium | Fallback to cached data + alert |
| Social platform API changes | Low | Abstract behind adapter pattern |

---

## 13. SUCCESS METRICS

| Metric | Target |
|--------|--------|
| Conversion Rate | Baseline + 15% improvement at 6 months |
| Order Completion Rate | > 95% of paid orders fulfilled |
| Dispute Resolution Time | Average < 3 business days |
| Gross Margin Improvement | +5% via COGS engine pricing optimization |
| ROI | Positive ROI within 12 months of launch |
| Uptime | > 99.5% monthly |
| Page Load Time | < 3s on P95 |

---

## APPENDIX: GLOSSARY

| Term | Definition |
|------|-----------|
| AWB | Air Waybill — shipment tracking number |
| COGS | Cost of Goods Sold |
| GMV | Gross Merchandise Value |
| AOV | Average Order Value |
| OMS | Order Management System |
| PDP | Product Detail Page |
| SLA | Service Level Agreement |
| VA | Virtual Account (payment method) |
| QRIS | QR-based payment standard (Indonesia) |

---

*Document Owner: Rahul*
*Next Review: After stakeholder alignment*
