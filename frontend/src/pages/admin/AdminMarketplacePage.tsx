import { useEffect, useState } from 'react'
import { adminService } from '../../services/api.service'
import type { MarketplaceOrder } from '../../types'

const CHANNEL_CLASSES: Record<string, string> = {
  SHOPEE: 'bg-[#EE4D2D] text-white',
  TOKOPEDIA: 'bg-[#03AC0E] text-white',
  TIKTOK: 'bg-black text-white',
  LAZADA: 'bg-[#121A6A] text-white',
}

export default function AdminMarketplacePage() {
  const [orders, setOrders] = useState<MarketplaceOrder[]>([])
  const [loading, setLoading] = useState(true)
  const [channel, setChannel] = useState('')

  useEffect(() => {
    adminService.getMarketplaceOrders({ channel: channel || undefined }).then(({ data }) => setOrders(data.items)).finally(() => setLoading(false))
  }, [channel])

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <header className="flex flex-col gap-1">
          <h1 className="text-3xl font-bold tracking-tight text-neutral-900 sm:text-4xl">
            Marketplace <span className="text-gradient">Orders</span>
          </h1>
          <p className="text-neutral-500 text-sm">Monitor orders synced from external channels.</p>
        </header>

        <div className="flex bg-neutral-100 p-1 rounded-xl w-fit">
          {['', 'SHOPEE', 'TOKOPEDIA', 'TIKTOK', 'LAZADA'].map((ch) => (
            <button key={ch}
              onClick={() => setChannel(ch)}
              className={`px-4 py-2 text-xs font-bold rounded-lg transition-all duration-200 ${
                channel === ch 
                  ? 'bg-white text-primary-600 shadow-sm' 
                  : 'text-neutral-500 hover:text-neutral-900'
              }`}>
              {ch || 'All Channels'}
            </button>
          ))}
        </div>
      </div>

      <div className="data-table-container">
        {loading ? (
          <div className="p-8 space-y-4">
            {[...Array(6)].map((_, i) => <div key={i} className="skeleton h-14 rounded-xl" />)}
          </div>
        ) : orders.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-neutral-400">
            <div className="text-4xl mb-4">🏪</div>
            <p className="font-medium">No marketplace orders found</p>
          </div>
        ) : (
          <div className="overflow-x-auto scrollbar-hide">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-neutral-50/50 border-b border-neutral-100">
                  <th className="px-6 py-4 text-left font-semibold text-neutral-600 uppercase tracking-wider text-[10px]">External Order ID</th>
                  <th className="px-6 py-4 text-left font-semibold text-neutral-600 uppercase tracking-wider text-[10px]">Sales Channel</th>
                  <th className="px-6 py-4 text-left font-semibold text-neutral-600 uppercase tracking-wider text-[10px]">Sync Status</th>
                  <th className="px-6 py-4 text-right font-semibold text-neutral-600 uppercase tracking-wider text-[10px]">Sync Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-50">
                {orders.map((o) => (
                  <tr key={o.id} className="data-table-row group">
                    <td className="px-6 py-4">
                      <span className="font-mono text-[11px] font-bold text-neutral-500 bg-neutral-100 px-2 py-1 rounded border border-neutral-200">
                        {o.external_order_id}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest shadow-sm ${CHANNEL_CLASSES[o.channel] || 'bg-neutral-900 text-white'}`}>
                        {o.channel}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="badge bg-primary-50 text-primary-600 border border-primary-100">
                        {o.sync_status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="text-neutral-500 font-medium">
                        {new Date(o.created_at).toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' })}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
