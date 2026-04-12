import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { dashboardService } from '../../services/api.service'
import type { Dispute } from '../../types'
import Breadcrumb from '../../components/common/Breadcrumb'

export default function DashboardDisputeDetailPage() {
  const { disputeId } = useParams<{ disputeId: string }>()
  const [dispute, setDispute] = useState<Dispute | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (disputeId) {
      dashboardService.getDispute(Number(disputeId)).then(({ data }) => setDispute(data)).finally(() => setLoading(false))
    }
  }, [disputeId])

  if (loading) return <div className="skeleton h-64 rounded-xl" />
  if (!dispute) return <div className="card text-center py-12 text-neutral-400">Dispute not found</div>

  return (
    <div className="space-y-5 max-w-lg">
      <Breadcrumb items={[{ label: 'Disputes', href: '/dashboard/disputes' }, { label: `Dispute #${dispute.id}` }]} />
      <h1 className="text-xl font-semibold text-neutral-900">Dispute #{dispute.id}</h1>

      <div className="card space-y-3">
        <div className="flex justify-between">
          <span className="text-sm text-neutral-500">Order</span>
          <span className="text-sm font-medium">#{dispute.order_number}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm text-neutral-500">Type</span>
          <span className="text-sm font-medium">{dispute.type}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm text-neutral-500">Status</span>
          <span className="badge bg-blue-100 text-blue-800">{dispute.status.replace('_', ' ')}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm text-neutral-500">SLA Deadline</span>
          <span className="text-sm font-medium">{new Date(dispute.sla_deadline).toLocaleDateString('id-ID')}</span>
        </div>
      </div>

      <div className="card">
        <h2 className="text-sm font-semibold text-neutral-900 mb-2">Reason</h2>
        <p className="text-sm text-neutral-600">{dispute.reason}</p>
      </div>

      {dispute.admin_response && (
        <div className="card bg-neutral-50">
          <h2 className="text-sm font-semibold text-neutral-900 mb-2">Admin Response</h2>
          <p className="text-sm text-neutral-600">{dispute.admin_response}</p>
        </div>
      )}

      {dispute.evidence?.length > 0 && (
        <div className="card">
          <h2 className="text-sm font-semibold text-neutral-900 mb-3">Evidence</h2>
          <div className="grid grid-cols-3 gap-2">
            {dispute.evidence.map((ev) => (
              <a key={ev.id} href={ev.file_url} target="_blank" rel="noopener noreferrer"
                className="aspect-square bg-neutral-100 rounded-lg overflow-hidden hover:opacity-80 transition-opacity block">
                {ev.file_name.match(/\.(jpg|jpeg|png|webp)$/i) ? (
                  <img src={ev.file_url} alt={ev.file_name} className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-xs text-neutral-500 p-2 text-center">
                    {ev.file_name}
                  </div>
                )}
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
