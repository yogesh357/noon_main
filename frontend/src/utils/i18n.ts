import type { Language } from '../types'

const translations: Record<string, string> = {
  // Navigation
  'Products': 'Products',
  'About Us': 'About Us',
  'FAQ': 'FAQ',
  'Contact': 'Contact',
  'Login': 'Login',
  'Register': 'Register',
  'Logout': 'Logout',
  'My Dashboard': 'My Dashboard',

  // Sort options
  'Newest': 'Newest',
  'Price Low to High': 'Price Low to High',
  'Price High to Low': 'Price High to Low',
  'Most Popular': 'Most Popular',
  'Highest Rated': 'Highest Rated',

  // Filters
  'Category': 'Category',
  'Brand': 'Brand',
  'Color': 'Color',
  'Size': 'Size',
  'Price Range': 'Price Range',
  'In Stock Only': 'In Stock Only',
  'All': 'All',
  'Apply': 'Apply',
  'Reset Filters': 'Reset Filters',
  'Filters': 'Filters',

  // Product
  'Add to Cart': 'Add to Cart',
  'Out of Stock': 'Out of Stock',
  'In Stock': 'In Stock',
  'Low Stock': 'Low Stock',
  'variants': 'variants',
  'products': 'products',

  // Cart
  'Cart': 'Cart',
  'Your cart is empty': 'Your cart is empty',
  'Subtotal': 'Subtotal',
  'Shipping': 'Shipping',
  'Total': 'Total',
  'Checkout': 'Checkout',
  'Continue Shopping': 'Continue Shopping',

  // Auth
  'Email': 'Email',
  'Password': 'Password',
  'Full Name': 'Full Name',
  'Phone': 'Phone',
  'Remember me': 'Remember me',
  'Forgot password?': 'Forgot password?',
  'Sign In': 'Sign In',
  'Create Account': 'Create Account',
  'Welcome Back': 'Welcome Back',

  // Order statuses
  'PENDING_PAYMENT': 'Pending Payment',
  'ACCEPTED': 'Accepted',
  'PROCESSING': 'Processing',
  'PICKING': 'Picking',
  'PACKING': 'Packing',
  'READY_TO_SHIP': 'Ready to Ship',
  'SHIPPED': 'Shipped',
  'DELIVERED': 'Delivered',
  'CANCELLED': 'Cancelled',

  // Dashboard
  'Overview': 'Overview',
  'Orders': 'Orders',
  'Track Shipment': 'Track Shipment',
  'Disputes': 'Disputes',
  'Addresses': 'Addresses',
  'Payments': 'Payments',
  'Wishlist': 'Wishlist',
  'Profile': 'Profile',
  'Notifications': 'Notifications',

  // Common
  'Save': 'Save',
  'Cancel': 'Cancel',
  'Delete': 'Delete',
  'Edit': 'Edit',
  'Back': 'Back',
  'Next': 'Next',
  'Previous': 'Previous',
  'Loading...': 'Loading...',
  'No results found': 'No results found',
  'Search': 'Search',
  'Search products...': 'Search products...',
  'Home': 'Home',
  'Shop': 'Shop',
  'Support': 'Support',
  'Account': 'Account',
  'All Products': 'All Products',
  'New Arrivals': 'New Arrivals',
  'Terms & Conditions': 'Terms & Conditions',
  'Disclaimer': 'Disclaimer',
  'Contact Us': 'Contact Us',
}

export function t(key: string, _language?: Language): string {
  return translations[key] ?? key
}

export function getProductName(
  product: { name_id: string; name_en: string },
  _language?: Language,
): string {
  return product.name_en || product.name_id
}

export function getCategoryName(
  category: { name_id: string; name_en: string },
  _language?: Language,
): string {
  return category.name_en || category.name_id
}
