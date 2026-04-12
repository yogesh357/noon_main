import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../../app/hooks'
import { addToCart } from '../../features/cart/cartSlice'
import { toggleWishlist } from '../../features/wishlist/wishlistSlice'
import { showToast } from '../../features/ui/uiSlice'
import { catalogService } from '../../services/api.service'
import { formatIDR } from '../../utils/currency'
import { getProductName } from '../../utils/i18n'
import type { Product, ProductVariant } from '../../types'
import Breadcrumb from '../../components/common/Breadcrumb'
import ProductCardSkeleton from '../../components/catalog/ProductCardSkeleton'

export default function ProductDetailPage() {
  const { slug } = useParams<{ slug: string }>()
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const { language } = useAppSelector((s) => s.ui)
  const { user } = useAppSelector((s) => s.auth)
  const { productIds } = useAppSelector((s) => s.wishlist)

  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeImage, setActiveImage] = useState<string>('')
  const [selectedColor, setSelectedColor] = useState<string>('')
  const [selectedSize, setSelectedSize] = useState<string>('')
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(null)
  const [quantity, setQuantity] = useState(1)
  const [addingToCart, setAddingToCart] = useState(false)

  const isWishlisted = product ? productIds.includes(product.id) : false

  useEffect(() => {
    if (!slug) return
    setLoading(true)
    catalogService.getProduct(slug)
      .then(({ data }) => {
        setProduct(data)
        const primary = data.images?.find((i) => i.is_primary) ?? data.images?.[0]
        setActiveImage(primary?.image_url ?? '')
        // Auto-select first available variant
        const first = data.variants?.[0]
        if (first) {
          setSelectedColor(first.color ?? '')
          setSelectedSize(first.size ?? '')
          setSelectedVariant(first)
        }
      })
      .catch(() => navigate('/404'))
      .finally(() => setLoading(false))
  }, [slug])

  // Find matching variant when color/size changes
  useEffect(() => {
    if (!product) return
    const match = product.variants?.find(
      (v) => v.color === selectedColor && v.size === selectedSize
    ) ?? product.variants?.find((v) => v.color === selectedColor)
      ?? product.variants?.[0]
    setSelectedVariant(match ?? null)
  }, [selectedColor, selectedSize, product])

  const handleAddToCart = async () => {
    if (!selectedVariant) return
    if (!user) { dispatch(showToast({ message: 'Please login to add to cart', type: 'info' })); return }
    setAddingToCart(true)
    try {
      await dispatch(addToCart({ variantId: selectedVariant.id, quantity })).unwrap()
      dispatch(showToast({ message: 'Added to cart!', type: 'success' }))
    } catch (err: unknown) {
      dispatch(showToast({ message: String(err) || 'Failed to add to cart', type: 'error' }))
    } finally {
      setAddingToCart(false)
    }
  }

  const handleWishlist = () => {
    if (!user) { dispatch(showToast({ message: 'Please login to save wishlist', type: 'info' })); return }
    if (product) dispatch(toggleWishlist(product.id))
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid lg:grid-cols-2 gap-10">
          <div className="space-y-4">
            <div className="aspect-square skeleton rounded-xl" />
          </div>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => <div key={i} className="skeleton h-6 rounded" />)}
          </div>
        </div>
      </div>
    )
  }

  if (!product) return null

  const name = getProductName(product, language)
  const description = language === 'en' ? product.description_en : product.description_id
  const uniqueColors = [...new Set(product.variants?.map((v) => v.color).filter(Boolean) ?? [])]
  const uniqueSizes = [...new Set(product.variants?.filter((v) => v.color === selectedColor || !selectedColor).map((v) => v.size).filter(Boolean) ?? [])]
  const isInStock = selectedVariant ? selectedVariant.stock_quantity > 0 : false
  const price = selectedVariant?.price ?? product.base_price

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Breadcrumb items={[{ label: 'Home', href: '/' }, { label: 'Products', href: '/products' }, { label: name }]} />

      <div className="grid lg:grid-cols-2 gap-10 xl:gap-16">
        {/* Image Gallery */}
        <div>
          <div className="aspect-square bg-neutral-100 rounded-xl overflow-hidden mb-4">
            <img
              src={activeImage || '/placeholder.svg'}
              alt={name}
              className="w-full h-full object-cover"
              onError={(e) => { (e.target as HTMLImageElement).src = '/placeholder.svg' }}
            />
          </div>
          {product.images && product.images.length > 1 && (
            <div className="flex gap-3 overflow-x-auto scrollbar-hide">
              {product.images.map((img) => (
                <button
                  key={img.id}
                  onClick={() => setActiveImage(img.image_url)}
                  className={`w-20 h-20 flex-shrink-0 rounded-lg overflow-hidden border-2 transition-colors ${
                    activeImage === img.image_url ? 'border-brand-red' : 'border-neutral-200 hover:border-neutral-400'
                  }`}
                >
                  <img src={img.image_url} alt={img.alt_text ?? name} className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Product Info */}
        <div className="space-y-5">
          {product.brand && (
            <p className="text-xs font-semibold text-neutral-400 uppercase tracking-widest">{product.brand}</p>
          )}

          <h1 className="text-2xl lg:text-3xl font-semibold text-neutral-900 leading-snug">{name}</h1>

          {/* Rating */}
          {product.avg_rating !== undefined && product.review_count ? (
            <div className="flex items-center gap-2">
              <div className="flex">
                {[...Array(5)].map((_, i) => (
                  <svg key={i} className={`w-4 h-4 ${i < Math.round(product.avg_rating!) ? 'text-yellow-400 fill-current' : 'text-neutral-200'}`} viewBox="0 0 24 24">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                  </svg>
                ))}
              </div>
              <span className="text-sm text-neutral-500">{product.avg_rating.toFixed(1)} ({product.review_count} reviews)</span>
            </div>
          ) : null}

          {/* Price */}
          <p className="text-3xl font-bold text-neutral-900">{formatIDR(price)}</p>

          {/* Stock Status */}
          {selectedVariant && (
            <div>
              {selectedVariant.stock_quantity <= 0 ? (
                <span className="inline-flex items-center gap-1.5 text-sm text-red-600 font-medium">
                  <span className="w-2 h-2 rounded-full bg-red-500" />
                  {language === 'id' ? 'Habis' : 'Out of Stock'}
                </span>
              ) : selectedVariant.stock_quantity <= 5 ? (
                <span className="inline-flex items-center gap-1.5 text-sm text-orange-600 font-medium">
                  <span className="w-2 h-2 rounded-full bg-orange-500" />
                  {language === 'id' ? `Sisa ${selectedVariant.stock_quantity}` : `Only ${selectedVariant.stock_quantity} left`}
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 text-sm text-green-600 font-medium">
                  <span className="w-2 h-2 rounded-full bg-green-500" />
                  {language === 'id' ? 'Tersedia' : 'In Stock'}
                </span>
              )}
            </div>
          )}

          <div className="border-t border-neutral-100" />

          {/* Color selector */}
          {uniqueColors.length > 0 && (
            <div>
              <p className="text-sm font-medium text-neutral-700 mb-2.5">
                {language === 'id' ? 'Warna' : 'Color'}
                {selectedColor && <span className="font-normal text-neutral-500 ml-1">: {selectedColor}</span>}
              </p>
              <div className="flex flex-wrap gap-2">
                {uniqueColors.map((color) => (
                  <button
                    key={color}
                    onClick={() => setSelectedColor(selectedColor === color ? '' : color!)}
                    className={`px-4 py-2 text-sm border rounded-lg transition-colors ${
                      selectedColor === color
                        ? 'bg-neutral-900 text-white border-neutral-900'
                        : 'border-neutral-300 text-neutral-600 hover:border-neutral-500'
                    }`}
                  >
                    {color}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Size selector */}
          {uniqueSizes.length > 0 && (
            <div>
              <p className="text-sm font-medium text-neutral-700 mb-2.5">
                {language === 'id' ? 'Ukuran' : 'Size'}
                {selectedSize && <span className="font-normal text-neutral-500 ml-1">: {selectedSize}</span>}
              </p>
              <div className="flex flex-wrap gap-2">
                {uniqueSizes.map((size) => {
                  const variant = product.variants?.find((v) => v.size === size && (v.color === selectedColor || !selectedColor))
                  const outOfStock = variant ? variant.stock_quantity <= 0 : false
                  return (
                    <button
                      key={size}
                      disabled={outOfStock}
                      onClick={() => setSelectedSize(selectedSize === size ? '' : size!)}
                      className={`px-4 py-2 text-sm border rounded-lg transition-colors ${
                        selectedSize === size
                          ? 'bg-neutral-900 text-white border-neutral-900'
                          : outOfStock
                            ? 'border-neutral-200 text-neutral-300 cursor-not-allowed line-through'
                            : 'border-neutral-300 text-neutral-600 hover:border-neutral-500'
                      }`}
                    >
                      {size}
                    </button>
                  )
                })}
              </div>
            </div>
          )}

          {/* Quantity */}
          <div>
            <p className="text-sm font-medium text-neutral-700 mb-2.5">{language === 'id' ? 'Jumlah' : 'Quantity'}</p>
            <div className="flex items-center gap-3">
              <div className="flex items-center border border-neutral-300 rounded-lg overflow-hidden">
                <button onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="px-3 py-2 text-neutral-600 hover:bg-neutral-50 transition-colors">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                  </svg>
                </button>
                <span className="px-4 py-2 text-sm font-medium min-w-[40px] text-center">{quantity}</span>
                <button onClick={() => setQuantity(Math.min(selectedVariant?.stock_quantity ?? 99, quantity + 1))}
                  className="px-3 py-2 text-neutral-600 hover:bg-neutral-50 transition-colors">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                </button>
              </div>
              {selectedVariant && selectedVariant.stock_quantity > 0 && (
                <span className="text-xs text-neutral-400">Max: {selectedVariant.stock_quantity}</span>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <button
              onClick={handleAddToCart}
              disabled={!isInStock || !selectedVariant || addingToCart}
              className="flex-1 btn-primary py-3.5 text-base"
            >
              {addingToCart ? (
                <span className="flex items-center gap-2 justify-center">
                  <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  {language === 'id' ? 'Menambahkan...' : 'Adding...'}
                </span>
              ) : !isInStock ? (
                language === 'id' ? 'Habis' : 'Out of Stock'
              ) : (
                language === 'id' ? 'Tambah ke Keranjang' : 'Add to Cart'
              )}
            </button>
            <button
              onClick={handleWishlist}
              className={`w-12 h-12 flex items-center justify-center border rounded-xl transition-colors flex-shrink-0 ${
                isWishlisted ? 'border-brand-red bg-brand-red/5' : 'border-neutral-300 hover:border-neutral-500'
              }`}
              aria-label={isWishlisted ? 'Remove from wishlist' : 'Add to wishlist'}
            >
              {isWishlisted ? (
                <svg className="w-5 h-5 text-brand-red fill-current" viewBox="0 0 24 24">
                  <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
                </svg>
              ) : (
                <svg className="w-5 h-5 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              )}
            </button>
          </div>

          {/* Description */}
          {description && (
            <div className="border-t border-neutral-100 pt-5">
              <h3 className="text-sm font-semibold text-neutral-900 mb-2">
                {language === 'id' ? 'Deskripsi' : 'Description'}
              </h3>
              <p className="text-sm text-neutral-600 leading-relaxed">{description}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
