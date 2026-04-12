import { useState } from 'react'
import { dashboardService } from '../../services/api.service'
import type { Shipment } from '../../types'

export default function DashboardTrackingPage() {
  const [orderNum, setOrderNum] = useState('')
  const [shipment, setShipment] = useState<Shipment | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!orderNum.trim()) return
    setLoading(true)
    setError('')
    try {
      const { data } = await dashboardService.getTracking(orderNum.trim())
      setShipment(data)
    } catch {
      setError('Order not found or not shipped yet')
      setShipment(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-semibold text-neutral-900">Track Shipment</h1>

      <div className="card">
        <form onSubmit={handleSearch} className="flex gap-3">
          <input type="text" value={orderNum} onChange={(e) => setOrderNum(e.target.value)}
            placeholder="Enter order number (e.g. PHX-20260412-001)"
            className="input flex-1" />
          <button type="submit" disabled={loading} className="btn-primary px-6">
            {loading ? 'Searching...' : 'Track'}
          </button>
        </form>
        {error && <p className="text-sm text-red-600 mt-3">{error}</p>}
      </div>

      {shipment && (
        <div className="card">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-sm text-neutral-500">Courier</p>
              <p className="font-semibold text-neutral-900">{shipment.courier}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-neutral-500">Tracking Number</p>
              <p className="font-mono font-medium text-neutral-900">{shipment.tracking_number}</p>
            </div>
          </div>

          {shipment.estimated_delivery && (
            <div className="bg-neutral-50 rounded-lg p-3 mb-4 text-sm">
              Estimated delivery: <span className="font-medium">{new Date(shipment.estimated_delivery).toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'long' })}</span>
            </div>
          )}

          <h2 className="text-sm font-semibold text-neutral-900 mb-4">Tracking History</h2>
          <div className="relative">
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-neutral-200" />
            <div className="space-y-4">
              {shipment.events?.map((ev, i) => (
                <div key={i} className="flex gap-4 relative">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 z-10 ${i === 0 ? 'bg-brand-red' : 'bg-neutral-200'}`}>
                    <svg className={`w-4 h-4 ${i === 0 ? 'text-white' : 'text-neutral-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div className="pb-4">
                    <p className="text-sm font-medium text-neutral-900">{ev.status}</p>
                    {ev.description && <p className="text-xs text-neutral-500">{ev.description}</p>}
                    {ev.location && <p className="text-xs text-neutral-400">{ev.location}</p>}
                    <p className="text-xs text-neutral-400 mt-0.5">{new Date(ev.timestamp).toLocaleString('id-ID')}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
