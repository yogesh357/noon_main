import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../../app/hooks'
import { fetchWishlist, toggleWishlist } from '../../features/wishlist/wishlistSlice'
import { formatIDR } from '../../utils/currency'
import { getProductName } from '../../utils/i18n'

export default function DashboardWishlistPage() {
  const dispatch = useAppDispatch()
  const { products, loading } = useAppSelector((s) => s.wishlist)
  const { language } = useAppSelector((s) => s.ui)

  useEffect(() => { dispatch(fetchWishlist()) }, [])

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-semibold text-neutral-900">My Wishlist ({products.length})</h1>

      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => <div key={i} className="skeleton aspect-square rounded-xl" />)}
        </div>
      ) : products.length === 0 ? (
        <div className="card text-center py-12">
          <svg className="w-16 h-16 text-neutral-200 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
          <p className="text-neutral-400 mb-4">Your wishlist is empty</p>
          <Link to="/products" className="btn-primary">Browse Products</Link>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {products.map((product) => {
            const primary = product.images?.find((i) => i.is_primary) ?? product.images?.[0]
            return (
              <div key={product.id} className="product-card group">
                <button
                  onClick={() => dispatch(toggleWishlist(product.id))}
                  className="absolute top-3 right-3 z-10 w-8 h-8 flex items-center justify-center bg-white/80 rounded-full shadow-sm"
                >
                  <svg className="w-4 h-4 text-brand-red fill-current" viewBox="0 0 24 24">
                    <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
                  </svg>
                </button>
                <Link to={`/products/${product.slug}`}>
                  <div className="aspect-square bg-neutral-100 overflow-hidden">
                    <img src={primary?.image_url ?? '/placeholder.svg'} alt={getProductName(product, language)}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                  </div>
                  <div className="p-3">
                    <p className="text-sm font-medium text-neutral-900 line-clamp-2">{getProductName(product, language)}</p>
                    <p className="text-sm font-semibold text-neutral-900 mt-1">{formatIDR(product.base_price)}</p>
                  </div>
                </Link>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
