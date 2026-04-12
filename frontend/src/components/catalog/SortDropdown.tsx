import { useAppSelector } from '../../app/hooks'
import { t } from '../../utils/i18n'
import type { ProductFilters } from '../../types'

interface Props {
  value: ProductFilters['sort']
  onChange: (sort: ProductFilters['sort']) => void
  total: number
}

const SORT_OPTIONS: { value: NonNullable<ProductFilters['sort']>; labelKey: string }[] = [
  { value: 'newest', labelKey: 'Newest' },
  { value: 'price_asc', labelKey: 'Price Low to High' },
  { value: 'price_desc', labelKey: 'Price High to Low' },
  { value: 'popular', labelKey: 'Most Popular' },
  { value: 'rating', labelKey: 'Highest Rated' },
]

export default function SortDropdown({ value, onChange, total }: Props) {
  const { language } = useAppSelector((s) => s.ui)

  return (
    <div className="flex items-center justify-between mb-6 gap-4">
      <p className="text-sm text-neutral-500 flex-shrink-0">
        <span className="font-medium text-neutral-900">{total.toLocaleString()}</span>{' '}
        {t('products', language)}
      </p>
      <div className="flex items-center gap-2">
        <label className="text-sm text-neutral-500 hidden sm:block flex-shrink-0">Urutkan:</label>
        <select
          value={value ?? 'newest'}
          onChange={(e) => onChange(e.target.value as ProductFilters['sort'])}
          className="text-sm border border-neutral-300 rounded-lg px-3 py-2 bg-white text-neutral-700 focus:outline-none focus:ring-2 focus:ring-brand-red/20 focus:border-brand-red cursor-pointer"
        >
          {SORT_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {t(opt.labelKey, language)}
            </option>
          ))}
        </select>
      </div>
    </div>
  )
}
