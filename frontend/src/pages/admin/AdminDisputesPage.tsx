import { useEffect, useState } from 'react'
import { adminService } from '../../services/api.service'
import { showToast } from '../../features/ui/uiSlice'
import { useAppDispatch } from '../../app/hooks'
import type { Dispute } from '../../types'

export default function AdminDisputesPage() {
  const dispatch = useAppDispatch()
  const [disputes, setDisputes] = useState<Dispute[]>([])
  const [loading, setLoading] = useState(true)
  const [respondingTo, setRespondingTo] = useState<number | null>(null)
  const [response, setResponse] = useState('')

  useEffect(() => {
    adminService.getDisputes().then(({ data }) => setDisputes(data.items)).finally(() => setLoading(false))
  }, [])

  const submitResponse = async (disputeId: number) => {
    try {
      await adminService.respondToDispute(disputeId, response)
      dispatch(showToast({ message: 'Response submitted', type: 'success' }))
      setRespondingTo(null)
      setResponse('')
      setDisputes((prev) => prev.map((d) => d.id === disputeId ? { ...d, admin_response: response, status: 'IN_REVIEW' as const } : d))
    } catch {
      dispatch(showToast({ message: 'Failed to submit response', type: 'error' }))
    }
  }

  const isOverdue = (sla: string) => new Date(sla) < new Date()

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-semibold text-neutral-900">Disputes</h1>

      {loading ? (
        <div className="space-y-3">{[...Array(4)].map((_, i) => <div key={i} className="skeleton h-20 rounded-xl" />)}</div>
      ) : disputes.length === 0 ? (
        <div className="card text-center py-12 text-neutral-400">No disputes</div>
      ) : (
        <div className="space-y-3">
          {disputes.map((d) => (
            <div key={d.id} className={`card ${isOverdue(d.sla_deadline) && d.status === 'OPEN' ? 'border-red-200 bg-red-50' : ''}`}>
              <div className="flex items-start justify-between gap-4 mb-3">
                <div>
                  <div className="flex items-center gap-2">
                    <p className="font-medium text-neutral-900 text-sm">Order #{d.order_number}</p>
                    <span className="badge bg-neutral-100 text-neutral-600">{d.type}</span>
                    <span className={`badge ${d.status === 'OPEN' ? 'bg-yellow-100 text-yellow-800' : d.status === 'RESOLVED' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}`}>
                      {d.status}
                    </span>
                  </div>
                  <p className="text-xs text-neutral-500 mt-0.5">
                    SLA: {new Date(d.sla_deadline).toLocaleDateString('id-ID')}
                    {isOverdue(d.sla_deadline) && <span className="text-red-500 font-medium ml-1">OVERDUE</span>}
                  </p>
                  <p className="text-sm text-neutral-600 mt-1 line-clamp-2">{d.reason}</p>
                </div>
                {d.status === 'OPEN' && (
                  <button onClick={() => setRespondingTo(respondingTo === d.id ? null : d.id)}
                    className="btn-primary text-xs py-1.5 px-3 flex-shrink-0">
                    Respond
                  </button>
                )}
              </div>

              {d.admin_response && (
                <div className="bg-neutral-50 rounded-lg p-3 text-sm">
                  <p className="font-medium text-neutral-700 mb-0.5">Your response:</p>
                  <p className="text-neutral-600">{d.admin_response}</p>
                </div>
              )}

              {respondingTo === d.id && (
                <div className="border-t border-neutral-100 pt-3 mt-2">
                  <textarea value={response} onChange={(e) => setResponse(e.target.value)}
                    rows={3} placeholder="Write your response..." className="input mb-2 resize-none" />
                  <div className="flex gap-2">
                    <button onClick={() => submitResponse(d.id)} className="btn-primary text-sm py-1.5">Submit</button>
                    <button onClick={() => { setRespondingTo(null); setResponse('') }} className="btn-secondary text-sm py-1.5">Cancel</button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
