import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { adminService } from '../../services/api.service'
import { showToast } from '../../features/ui/uiSlice'
import { useAppDispatch } from '../../app/hooks'
import { formatIDR } from '../../utils/currency'
import type { Order } from '../../types'

const STATUS_CLASSES: Record<string, string> = {
  PENDING_PAYMENT: 'status-pending',
  ACCEPTED: 'status-processing',
  PROCESSING: 'status-processing',
  PICKING: 'status-shipped',
  PACKING: 'status-shipped',
  READY_TO_SHIP: 'status-delivered',
  SHIPPED: 'status-shipped',
  DELIVERED: 'status-delivered',
  CANCELLED: 'status-cancelled',
}

export default function AdminOrdersPage() {
  const dispatch = useAppDispatch()
  const [orders, setOrders] = useState<Order[]>([])
  const [selected, setSelected] = useState<Set<number>>(new Set())
  const [loading, setLoading] = useState(true)
  const [processing, setProcessing] = useState(false)
  const [page, setPage] = useState(1)

  const load = () => {
    setLoading(true)
    adminService.getOrders({ page }).then(({ data }) => setOrders(data.items)).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [page])

  const toggleSelect = (id: number) => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const toggleSelectAll = () => {
    if (selected.size === orders.length) setSelected(new Set())
    else setSelected(new Set(orders.map((o) => o.id)))
  }

  const bulkProcess = async () => {
    if (!selected.size) return
    setProcessing(true)
    try {
      await adminService.bulkProcess([...selected])
      dispatch(showToast({ message: `${selected.size} order(s) accepted`, type: 'success' }))
      setSelected(new Set())
      load()
    } catch {
      dispatch(showToast({ message: 'Failed to process orders', type: 'error' }))
    } finally {
      setProcessing(false)
    }
  }

  const downloadLabel = async (orderId: number) => {
    try {
      const { data } = await adminService.getShippingLabel(orderId)
      const url = URL.createObjectURL(data)
      const a = document.createElement('a')
      a.href = url
      a.download = `label-${orderId}.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      dispatch(showToast({ message: 'Failed to download label', type: 'error' }))
    }
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <header className="flex flex-col gap-1">
          <h1 className="text-3xl font-bold tracking-tight text-neutral-900 sm:text-4xl">
            Order <span className="text-gradient">Queue</span>
          </h1>
          <p className="text-neutral-500 text-sm">Manage and process your incoming orders.</p>
        </header>

        <div className="flex items-center gap-3">
          {selected.size > 0 && (
            <button
              onClick={bulkProcess}
              disabled={processing}
              className="btn-primary"
            >
              {processing ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Processing...
                </span>
              ) : (
                `Accept ${selected.size} Selected`
              )}
            </button>
          )}
        </div>
      </div>

      <div className="data-table-container">
        {loading ? (
          <div className="p-8 space-y-4">
            {[...Array(6)].map((_, i) => <div key={i} className="skeleton h-14 rounded-xl" />)}
          </div>
        ) : (
          <div className="overflow-x-auto scrollbar-hide">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-neutral-50/50 border-b border-neutral-100">
                  <th className="px-6 py-4 text-left w-10">
                    <input
                      type="checkbox"
                      checked={selected.size === orders.length && orders.length > 0}
                      onChange={toggleSelectAll}
                      className="rounded border-neutral-300 text-primary-600 focus:ring-primary-500 transition-all"
                    />
                  </th>
                  <th className="px-6 py-4 text-left font-semibold text-neutral-600 uppercase tracking-wider text-[10px]">Order Details</th>
                  <th className="px-6 py-4 text-left font-semibold text-neutral-600 uppercase tracking-wider text-[10px] hidden md:table-cell">Source</th>
                  <th className="px-6 py-4 text-left font-semibold text-neutral-600 uppercase tracking-wider text-[10px]">Status</th>
                  <th className="px-6 py-4 text-right font-semibold text-neutral-600 uppercase tracking-wider text-[10px]">Total Amount</th>
                  <th className="px-6 py-4 text-right font-semibold text-neutral-600 uppercase tracking-wider text-[10px]">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-50">
                {orders.map((order) => (
                  <tr key={order.id} className="data-table-row group">
                    <td className="px-6 py-4">
                      <input
                        type="checkbox"
                        checked={selected.has(order.id)}
                        onChange={() => toggleSelect(order.id)}
                        className="rounded border-neutral-300 text-primary-600 focus:ring-primary-500 transition-all"
                      />
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <Link to={`/admin-panel/orders/${order.id}`} className="font-bold text-neutral-900 hover:text-primary-600 transition-colors">
                          #{order.order_number}
                        </Link>
                        <span className="text-xs text-neutral-400 mt-0.5">{new Date(order.created_at).toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' })}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 hidden md:table-cell">
                      <span className="px-2.5 py-1 rounded-lg bg-neutral-100 text-neutral-600 text-[10px] font-bold uppercase tracking-wide border border-neutral-200">
                        {order.source}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={STATUS_CLASSES[order.status] || 'badge bg-neutral-100'}>
                        {order.status.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right font-black text-neutral-900">{formatIDR(order.total)}</td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2 transition-all duration-300">
                        <Link to={`/admin-panel/orders/${order.id}`} className="p-2 rounded-lg bg-primary-50 text-primary-600 hover:bg-primary-100 transition-colors">
                          <span className="text-xs font-bold uppercase tracking-tighter">View</span>
                        </Link>
                        <button onClick={() => downloadLabel(order.id)} className="p-2 rounded-lg bg-neutral-50 text-neutral-500 hover:bg-neutral-100 hover:text-neutral-900 transition-colors">
                          <span className="text-xs font-bold uppercase tracking-tighter">Label</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between pt-4">
        <button
          disabled={page === 1}
          onClick={() => setPage(page - 1)}
          className="btn-secondary px-4 py-2 text-xs"
        >
          Previous
        </button>
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-neutral-400 bg-neutral-50 px-3 py-1 rounded-full border border-neutral-100">
            Page {page}
          </span>
        </div>
        <button
          disabled={orders.length < 10}
          onClick={() => setPage(page + 1)}
          className="btn-secondary px-4 py-2 text-xs"
        >
          Next
        </button>
      </div>
    </div>
  )
}
