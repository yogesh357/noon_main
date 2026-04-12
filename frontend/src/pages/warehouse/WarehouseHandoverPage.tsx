import { useState } from 'react'
import { warehouseService } from '../../services/api.service'

interface ScannedOrder { order_number: string }

export default function WarehouseHandoverPage() {
  const [orderNum, setOrderNum] = useState('')
  const [scanned, setScanned] = useState<ScannedOrder[]>([])
  const [batchId, setBatchId] = useState<number | null>(null)
  const [scanning, setScanning] = useState(false)
  const [completing, setCompleting] = useState(false)
  const [msg, setMsg] = useState<{ text: string; ok: boolean } | null>(null)

  const showMsg = (text: string, ok: boolean) => {
    setMsg({ text, ok })
    setTimeout(() => setMsg(null), 3000)
  }

  const scan = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!orderNum.trim()) return
    setScanning(true)
    try {
      const { data } = await warehouseService.scanHandover(orderNum.trim(), batchId ?? undefined)
      // Use batch ID from first scan
      if (!batchId && data) setBatchId((data as { batch_id?: number }).batch_id ?? null)
      setScanned((prev) => [...prev, { order_number: orderNum.trim() }])
      showMsg(`✓ Order ${orderNum} added to handover batch`, true)
      setOrderNum('')
      document.getElementById('handover-input')?.focus()
    } catch {
      showMsg(`✗ Order ${orderNum} not found or not ready`, false)
    } finally {
      setScanning(false)
    }
  }

  const complete = async () => {
    if (!batchId) return
    setCompleting(true)
    try {
      await warehouseService.completeHandover(batchId)
      showMsg('Handover batch completed! Orders are SHIPPED.', true)
      setScanned([])
      setBatchId(null)
    } catch {
      showMsg('Failed to complete handover batch', false)
    } finally {
      setCompleting(false)
    }
  }

  return (
    <div className="space-y-5 max-w-lg">
      <h1 className="text-xl font-semibold text-white">Handover to Courier</h1>

      {msg && (
        <div className={`rounded-xl p-4 text-sm font-medium ${msg.ok ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'}`}>
          {msg.text}
        </div>
      )}

      {batchId && (
        <div className="bg-brand-red/20 border border-brand-red/30 rounded-xl p-3 text-sm text-brand-red-light">
          Batch #{batchId} — {scanned.length} order(s) scanned
        </div>
      )}

      <div className="bg-neutral-800 rounded-xl p-5">
        <h2 className="text-sm font-semibold text-neutral-300 mb-3">Scan Order Number</h2>
        <form onSubmit={scan} className="flex gap-3">
          <input
            id="handover-input"
            type="text"
            value={orderNum}
            onChange={(e) => setOrderNum(e.target.value)}
            placeholder="Order number or scan..."
            autoFocus
            className="flex-1 bg-neutral-700 text-white border border-neutral-600 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-red/40 placeholder:text-neutral-500 font-mono"
          />
          <button type="submit" disabled={scanning}
            className="bg-brand-red hover:bg-brand-red-dark text-white px-5 py-2.5 rounded-lg text-sm disabled:opacity-50">
            Scan
          </button>
        </form>
      </div>

      {scanned.length > 0 && (
        <>
          <div className="bg-neutral-800 rounded-xl p-5">
            <h2 className="text-sm font-semibold text-neutral-300 mb-3">Scanned Orders ({scanned.length})</h2>
            <div className="space-y-1.5 max-h-48 overflow-y-auto">
              {scanned.map((o, i) => (
                <div key={i} className="flex items-center gap-2 text-sm text-green-400">
                  <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="font-mono">{o.order_number}</span>
                </div>
              ))}
            </div>
          </div>

          <button onClick={complete} disabled={completing}
            className="w-full bg-green-600 hover:bg-green-700 disabled:opacity-40 text-white font-semibold py-4 rounded-xl text-sm transition-colors">
            {completing ? 'Completing...' : `✓ Complete Handover (${scanned.length} orders)`}
          </button>
        </>
      )}
    </div>
  )
}
