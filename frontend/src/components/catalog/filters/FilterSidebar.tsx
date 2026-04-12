import { useState } from 'react'
import { useAppSelector } from '../../../app/hooks'
import { t, getCategoryName } from '../../../utils/i18n'
import { formatIDR } from '../../../utils/currency'
import type { ProductFilters, AvailableFilters, Category } from '../../../types'

interface Props {
  filters: ProductFilters
  availableFilters: AvailableFilters | null
  categories: Category[]
  onFilterChange: (patch: Partial<ProductFilters>) => void
  onReset: () => void
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function FilterSection({ title, children }: { title: string; children: React.ReactNode }) {
  const [open, setOpen] = useState(true)
  return (
    <div className="border-b border-neutral-100 pb-5">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between mb-3 group"
      >
        <h3 className="text-xs font-semibold text-neutral-900 uppercase tracking-wider">
          {title}
        </h3>
        <svg
          className={`w-4 h-4 text-neutral-400 transition-transform ${open ? '' : '-rotate-90'}`}
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && children}
    </div>
  )
}

// Category tree (recursive)
function CategoryTree({
  categories, selected, onSelect, language, depth = 0,
}: {
  categories: Category[]
  selected?: string
  onSelect: (slug: string | undefined) => void
  language: 'id' | 'en'
  depth?: number
}) {
  return (
    <ul className={depth > 0 ? 'ml-3 border-l border-neutral-100 pl-3' : ''}>
      {depth === 0 && (
        <li>
          <button
            onClick={() => onSelect(undefined)}
            className={`block w-full text-left py-1 text-sm transition-colors ${
              !selected ? 'text-brand-red font-medium' : 'text-neutral-600 hover:text-neutral-900'
            }`}
          >
            {t('All', language)}
          </button>
        </li>
      )}
      {categories.map((cat) => (
        <li key={cat.id}>
          <button
            onClick={() => onSelect(cat.slug)}
            className={`block w-full text-left py-1 text-sm transition-colors ${
              selected === cat.slug ? 'text-brand-red font-medium' : 'text-neutral-600 hover:text-neutral-900'
            }`}
          >
            {getCategoryName(cat, language)}
          </button>
          {cat.children?.length ? (
            <CategoryTree
              categories={cat.children}
              selected={selected}
              onSelect={onSelect}
              language={language}
              depth={depth + 1}
            />
          ) : null}
        </li>
      ))}
    </ul>
  )
}

// Color mapping for known color names
const COLOR_MAP: Record<string, string> = {
  black: '#000000', white: '#FFFFFF', red: '#DC2626', blue: '#2563EB',
  green: '#16A34A', yellow: '#CA8A04', pink: '#EC4899', purple: '#9333EA',
  orange: '#EA580C', gray: '#6B7280', grey: '#6B7280', brown: '#92400E',
  navy: '#1E3A5F', beige: '#D4C5A9', gold: '#B7932C', silver: '#9CA3AF',
}

function getColorHex(colorName: string): string {
  return COLOR_MAP[colorName.toLowerCase()] ?? colorName
}

// ─── Main FilterSidebar ───────────────────────────────────────────────────────

export default function FilterSidebar({ filters, availableFilters, categories, onFilterChange, onReset }: Props) {
  const { language } = useAppSelector((s) => s.ui)
  const [priceMin, setPriceMin] = useState(filters.price_min?.toString() ?? '')
  const [priceMax, setPriceMax] = useState(filters.price_max?.toString() ?? '')
  const [mobileOpen, setMobileOpen] = useState(false)

  const hasActiveFilters = Boolean(
    filters.category || filters.brand || filters.color || filters.size ||
    filters.price_min || filters.price_max || filters.in_stock
  )

  const applyPrice = () => {
    onFilterChange({
      price_min: priceMin ? Number(priceMin) : undefined,
      price_max: priceMax ? Number(priceMax) : undefined,
    })
  }

  const sidebar = (
    <div className="space-y-5">
      {/* Reset */}
      {hasActiveFilters && (
        <button
          onClick={() => { onReset(); setPriceMin(''); setPriceMax('') }}
          className="w-full text-xs text-brand-red hover:text-brand-red-dark font-medium text-left flex items-center gap-1"
        >
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {t('Reset Filters', language)}
        </button>
      )}

      {/* Category */}
      {categories.length > 0 && (
        <FilterSection title={t('Category', language)}>
          <CategoryTree
            categories={categories}
            selected={filters.category}
            onSelect={(slug) => onFilterChange({ category: slug })}
            language={language}
          />
        </FilterSection>
      )}

      {/* Brand */}
      {availableFilters?.brands?.length ? (
        <FilterSection title={t('Brand', language)}>
          <div className="space-y-1.5">
            {availableFilters.brands.map((brand) => (
              <label key={brand} className="flex items-center gap-2.5 cursor-pointer group">
                <input
                  type="checkbox"
                  checked={filters.brand === brand}
                  onChange={(e) => onFilterChange({ brand: e.target.checked ? brand : undefined })}
                  className="w-3.5 h-3.5 rounded border-neutral-300 text-brand-red focus:ring-brand-red/20 cursor-pointer"
                />
                <span className={`text-sm transition-colors ${filters.brand === brand ? 'text-neutral-900 font-medium' : 'text-neutral-600 group-hover:text-neutral-900'}`}>
                  {brand}
                </span>
              </label>
            ))}
          </div>
        </FilterSection>
      ) : null}

      {/* Color */}
      {availableFilters?.colors?.length ? (
        <FilterSection title={t('Color', language)}>
          <div className="flex flex-wrap gap-2">
            {availableFilters.colors.map((color) => {
              const hex = getColorHex(color)
              const isLight = ['white', 'beige', 'silver', 'yellow', 'gold'].includes(color.toLowerCase())
              const isSelected = filters.color === color
              return (
                <button
                  key={color}
                  title={color}
                  onClick={() => onFilterChange({ color: isSelected ? undefined : color })}
                  className={`w-7 h-7 rounded-full flex-shrink-0 transition-all ${
                    isSelected ? 'ring-2 ring-offset-2 ring-neutral-900 scale-110' : 'hover:scale-110'
                  } ${isLight ? 'border border-neutral-300' : ''}`}
                  style={{ backgroundColor: hex }}
                  aria-label={color}
                  aria-pressed={isSelected}
                />
              )
            })}
          </div>
        </FilterSection>
      ) : null}

      {/* Size */}
      {availableFilters?.sizes?.length ? (
        <FilterSection title={t('Size', language)}>
          <div className="flex flex-wrap gap-2">
            {availableFilters.sizes.map((size) => {
              const isSelected = filters.size === size
              return (
                <button
                  key={size}
                  onClick={() => onFilterChange({ size: isSelected ? undefined : size })}
                  className={`px-3 py-1.5 text-sm border rounded-lg transition-colors ${
                    isSelected
                      ? 'bg-neutral-900 text-white border-neutral-900'
                      : 'border-neutral-300 text-neutral-600 hover:border-neutral-500 hover:text-neutral-900'
                  }`}
                >
                  {size}
                </button>
              )
            })}
          </div>
        </FilterSection>
      ) : null}

      {/* Price Range */}
      <FilterSection title={t('Price Range', language)}>
        <div className="space-y-3">
          {/* Range slider visual */}
          {availableFilters && (
            <div className="px-1">
              <input
                type="range"
                min={availableFilters.price_min}
                max={availableFilters.price_max}
                value={priceMax || availableFilters.price_max}
                onChange={(e) => setPriceMax(e.target.value)}
                onMouseUp={applyPrice}
                onTouchEnd={applyPrice}
                className="w-full h-1.5 bg-neutral-200 rounded-full appearance-none cursor-pointer accent-brand-red"
              />
              <div className="flex justify-between text-[11px] text-neutral-400 mt-1">
                <span>{formatIDR(availableFilters.price_min)}</span>
                <span>{formatIDR(availableFilters.price_max)}</span>
              </div>
            </div>
          )}

          {/* Min/Max inputs */}
          <div className="flex gap-2 items-center">
            <input
              type="number"
              value={priceMin}
              onChange={(e) => setPriceMin(e.target.value)}
              placeholder="Min"
              className="w-full px-3 py-2 text-sm border border-neutral-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-brand-red/30 focus:border-brand-red"
            />
            <span className="text-neutral-400 flex-shrink-0">—</span>
            <input
              type="number"
              value={priceMax}
              onChange={(e) => setPriceMax(e.target.value)}
              placeholder="Max"
              className="w-full px-3 py-2 text-sm border border-neutral-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-brand-red/30 focus:border-brand-red"
            />
          </div>
          <button
            onClick={applyPrice}
            className="w-full py-2 text-sm font-medium bg-neutral-900 text-white rounded-lg hover:bg-neutral-700 transition-colors"
          >
            {t('Apply', language)}
          </button>
        </div>
      </FilterSection>

      {/* In Stock Toggle */}
      <div className="flex items-center justify-between py-2">
        <span className="text-sm font-medium text-neutral-700">{t('In Stock Only', language)}</span>
        <button
          role="switch"
          aria-checked={!!filters.in_stock}
          onClick={() => onFilterChange({ in_stock: filters.in_stock ? undefined : true })}
          className={`relative inline-flex h-5 w-9 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus:outline-none ${
            filters.in_stock ? 'bg-brand-red' : 'bg-neutral-200'
          }`}
        >
          <span
            className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition-transform ${
              filters.in_stock ? 'translate-x-4' : 'translate-x-0'
            }`}
          />
        </button>
      </div>
    </div>
  )

  return (
    <>
      {/* Mobile trigger */}
      <button
        className="lg:hidden w-full flex items-center justify-between py-3 px-4 bg-neutral-100 rounded-xl mb-4 text-sm font-medium"
        onClick={() => setMobileOpen(!mobileOpen)}
      >
        <span className="flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          {t('Filters', language)}
          {hasActiveFilters && (
            <span className="bg-brand-red text-white text-[10px] w-4 h-4 rounded-full flex items-center justify-center">
              !
            </span>
          )}
        </span>
        <svg className={`w-4 h-4 text-neutral-500 transition-transform ${mobileOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Desktop: always visible */}
      <div className="hidden lg:block">{sidebar}</div>

      {/* Mobile: collapsible */}
      {mobileOpen && <div className="lg:hidden mb-6 p-4 bg-neutral-50 rounded-xl">{sidebar}</div>}
    </>
  )
}
