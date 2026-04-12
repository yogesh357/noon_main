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
    { label: "Today's Orders", value: stats.total_orders_today, icon: '📦', color: 'text-blue-600', bg: 'bg-blue-50/50' },
    { label: "Today's Revenue", value: formatIDR(stats.revenue_today), icon: '💰', color: 'text-emerald-600', bg: 'bg-emerald-50/50' },
    { label: 'Pending Orders', value: stats.pending_orders, icon: '⏳', color: 'text-amber-600', bg: 'bg-amber-50/50' },
    { label: 'Active Disputes', value: stats.active_disputes, icon: '⚠️', color: 'text-rose-600', bg: 'bg-rose-50/50' },
  ] : []

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-10">
      <header className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold tracking-tight text-neutral-900 sm:text-4xl">
          Admin <span className="text-gradient">Dashboard</span>
        </h1>
        <p className="text-neutral-500 text-sm">Welcome back. Here's what's happening today.</p>
      </header>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => <div key={i} className="skeleton h-32 rounded-2xl shadow-sm" />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.map((card) => (
            <div key={card.label} className="stat-card group cursor-pointer hover:border-primary-200">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-neutral-500 mb-1">{card.label}</p>
                  <p className="text-2xl font-bold text-neutral-900 group-hover:text-primary-600 transition-colors">
                    {card.value}
                  </p>
                </div>
                <div className={`p-3 rounded-xl ${card.bg} ${card.color} text-xl transition-transform group-hover:scale-110 duration-300`}>
                  {card.icon}
                </div>
              </div>
              <div className="mt-4 flex items-center text-xs text-neutral-400">
                <span className="text-emerald-500 font-medium mr-1.5">↑ 12%</span>
                vs yesterday
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        {stats?.orders_by_status && (
          <div className="elevated-card lg:col-span-2">
            <h2 className="text-lg font-bold text-neutral-900 mb-6 flex items-center gap-2">
              <span className="w-2 h-6 bg-primary-600 rounded-full"></span>
              Orders by Status
            </h2>
            <div className="grid sm:grid-cols-2 gap-6">
              {Object.entries(stats.orders_by_status).map(([status, count]) => {
                const percentage = Math.round((count / (Object.values(stats.orders_by_status).reduce((a, b) => a + b, 0) || 1)) * 100)
                return (
                  <div key={status} className="p-4 rounded-xl border border-neutral-100 hover:bg-neutral-50 transition-colors group">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-neutral-600 capitalize group-hover:text-neutral-900">
                        {status.replace(/_/g, ' ').toLowerCase()}
                      </span>
                      <span className="text-sm font-bold text-neutral-900">{count}</span>
                    </div>
                    <div className="w-full bg-neutral-100 h-1.5 rounded-full overflow-hidden">
                      <div 
                        className="bg-primary-500 h-full rounded-full transition-all duration-1000" 
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        <div className="elevated-card h-fit">
          <h2 className="text-lg font-bold text-neutral-900 mb-4 flex items-center gap-2">
            快速操作 Quick Actions
          </h2>
          <div className="space-y-2">
            <button className="w-full sidebar-link border border-transparent hover:border-primary-100">
              <span>🚀</span> Export today's orders
            </button>
            <button className="w-full sidebar-link border border-transparent hover:border-primary-100">
              <span>📨</span> Send notifications
            </button>
            <button className="w-full sidebar-link border border-transparent hover:border-primary-100">
              <span>⚙️</span> System health check
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
