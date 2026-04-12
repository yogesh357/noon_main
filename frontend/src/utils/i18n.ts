import type { Language } from '../types'

type Translations = Record<string, { id: string; en: string }>

const translations: Translations = {
  // Navigation
  'Products': { id: 'Produk', en: 'Products' },
  'About Us': { id: 'Tentang Kami', en: 'About Us' },
  'FAQ': { id: 'FAQ', en: 'FAQ' },
  'Contact': { id: 'Kontak', en: 'Contact' },
  'Login': { id: 'Masuk', en: 'Login' },
  'Register': { id: 'Daftar', en: 'Register' },
  'Logout': { id: 'Keluar', en: 'Logout' },
  'My Dashboard': { id: 'Dashboard Saya', en: 'My Dashboard' },

  // Sort options
  'Newest': { id: 'Terbaru', en: 'Newest' },
  'Price Low to High': { id: 'Termurah', en: 'Price Low to High' },
  'Price High to Low': { id: 'Termahal', en: 'Price High to Low' },
  'Most Popular': { id: 'Terpopuler', en: 'Most Popular' },
  'Highest Rated': { id: 'Rating Tertinggi', en: 'Highest Rated' },

  // Filters
  'Category': { id: 'Kategori', en: 'Category' },
  'Brand': { id: 'Merek', en: 'Brand' },
  'Color': { id: 'Warna', en: 'Color' },
  'Size': { id: 'Ukuran', en: 'Size' },
  'Price Range': { id: 'Rentang Harga', en: 'Price Range' },
  'In Stock Only': { id: 'Tersedia Saja', en: 'In Stock Only' },
  'All': { id: 'Semua', en: 'All' },
  'Apply': { id: 'Terapkan', en: 'Apply' },
  'Reset Filters': { id: 'Reset Filter', en: 'Reset Filters' },
  'Filters': { id: 'Filter', en: 'Filters' },

  // Product
  'Add to Cart': { id: 'Tambah ke Keranjang', en: 'Add to Cart' },
  'Out of Stock': { id: 'Habis', en: 'Out of Stock' },
  'In Stock': { id: 'Tersedia', en: 'In Stock' },
  'Low Stock': { id: 'Stok Terbatas', en: 'Low Stock' },
  'variants': { id: 'varian', en: 'variants' },
  'products': { id: 'produk', en: 'products' },

  // Cart
  'Cart': { id: 'Keranjang', en: 'Cart' },
  'Your cart is empty': { id: 'Keranjang Anda kosong', en: 'Your cart is empty' },
  'Subtotal': { id: 'Subtotal', en: 'Subtotal' },
  'Shipping': { id: 'Pengiriman', en: 'Shipping' },
  'Total': { id: 'Total', en: 'Total' },
  'Checkout': { id: 'Checkout', en: 'Checkout' },
  'Continue Shopping': { id: 'Lanjut Belanja', en: 'Continue Shopping' },

  // Auth
  'Email': { id: 'Email', en: 'Email' },
  'Password': { id: 'Kata Sandi', en: 'Password' },
  'Full Name': { id: 'Nama Lengkap', en: 'Full Name' },
  'Phone': { id: 'Telepon', en: 'Phone' },
  'Remember me': { id: 'Ingat saya', en: 'Remember me' },
  'Forgot password?': { id: 'Lupa kata sandi?', en: 'Forgot password?' },
  'Sign In': { id: 'Masuk', en: 'Sign In' },
  'Create Account': { id: 'Buat Akun', en: 'Create Account' },
  'Welcome Back': { id: 'Selamat Datang', en: 'Welcome Back' },

  // Order statuses
  'PENDING_PAYMENT': { id: 'Menunggu Pembayaran', en: 'Pending Payment' },
  'ACCEPTED': { id: 'Diterima', en: 'Accepted' },
  'PROCESSING': { id: 'Diproses', en: 'Processing' },
  'PICKING': { id: 'Picking', en: 'Picking' },
  'PACKING': { id: 'Packing', en: 'Packing' },
  'READY_TO_SHIP': { id: 'Siap Kirim', en: 'Ready to Ship' },
  'SHIPPED': { id: 'Dikirim', en: 'Shipped' },
  'DELIVERED': { id: 'Terkirim', en: 'Delivered' },
  'CANCELLED': { id: 'Dibatalkan', en: 'Cancelled' },

  // Dashboard
  'Overview': { id: 'Ringkasan', en: 'Overview' },
  'Orders': { id: 'Pesanan', en: 'Orders' },
  'Track Shipment': { id: 'Lacak Pengiriman', en: 'Track Shipment' },
  'Disputes': { id: 'Sengketa', en: 'Disputes' },
  'Addresses': { id: 'Alamat', en: 'Addresses' },
  'Payments': { id: 'Pembayaran', en: 'Payments' },
  'Wishlist': { id: 'Favorit', en: 'Wishlist' },
  'Profile': { id: 'Profil', en: 'Profile' },
  'Notifications': { id: 'Notifikasi', en: 'Notifications' },

  // Common
  'Save': { id: 'Simpan', en: 'Save' },
  'Cancel': { id: 'Batal', en: 'Cancel' },
  'Delete': { id: 'Hapus', en: 'Delete' },
  'Edit': { id: 'Edit', en: 'Edit' },
  'Back': { id: 'Kembali', en: 'Back' },
  'Next': { id: 'Berikutnya', en: 'Next' },
  'Previous': { id: 'Sebelumnya', en: 'Previous' },
  'Loading...': { id: 'Memuat...', en: 'Loading...' },
  'No results found': { id: 'Tidak ada hasil', en: 'No results found' },
  'Search': { id: 'Cari', en: 'Search' },
  'Search products...': { id: 'Cari produk...', en: 'Search products...' },
  'Home': { id: 'Beranda', en: 'Home' },
  'Shop': { id: 'Toko', en: 'Shop' },
  'Support': { id: 'Dukungan', en: 'Support' },
  'Account': { id: 'Akun', en: 'Account' },
  'All Products': { id: 'Semua Produk', en: 'All Products' },
  'New Arrivals': { id: 'Produk Baru', en: 'New Arrivals' },
  'Terms & Conditions': { id: 'Syarat & Ketentuan', en: 'Terms & Conditions' },
  'Disclaimer': { id: 'Disclaimer', en: 'Disclaimer' },
  'Contact Us': { id: 'Hubungi Kami', en: 'Contact Us' },
}

export function t(key: string, language: Language): string {
  const entry = translations[key]
  if (!entry) return key
  return entry[language] ?? entry['id'] ?? key
}

export function getProductName(
  product: { name_id: string; name_en: string },
  language: Language,
): string {
  return language === 'en' ? product.name_en : product.name_id
}

export function getCategoryName(
  category: { name_id: string; name_en: string },
  language: Language,
): string {
  return language === 'en' ? category.name_en : category.name_id
}
