import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../../app/hooks'
import { fetchProducts, fetchCategories } from '../../features/catalog/catalogSlice'
import { t, getCategoryName } from '../../utils/i18n'
import ProductCard from '../../components/catalog/ProductCard'
import ProductCardSkeleton from '../../components/catalog/ProductCardSkeleton'

export default function HomePage() {
  const dispatch = useAppDispatch()
  const { language } = useAppSelector((s) => s.ui)
  const { products, categories, loading } = useAppSelector((s) => s.catalog)

  useEffect(() => {
    dispatch(fetchCategories())
    dispatch(fetchProducts({ sort: 'newest', per_page: 8, page: 1 }))
  }, [])

  return (
    <div>
      {/* Hero */}
      <section className="relative bg-neutral-100 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
          <div className="max-w-2xl">
            <p className="text-sm font-semibold text-brand-red uppercase tracking-widest mb-4">
              {language === 'id' ? 'Koleksi Terbaru' : 'New Collection'}
            </p>
            <h1 className="text-4xl lg:text-6xl font-bold text-neutral-900 leading-tight">
              {language === 'id' ? (
                <>Temukan <span className="text-brand-red">Gaya</span> Sempurnamu</>
              ) : (
                <>Discover Your <span className="text-brand-red">Perfect Style</span></>
              )}
            </h1>
            <p className="mt-6 text-lg text-neutral-600 leading-relaxed">
              {language === 'id'
                ? 'Produk berkualitas premium yang dikurasi khusus untuk Anda. Belanja dengan percaya diri — gratis ongkos kirim, pengembalian mudah.'
                : 'Premium quality products curated for you. Shop with confidence — free shipping, easy returns.'}
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <Link to="/products" className="btn-primary px-8 py-3.5">
                {language === 'id' ? 'Belanja Sekarang' : 'Shop Now'}
              </Link>
              <Link to="/about" className="btn-secondary px-8 py-3.5">
                {language === 'id' ? 'Tentang Kami' : 'Our Story'}
              </Link>
            </div>
          </div>
        </div>

        {/* Decorative shape */}
        <div className="absolute right-0 top-0 w-1/2 h-full bg-neutral-200/50 hidden lg:block" style={{ clipPath: 'polygon(15% 0, 100% 0, 100% 100%, 0% 100%)' }} />
      </section>

      {/* Categories */}
      {categories.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="flex items-center justify-between mb-10">
            <h2 className="text-2xl font-semibold text-neutral-900">
              {language === 'id' ? 'Belanja Berdasarkan Kategori' : 'Shop by Category'}
            </h2>
            <Link to="/products" className="text-sm text-brand-red hover:text-brand-red-dark font-medium">
              {language === 'id' ? 'Lihat Semua →' : 'View All →'}
            </Link>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {categories.slice(0, 5).map((cat) => (
              <Link
                key={cat.id}
                to={`/products?category=${cat.slug}`}
                className="group block text-center"
              >
                <div className="aspect-square bg-neutral-100 rounded-xl overflow-hidden mb-3 group-hover:bg-neutral-200 transition-colors">
                  <div className="w-full h-full flex items-center justify-center text-neutral-300 group-hover:text-neutral-400 transition-colors">
                    <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                </div>
                <p className="text-sm font-medium text-neutral-700 group-hover:text-neutral-900 transition-colors">
                  {getCategoryName(cat, language)}
                </p>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* New Arrivals */}
      <section className="bg-neutral-50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-10">
            <h2 className="text-2xl font-semibold text-neutral-900">
              {t('New Arrivals', language)}
            </h2>
            <Link to="/products?sort=newest" className="text-sm text-brand-red hover:text-brand-red-dark font-medium">
              {language === 'id' ? 'Lihat Semua →' : 'View All →'}
            </Link>
          </div>
          {loading ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 lg:gap-6">
              {[...Array(8)].map((_, i) => <ProductCardSkeleton key={i} />)}
            </div>
          ) : products.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 lg:gap-6">
              {products.map((p) => <ProductCard key={p.id} product={p} />)}
            </div>
          ) : (
            <div className="text-center py-12 text-neutral-400">
              {language === 'id' ? 'Produk segera hadir' : 'Products coming soon'}
            </div>
          )}
        </div>
      </section>

      {/* Value Props */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 text-center">
          {[
            { icon: '🚚', title: language === 'id' ? 'Gratis Ongkir' : 'Free Shipping', desc: language === 'id' ? 'Untuk pembelian di atas minimum' : 'On qualifying orders' },
            { icon: '↩️', title: language === 'id' ? 'Pengembalian Mudah' : 'Easy Returns', desc: language === 'id' ? 'Pengembalian dalam 30 hari' : '30-day return policy' },
            { icon: '🔒', title: language === 'id' ? 'Pembayaran Aman' : 'Secure Payment', desc: language === 'id' ? 'Transaksi aman & terenkripsi' : 'Safe & encrypted transactions' },
          ].map((item) => (
            <div key={item.title} className="p-6">
              <div className="text-4xl mb-4">{item.icon}</div>
              <h3 className="font-semibold text-neutral-900 mb-1">{item.title}</h3>
              <p className="text-sm text-neutral-500">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
