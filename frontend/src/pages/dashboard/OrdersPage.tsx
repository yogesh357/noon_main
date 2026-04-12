import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { dashboardService } from '../../services/api.service'
import { formatIDR } from '../../utils/currency'
import type { Order, OrderStatus } from '../../types'

const STATUSES: { value: string; label: string }[] = [
  { value: '', label: 'All' },
  { value: 'PENDING_PAYMENT', label: 'Awaiting Payment' },
  { value: 'PROCESSING', label: 'Processing' },
  { value: 'SHIPPED', label: 'Shipped' },
  { value: 'DELIVERED', label: 'Delivered' },
  { value: 'CANCELLED', label: 'Cancelled' },
]

const STATUS_BADGE: Record<string, string> = {
  PENDING_PAYMENT: 'bg-yellow-100 text-yellow-800',
  ACCEPTED: 'bg-blue-100 text-blue-800',
  PROCESSING: 'bg-blue-100 text-blue-800',
  PICKING: 'bg-indigo-100 text-indigo-800',
  PACKING: 'bg-indigo-100 text-indigo-800',
  READY_TO_SHIP: 'bg-purple-100 text-purple-800',
  SHIPPED: 'bg-indigo-100 text-indigo-800',
  DELIVERED: 'bg-green-100 text-green-800',
  CANCELLED: 'bg-red-100 text-red-800',
}

export default function DashboardOrdersPage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)

  useEffect(() => {
    setLoading(true)
    dashboardService.getOrders({ status: filter || undefined, page })
      .then(({ data }) => { setOrders(data.items); setTotal(data.total) })
      .finally(() => setLoading(false))
  }, [filter, page])

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-semibold text-neutral-900">My Orders</h1>

      {/* Status filter tabs */}
      <div className="flex gap-1 overflow-x-auto scrollbar-hide pb-1">
        {STATUSES.map((s) => (
          <button key={s.value}
            onClick={() => { setFilter(s.value); setPage(1) }}
            className={`flex-shrink-0 px-3.5 py-1.5 rounded-full text-sm font-medium transition-colors ${
              filter === s.value
                ? 'bg-neutral-900 text-white'
                : 'bg-white text-neutral-600 border border-neutral-200 hover:border-neutral-400'
            }`}
          >
            {s.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => <div key={i} className="skeleton h-24 rounded-xl" />)}
        </div>
      ) : orders.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-neutral-400 mb-4">No orders found</p>
          <Link to="/products" className="btn-primary">Shop Now</Link>
        </div>
      ) : (
        <div className="space-y-3">
          {orders.map((order) => (
            <Link key={order.id} to={`/dashboard/orders/${order.order_number}`}
              className="card block hover:border-neutral-300 transition-colors">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <p className="font-medium text-neutral-900 text-sm">#{order.order_number}</p>
                    <span className={`badge ${STATUS_BADGE[order.status] ?? 'bg-neutral-100 text-neutral-700'}`}>
                      {order.status.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <p className="text-xs text-neutral-500">{new Date(order.created_at).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })}</p>
                  <p className="text-xs text-neutral-500 mt-0.5">{order.items?.length ?? 0} item(s)</p>
                </div>
                <div className="text-right flex-shrink-0">
                  <p className="font-semibold text-neutral-900">{formatIDR(order.total)}</p>
                  <p className="text-xs text-neutral-400 mt-0.5 capitalize">{order.source.toLowerCase()}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Pagination */}
      {total > 10 && (
        <div className="flex justify-center gap-2 mt-4">
          <button disabled={page === 1} onClick={() => setPage(page - 1)} className="btn-secondary text-sm px-4 py-2">Prev</button>
          <button disabled={orders.length < 10} onClick={() => setPage(page + 1)} className="btn-secondary text-sm px-4 py-2">Next</button>
        </div>
      )}
    </div>
  )
}
