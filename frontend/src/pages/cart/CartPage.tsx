import { useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../../app/hooks'
import { fetchCart, updateCartItem, removeFromCart } from '../../features/cart/cartSlice'
import { formatIDR } from '../../utils/currency'

export default function CartPage() {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const { cart, loading } = useAppSelector((s) => s.cart)
  const { user } = useAppSelector((s) => s.auth)
  const { language } = useAppSelector((s) => s.ui)

  useEffect(() => { dispatch(fetchCart()) }, [])

  const items = cart?.items ?? []
  const subtotal = cart?.subtotal ?? 0
  const isEmpty = !loading && items.length === 0

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-semibold text-neutral-900 mb-6">
        {language === 'id' ? 'Keranjang Belanja' : 'Shopping Cart'}
      </h1>

      {loading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex gap-4 p-4 bg-white rounded-xl border border-neutral-100">
              <div className="skeleton w-20 h-20 rounded-lg flex-shrink-0" />
              <div className="flex-1 space-y-2">
                <div className="skeleton h-4 w-3/4 rounded" />
                <div className="skeleton h-4 w-1/4 rounded" />
              </div>
            </div>
          ))}
        </div>
      ) : isEmpty ? (
        <div className="text-center py-20">
          <svg className="w-20 h-20 text-neutral-200 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
          <p className="text-neutral-500 font-medium text-lg mb-2">
            {language === 'id' ? 'Keranjang kosong' : 'Your cart is empty'}
          </p>
          <p className="text-neutral-400 text-sm mb-6">
            {language === 'id' ? 'Tambahkan produk favorit Anda' : 'Add some products you love'}
          </p>
          <Link to="/products" className="btn-primary">
            {language === 'id' ? 'Mulai Belanja' : 'Start Shopping'}
          </Link>
        </div>
      ) : (
        <div className="lg:grid lg:grid-cols-3 lg:gap-8">
          {/* Items */}
          <div className="lg:col-span-2 space-y-3">
            {items.map((item) => (
              <div key={item.id} className="flex gap-4 p-4 bg-white rounded-xl border border-neutral-100">
                {/* Image */}
                <Link to={`/products/${item.product_slug}`} className="flex-shrink-0">
                  <div className="w-20 h-20 sm:w-24 sm:h-24 bg-neutral-100 rounded-lg overflow-hidden">
                    <img src={item.image_url ?? '/placeholder.svg'} alt={item.product_name}
                      className="w-full h-full object-cover"
                      onError={(e) => { (e.target as HTMLImageElement).src = '/placeholder.svg' }} />
                  </div>
                </Link>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <Link to={`/products/${item.product_slug}`}>
                    <h3 className="text-sm font-medium text-neutral-900 hover:text-brand-red transition-colors line-clamp-2">
                      {item.product_name}
                    </h3>
                  </Link>
                  <p className="text-xs text-neutral-500 mt-0.5">{item.variant_label}</p>
                  <p className="text-sm font-semibold text-neutral-900 mt-1">{formatIDR(item.price)}</p>

                  <div className="flex items-center justify-between mt-3">
                    {/* Qty controls */}
                    <div className="flex items-center border border-neutral-200 rounded-lg overflow-hidden">
                      <button
                        onClick={() => {
                          if (item.quantity <= 1) dispatch(removeFromCart(item.id))
                          else dispatch(updateCartItem({ itemId: item.id, quantity: item.quantity - 1 }))
                        }}
                        className="px-2.5 py-1.5 text-neutral-600 hover:bg-neutral-50 text-sm"
                      >−</button>
                      <span className="px-3 py-1.5 text-sm font-medium min-w-[32px] text-center">{item.quantity}</span>
                      <button
                        onClick={() => {
                          if (item.quantity < item.stock_quantity)
                            dispatch(updateCartItem({ itemId: item.id, quantity: item.quantity + 1 }))
                        }}
                        disabled={item.quantity >= item.stock_quantity}
                        className="px-2.5 py-1.5 text-neutral-600 hover:bg-neutral-50 text-sm disabled:opacity-40"
                      >+</button>
                    </div>

                    {/* Remove */}
                    <button
                      onClick={() => dispatch(removeFromCart(item.id))}
                      className="text-xs text-neutral-400 hover:text-red-500 transition-colors"
                    >
                      {language === 'id' ? 'Hapus' : 'Remove'}
                    </button>
                  </div>
                </div>

                {/* Line total */}
                <div className="text-right flex-shrink-0">
                  <p className="text-sm font-semibold text-neutral-900">
                    {formatIDR(item.price * item.quantity)}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* Summary */}
          <div className="mt-6 lg:mt-0">
            <div className="bg-white rounded-xl border border-neutral-200 p-5 sticky top-24">
              <h2 className="font-semibold text-neutral-900 mb-4">
                {language === 'id' ? 'Ringkasan Pesanan' : 'Order Summary'}
              </h2>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between text-neutral-600">
                  <span>{language === 'id' ? 'Subtotal' : 'Subtotal'} ({items.length} items)</span>
                  <span className="font-medium text-neutral-900">{formatIDR(subtotal)}</span>
                </div>
                <div className="flex justify-between text-neutral-600">
                  <span>{language === 'id' ? 'Ongkir' : 'Shipping'}</span>
                  <span className="text-neutral-400">{language === 'id' ? 'Dihitung saat checkout' : 'Calculated at checkout'}</span>
                </div>
                <div className="border-t border-neutral-100 pt-3 flex justify-between font-semibold text-neutral-900">
                  <span>Total</span>
                  <span className="text-lg">{formatIDR(subtotal)}</span>
                </div>
              </div>

              <button
                onClick={() => {
                  if (!user) navigate('/auth/login', { state: { from: '/checkout' } })
                  else navigate('/checkout')
                }}
                className="btn-primary w-full mt-5 py-3.5"
              >
                {language === 'id' ? 'Lanjut ke Checkout' : 'Proceed to Checkout'}
              </button>

              <Link to="/products" className="block text-center text-sm text-neutral-500 hover:text-neutral-700 mt-3">
                {language === 'id' ? '← Lanjut Belanja' : '← Continue Shopping'}
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
