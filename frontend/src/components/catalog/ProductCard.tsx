import { Link } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../../app/hooks'
import { toggleWishlist } from '../../features/wishlist/wishlistSlice'
import { showToast } from '../../features/ui/uiSlice'
import { formatIDR } from '../../utils/currency'
import { getProductName } from '../../utils/i18n'
import type { Product } from '../../types'

interface Props {
  product: Product
}

export default function ProductCard({ product }: Props) {
  const dispatch = useAppDispatch()
  const { language } = useAppSelector((s) => s.ui)
  const { productIds, loading } = useAppSelector((s) => s.wishlist)
  const { user } = useAppSelector((s) => s.auth)

  const isWishlisted = productIds.includes(product.id)
  const name = getProductName(product, language)
  const primaryImage = product.images?.find((i) => i.is_primary) ?? product.images?.[0]
  const imageUrl = primaryImage?.image_url ?? '/placeholder.svg'
  const variantCount = product.variants?.length ?? 0
  const uniqueColors = [...new Set(product.variants?.map((v) => v.color).filter(Boolean) ?? [])]
  const hasStock = product.variants?.some((v) => v.stock_quantity > 0) ?? false
  const lowStock = !hasStock ? false : product.variants?.some((v) => v.stock_quantity > 0 && v.stock_quantity <= 5)

  const handleWishlist = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (!user) {
      dispatch(showToast({ message: 'Please login to save wishlist', type: 'info' }))
      return
    }
    if (!loading) dispatch(toggleWishlist(product.id))
  }

  return (
    <div className="product-card group">
      {/* Wishlist heart */}
      <button
        onClick={handleWishlist}
        className="absolute top-3 right-3 z-10 w-8 h-8 flex items-center justify-center bg-white/80 backdrop-blur-sm rounded-full shadow-sm hover:bg-white transition-colors"
        aria-label={isWishlisted ? 'Remove from wishlist' : 'Add to wishlist'}
      >
        {isWishlisted ? (
          <svg className="w-4.5 h-4.5 text-brand-red fill-current" viewBox="0 0 24 24">
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
          </svg>
        ) : (
          <svg className="w-4.5 h-4.5 text-neutral-400 group-hover:text-brand-red transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        )}
      </button>

      {/* Image */}
      <Link to={`/products/${product.slug}`} className="block">
        <div className="aspect-square bg-neutral-100 overflow-hidden">
          <img
            src={imageUrl}
            alt={name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            loading="lazy"
            onError={(e) => { (e.target as HTMLImageElement).src = '/placeholder.svg' }}
          />
        </div>
      </Link>

      {/* Info */}
      <div className="p-3.5">
        <Link to={`/products/${product.slug}`}>
          <h3 className="text-sm font-medium text-neutral-900 line-clamp-2 hover:text-brand-red transition-colors leading-snug">
            {name}
          </h3>
        </Link>

        {product.brand && (
          <p className="text-xs text-neutral-400 mt-0.5 uppercase tracking-wide">{product.brand}</p>
        )}

        {/* Price */}
        <p className="mt-2 text-sm font-semibold text-neutral-900">
          {formatIDR(product.base_price)}
        </p>

        {/* Color swatches */}
        {uniqueColors.length > 0 && (
          <div className="flex items-center gap-1 mt-2">
            {uniqueColors.slice(0, 6).map((color) => (
              <span
                key={color}
                title={color!}
                className="w-3.5 h-3.5 rounded-full border border-neutral-200 flex-shrink-0"
                style={{ backgroundColor: color!.toLowerCase() }}
              />
            ))}
            {uniqueColors.length > 6 && (
              <span className="text-[10px] text-neutral-400">+{uniqueColors.length - 6}</span>
            )}
          </div>
        )}

        {/* Footer row */}
        <div className="flex items-center justify-between mt-2.5">
          {/* Variant count */}
          {variantCount > 1 && (
            <span className="text-[11px] text-neutral-400 bg-neutral-100 px-2 py-0.5 rounded-full">
              {variantCount} {language === 'id' ? 'varian' : 'variants'}
            </span>
          )}

          {/* Stock status */}
          {!hasStock ? (
            <span className="text-[11px] font-medium text-red-500 ml-auto">
              {language === 'id' ? 'Habis' : 'Out of Stock'}
            </span>
          ) : lowStock ? (
            <span className="text-[11px] font-medium text-orange-500 ml-auto">
              {language === 'id' ? 'Stok Terbatas' : 'Low Stock'}
            </span>
          ) : null}
        </div>

        {/* Rating */}
        {product.avg_rating !== undefined && product.review_count ? (
          <div className="flex items-center gap-1 mt-1.5">
            <svg className="w-3 h-3 text-yellow-400 fill-current" viewBox="0 0 24 24">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
            </svg>
            <span className="text-[11px] text-neutral-500">
              {product.avg_rating.toFixed(1)} ({product.review_count})
            </span>
          </div>
        ) : null}
      </div>
    </div>
  )
}
