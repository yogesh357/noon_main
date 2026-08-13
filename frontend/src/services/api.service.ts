import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import type {
  User, Address, Category, Product, ProductListResponse, ProductFilters,
  Cart, CartItem, Order, Dispute, Notification, Payment, Shipment,
  ShippingRate, AdminStats, MarketplaceOrder, HandoverBatch, PickingTask,
  PackingTask, LoginPayload, RegisterPayload, CheckoutPayload,
  AddressPayload, PaginatedResponse,
} from '../types'

// ─── Axios Client ─────────────────────────────────────────────────────────────

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true, // send cookies (session auth)
})

const normalizeUser = (user: Record<string, unknown>): User => ({
  id: String(user.id ?? ''),
  email: String(user.email ?? ''),
  full_name: String(user.full_name ?? ''),
  phone: typeof user.phone === 'string' ? user.phone : undefined,
  avatar_url: typeof user.avatar_url === 'string' ? user.avatar_url : undefined,
  language: (user.language ?? user.language_pref ?? 'id') as User['language'],
  role: String(user.role ?? 'customer').toUpperCase() as User['role'],
  is_verified: Boolean(user.is_verified),
  is_active: Boolean(user.is_active),
  created_at: String(user.created_at ?? ''),
})

const authFormPayload = (payload: LoginPayload) => {
  const form = new URLSearchParams()
  form.set('username', payload.username)
  form.set('password', payload.password)
  return form
}

// Attach JWT bearer token from localStorage if present
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token')
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Global response error handling
apiClient.interceptors.response.use(
  (res) => res,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      // Redirect to login only if not already there
      if (!window.location.pathname.startsWith('/auth')) {
        window.location.href = '/auth/login'
      }
    }
    return Promise.reject(error)
  },
)

// ─── Auth ─────────────────────────────────────────────────────────────────────

export const authService = {
  /** Cookie-based login (for web sessions) */
  login: (payload: LoginPayload) =>
    apiClient.post<{ access_token: string }>('/auth/login', authFormPayload(payload), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),

  /** JWT bearer login */
  bearerLogin: (payload: LoginPayload) =>
    apiClient.post<{ access_token: string; token_type: string }>('/auth/bearer/login', authFormPayload(payload), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),

  /** Register new account */
  register: (payload: RegisterPayload) =>
    apiClient.post('/auth/register', payload).then(({ data }) => ({ data: normalizeUser(data as Record<string, unknown>) })),

  /** Logout (clears cookie) */
  logout: () =>
    apiClient.post('/auth/logout'),

  /** Request password reset email */
  forgotPassword: (email: string) =>
    apiClient.post('/auth/forgot-password', { email }),

  /** Confirm password reset */
  resetPassword: (token: string, password: string) =>
    apiClient.post('/auth/reset-password', { token, password }),

  /** Request email verification */
  requestVerifyEmail: (email: string) =>
    apiClient.post('/auth/request-verify-email', { email }),

  /** Confirm email verification */
  verifyEmail: (token: string) =>
    apiClient.post('/auth/verify', { token }),

  /** Get current user */
  getMe: () =>
    apiClient.get('/users/me').then(({ data }) => ({ data: normalizeUser(data as Record<string, unknown>) })),

  /** Update profile */
  updateMe: (data: Partial<Pick<User, 'full_name' | 'phone' | 'language'>>) =>
    apiClient.patch('/users/me', data).then(({ data: user }) => ({ data: normalizeUser(user as Record<string, unknown>) })),
}

// ─── Catalog ──────────────────────────────────────────────────────────────────

export const catalogService = {
  /** List products with filters & pagination */
  getProducts: (filters: ProductFilters = {}) =>
    apiClient.get<ProductListResponse>('/catalog/products', { params: filters }),

  /** Get single product by slug */
  getProduct: (slug: string) =>
    apiClient.get<Product>(`/catalog/products/${slug}`),

  /** Get all categories (tree) */
  getCategories: () =>
    apiClient.get<Category[]>('/catalog/categories'),

  /** Live search suggestions */
  getSearchSuggestions: (q: string) =>
    apiClient.get<{ suggestions: string[] }>('/search/suggestions', { params: { q } }),

  /** Get product reviews */
  getReviews: (productId: number) =>
    apiClient.get(`/catalog/products/${productId}/reviews`),

  /** Real-time stock status */
  getStockStatus: (productId: number) =>
    apiClient.get(`/stock/${productId}`),
}

// ─── Cart ─────────────────────────────────────────────────────────────────────

export const cartService = {
  /** Get current cart */
  getCart: () =>
    apiClient.get<Cart>('/cart'),

  /** Add item to cart */
  addItem: (variantId: number, quantity: number) =>
    apiClient.post<CartItem>('/cart/add', { variant_id: variantId, quantity }),

  /** Update item quantity */
  updateItem: (itemId: number, quantity: number) =>
    apiClient.patch<CartItem>(`/cart/item/${itemId}`, { quantity }),

  /** Remove item from cart */
  removeItem: (itemId: number) =>
    apiClient.delete(`/cart/item/${itemId}`),

  /** Get cart count (for badge) */
  getCount: () =>
    apiClient.get<{ count: number }>('/cart/count'),

  /** Get shipping rates for cart */
  getShippingRates: (addressId: number) =>
    apiClient.get<ShippingRate[]>('/cart/shipping-rates', { params: { address_id: addressId } }),
}

// ─── Checkout ─────────────────────────────────────────────────────────────────

export const checkoutService = {
  /** Process checkout — returns order + payment URL */
  checkout: (payload: CheckoutPayload) =>
    apiClient.post<{ order: Order; payment_url: string }>('/checkout', payload),

  /** Get order success details */
  getOrderSuccess: (orderNumber: string) =>
    apiClient.get<Order>(`/order/success/${orderNumber}`),
}

// ─── Wishlist ─────────────────────────────────────────────────────────────────

export const wishlistService = {
  /** Get user's wishlist product IDs */
  getWishlist: () =>
    apiClient.get<{ product_ids: number[]; products: Product[] }>('/wishlist'),

  /** Toggle wishlist (add/remove) */
  toggle: (productId: number) =>
    apiClient.post<{ is_wishlisted: boolean }>(`/wishlist/toggle/${productId}`),
}

// ─── Dashboard ────────────────────────────────────────────────────────────────

export const dashboardService = {
  /** Get dashboard overview stats */
  getOverview: () =>
    apiClient.get('/dashboard/overview'),

  /** List user orders */
  getOrders: (params?: { status?: string; page?: number }) =>
    apiClient.get<PaginatedResponse<Order>>('/dashboard/orders', { params }),

  /** Get single order detail */
  getOrder: (orderNumber: string) =>
    apiClient.get<Order>(`/dashboard/orders/${orderNumber}`),

  /** Track shipment */
  getTracking: (orderNumber: string) =>
    apiClient.get<Shipment>(`/dashboard/tracking/${orderNumber}`),

  /** List disputes */
  getDisputes: () =>
    apiClient.get<Dispute[]>('/dashboard/disputes'),

  /** Get single dispute */
  getDispute: (disputeId: number) =>
    apiClient.get<Dispute>(`/dashboard/disputes/${disputeId}`),

  /** Raise a dispute */
  raiseDispute: (orderId: number, data: FormData) =>
    apiClient.post<Dispute>(`/dashboard/disputes/raise/${orderId}`, data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  /** List addresses */
  getAddresses: () =>
    apiClient.get<Address[]>('/dashboard/addresses'),

  /** Create address */
  createAddress: (data: AddressPayload) =>
    apiClient.post<Address>('/dashboard/addresses', data),

  /** Update address */
  updateAddress: (id: number, data: Partial<AddressPayload>) =>
    apiClient.patch<Address>(`/dashboard/addresses/${id}`, data),

  /** Delete address */
  deleteAddress: (id: number) =>
    apiClient.delete(`/dashboard/addresses/${id}`),

  /** Set default address */
  setDefaultAddress: (id: number) =>
    apiClient.post(`/dashboard/addresses/${id}/default`),

  /** Update profile */
  updateProfile: (data: FormData) =>
    apiClient.post('/dashboard/profile', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  /** List payment history */
  getPayments: () =>
    apiClient.get<Payment[]>('/dashboard/payments'),

  /** Unread notification count */
  getNotificationCount: () =>
    apiClient.get<{ count: number }>('/dashboard/notifications/count'),

  /** List notifications */
  getNotifications: () =>
    apiClient.get<Notification[]>('/dashboard/notifications'),

  /** Mark all notifications read */
  markAllRead: () =>
    apiClient.post('/dashboard/notifications/read-all'),

  /** Mark single notification read */
  markRead: (id: number) =>
    apiClient.post(`/dashboard/notifications/${id}/read`),
}

// ─── Admin ────────────────────────────────────────────────────────────────────

export const adminService = {
  /** Dashboard stats */
  getStats: () =>
    apiClient.get<AdminStats>('/admin-panel/stats'),

  /** List orders with filters */
  getOrders: (params?: { status?: string; source?: string; page?: number }) =>
    apiClient.get<PaginatedResponse<Order>>('/admin-panel/orders', { params }),

  /** Get single order */
  getOrder: (orderId: number) =>
    apiClient.get<Order>(`/admin-panel/orders/${orderId}`),

  /** Bulk accept orders */
  bulkProcess: (orderIds: number[]) =>
    apiClient.post('/admin-panel/orders/bulk-process', { order_ids: orderIds }),

  /** Update order status */
  updateOrderStatus: (orderId: number, status: string) =>
    apiClient.patch(`/admin-panel/orders/${orderId}/status`, { status }),

  /** Generate shipping label PDF */
  getShippingLabel: (orderId: number) =>
    apiClient.get(`/admin-panel/orders/${orderId}/label`, { responseType: 'blob' }),

  /** List marketplace orders */
  getMarketplaceOrders: (params?: { channel?: string; page?: number }) =>
    apiClient.get<PaginatedResponse<MarketplaceOrder>>('/admin-panel/marketplace-orders', { params }),

  /** List disputes */
  getDisputes: (params?: { status?: string }) =>
    apiClient.get<PaginatedResponse<Dispute>>('/admin-panel/disputes', { params }),

  /** Respond to dispute */
  respondToDispute: (disputeId: number, response: string) =>
    apiClient.patch(`/admin-panel/disputes/${disputeId}`, { admin_response: response }),

  /** List products (admin view) */
  getProducts: (params?: { page?: number; per_page?: number; search?: string }) =>
    apiClient.get<PaginatedResponse<Product>>('/admin-panel/products', { params }),

  /** Create product */
  createProduct: (data: {
    name_id: string
    name_en: string
    description_id?: string
    description_en?: string
    brand?: string
    base_price: number
    is_active?: boolean
    category_ids?: number[]
    variants?: Array<{ sku: string; color?: string; size?: string; variant_type?: string; price_override?: number; stock_quantity?: number; weight_grams?: number; barcode?: string }>
    images?: Array<{ image_url: string; alt_text?: string }>
  }) => apiClient.post<Product>('/admin-panel/products', data),

  /** Update product */
  updateProduct: (productId: number, data: Partial<{ name_id: string; name_en: string; description_id: string; description_en: string; brand: string; base_price: number; is_active: boolean }>) =>
    apiClient.patch<Product>(`/admin-panel/products/${productId}`, data),

  /** Soft-delete product */
  deleteProduct: (productId: number) =>
    apiClient.delete(`/admin-panel/products/${productId}`),
}

// ─── Warehouse ────────────────────────────────────────────────────────────────

export const warehouseService = {
  /** Get warehouse dashboard (picking queue etc) */
  getHome: () =>
    apiClient.get('/warehouse'),

  /** Start picking task */
  startPicking: (orderId: number) =>
    apiClient.post<PickingTask>(`/warehouse/picking/start/${orderId}`),

  /** Complete picking task */
  completePicking: (taskId: number) =>
    apiClient.post<PickingTask>(`/warehouse/picking/complete/${taskId}`),

  /** Start packing task */
  startPacking: (orderId: number) =>
    apiClient.post<PackingTask>(`/warehouse/packing/start/${orderId}`),

  /** Scan product barcode during packing */
  scanPacking: (taskId: number, barcode: string) =>
    apiClient.post(`/warehouse/packing/scan/${taskId}`, { barcode }),

  /** Complete packing */
  completePacking: (taskId: number) =>
    apiClient.post<PackingTask>(`/warehouse/packing/complete/${taskId}`),

  /** Return order to picker */
  returnToPicker: (taskId: number, reason: string) =>
    apiClient.post(`/warehouse/packing/return/${taskId}`, { reason }),

  /** Scan order for handover */
  scanHandover: (orderNumber: string, batchId?: number) =>
    apiClient.post('/warehouse/handover/scan', { order_number: orderNumber, batch_id: batchId }),

  /** Complete handover batch */
  completeHandover: (batchId: number) =>
    apiClient.post<HandoverBatch>(`/warehouse/handover/complete/${batchId}`),
}

// ─── Language ─────────────────────────────────────────────────────────────────

export const languageService = {
  toggle: (lang: 'id' | 'en') =>
    apiClient.post('/language', { language: lang }),
}

export default apiClient
