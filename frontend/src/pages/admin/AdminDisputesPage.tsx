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
    <div className="space-y-6 max-w-5xl mx-auto pb-10">
      <header className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold tracking-tight text-neutral-900 sm:text-4xl">
          Customer <span className="text-gradient">Disputes</span>
        </h1>
        <p className="text-neutral-500 text-sm">Review and resolve claims raised by customers.</p>
      </header>

      {loading ? (
        <div className="space-y-4">{[...Array(4)].map((_, i) => <div key={i} className="skeleton h-24 rounded-2xl" />)}</div>
      ) : disputes.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-neutral-400">
          <div className="text-4xl mb-4">✅</div>
          <p className="font-bold text-lg">All clear! No pending disputes.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {disputes.map((d) => {
            const overdue = isOverdue(d.sla_deadline) && d.status === 'OPEN'
            return (
              <div key={d.id} className={`elevated-card group transition-all duration-300 hover:border-primary-200 ${overdue ? 'border-rose-200 bg-rose-50/10' : ''}`}>
                <div className="flex items-start justify-between gap-6">
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-2 mb-2">
                      <p className="text-sm font-black text-neutral-900 tracking-tight">Order #{d.order_number}</p>
                      <span className="px-2 py-0.5 bg-neutral-100 text-[10px] font-black uppercase text-neutral-500 rounded border border-neutral-200">
                        {d.type}
                      </span>
                      <span className={`status-${d.status.toLowerCase().replace('_', '')} text-[10px]`}>
                        {d.status}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-2 text-xs mb-3">
                      <span className="text-neutral-400 font-medium">SLA Deadline:</span>
                      <span className={`font-black ${overdue ? 'text-rose-600 animate-pulse' : 'text-neutral-600'}`}>
                        {new Date(d.sla_deadline).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })}
                        {overdue && ' · OVERDUE'}
                      </span>
                    </div>
                    
                    <div className="p-3 bg-neutral-50 rounded-xl border border-neutral-100 italic text-sm text-neutral-600 line-clamp-2 group-hover:line-clamp-none transition-all duration-500">
                      "{d.reason}"
                    </div>
                  </div>
                  
                  {d.status === 'OPEN' && (
                    <button 
                      onClick={() => setRespondingTo(respondingTo === d.id ? null : d.id)}
                      className={`btn-primary px-4 py-2 text-[10px] font-black uppercase tracking-widest flex-shrink-0 ${respondingTo === d.id ? 'bg-neutral-900' : ''}`}
                    >
                      {respondingTo === d.id ? 'Close Panel' : 'Take Action'}
                    </button>
                  )}
                </div>

                {d.admin_response && (
                  <div className="mt-4 pt-4 border-t border-neutral-100">
                    <div className="flex items-start gap-3 bg-emerald-50/50 p-3 rounded-xl border border-emerald-100">
                      <span className="bg-emerald-100 p-1.5 rounded-lg text-emerald-600">🏛️</span>
                      <div>
                        <p className="text-[10px] font-black text-emerald-800 uppercase tracking-widest mb-1">Official Response</p>
                        <p className="text-sm text-emerald-700 font-medium leading-relaxed">{d.admin_response}</p>
                      </div>
                    </div>
                  </div>
                )}

                {respondingTo === d.id && (
                  <div className="mt-4 pt-4 border-t border-primary-100 animate-in fade-in slide-in-from-top-2 duration-300">
                    <h3 className="text-[10px] font-black text-neutral-400 uppercase tracking-[0.2em] mb-3 ml-1">Resolver Interface</h3>
                    <div className="relative group/field">
                      <textarea 
                        value={response} 
                        onChange={(e) => setResponse(e.target.value)}
                        rows={3} 
                        placeholder="State the resolution clearly..." 
                        className="input mb-3 bg-neutral-50 border-neutral-200 focus:bg-white transition-all text-sm font-medium pt-3" 
                      />
                    </div>
                    <div className="flex gap-2">
                      <button onClick={() => submitResponse(d.id)} className="btn-primary text-xs px-6">Submit Decision</button>
                      <button onClick={() => { setRespondingTo(null); setResponse('') }} className="btn-secondary text-xs px-6">Discard</button>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
