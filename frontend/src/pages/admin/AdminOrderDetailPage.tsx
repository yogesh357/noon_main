import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { adminService } from '../../services/api.service'
import { showToast } from '../../features/ui/uiSlice'
import { useAppDispatch } from '../../app/hooks'
import { formatIDR } from '../../utils/currency'
import type { Order, OrderStatus } from '../../types'
import Breadcrumb from '../../components/common/Breadcrumb'

const NEXT_STATUS: Partial<Record<OrderStatus, OrderStatus>> = {
  ACCEPTED: 'PROCESSING',
  PROCESSING: 'PICKING',
}

export default function AdminOrderDetailPage() {
  const { orderId } = useParams<{ orderId: string }>()
  const dispatch = useAppDispatch()
  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)

  useEffect(() => {
    if (orderId) adminService.getOrder(Number(orderId)).then(({ data }) => setOrder(data)).finally(() => setLoading(false))
  }, [orderId])

  const updateStatus = async (status: string) => {
    if (!order) return
    setUpdating(true)
    try {
      await adminService.updateOrderStatus(order.id, status)
      setOrder((prev) => prev ? { ...prev, status: status as OrderStatus } : null)
      dispatch(showToast({ message: `Status updated to ${status}`, type: 'success' }))
    } catch {
      dispatch(showToast({ message: 'Failed to update status', type: 'error' }))
    } finally {
      setUpdating(false)
    }
  }

  if (loading) return <div className="skeleton h-64 rounded-xl" />
  if (!order) return <div className="card text-center py-12 text-neutral-400">Order not found</div>

  const nextStatus = NEXT_STATUS[order.status]

  return (
    <div className="space-y-5">
      <Breadcrumb items={[{ label: 'Orders', href: '/admin-panel/orders' }, { label: `#${order.order_number}` }]} />

      <div className="flex items-center justify-between flex-wrap gap-3">
        <h1 className="text-2xl font-semibold text-neutral-900">Order #{order.order_number}</h1>
        <div className="flex gap-2">
          {nextStatus && (
            <button onClick={() => updateStatus(nextStatus)} disabled={updating} className="btn-primary text-sm py-2">
              Move to {nextStatus.replace(/_/g, ' ')}
            </button>
          )}
          <button onClick={async () => {
            try {
              const { data } = await adminService.getShippingLabel(order.id)
              const url = URL.createObjectURL(data)
              window.open(url)
            } catch {
              dispatch(showToast({ message: 'Failed to download label', type: 'error' }))
            }
          }} className="btn-secondary text-sm py-2">
            🖨️ Print Label
          </button>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="card">
          <h2 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-2">Status</h2>
          <span className="badge bg-blue-100 text-blue-800">{order.status.replace(/_/g, ' ')}</span>
        </div>
        <div className="card">
          <h2 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-2">Source</h2>
          <span className="badge bg-neutral-100 text-neutral-700">{order.source}</span>
        </div>
        <div className="card">
          <h2 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-2">Payment</h2>
          <span className={`badge ${order.payment?.status === 'PAID' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
            {order.payment?.status ?? 'N/A'}
          </span>
        </div>
      </div>

      <div className="card">
        <h2 className="font-semibold text-neutral-900 mb-3">Items</h2>
        <div className="space-y-3">
          {order.items?.map((item, i) => (
            <div key={i} className="flex gap-3">
              <div className="w-14 h-14 bg-neutral-100 rounded-lg overflow-hidden flex-shrink-0">
                <img src={item.image_url ?? '/placeholder.svg'} alt={item.product_name} className="w-full h-full object-cover" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">{item.product_name}</p>
                <p className="text-xs text-neutral-500">{item.variant_label} × {item.quantity}</p>
              </div>
              <span className="text-sm font-medium">{formatIDR(item.subtotal)}</span>
            </div>
          ))}
        </div>
        <div className="border-t border-neutral-100 mt-4 pt-3 space-y-1 text-sm">
          <div className="flex justify-between text-neutral-600"><span>Subtotal</span><span>{formatIDR(order.subtotal)}</span></div>
          <div className="flex justify-between text-neutral-600"><span>Shipping</span><span>{formatIDR(order.shipping_cost)}</span></div>
          <div className="flex justify-between font-semibold text-neutral-900 text-base pt-1.5 border-t border-neutral-100">
            <span>Total</span><span>{formatIDR(order.total)}</span>
          </div>
        </div>
      </div>

      {order.shipping_address && (
        <div className="card">
          <h2 className="font-semibold text-neutral-900 mb-2">Shipping Address</h2>
          <p className="text-sm font-medium">{order.shipping_address.name} · {order.shipping_address.phone}</p>
          <p className="text-sm text-neutral-500">{order.shipping_address.street}, {order.shipping_address.city}, {order.shipping_address.province} {order.shipping_address.postal_code}</p>
        </div>
      )}
    </div>
  )
}
