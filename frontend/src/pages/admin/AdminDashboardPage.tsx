import { useEffect, useState } from 'react'
import { adminService } from '../../services/api.service'
import { formatIDR } from '../../utils/currency'
import type { AdminStats } from '../../types'

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    adminService.getStats().then(({ data }) => setStats(data)).finally(() => setLoading(false))
  }, [])

  const statCards = stats ? [
    { label: "Today's Orders", value: stats.total_orders_today, icon: '📦', color: 'bg-blue-50 text-blue-700' },
    { label: "Today's Revenue", value: formatIDR(stats.revenue_today), icon: '💰', color: 'bg-green-50 text-green-700' },
    { label: 'Pending Orders', value: stats.pending_orders, icon: '⏳', color: 'bg-yellow-50 text-yellow-700' },
    { label: 'Active Disputes', value: stats.active_disputes, icon: '⚠️', color: 'bg-red-50 text-red-700' },
  ] : []

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-neutral-900">Admin Dashboard</h1>

      {loading ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <div key={i} className="skeleton h-28 rounded-xl" />)}
        </div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {statCards.map((card) => (
            <div key={card.label} className={`card ${card.color}`}>
              <div className="text-2xl mb-2">{card.icon}</div>
              <p className="text-2xl font-bold">{card.value}</p>
              <p className="text-sm font-medium mt-1">{card.label}</p>
            </div>
          ))}
        </div>
      )}

      {stats?.orders_by_status && (
        <div className="card">
          <h2 className="font-semibold text-neutral-900 mb-4">Orders by Status</h2>
          <div className="space-y-2">
            {Object.entries(stats.orders_by_status).map(([status, count]) => (
              <div key={status} className="flex items-center justify-between text-sm">
                <span className="text-neutral-600">{status.replace(/_/g, ' ')}</span>
                <span className="font-medium text-neutral-900">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
