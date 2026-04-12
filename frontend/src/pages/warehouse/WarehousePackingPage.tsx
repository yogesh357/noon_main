import { useState } from 'react'
import { warehouseService } from '../../services/api.service'
import type { PackingTask } from '../../types'

export default function WarehousePackingPage() {
  const [orderId, setOrderId] = useState('')
  const [task, setTask] = useState<PackingTask | null>(null)
  const [barcode, setBarcode] = useState('')
  const [loading, setLoading] = useState(false)
  const [scanMsg, setScanMsg] = useState<{ text: string; ok: boolean } | null>(null)

  const startPacking = async () => {
    if (!orderId.trim()) return
    setLoading(true)
    try {
      const { data } = await warehouseService.startPacking(Number(orderId))
      setTask(data)
    } catch {
      setScanMsg({ text: 'Failed to start packing. Check order ID.', ok: false })
    } finally {
      setLoading(false)
    }
  }

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!task || !barcode.trim()) return
    try {
      await warehouseService.scanPacking(task.id, barcode.trim())
      setScanMsg({ text: `✓ Scanned: ${barcode}`, ok: true })
      setTask((prev) => prev ? { ...prev, scan_log: [...(prev.scan_log ?? []), barcode.trim()] } : null)
      setBarcode('')
      const el = document.getElementById('barcode-input') as HTMLInputElement
      el?.focus()
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setScanMsg({ text: error.response?.data?.detail ?? 'Scan error', ok: false })
      setBarcode('')
    }
    setTimeout(() => setScanMsg(null), 2000)
  }

  const completePacking = async () => {
    if (!task) return
    setLoading(true)
    try {
      await warehouseService.completePacking(task.id)
      setScanMsg({ text: 'Packing complete! Order is READY_TO_SHIP.', ok: true })
      setTask(null)
      setOrderId('')
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setScanMsg({ text: error.response?.data?.detail ?? 'Failed to complete', ok: false })
    } finally {
      setLoading(false)
    }
  }

  const allItems = task?.items ?? []
  const scannedCount = task?.scan_log?.length ?? 0
  const totalItems = allItems.reduce((sum, i) => sum + i.quantity, 0)
  const isComplete = scannedCount >= totalItems

  return (
    <div className="space-y-5 max-w-lg">
      <h1 className="text-xl font-semibold text-white">Packing</h1>

      {scanMsg && (
        <div className={`rounded-xl p-4 text-sm font-medium ${scanMsg.ok ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'}`}>
          {scanMsg.text}
        </div>
      )}

      {!task ? (
        <div className="bg-neutral-800 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-neutral-300 mb-3">Start Packing Task</h2>
          <div className="flex gap-3">
            <input type="number" value={orderId} onChange={(e) => setOrderId(e.target.value)}
              placeholder="Order ID" className="flex-1 bg-neutral-700 text-white border border-neutral-600 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-red/40 placeholder:text-neutral-500" />
            <button onClick={startPacking} disabled={loading || !orderId}
              className="bg-brand-red hover:bg-brand-red-dark text-white font-medium px-5 py-2.5 rounded-lg text-sm disabled:opacity-50">
              Start
            </button>
          </div>
        </div>
      ) : (
        <>
          {/* Progress */}
          <div className="bg-neutral-800 rounded-xl p-5">
            <div className="flex items-center justify-between mb-2">
              <p className="text-white font-semibold">Order #{task.order_number}</p>
              <span className="text-sm text-neutral-400">{scannedCount} / {totalItems} scanned</span>
            </div>
            <div className="w-full bg-neutral-700 rounded-full h-2">
              <div className="bg-brand-red h-2 rounded-full transition-all"
                style={{ width: `${totalItems > 0 ? (scannedCount / totalItems) * 100 : 0}%` }} />
            </div>
          </div>

          {/* Items list */}
          <div className="bg-neutral-800 rounded-xl p-5">
            <h2 className="text-sm font-semibold text-neutral-300 mb-3">Items to Pack</h2>
            <div className="space-y-2">
              {allItems.map((item, i) => (
                <div key={i} className="flex items-center justify-between text-sm">
                  <span className="text-neutral-300">{item.product_name} <span className="text-neutral-500">×{item.quantity}</span></span>
                </div>
              ))}
            </div>
          </div>

          {/* Barcode scan */}
          <div className="bg-neutral-800 rounded-xl p-5">
            <h2 className="text-sm font-semibold text-neutral-300 mb-3">Scan Barcode</h2>
            <form onSubmit={handleScan} className="flex gap-3">
              <input
                id="barcode-input"
                type="text"
                value={barcode}
                onChange={(e) => setBarcode(e.target.value)}
                placeholder="Scan or type barcode..."
                autoFocus
                className="flex-1 bg-neutral-700 text-white border border-neutral-600 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-red/40 placeholder:text-neutral-500 font-mono"
              />
              <button type="submit" className="bg-brand-red hover:bg-brand-red-dark text-white px-5 py-2.5 rounded-lg text-sm">Scan</button>
            </form>
            {task.scan_log?.length > 0 && (
              <div className="mt-3 space-y-1 max-h-32 overflow-y-auto">
                {[...task.scan_log].reverse().map((s, i) => (
                  <p key={i} className="text-xs text-green-400 font-mono">✓ {s}</p>
                ))}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <button onClick={completePacking} disabled={!isComplete || loading}
              className="flex-1 bg-green-600 hover:bg-green-700 disabled:opacity-40 text-white font-medium py-3 rounded-xl text-sm transition-colors">
              ✓ Complete Packing
            </button>
            <button onClick={async () => {
              const reason = prompt('Return reason?')
              if (!reason) return
              await warehouseService.returnToPicker(task.id, reason)
              setTask(null)
              setOrderId('')
            }} className="bg-neutral-700 hover:bg-neutral-600 text-neutral-300 font-medium py-3 px-4 rounded-xl text-sm">
              ↩ Return
            </button>
          </div>
        </>
      )}
    </div>
  )
}
