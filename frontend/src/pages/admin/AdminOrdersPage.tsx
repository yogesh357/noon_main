import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { adminService } from '../../services/api.service'
import { showToast } from '../../features/ui/uiSlice'
import { useAppDispatch } from '../../app/hooks'
import { formatIDR } from '../../utils/currency'
import type { Order } from '../../types'

const STATUS_COLORS: Record<string, string> = {
  PENDING_PAYMENT: 'bg-yellow-100 text-yellow-800',
  ACCEPTED: 'bg-blue-100 text-blue-800',
  PROCESSING: 'bg-blue-100 text-blue-800',
  PICKING: 'bg-indigo-100 text-indigo-800',
  PACKING: 'bg-indigo-100 text-indigo-800',
  READY_TO_SHIP: 'bg-purple-100 text-purple-800',
  SHIPPED: 'bg-indigo-100 text-indigo-800',
  DELIVERED: 'bg-green-100 text-green-800',
  CANCELLED: 'bg-red-100 text-red-800',
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
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-neutral-900">Order Queue</h1>
        {selected.size > 0 && (
          <button onClick={bulkProcess} disabled={processing} className="btn-primary text-sm py-2">
            {processing ? 'Processing...' : `Accept ${selected.size} Order(s)`}
          </button>
        )}
      </div>

      <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
        {loading ? (
          <div className="p-6 space-y-3">{[...Array(5)].map((_, i) => <div key={i} className="skeleton h-12 rounded-lg" />)}</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-neutral-50 border-b border-neutral-200">
              <tr>
                <th className="px-4 py-3 text-left">
                  <input type="checkbox" checked={selected.size === orders.length && orders.length > 0}
                    onChange={toggleSelectAll} className="rounded border-neutral-300" />
                </th>
                <th className="px-4 py-3 text-left font-medium text-neutral-700">Order</th>
                <th className="px-4 py-3 text-left font-medium text-neutral-700 hidden md:table-cell">Source</th>
                <th className="px-4 py-3 text-left font-medium text-neutral-700">Status</th>
                <th className="px-4 py-3 text-right font-medium text-neutral-700">Total</th>
                <th className="px-4 py-3 text-left font-medium text-neutral-700">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100">
              {orders.map((order) => (
                <tr key={order.id} className="hover:bg-neutral-50 transition-colors">
                  <td className="px-4 py-3">
                    <input type="checkbox" checked={selected.has(order.id)}
                      onChange={() => toggleSelect(order.id)} className="rounded border-neutral-300" />
                  </td>
                  <td className="px-4 py-3">
                    <Link to={`/admin-panel/orders/${order.id}`} className="font-medium text-neutral-900 hover:text-brand-red">
                      #{order.order_number}
                    </Link>
                    <p className="text-xs text-neutral-400">{new Date(order.created_at).toLocaleDateString('id-ID')}</p>
                  </td>
                  <td className="px-4 py-3 hidden md:table-cell">
                    <span className="badge bg-neutral-100 text-neutral-600">{order.source}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`badge ${STATUS_COLORS[order.status]}`}>{order.status.replace(/_/g, ' ')}</span>
                  </td>
                  <td className="px-4 py-3 text-right font-semibold">{formatIDR(order.total)}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <Link to={`/admin-panel/orders/${order.id}`} className="text-xs text-brand-red hover:text-brand-red-dark">View</Link>
                      <button onClick={() => downloadLabel(order.id)} className="text-xs text-neutral-500 hover:text-neutral-900">Label</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="flex justify-between">
        <button disabled={page === 1} onClick={() => setPage(page - 1)} className="btn-secondary text-sm py-2 px-4">Previous</button>
        <button disabled={orders.length < 10} onClick={() => setPage(page + 1)} className="btn-secondary text-sm py-2 px-4">Next</button>
      </div>
    </div>
  )
}
