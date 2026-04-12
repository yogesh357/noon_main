# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an e-commerce web application project for a client in Indonesia (referred to as Kevin/Ervin). The project is currently in the **requirements/planning phase** — no code has been written yet. The repository contains client meeting transcripts, a sitemap PDF, and reference images/videos.

## What Is Being Built

A full-stack e-commerce platform with an integrated ERP/WMS system. The project has two major components:

### 1. Customer-Facing Website (E-commerce)
- Product listing with filter (price range, eye color, category) and sort
- Product detail pages, cart, checkout, payment (via **Xendit** payment gateway)
- User accounts: registration, profile editing, order tracking, wishlist, dispute/return requests
- Static pages: FAQ, Terms & Conditions, Disclaimer, Contact Us, Search Results
- **Bilingual support**: Indonesian (default) + English toggle
- Design inspiration: warbyparker.com (structure), uniqlo.com/id (design)

### 2. ERP / Backend System
- Integrated with **Jubelio** (existing WMS/ERP used by client)
- Order management for both website orders and marketplace orders (Shopee, TikTok, Tokopedia)
- Bulk order acceptance, auto-generate tracking numbers and shipping labels (100mm × 150mm)
- Picking & Packing SOP with barcode scanning workflow (scan user ID → scan order → scan products)
- Package handover workflow
- **Omni-channel product sync**: one-click update of product title, description, variants, images across all marketplace listings (Shopee, Tokopedia, TikTok, Lazada, etc.)
- Real-time stock sync across all channels (updates every few seconds)
- Expedition/courier integration for auto-tracking number generation

### Customer Order Flow
Customer → Product List → Product Detail → Add to Cart → Cart → Checkout → Payment → Order Success → Order Summary

### Backend Order Flow
Order Received → Accept (bulk) → Auto-generate Tracking + Label → WMS prints label → Picking & Packing → Package Handover

## Key Integrations
- **Jubelio** (WMS/ERP): primary backend system — get access credentials from client
- **Xendit**: payment gateway
- **Shopee, Tokopedia, TikTok Shop, Lazada**: marketplace sync (stock + product data)
- Expedition/courier APIs (list to be provided by client)

## Secondary / Future Features (lower priority)
- AI competitor analysis: scrape marketplace competitor products, pricing, sales volume
- COGS calculator: help client understand true cost of goods vs. selling price
- Social media post management (multi-platform posting with auto-dimension adjustment)
- Market data analysis (similar to TALO data tool)

## Outstanding Items Needed from Client
- Two SOPs (website orders vs. marketplace orders) — client is writing these
- List of expedition/courier companies to integrate
- Detailed dispute/return SOP
- Jubelio account access for API exploration
- Reference website URLs for design inspiration
