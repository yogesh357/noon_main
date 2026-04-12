import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { dashboardService } from '../../services/api.service'
import type { Dispute } from '../../types'

const STATUS_BADGE: Record<string, string> = {
  OPEN: 'bg-yellow-100 text-yellow-800',
  IN_REVIEW: 'bg-blue-100 text-blue-800',
  RESOLVED: 'bg-green-100 text-green-800',
  REJECTED: 'bg-red-100 text-red-800',
}

export default function DashboardDisputesPage() {
  const [disputes, setDisputes] = useState<Dispute[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    dashboardService.getDisputes().then(({ data }) => setDisputes(data)).finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-semibold text-neutral-900">My Disputes</h1>

      {loading ? (
        <div className="space-y-3">{[...Array(3)].map((_, i) => <div key={i} className="skeleton h-20 rounded-xl" />)}</div>
      ) : disputes.length === 0 ? (
        <div className="card text-center py-12 text-neutral-400">No disputes filed</div>
      ) : (
        <div className="space-y-3">
          {disputes.map((d) => (
            <Link key={d.id} to={`/dashboard/disputes/${d.id}`} className="card block hover:border-neutral-300 transition-colors">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <p className="text-sm font-medium text-neutral-900">Order #{d.order_number}</p>
                    <span className={`badge ${STATUS_BADGE[d.status]}`}>{d.status.replace('_', ' ')}</span>
                  </div>
                  <p className="text-xs text-neutral-500">Type: {d.type} · SLA: {new Date(d.sla_deadline).toLocaleDateString('id-ID')}</p>
                  <p className="text-xs text-neutral-500 line-clamp-1 mt-0.5">{d.reason}</p>
                </div>
                <svg className="w-4 h-4 text-neutral-400 flex-shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
