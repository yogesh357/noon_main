import { useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../../app/hooks'
import { fetchProducts, fetchCategories, setFilters, setPage, clearFilters } from '../../features/catalog/catalogSlice'
import { fetchWishlist } from '../../features/wishlist/wishlistSlice'
import type { ProductFilters } from '../../types'
import Breadcrumb from '../../components/common/Breadcrumb'
import FilterSidebar from '../../components/catalog/filters/FilterSidebar'
import SortDropdown from '../../components/catalog/SortDropdown'
import ProductGrid from '../../components/catalog/ProductGrid'
import Pagination from '../../components/catalog/Pagination'

// Sync filters to/from URL search params
function useProductFiltersFromURL(): [ProductFilters, (patch: Partial<ProductFilters>) => void] {
  const [searchParams, setSearchParams] = useSearchParams()

  const filters: ProductFilters = {
    category: searchParams.get('category') ?? undefined,
    brand: searchParams.get('brand') ?? undefined,
    color: searchParams.get('color') ?? undefined,
    size: searchParams.get('size') ?? undefined,
    price_min: searchParams.get('price_min') ? Number(searchParams.get('price_min')) : undefined,
    price_max: searchParams.get('price_max') ? Number(searchParams.get('price_max')) : undefined,
    in_stock: searchParams.get('in_stock') === '1' ? true : undefined,
    sort: (searchParams.get('sort') as ProductFilters['sort']) ?? 'newest',
    page: searchParams.get('page') ? Number(searchParams.get('page')) : 1,
    per_page: 20,
  }

  const updateFilters = useCallback((patch: Partial<ProductFilters>) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      // Reset page when filters change (not when page itself changes)
      if (!('page' in patch)) next.set('page', '1')
      Object.entries(patch).forEach(([k, v]) => {
        if (v === undefined || v === null || v === '') {
          next.delete(k)
        } else if (k === 'in_stock') {
          next.set(k, v ? '1' : '0')
        } else {
          next.set(k, String(v))
        }
      })
      return next
    }, { replace: false })
  }, [setSearchParams])

  return [filters, updateFilters]
}

export default function ProductListPage() {
  const dispatch = useAppDispatch()
  const [urlFilters, updateURLFilters] = useProductFiltersFromURL()
  const { products, categories, total, page, pages, loading, availableFilters } = useAppSelector((s) => s.catalog)
  const { user } = useAppSelector((s) => s.auth)

  // Load wishlist if logged in
  useEffect(() => {
    if (user) dispatch(fetchWishlist())
    dispatch(fetchCategories())
  }, [user])

  // Fetch products whenever URL filters change
  useEffect(() => {
    dispatch(fetchProducts(urlFilters))
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, [JSON.stringify(urlFilters)])

  const handleReset = () => {
    dispatch(clearFilters())
    updateURLFilters({
      category: undefined, brand: undefined, color: undefined,
      size: undefined, price_min: undefined, price_max: undefined, in_stock: undefined,
      sort: 'newest', page: 1,
    })
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Breadcrumb items={[{ label: 'Home', href: '/' }, { label: 'Products' }]} />

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Filter Sidebar */}
        <aside className="w-full lg:w-60 xl:w-64 flex-shrink-0">
          <FilterSidebar
            filters={urlFilters}
            availableFilters={availableFilters}
            categories={categories}
            onFilterChange={updateURLFilters}
            onReset={handleReset}
          />
        </aside>

        {/* Product listing */}
        <div className="flex-1 min-w-0">
          <SortDropdown
            value={urlFilters.sort}
            onChange={(sort) => updateURLFilters({ sort })}
            total={total}
          />

          <ProductGrid
            products={products}
            loading={loading}
            skeletonCount={20}
          />

          <Pagination
            page={page}
            pages={pages}
            onPageChange={(p) => updateURLFilters({ page: p })}
          />
        </div>
      </div>
    </div>
  )
}
