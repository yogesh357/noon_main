import { useEffect } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../../app/hooks'
import { fetchProducts } from '../../features/catalog/catalogSlice'
import ProductGrid from '../../components/catalog/ProductGrid'
import Pagination from '../../components/catalog/Pagination'

export default function SearchResultsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const dispatch = useAppDispatch()
  const { products, total, page, pages, loading } = useAppSelector((s) => s.catalog)
  const q = searchParams.get('q') ?? ''
  const currentPage = Number(searchParams.get('page') ?? 1)

  useEffect(() => {
    if (q) dispatch(fetchProducts({ q, page: currentPage, per_page: 20 }))
  }, [q, currentPage])

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-neutral-900">
          {q ? `Search results for "${q}"` : 'Search'}
        </h1>
        {!loading && q && (
          <p className="text-sm text-neutral-500 mt-1">{total.toLocaleString()} products found</p>
        )}
      </div>

      {!q ? (
        <div className="text-center py-16">
          <p className="text-neutral-500">Enter a search term to find products</p>
        </div>
      ) : (
        <>
          <ProductGrid products={products} loading={loading} />
          <Pagination page={page} pages={pages}
            onPageChange={(p) => setSearchParams({ q, page: String(p) })} />
        </>
      )}

      {!loading && q && total === 0 && (
        <div className="text-center py-8">
          <Link to="/products" className="btn-primary">Browse All Products</Link>
        </div>
      )}
    </div>
  )
}
