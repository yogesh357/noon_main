import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { dashboardService } from '../../services/api.service'
import { formatIDR } from '../../utils/currency'
import type { Order } from '../../types'
import Breadcrumb from '../../components/common/Breadcrumb'

export default function DashboardOrderDetailPage() {
  const { orderNumber } = useParams<{ orderNumber: string }>()
  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (orderNumber) {
      dashboardService.getOrder(orderNumber)
        .then(({ data }) => setOrder(data))
        .finally(() => setLoading(false))
    }
  }, [orderNumber])

  if (loading) return <div className="skeleton h-64 rounded-xl" />
  if (!order) return <div className="card text-center py-12 text-neutral-400">Order not found</div>

  return (
    <div className="space-y-5">
      <Breadcrumb items={[
        { label: 'Orders', href: '/dashboard/orders' },
        { label: `#${order.order_number}` },
      ]} />

      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-neutral-900">Order #{order.order_number}</h1>
        {order.status === 'DELIVERED' && (
          <Link to={`/dashboard/disputes/raise/${order.id}`} className="btn-secondary text-sm">Raise Dispute</Link>
        )}
      </div>

      <div className="grid sm:grid-cols-2 gap-4">
        {/* Status */}
        <div className="card">
          <h2 className="text-sm font-semibold text-neutral-900 mb-3">Status</h2>
          <div className="flex items-center gap-2">
            <span className="badge bg-blue-100 text-blue-800">{order.status.replace(/_/g, ' ')}</span>
          </div>
          {order.tracking_number && (
            <p className="text-xs text-neutral-500 mt-2">Tracking: <span className="font-mono font-medium">{order.tracking_number}</span></p>
          )}
        </div>

        {/* Payment */}
        {order.payment && (
          <div className="card">
            <h2 className="text-sm font-semibold text-neutral-900 mb-3">Payment</h2>
            <span className={`badge ${order.payment.status === 'PAID' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
              {order.payment.status}
            </span>
            {order.payment.payment_url && order.payment.status === 'PENDING' && (
              <a href={order.payment.payment_url} className="btn-primary mt-3 text-sm py-2 w-full block text-center">Pay Now</a>
            )}
          </div>
        )}
      </div>

      {/* Items */}
      <div className="card">
        <h2 className="text-sm font-semibold text-neutral-900 mb-3">Items</h2>
        <div className="space-y-3">
          {order.items?.map((item, i) => (
            <div key={i} className="flex gap-3">
              <div className="w-14 h-14 bg-neutral-100 rounded-lg overflow-hidden flex-shrink-0">
                <img src={item.image_url ?? '/placeholder.svg'} alt={item.product_name}
                  className="w-full h-full object-cover" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-neutral-900 line-clamp-1">{item.product_name}</p>
                <p className="text-xs text-neutral-500">{item.variant_label} × {item.quantity}</p>
              </div>
              <span className="text-sm font-medium text-neutral-900">{formatIDR(item.subtotal)}</span>
            </div>
          ))}
        </div>
        <div className="border-t border-neutral-100 mt-4 pt-4 space-y-1.5 text-sm">
          <div className="flex justify-between text-neutral-600"><span>Subtotal</span><span>{formatIDR(order.subtotal)}</span></div>
          <div className="flex justify-between text-neutral-600"><span>Shipping</span><span>{formatIDR(order.shipping_cost)}</span></div>
          <div className="flex justify-between font-semibold text-neutral-900 text-base pt-1.5 border-t border-neutral-100">
            <span>Total</span><span>{formatIDR(order.total)}</span>
          </div>
        </div>
      </div>

      {/* Shipping address */}
      {order.shipping_address && (
        <div className="card">
          <h2 className="text-sm font-semibold text-neutral-900 mb-2">Delivery Address</h2>
          <p className="text-sm text-neutral-700 font-medium">{order.shipping_address.name}</p>
          <p className="text-sm text-neutral-500">{order.shipping_address.phone}</p>
          <p className="text-sm text-neutral-500">{order.shipping_address.street}, {order.shipping_address.city}, {order.shipping_address.province} {order.shipping_address.postal_code}</p>
        </div>
      )}
    </div>
  )
}
