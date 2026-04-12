import { useEffect, useState } from 'react'
import { adminService } from '../../services/api.service'
import type { MarketplaceOrder } from '../../types'

const CHANNEL_COLORS: Record<string, string> = {
  SHOPEE: 'bg-orange-100 text-orange-800',
  TOKOPEDIA: 'bg-green-100 text-green-800',
  TIKTOK: 'bg-black text-white',
  LAZADA: 'bg-blue-100 text-blue-800',
}

export default function AdminMarketplacePage() {
  const [orders, setOrders] = useState<MarketplaceOrder[]>([])
  const [loading, setLoading] = useState(true)
  const [channel, setChannel] = useState('')

  useEffect(() => {
    adminService.getMarketplaceOrders({ channel: channel || undefined }).then(({ data }) => setOrders(data.items)).finally(() => setLoading(false))
  }, [channel])

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h1 className="text-2xl font-semibold text-neutral-900">Marketplace Orders</h1>
        <div className="flex gap-2">
          {['', 'SHOPEE', 'TOKOPEDIA', 'TIKTOK', 'LAZADA'].map((ch) => (
            <button key={ch}
              onClick={() => setChannel(ch)}
              className={`px-3 py-1.5 text-xs font-medium rounded-full border transition-colors ${
                channel === ch ? 'bg-neutral-900 text-white border-neutral-900' : 'border-neutral-200 text-neutral-600 hover:border-neutral-400'
              }`}>
              {ch || 'All'}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
        {loading ? (
          <div className="p-6 space-y-3">{[...Array(5)].map((_, i) => <div key={i} className="skeleton h-12 rounded-lg" />)}</div>
        ) : orders.length === 0 ? (
          <div className="text-center py-12 text-neutral-400">No marketplace orders</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-neutral-50 border-b border-neutral-200">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-neutral-700">External ID</th>
                <th className="px-4 py-3 text-left font-medium text-neutral-700">Channel</th>
                <th className="px-4 py-3 text-left font-medium text-neutral-700">Sync Status</th>
                <th className="px-4 py-3 text-left font-medium text-neutral-700">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100">
              {orders.map((o) => (
                <tr key={o.id} className="hover:bg-neutral-50">
                  <td className="px-4 py-3 font-mono text-xs text-neutral-700">{o.external_order_id}</td>
                  <td className="px-4 py-3"><span className={`badge ${CHANNEL_COLORS[o.channel]}`}>{o.channel}</span></td>
                  <td className="px-4 py-3"><span className="badge bg-neutral-100 text-neutral-600">{o.sync_status}</span></td>
                  <td className="px-4 py-3 text-neutral-500">{new Date(o.created_at).toLocaleDateString('id-ID')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
