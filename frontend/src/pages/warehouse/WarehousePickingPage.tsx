import { useState } from 'react'
import { warehouseService } from '../../services/api.service'
import type { PickingTask } from '../../types'

export default function WarehousePickingPage() {
  const [orderId, setOrderId] = useState('')
  const [task, setTask] = useState<PickingTask | null>(null)
  const [loading, setLoading] = useState(false)
  const [completing, setCompleting] = useState(false)
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null)

  const startPicking = async () => {
    if (!orderId.trim()) return
    setLoading(true)
    setMessage(null)
    try {
      const { data } = await warehouseService.startPicking(Number(orderId))
      setTask(data)
      setMessage({ text: `Picking started for Order #${data.order_number}`, type: 'success' })
    } catch {
      setMessage({ text: 'Failed to start picking. Check order ID.', type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  const completePicking = async () => {
    if (!task) return
    setCompleting(true)
    try {
      await warehouseService.completePicking(task.id)
      setMessage({ text: 'Picking completed! Order moved to PACKING.', type: 'success' })
      setTask(null)
      setOrderId('')
    } catch {
      setMessage({ text: 'Failed to complete picking.', type: 'error' })
    } finally {
      setCompleting(false)
    }
  }

  return (
    <div className="space-y-5 max-w-lg">
      <h1 className="text-xl font-semibold text-white">Picking</h1>

      {message && (
        <div className={`rounded-xl p-4 text-sm font-medium ${message.type === 'success' ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'}`}>
          {message.text}
        </div>
      )}

      <div className="bg-neutral-800 rounded-xl p-5">
        <h2 className="text-sm font-semibold text-neutral-300 mb-3">Start Picking Task</h2>
        <div className="flex gap-3">
          <input type="number" value={orderId} onChange={(e) => setOrderId(e.target.value)}
            placeholder="Order ID" className="flex-1 bg-neutral-700 text-white border border-neutral-600 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-red/40 placeholder:text-neutral-500" />
          <button onClick={startPicking} disabled={loading || !orderId}
            className="bg-brand-red hover:bg-brand-red-dark text-white font-medium px-5 py-2.5 rounded-lg text-sm transition-colors disabled:opacity-50">
            {loading ? '...' : 'Start'}
          </button>
        </div>
      </div>

      {task && (
        <div className="bg-neutral-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm text-neutral-400">Current Task</p>
              <p className="text-white font-semibold">Order #{task.order_number}</p>
            </div>
            <span className="badge bg-blue-900 text-blue-200">In Progress</span>
          </div>
          <p className="text-xs text-neutral-500 mb-4">
            Pick all items for this order, then mark as complete.
          </p>
          <button onClick={completePicking} disabled={completing}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 rounded-lg text-sm transition-colors disabled:opacity-50">
            {completing ? 'Completing...' : '✓ Mark Picking Complete'}
          </button>
        </div>
      )}
    </div>
  )
}
