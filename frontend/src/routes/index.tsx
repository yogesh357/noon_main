import { createBrowserRouter, Navigate } from 'react-router-dom'

// Layouts
import PublicLayout from '../layouts/PublicLayout'
import CheckoutLayout from '../layouts/CheckoutLayout'
import CustomerDashboardLayout from '../layouts/CustomerDashboardLayout'
import AdminLayout from '../layouts/AdminLayout'
import WarehouseLayout from '../layouts/WarehouseLayout'

// Public pages
import HomePage from '../pages/public/HomePage'
import ProductListPage from '../pages/catalog/ProductListPage'
import ProductDetailPage from '../pages/catalog/ProductDetailPage'
import SearchResultsPage from '../pages/catalog/SearchResultsPage'
import CartPage from '../pages/cart/CartPage'
import FAQPage from '../pages/static/FAQPage'
import TermsPage from '../pages/static/TermsPage'
import DisclaimerPage from '../pages/static/DisclaimerPage'
import ContactPage from '../pages/static/ContactPage'
import AboutPage from '../pages/static/AboutPage'
import NotFoundPage from '../pages/static/NotFoundPage'

// Auth pages
import LoginPage from '../pages/auth/LoginPage'
import RegisterPage from '../pages/auth/RegisterPage'
import ForgotPasswordPage from '../pages/auth/ForgotPasswordPage'

// Checkout pages
import CheckoutPage from '../pages/checkout/CheckoutPage'
import OrderSuccessPage from '../pages/checkout/OrderSuccessPage'

// Customer dashboard pages
import DashboardOverviewPage from '../pages/dashboard/OverviewPage'
import DashboardOrdersPage from '../pages/dashboard/OrdersPage'
import DashboardOrderDetailPage from '../pages/dashboard/OrderDetailPage'
import DashboardTrackingPage from '../pages/dashboard/TrackingPage'
import DashboardDisputesPage from '../pages/dashboard/DisputesPage'
import DashboardDisputeDetailPage from '../pages/dashboard/DisputeDetailPage'
import DashboardAddressesPage from '../pages/dashboard/AddressesPage'
import DashboardPaymentsPage from '../pages/dashboard/PaymentsPage'
import DashboardWishlistPage from '../pages/dashboard/WishlistPage'
import DashboardProfilePage from '../pages/dashboard/ProfilePage'
import DashboardNotificationsPage from '../pages/dashboard/NotificationsPage'

// Admin pages
import AdminDashboardPage from '../pages/admin/AdminDashboardPage'
import AdminOrdersPage from '../pages/admin/AdminOrdersPage'
import AdminOrderDetailPage from '../pages/admin/AdminOrderDetailPage'
import AdminMarketplacePage from '../pages/admin/AdminMarketplacePage'
import AdminDisputesPage from '../pages/admin/AdminDisputesPage'

// Warehouse pages
import WarehouseHomePage from '../pages/warehouse/WarehouseHomePage'
import WarehousePickingPage from '../pages/warehouse/WarehousePickingPage'
import WarehousePackingPage from '../pages/warehouse/WarehousePackingPage'
import WarehouseHandoverPage from '../pages/warehouse/WarehouseHandoverPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <PublicLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'products', element: <ProductListPage /> },
      { path: 'products/:slug', element: <ProductDetailPage /> },
      { path: 'search', element: <SearchResultsPage /> },
      { path: 'cart', element: <CartPage /> },
      { path: 'faq', element: <FAQPage /> },
      { path: 'terms', element: <TermsPage /> },
      { path: 'disclaimer', element: <DisclaimerPage /> },
      { path: 'contact', element: <ContactPage /> },
      { path: 'about', element: <AboutPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
  {
    path: '/auth',
    element: <PublicLayout />,
    children: [
      { path: 'login', element: <LoginPage /> },
      { path: 'register', element: <RegisterPage /> },
      { path: 'forgot-password', element: <ForgotPasswordPage /> },
    ],
  },
  {
    path: '/checkout',
    element: <CheckoutLayout />,
    children: [
      { index: true, element: <CheckoutPage /> },
    ],
  },
  {
    path: '/order/success/:orderNumber',
    element: <CheckoutLayout />,
    children: [
      { index: true, element: <OrderSuccessPage /> },
    ],
  },
  {
    path: '/dashboard',
    element: <CustomerDashboardLayout />,
    children: [
      { index: true, element: <DashboardOverviewPage /> },
      { path: 'orders', element: <DashboardOrdersPage /> },
      { path: 'orders/:orderNumber', element: <DashboardOrderDetailPage /> },
      { path: 'tracking', element: <DashboardTrackingPage /> },
      { path: 'disputes', element: <DashboardDisputesPage /> },
      { path: 'disputes/:disputeId', element: <DashboardDisputeDetailPage /> },
      { path: 'addresses', element: <DashboardAddressesPage /> },
      { path: 'payments', element: <DashboardPaymentsPage /> },
      { path: 'wishlist', element: <DashboardWishlistPage /> },
      { path: 'profile', element: <DashboardProfilePage /> },
      { path: 'notifications', element: <DashboardNotificationsPage /> },
    ],
  },
  {
    path: '/admin-panel',
    element: <AdminLayout />,
    children: [
      { index: true, element: <AdminDashboardPage /> },
      { path: 'orders', element: <AdminOrdersPage /> },
      { path: 'orders/:orderId', element: <AdminOrderDetailPage /> },
      { path: 'marketplace-orders', element: <AdminMarketplacePage /> },
      { path: 'disputes', element: <AdminDisputesPage /> },
    ],
  },
  {
    path: '/warehouse',
    element: <WarehouseLayout />,
    children: [
      { index: true, element: <WarehouseHomePage /> },
      { path: 'picking', element: <WarehousePickingPage /> },
      { path: 'packing', element: <WarehousePackingPage /> },
      { path: 'handover', element: <WarehouseHandoverPage /> },
    ],
  },
  // Redirect old paths
  { path: '/admin', element: <Navigate to="/admin-panel" replace /> },
])
