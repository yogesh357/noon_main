import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../../app/hooks'
import { fetchCart } from '../../features/cart/cartSlice'
import { checkoutService, dashboardService, cartService } from '../../services/api.service'
import { showToast } from '../../features/ui/uiSlice'
import { formatIDR } from '../../utils/currency'
import type { Address, ShippingRate } from '../../types'

export default function CheckoutPage() {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const { cart } = useAppSelector((s) => s.cart)
  const { user } = useAppSelector((s) => s.auth)
  const { language } = useAppSelector((s) => s.ui)

  const [addresses, setAddresses] = useState<Address[]>([])
  const [selectedAddressId, setSelectedAddressId] = useState<number | null>(null)
  const [shippingRates, setShippingRates] = useState<ShippingRate[]>([])
  const [selectedRate, setSelectedRate] = useState<ShippingRate | null>(null)
  const [notes, setNotes] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingRates, setLoadingRates] = useState(false)

  useEffect(() => {
    if (!user) { navigate('/auth/login', { state: { from: '/checkout' } }); return }
    dispatch(fetchCart())
    dashboardService.getAddresses().then(({ data }) => {
      setAddresses(data)
      const def = data.find((a) => a.is_default) ?? data[0]
      if (def) setSelectedAddressId(def.id)
    })
  }, [user])

  useEffect(() => {
    if (!selectedAddressId) return
    setLoadingRates(true)
    cartService.getShippingRates(selectedAddressId)
      .then(({ data }) => { setShippingRates(data); setSelectedRate(data[0] ?? null) })
      .catch(() => { /* ignore */ })
      .finally(() => setLoadingRates(false))
  }, [selectedAddressId])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedAddressId || !selectedRate) return
    setLoading(true)
    try {
      const { data } = await checkoutService.checkout({
        address_id: selectedAddressId,
        shipping_method: selectedRate.service,
        courier: selectedRate.courier,
        notes: notes || undefined,
      })
      if (data.payment_url) window.location.href = data.payment_url
      else navigate(`/order/success/${data.order.order_number}`)
    } catch {
      dispatch(showToast({ message: 'Checkout failed. Please try again.', type: 'error' }))
    } finally {
      setLoading(false)
    }
  }

  const items = cart?.items ?? []
  const subtotal = cart?.subtotal ?? 0
  const shippingCost = selectedRate?.cost ?? 0
  const total = subtotal + shippingCost

  if (items.length === 0) {
    navigate('/cart')
    return null
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold text-neutral-900 mb-8">
        {language === 'id' ? 'Checkout' : 'Checkout'}
      </h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="lg:grid lg:grid-cols-5 lg:gap-8">
          <div className="lg:col-span-3 space-y-6">
            {/* Address */}
            <div className="card">
              <h2 className="font-semibold text-neutral-900 mb-4">
                {language === 'id' ? 'Alamat Pengiriman' : 'Shipping Address'}
              </h2>
              <div className="space-y-3">
                {addresses.map((addr) => (
                  <label key={addr.id} className={`flex gap-3 p-3 rounded-xl border cursor-pointer transition-colors ${
                    selectedAddressId === addr.id ? 'border-brand-red bg-brand-red/5' : 'border-neutral-200 hover:border-neutral-300'
                  }`}>
                    <input type="radio" name="address" value={addr.id}
                      checked={selectedAddressId === addr.id}
                      onChange={() => setSelectedAddressId(addr.id)}
                      className="mt-0.5 text-brand-red focus:ring-brand-red" />
                    <div className="text-sm">
                      <p className="font-medium text-neutral-900">{addr.name} · {addr.phone}</p>
                      <p className="text-neutral-500">{addr.street}, {addr.city}, {addr.province} {addr.postal_code}</p>
                      {addr.is_default && <span className="text-[11px] text-brand-red font-medium">Default</span>}
                    </div>
                  </label>
                ))}
                {addresses.length === 0 && (
                  <p className="text-sm text-neutral-500">
                    No addresses saved.{' '}
                    <a href="/dashboard/addresses" className="text-brand-red">Add one</a>
                  </p>
                )}
              </div>
            </div>

            {/* Shipping */}
            <div className="card">
              <h2 className="font-semibold text-neutral-900 mb-4">
                {language === 'id' ? 'Metode Pengiriman' : 'Shipping Method'}
              </h2>
              {loadingRates ? (
                <div className="space-y-2">
                  {[...Array(3)].map((_, i) => <div key={i} className="skeleton h-14 rounded-xl" />)}
                </div>
              ) : shippingRates.length > 0 ? (
                <div className="space-y-2">
                  {shippingRates.map((rate, i) => (
                    <label key={i} className={`flex items-center justify-between p-3.5 rounded-xl border cursor-pointer transition-colors ${
                      selectedRate?.service === rate.service && selectedRate?.courier === rate.courier
                        ? 'border-brand-red bg-brand-red/5'
                        : 'border-neutral-200 hover:border-neutral-300'
                    }`}>
                      <div className="flex items-center gap-3">
                        <input type="radio" name="shipping" value={`${rate.courier}-${rate.service}`}
                          checked={selectedRate?.service === rate.service && selectedRate?.courier === rate.courier}
                          onChange={() => setSelectedRate(rate)}
                          className="text-brand-red focus:ring-brand-red" />
                        <div>
                          <p className="text-sm font-medium text-neutral-900">{rate.courier} — {rate.service}</p>
                          <p className="text-xs text-neutral-500">{rate.estimated_days}</p>
                        </div>
                      </div>
                      <span className="text-sm font-semibold text-neutral-900">{formatIDR(rate.cost)}</span>
                    </label>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-neutral-500">Select an address to see shipping options</p>
              )}
            </div>

            {/* Notes */}
            <div className="card">
              <h2 className="font-semibold text-neutral-900 mb-3">
                {language === 'id' ? 'Catatan Pesanan (opsional)' : 'Order Notes (optional)'}
              </h2>
              <textarea value={notes} onChange={(e) => setNotes(e.target.value)}
                rows={3} placeholder={language === 'id' ? 'Catatan untuk penjual...' : 'Notes for seller...'}
                className="input resize-none" />
            </div>
          </div>

          {/* Summary */}
          <div className="lg:col-span-2 mt-6 lg:mt-0">
            <div className="card sticky top-8">
              <h2 className="font-semibold text-neutral-900 mb-4">
                {language === 'id' ? 'Ringkasan Pesanan' : 'Order Summary'}
              </h2>
              <div className="space-y-3 mb-4">
                {items.map((item) => (
                  <div key={item.id} className="flex gap-3">
                    <div className="w-12 h-12 bg-neutral-100 rounded-lg overflow-hidden flex-shrink-0">
                      <img src={item.image_url ?? '/placeholder.svg'} alt={item.product_name}
                        className="w-full h-full object-cover" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-neutral-900 line-clamp-1">{item.product_name}</p>
                      <p className="text-xs text-neutral-500">{item.variant_label} × {item.quantity}</p>
                    </div>
                    <span className="text-sm font-medium text-neutral-900 flex-shrink-0">
                      {formatIDR(item.price * item.quantity)}
                    </span>
                  </div>
                ))}
              </div>
              <div className="border-t border-neutral-100 pt-4 space-y-2 text-sm">
                <div className="flex justify-between text-neutral-600">
                  <span>Subtotal</span>
                  <span>{formatIDR(subtotal)}</span>
                </div>
                <div className="flex justify-between text-neutral-600">
                  <span>{language === 'id' ? 'Ongkir' : 'Shipping'}</span>
                  <span>{selectedRate ? formatIDR(shippingCost) : '—'}</span>
                </div>
                <div className="flex justify-between font-semibold text-neutral-900 text-base pt-2 border-t border-neutral-100">
                  <span>Total</span>
                  <span>{formatIDR(total)}</span>
                </div>
              </div>
              <button type="submit" disabled={loading || !selectedAddressId || !selectedRate}
                className="btn-primary w-full mt-5 py-3.5">
                {loading ? (
                  <span className="flex items-center gap-2 justify-center">
                    <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    {language === 'id' ? 'Memproses...' : 'Processing...'}
                  </span>
                ) : language === 'id' ? 'Bayar Sekarang' : 'Pay Now'}
              </button>
              <p className="text-xs text-neutral-400 text-center mt-3 flex items-center justify-center gap-1">
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                {language === 'id' ? 'Transaksi aman & terenkripsi' : 'Secured by SSL encryption'}
              </p>
            </div>
          </div>
        </div>
      </form>
    </div>
  )
}
