import { useState, useEffect, useCallback } from 'react'
import { useAppSelector } from '../../app/hooks'
import { adminService, catalogService } from '../../services/api.service'
import { formatIDR } from '../../utils/currency'
import { Plus, Trash2, Search, X, PackagePlus } from 'lucide-react'

interface Variant {
  sku: string
  color: string
  size: string
  variant_type: string
  price_override: string
  stock_quantity: string
  weight_grams: string
  barcode: string
}

interface ImageRow {
  image_url: string
  alt_text: string
}

const EMPTY_VARIANT: Variant = { sku: '', color: '', size: '', variant_type: '', price_override: '', stock_quantity: '0', weight_grams: '', barcode: '' }
const EMPTY_IMAGE: ImageRow = { image_url: '', alt_text: '' }

export default function AdminProductsPage() {
  const { language } = useAppSelector((s) => s.ui)

  // List state
  const [products, setProducts] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [searchQ, setSearchQ] = useState('')
  const [loading, setLoading] = useState(false)

  // Delete confirmation modal state
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null)
  const [confirmDeleteName, setConfirmDeleteName] = useState('')

  // Form state
  const [showForm, setShowForm] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [formError, setFormError] = useState('')
  const [categories, setCategories] = useState<any[]>([])

  const [nameId, setNameId] = useState('')
  const [nameEn, setNameEn] = useState('')
  const [descId, setDescId] = useState('')
  const [descEn, setDescEn] = useState('')
  const [brand, setBrand] = useState('')
  const [basePrice, setBasePrice] = useState('')
  const [isActive, setIsActive] = useState(true)
  const [selectedCats, setSelectedCats] = useState<number[]>([])
  const [variants, setVariants] = useState<Variant[]>([{ ...EMPTY_VARIANT }])
  const [images, setImages] = useState<ImageRow[]>([{ ...EMPTY_IMAGE }])

  const PER_PAGE = 20

  const loadProducts = useCallback(async () => {
    setLoading(true)
    try {
      const res = await adminService.getProducts({ page, per_page: PER_PAGE, search: searchQ || undefined })
      setProducts(res.data.items)
      setTotal(res.data.total)
    } catch {
      // ignore
    } finally {
      setLoading(false)
    }
  }, [page, searchQ])

  useEffect(() => { loadProducts() }, [loadProducts])

  useEffect(() => {
    catalogService.getCategories().then((res) => setCategories(res.data)).catch(() => {})
  }, [])

  const resetForm = () => {
    setNameId(''); setNameEn(''); setDescId(''); setDescEn('')
    setBrand(''); setBasePrice(''); setIsActive(true); setSelectedCats([])
    setVariants([{ ...EMPTY_VARIANT }]); setImages([{ ...EMPTY_IMAGE }])
    setFormError('')
  }

  const toggleCat = (id: number) =>
    setSelectedCats((prev) => prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id])

  const updateVariant = (idx: number, field: keyof Variant, value: string) =>
    setVariants((prev) => prev.map((v, i) => i === idx ? { ...v, [field]: value } : v))

  const updateImage = (idx: number, field: keyof ImageRow, value: string) =>
    setImages((prev) => prev.map((img, i) => i === idx ? { ...img, [field]: value } : img))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError('')
    if (!nameId.trim() || !nameEn.trim()) { setFormError('Nama produk (ID & EN) wajib diisi'); return }
    if (!basePrice || isNaN(Number(basePrice)) || Number(basePrice) < 0) { setFormError('Harga dasar tidak valid'); return }
    for (const v of variants) {
      if (!v.sku.trim()) { setFormError('Setiap varian harus memiliki SKU'); return }
    }

    setSubmitting(true)
    try {
      await adminService.createProduct({
        name_id: nameId.trim(),
        name_en: nameEn.trim(),
        description_id: descId.trim() || undefined,
        description_en: descEn.trim() || undefined,
        brand: brand.trim() || undefined,
        base_price: Number(basePrice),
        is_active: isActive,
        category_ids: selectedCats,
        variants: variants.map((v) => ({
          sku: v.sku.trim(),
          color: v.color.trim() || undefined,
          size: v.size.trim() || undefined,
          variant_type: v.variant_type.trim() || undefined,
          price_override: v.price_override ? Number(v.price_override) : undefined,
          stock_quantity: Number(v.stock_quantity) || 0,
          weight_grams: v.weight_grams ? Number(v.weight_grams) : undefined,
          barcode: v.barcode.trim() || undefined,
        })),
        images: images.filter((img) => img.image_url.trim()).map((img) => ({
          image_url: img.image_url.trim(),
          alt_text: img.alt_text.trim() || undefined,
        })),
      })
      resetForm()
      setShowForm(false)
      loadProducts()
    } catch (err: any) {
      setFormError(err?.response?.data?.detail || 'Gagal menyimpan produk')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDeleteClick = (id: number, name: string) => {
    setConfirmDeleteId(id)
    setConfirmDeleteName(name)
  }

  const handleDeleteConfirm = async () => {
    if (confirmDeleteId === null) return
    try {
      await adminService.deleteProduct(confirmDeleteId)
      loadProducts()
    } catch {
      // ignore
    } finally {
      setConfirmDeleteId(null)
      setConfirmDeleteName('')
    }
  }

  const handleDeleteCancel = () => {
    setConfirmDeleteId(null)
    setConfirmDeleteName('')
  }

  const pages = Math.max(1, Math.ceil(total / PER_PAGE))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-neutral-900">
            {language === 'id' ? 'Manajemen Produk' : 'Product Management'}
          </h1>
          <p className="text-sm text-neutral-500 mt-0.5">{total} {language === 'id' ? 'total produk' : 'total products'}</p>
        </div>
        <button
          onClick={() => { resetForm(); setShowForm(true) }}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={16} />
          {language === 'id' ? 'Tambah Produk' : 'Add Product'}
        </button>
      </div>

      {/* Search */}
      <div className="relative max-w-sm">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400" />
        <input
          type="text"
          value={searchQ}
          onChange={(e) => { setSearchQ(e.target.value); setPage(1) }}
          placeholder={language === 'id' ? 'Cari produk...' : 'Search products...'}
          className="input pl-10 py-2 text-sm"
        />
      </div>

      {/* Product Table */}
      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-neutral-50 border-b border-neutral-100">
              <tr>
                <th className="text-left py-3 px-4 font-semibold text-neutral-600">
                  {language === 'id' ? 'Produk' : 'Product'}
                </th>
                <th className="text-left py-3 px-4 font-semibold text-neutral-600">Brand</th>
                <th className="text-right py-3 px-4 font-semibold text-neutral-600">
                  {language === 'id' ? 'Harga' : 'Price'}
                </th>
                <th className="text-center py-3 px-4 font-semibold text-neutral-600">
                  {language === 'id' ? 'Varian' : 'Variants'}
                </th>
                <th className="text-center py-3 px-4 font-semibold text-neutral-600">Status</th>
                <th className="py-3 px-4" />
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-50">
              {loading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i}>
                    {Array.from({ length: 6 }).map((_, j) => (
                      <td key={j} className="py-3 px-4">
                        <div className="h-4 bg-neutral-100 rounded animate-pulse" />
                      </td>
                    ))}
                  </tr>
                ))
              ) : products.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-16 text-center text-neutral-400">
                    <PackagePlus size={32} className="mx-auto mb-2 opacity-30" />
                    <p className="font-medium">{language === 'id' ? 'Belum ada produk' : 'No products yet'}</p>
                  </td>
                </tr>
              ) : (
                products.map((p) => (
                  <tr key={p.id} className="hover:bg-neutral-50/60 transition-colors">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-3">
                        {p.primary_image_url ? (
                          <img src={p.primary_image_url} alt={p.name_en} className="w-10 h-10 rounded-lg object-cover border border-neutral-100" />
                        ) : (
                          <div className="w-10 h-10 rounded-lg bg-neutral-100 flex items-center justify-center text-neutral-300">
                            <PackagePlus size={18} />
                          </div>
                        )}
                        <div>
                          <p className="font-semibold text-neutral-900">{language === 'id' ? p.name_id : p.name_en}</p>
                          <p className="text-[11px] text-neutral-400">{p.slug}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-neutral-500">{p.brand || '—'}</td>
                    <td className="py-3 px-4 text-right font-semibold">{formatIDR(p.base_price)}</td>
                    <td className="py-3 px-4 text-center">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-neutral-100 text-neutral-600">
                        {p.variants?.length ?? 0}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold ${p.status === 'ACTIVE' ? 'bg-emerald-50 text-emerald-700' : 'bg-neutral-100 text-neutral-500'}`}>
                        {p.status === 'ACTIVE' ? (language === 'id' ? 'Aktif' : 'Active') : (language === 'id' ? 'Nonaktif' : 'Inactive')}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={() => handleDeleteClick(p.id, language === 'id' ? p.name_id : p.name_en)}
                          className="p-1.5 text-neutral-400 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-colors"
                          title={language === 'id' ? 'Hapus' : 'Delete'}
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {pages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-neutral-100 bg-neutral-50/50">
            <p className="text-sm text-neutral-500">
              {language === 'id' ? `Halaman ${page} dari ${pages}` : `Page ${page} of ${pages}`}
            </p>
            <div className="flex gap-2">
              <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1} className="btn-secondary py-1.5 px-3 text-sm disabled:opacity-40">
                {language === 'id' ? 'Sebelumnya' : 'Previous'}
              </button>
              <button onClick={() => setPage((p) => Math.min(pages, p + 1))} disabled={page === pages} className="btn-secondary py-1.5 px-3 text-sm disabled:opacity-40">
                {language === 'id' ? 'Berikutnya' : 'Next'}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {confirmDeleteId !== null && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center px-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 animate-in fade-in zoom-in-95">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-xl bg-rose-100 flex items-center justify-center flex-shrink-0">
                <Trash2 size={18} className="text-rose-500" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-base font-black text-neutral-900 mb-1">
                  {language === 'id' ? 'Hapus Produk?' : 'Delete Product?'}
                </h3>
                <p className="text-sm text-neutral-500 leading-relaxed">
                  {language === 'id'
                    ? <>Produk <span className="font-semibold text-neutral-700">"{confirmDeleteName}"</span> akan dihapus permanen beserta semua varian dan gambarnya. Tindakan ini tidak bisa dibatalkan.</>
                    : <><span className="font-semibold text-neutral-700">"{confirmDeleteName}"</span> and all its variants and images will be permanently deleted. This cannot be undone.</>
                  }
                </p>
              </div>
            </div>
            <div className="flex items-center justify-end gap-3 mt-6">
              <button
                onClick={handleDeleteCancel}
                className="btn-secondary"
              >
                {language === 'id' ? 'Batal' : 'Cancel'}
              </button>
              <button
                onClick={handleDeleteConfirm}
                className="px-4 py-2 bg-rose-500 hover:bg-rose-600 text-white text-sm font-bold rounded-xl transition-colors flex items-center gap-2"
              >
                <Trash2 size={14} />
                {language === 'id' ? 'Ya, Hapus Permanen' : 'Yes, Delete'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Product Modal */}
      {showForm && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-start justify-center overflow-y-auto py-8 px-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-neutral-100">
              <h2 className="text-lg font-black text-neutral-900">
                {language === 'id' ? 'Tambah Produk Baru' : 'Add New Product'}
              </h2>
              <button onClick={() => setShowForm(false)} className="p-2 text-neutral-400 hover:text-neutral-700 hover:bg-neutral-50 rounded-xl transition-colors">
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              {formError && (
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-100 text-rose-700 text-sm font-medium">
                  {formError}
                </div>
              )}

              {/* Basic Info */}
              <section>
                <h3 className="text-sm font-black text-neutral-700 uppercase tracking-widest mb-3">
                  {language === 'id' ? 'Informasi Dasar' : 'Basic Info'}
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="label">Nama (Bahasa Indonesia) *</label>
                    <input type="text" value={nameId} onChange={(e) => setNameId(e.target.value)} className="input" placeholder="contoh: Kacamata Hitam Elegan" required />
                  </div>
                  <div>
                    <label className="label">Name (English) *</label>
                    <input type="text" value={nameEn} onChange={(e) => setNameEn(e.target.value)} className="input" placeholder="e.g. Elegant Black Sunglasses" required />
                  </div>
                  <div>
                    <label className="label">{language === 'id' ? 'Merek' : 'Brand'}</label>
                    <input type="text" value={brand} onChange={(e) => setBrand(e.target.value)} className="input" placeholder="e.g. Ray-Ban" />
                  </div>
                  <div>
                    <label className="label">{language === 'id' ? 'Harga Dasar (IDR)' : 'Base Price (IDR)'} *</label>
                    <input type="number" min="0" step="1000" value={basePrice} onChange={(e) => setBasePrice(e.target.value)} className="input" placeholder="150000" required />
                  </div>
                  <div className="sm:col-span-2">
                    <label className="label">Deskripsi (Bahasa Indonesia)</label>
                    <textarea rows={3} value={descId} onChange={(e) => setDescId(e.target.value)} className="input resize-none" placeholder="Deskripsi produk dalam Bahasa Indonesia..." />
                  </div>
                  <div className="sm:col-span-2">
                    <label className="label">Description (English)</label>
                    <textarea rows={3} value={descEn} onChange={(e) => setDescEn(e.target.value)} className="input resize-none" placeholder="Product description in English..." />
                  </div>
                  <div className="sm:col-span-2 flex items-center gap-3">
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} className="sr-only peer" />
                      <div className="w-10 h-5 bg-neutral-200 peer-focus:ring-2 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-5 after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary-600" />
                    </label>
                    <span className="text-sm font-medium text-neutral-700">
                      {language === 'id' ? 'Produk Aktif (ditampilkan di toko)' : 'Active (visible in storefront)'}
                    </span>
                  </div>
                </div>
              </section>

              {/* Categories */}
              {categories.length > 0 && (
                <section>
                  <h3 className="text-sm font-black text-neutral-700 uppercase tracking-widest mb-3">
                    {language === 'id' ? 'Kategori' : 'Categories'}
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {categories.map((cat: any) => (
                      <button
                        key={cat.id}
                        type="button"
                        onClick={() => toggleCat(cat.id)}
                        className={`px-3 py-1.5 rounded-xl text-sm font-semibold border transition-all ${
                          selectedCats.includes(cat.id)
                            ? 'bg-primary-600 text-white border-primary-600'
                            : 'bg-white text-neutral-600 border-neutral-200 hover:border-primary-300'
                        }`}
                      >
                        {language === 'id' ? cat.name_id : cat.name_en}
                      </button>
                    ))}
                  </div>
                </section>
              )}

              {/* Variants */}
              <section>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-black text-neutral-700 uppercase tracking-widest">
                    {language === 'id' ? 'Varian Produk' : 'Product Variants'}
                  </h3>
                  <button
                    type="button"
                    onClick={() => setVariants((prev) => [...prev, { ...EMPTY_VARIANT }])}
                    className="text-xs font-bold text-primary-600 hover:text-primary-700 flex items-center gap-1"
                  >
                    <Plus size={13} />
                    {language === 'id' ? 'Tambah Varian' : 'Add Variant'}
                  </button>
                </div>
                <div className="space-y-3">
                  {variants.map((v, idx) => (
                    <div key={idx} className="p-4 rounded-xl border border-neutral-200 bg-neutral-50/50 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-black text-neutral-500 uppercase tracking-wider">
                          {language === 'id' ? `Varian ${idx + 1}` : `Variant ${idx + 1}`}
                        </span>
                        {variants.length > 1 && (
                          <button type="button" onClick={() => setVariants((prev) => prev.filter((_, i) => i !== idx))} className="text-rose-400 hover:text-rose-600 transition-colors">
                            <X size={14} />
                          </button>
                        )}
                      </div>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                        <div className="sm:col-span-2">
                          <label className="label">SKU *</label>
                          <input type="text" value={v.sku} onChange={(e) => updateVariant(idx, 'sku', e.target.value)} className="input py-2 text-sm" placeholder="KCM-BLK-L" required />
                        </div>
                        <div>
                          <label className="label">{language === 'id' ? 'Warna' : 'Color'}</label>
                          <input type="text" value={v.color} onChange={(e) => updateVariant(idx, 'color', e.target.value)} className="input py-2 text-sm" placeholder="Black" />
                        </div>
                        <div>
                          <label className="label">{language === 'id' ? 'Ukuran' : 'Size'}</label>
                          <input type="text" value={v.size} onChange={(e) => updateVariant(idx, 'size', e.target.value)} className="input py-2 text-sm" placeholder="L" />
                        </div>
                        <div>
                          <label className="label">{language === 'id' ? 'Harga Override' : 'Price Override'}</label>
                          <input type="number" min="0" value={v.price_override} onChange={(e) => updateVariant(idx, 'price_override', e.target.value)} className="input py-2 text-sm" placeholder={language === 'id' ? 'Kosong = harga dasar' : 'Empty = base price'} />
                        </div>
                        <div>
                          <label className="label">{language === 'id' ? 'Stok' : 'Stock'}</label>
                          <input type="number" min="0" value={v.stock_quantity} onChange={(e) => updateVariant(idx, 'stock_quantity', e.target.value)} className="input py-2 text-sm" placeholder="0" />
                        </div>
                        <div>
                          <label className="label">{language === 'id' ? 'Berat (gram)' : 'Weight (g)'}</label>
                          <input type="number" min="0" value={v.weight_grams} onChange={(e) => updateVariant(idx, 'weight_grams', e.target.value)} className="input py-2 text-sm" placeholder="200" />
                        </div>
                        <div>
                          <label className="label">Barcode</label>
                          <input type="text" value={v.barcode} onChange={(e) => updateVariant(idx, 'barcode', e.target.value)} className="input py-2 text-sm" placeholder="8991234567890" />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              {/* Images */}
              <section>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-black text-neutral-700 uppercase tracking-widest">
                    {language === 'id' ? 'Gambar Produk' : 'Product Images'}
                  </h3>
                  <button
                    type="button"
                    onClick={() => setImages((prev) => [...prev, { ...EMPTY_IMAGE }])}
                    className="text-xs font-bold text-primary-600 hover:text-primary-700 flex items-center gap-1"
                  >
                    <Plus size={13} />
                    {language === 'id' ? 'Tambah Gambar' : 'Add Image'}
                  </button>
                </div>
                <div className="space-y-2">
                  {images.map((img, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <div className="flex-1">
                        <input
                          type="url"
                          value={img.image_url}
                          onChange={(e) => updateImage(idx, 'image_url', e.target.value)}
                          className="input py-2 text-sm"
                          placeholder={`${language === 'id' ? 'URL Gambar' : 'Image URL'} ${idx + 1}${idx === 0 ? ' (primary)' : ''}`}
                        />
                      </div>
                      <div className="w-40">
                        <input
                          type="text"
                          value={img.alt_text}
                          onChange={(e) => updateImage(idx, 'alt_text', e.target.value)}
                          className="input py-2 text-sm"
                          placeholder="Alt text"
                        />
                      </div>
                      {images.length > 1 && (
                        <button type="button" onClick={() => setImages((prev) => prev.filter((_, i) => i !== idx))} className="text-rose-400 hover:text-rose-600 transition-colors flex-shrink-0">
                          <X size={14} />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
                <p className="text-xs text-neutral-400 mt-1.5">
                  {language === 'id' ? 'Gambar pertama akan dijadikan gambar utama.' : 'First image will be used as primary.'}
                </p>
              </section>

              {/* Actions */}
              <div className="flex items-center justify-end gap-3 pt-2 border-t border-neutral-100">
                <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">
                  {language === 'id' ? 'Batal' : 'Cancel'}
                </button>
                <button type="submit" disabled={submitting} className="btn-primary flex items-center gap-2 disabled:opacity-60">
                  {submitting ? (
                    <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />{language === 'id' ? 'Menyimpan...' : 'Saving...'}</>
                  ) : (
                    <><Plus size={15} />{language === 'id' ? 'Simpan Produk' : 'Save Product'}</>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
