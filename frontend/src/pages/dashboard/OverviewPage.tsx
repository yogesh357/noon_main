import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAppSelector } from '../../app/hooks'
import { dashboardService } from '../../services/api.service'
import { formatIDR } from '../../utils/currency'
import type { Order } from '../../types'

const STATUS_COLORS: Record<string, string> = {
  PENDING_PAYMENT: 'status-pending',
  ACCEPTED: 'bg-blue-100 text-blue-800 badge',
  PROCESSING: 'bg-blue-100 text-blue-800 badge',
  PICKING: 'bg-indigo-100 text-indigo-800 badge',
  PACKING: 'bg-indigo-100 text-indigo-800 badge',
  READY_TO_SHIP: 'bg-purple-100 text-purple-800 badge',
  SHIPPED: 'status-shipped',
  DELIVERED: 'status-delivered',
  CANCELLED: 'status-cancelled',
}

export default function DashboardOverviewPage() {
  const { user } = useAppSelector((s) => s.auth)
  const [recentOrders, setRecentOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    dashboardService.getOrders({ page: 1 })
      .then(({ data }) => setRecentOrders(data.items.slice(0, 5)))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-6">
      {/* Welcome */}
      <div className="card bg-gradient-to-r from-neutral-900 to-neutral-700 text-white border-0">
        <p className="text-neutral-400 text-sm mb-1">Welcome back,</p>
        <h1 className="text-2xl font-semibold">{user?.full_name}</h1>
        <p className="text-neutral-400 text-sm mt-1">{user?.email}</p>
      </div>

      {/* Quick links */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'My Orders', to: '/dashboard/orders', icon: '📦' },
          { label: 'Track Shipment', to: '/dashboard/tracking', icon: '🚚' },
          { label: 'Wishlist', to: '/dashboard/wishlist', icon: '❤️' },
          { label: 'Disputes', to: '/dashboard/disputes', icon: '🔔' },
        ].map((item) => (
          <Link key={item.to} to={item.to}
            className="card text-center hover:border-neutral-300 transition-colors cursor-pointer group">
            <div className="text-2xl mb-2">{item.icon}</div>
            <p className="text-sm font-medium text-neutral-700 group-hover:text-neutral-900">{item.label}</p>
          </Link>
        ))}
      </div>

      {/* Recent orders */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-neutral-900">Recent Orders</h2>
          <Link to="/dashboard/orders" className="text-sm text-brand-red hover:text-brand-red-dark">View all →</Link>
        </div>

        {loading ? (
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => <div key={i} className="skeleton h-14 rounded-lg" />)}
          </div>
        ) : recentOrders.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-neutral-400 text-sm">No orders yet</p>
            <Link to="/products" className="btn-primary mt-4 text-sm">Start Shopping</Link>
          </div>
        ) : (
          <div className="space-y-2">
            {recentOrders.map((order) => (
              <Link key={order.id} to={`/dashboard/orders/${order.order_number}`}
                className="flex items-center justify-between p-3 rounded-lg hover:bg-neutral-50 transition-colors">
                <div>
                  <p className="text-sm font-medium text-neutral-900">#{order.order_number}</p>
                  <p className="text-xs text-neutral-500">{new Date(order.created_at).toLocaleDateString('id-ID')}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className={STATUS_COLORS[order.status] ?? 'badge bg-neutral-100 text-neutral-700'}>
                    {order.status.replace(/_/g, ' ')}
                  </span>
                  <span className="text-sm font-semibold text-neutral-900">{formatIDR(order.total)}</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
