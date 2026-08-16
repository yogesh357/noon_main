// ─── Auth & Users ────────────────────────────────────────────────────────────

export type UserRole = 'CUSTOMER' | 'ADMIN' | 'WAREHOUSE'
export type Language = 'en' | 'id'

export interface User {
  id: string
  email: string
  full_name: string
  phone?: string
  avatar_url?: string
  language: Language
  role: UserRole
  is_verified: boolean
  is_active: boolean
  created_at: string
}

export interface Address {
  id: number
  name: string
  phone: string
  street: string
  city: string
  province: string
  postal_code: string
  country: string
  is_default: boolean
}

// ─── Catalog ─────────────────────────────────────────────────────────────────

export interface Category {
  id: number
  name_id: string
  name_en: string
  slug: string
  description_id?: string
  description_en?: string
  parent_id?: number
  children?: Category[]
}

export interface ProductImage {
  id: number
  image_url: string
  alt_text?: string
  is_primary: boolean
  sort_order: number
}

export interface ProductVariant {
  id: number
  sku: string
  color?: string
  size?: string
  variant_type?: string
  price: number
  stock_quantity: number
  weight?: number
  barcode?: string
}

export interface Review {
  id: number
  user_id: string
  user_name: string
  rating: number
  comment?: string
  is_verified: boolean
  created_at: string
}

export type ProductStatus = 'ACTIVE' | 'DRAFT' | 'ARCHIVED'

export interface Product {
  id: number
  name_id: string
  name_en: string
  slug: string
  description_id?: string
  description_en?: string
  brand?: string
  base_price: number
  status: ProductStatus
  category_id?: number
  category?: Category
  images: ProductImage[]
  variants: ProductVariant[]
  avg_rating?: number
  review_count?: number
}

// ─── Cart ─────────────────────────────────────────────────────────────────────

export interface CartItem {
  id: number
  product_id: number
  variant_id: number
  product_name: string
  product_slug: string
  variant_label: string
  image_url?: string
  price: number
  quantity: number
  stock_quantity: number
}

export interface Cart {
  items: CartItem[]
  total_items: number
  subtotal: number
}

// ─── Orders ───────────────────────────────────────────────────────────────────

export type OrderStatus =
  | 'PENDING_PAYMENT'
  | 'ACCEPTED'
  | 'PROCESSING'
  | 'PICKING'
  | 'PACKING'
  | 'READY_TO_SHIP'
  | 'SHIPPED'
  | 'DELIVERED'
  | 'CANCELLED'

export type OrderSource = 'WEBSITE' | 'SHOPEE' | 'TOKOPEDIA' | 'TIKTOK' | 'LAZADA'

export type PaymentMethod = 'VIRTUAL_ACCOUNT' | 'EWALLET' | 'QRIS' | 'CREDIT_CARD' | 'RETAIL_OUTLET'
export type PaymentStatus = 'PENDING' | 'PAID' | 'FAILED' | 'EXPIRED' | 'REFUNDED'

export interface OrderItem {
  id: number
  product_name: string
  variant_label: string
  image_url?: string
  price: number
  quantity: number
  subtotal: number
}

export interface Payment {
  id: number
  xendit_invoice_id?: string
  payment_url?: string
  method?: PaymentMethod
  status: PaymentStatus
  amount: number
  paid_at?: string
}

export interface Order {
  id: number
  order_number: string
  status: OrderStatus
  source: OrderSource
  items: OrderItem[]
  payment?: Payment
  shipping_address?: Address
  courier?: string
  tracking_number?: string
  subtotal: number
  shipping_cost: number
  total: number
  notes?: string
  created_at: string
  updated_at: string
}

// ─── Shipment & Tracking ──────────────────────────────────────────────────────

export interface TrackingEvent {
  id: number
  status: string
  description: string
  location?: string
  timestamp: string
}

export interface Shipment {
  id: number
  courier: string
  tracking_number: string
  status: string
  estimated_delivery?: string
  events: TrackingEvent[]
}

// ─── Disputes ─────────────────────────────────────────────────────────────────

export type DisputeType = 'REFUND' | 'REPLACEMENT'
export type DisputeStatus = 'OPEN' | 'IN_REVIEW' | 'RESOLVED' | 'REJECTED'

export interface DisputeEvidence {
  id: number
  file_url: string
  file_name: string
  uploaded_at: string
}

export interface Dispute {
  id: number
  order_id: number
  order_number: string
  type: DisputeType
  status: DisputeStatus
  reason: string
  admin_response?: string
  sla_deadline: string
  evidence: DisputeEvidence[]
  created_at: string
  updated_at: string
}

// ─── Notifications ────────────────────────────────────────────────────────────

export type NotificationType = 'ORDER_UPDATE' | 'DELIVERY_UPDATE' | 'DISPUTE_UPDATE' | 'SYSTEM'

export interface Notification {
  id: number
  type: NotificationType
  title_id: string
  title_en: string
  message_id: string
  message_en: string
  is_read: boolean
  created_at: string
}

// ─── Warehouse ────────────────────────────────────────────────────────────────

export interface PickingTask {
  id: number
  order_id: number
  order_number: string
  assigned_to?: string
  started_at?: string
  completed_at?: string
}

export interface PackingTask {
  id: number
  order_id: number
  order_number: string
  items: OrderItem[]
  scan_log: string[]
  started_at?: string
  completed_at?: string
}

export interface HandoverBatch {
  id: number
  courier: string
  sender_name: string
  items: { order_number: string; order_id: number }[]
  is_completed: boolean
  created_at: string
}

// ─── Marketplace ──────────────────────────────────────────────────────────────

export type MarketplaceChannel = 'SHOPEE' | 'TOKOPEDIA' | 'TIKTOK' | 'LAZADA'

export interface MarketplaceListing {
  id: number
  product_id: number
  variant_id?: number
  channel: MarketplaceChannel
  external_item_id: string
  external_sku?: string
  is_active: boolean
}

export interface MarketplaceOrder {
  id: number
  order_id: number
  channel: MarketplaceChannel
  external_order_id: string
  sync_status: string
  raw_data: Record<string, unknown>
  created_at: string
}

// ─── API Payloads / Responses ─────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface ProductFilters {
  category?: string
  brand?: string
  color?: string
  size?: string
  price_min?: number
  price_max?: number
  in_stock?: boolean
  sort?: 'newest' | 'price_asc' | 'price_desc' | 'popular' | 'rating'
  page?: number
  per_page?: number
  q?: string
}

export interface AvailableFilters {
  brands: string[]
  colors: string[]
  sizes: string[]
  price_min: number
  price_max: number
}

export interface ProductListResponse {
  products: Product[]
  total: number
  page: number
  pages: number
  per_page: number
  filters: AvailableFilters
  categories: Category[]
}

export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterPayload {
  email: string
  password: string
  full_name: string
  phone?: string
}

export interface CheckoutPayload {
  address_id: number
  shipping_method: string
  courier: string
  notes?: string
}

export interface AddressPayload {
  name: string
  phone: string
  street: string
  city: string
  province: string
  postal_code: string
  country: string
  is_default?: boolean
}

export interface ShippingRate {
  courier: string
  service: string
  cost: number
  estimated_days: string
}

export interface AdminStats {
  total_orders_today: number
  revenue_today: number
  pending_orders: number
  active_disputes: number
  orders_by_status: Record<OrderStatus, number>
  revenue_last_7_days: { date: string; revenue: number }[]
}
