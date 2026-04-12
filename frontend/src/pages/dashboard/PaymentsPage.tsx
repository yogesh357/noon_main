import { useEffect, useState } from 'react'
import { dashboardService } from '../../services/api.service'
import { formatIDR } from '../../utils/currency'
import type { Payment } from '../../types'

const STATUS_BADGE: Record<string, string> = {
  PENDING: 'bg-yellow-100 text-yellow-800',
  PAID: 'bg-green-100 text-green-800',
  FAILED: 'bg-red-100 text-red-800',
  EXPIRED: 'bg-neutral-100 text-neutral-600',
  REFUNDED: 'bg-purple-100 text-purple-800',
}

export default function DashboardPaymentsPage() {
  const [payments, setPayments] = useState<Payment[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    dashboardService.getPayments().then(({ data }) => setPayments(data)).finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-semibold text-neutral-900">Payment History</h1>

      {loading ? (
        <div className="space-y-3">{[...Array(4)].map((_, i) => <div key={i} className="skeleton h-16 rounded-xl" />)}</div>
      ) : payments.length === 0 ? (
        <div className="card text-center py-12 text-neutral-400">No payment history</div>
      ) : (
        <div className="space-y-3">
          {payments.map((p) => (
            <div key={p.id} className="card flex items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium text-neutral-900">{p.method?.replace('_', ' ') ?? 'Payment'}</p>
                  <span className={`badge ${STATUS_BADGE[p.status]}`}>{p.status}</span>
                </div>
                {p.paid_at && <p className="text-xs text-neutral-500 mt-0.5">{new Date(p.paid_at).toLocaleDateString('id-ID')}</p>}
              </div>
              <span className="font-semibold text-neutral-900">{formatIDR(p.amount)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
