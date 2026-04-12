import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
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

  if (loading) return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      <div className="skeleton h-8 w-48 mb-4" />
      <div className="flex justify-between items-center mb-8">
        <div className="skeleton h-10 w-64" />
        <div className="flex gap-2">
          <div className="skeleton h-10 w-32 rounded-xl" />
          <div className="skeleton h-10 w-32 rounded-xl" />
        </div>
      </div>
      <div className="grid md:grid-cols-3 gap-6">
        {[...Array(3)].map((_, i) => <div key={i} className="skeleton h-24 rounded-2xl" />)}
      </div>
      <div className="skeleton h-64 rounded-2xl" />
    </div>
  )

  if (!order) return (
    <div className="flex flex-col items-center justify-center py-20 text-neutral-400">
      <div className="text-64 mb-4">🔍</div>
      <p className="font-bold text-xl">Order not found</p>
      <Link to="/admin-panel/orders" className="btn-secondary mt-4">Back to Orders</Link>
    </div>
  )

  const nextStatus = NEXT_STATUS[order.status]

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      <div className="flex flex-col gap-4">
        <Breadcrumb items={[{ label: 'Orders', href: '/admin-panel/orders' }, { label: `#${order.order_number}` }]} />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex flex-col gap-1">
            <h1 className="text-3xl font-bold tracking-tight text-neutral-900 sm:text-4xl">
              Order <span className="text-gradient">#{order.order_number}</span>
            </h1>
            <p className="text-neutral-500 text-sm">Placed on {new Date(order.created_at).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</p>
          </div>

          <div className="flex items-center gap-3">
            {nextStatus && (
              <button
                onClick={() => updateStatus(nextStatus)}
                disabled={updating}
                className="btn-primary shadow-lg shadow-primary-200"
              >
                {updating ? 'Updating...' : `Move to ${nextStatus.replace(/_/g, ' ')}`}
              </button>
            )}
            <button
              onClick={async () => {
                try {
                  const { data } = await adminService.getShippingLabel(order.id)
                  const url = URL.createObjectURL(data)
                  window.open(url)
                } catch {
                  dispatch(showToast({ message: 'Failed to download label', type: 'error' }))
                }
              }}
              className="btn-secondary group"
            >
              <span className="mr-2 group-hover:scale-125 transition-transform duration-200">🖨️</span>
              Print Label
            </button>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="elevated-card relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
            <span className="text-4xl">📦</span>
          </div>
          <h2 className="text-[10px] font-black text-neutral-400 uppercase tracking-[0.2em] mb-3">Order Status</h2>
          <span className={`status-${order.status.toLowerCase()} text-xs`}>
            {order.status.replace(/_/g, ' ')}
          </span>
        </div>

        <div className="elevated-card relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
            <span className="text-4xl">🔌</span>
          </div>
          <h2 className="text-[10px] font-black text-neutral-400 uppercase tracking-[0.2em] mb-3">Sales Source</h2>
          <span className="px-3 py-1 bg-neutral-100 text-neutral-900 text-xs font-bold rounded-full border border-neutral-200">
            {order.source}
          </span>
        </div>

        <div className="elevated-card relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
            <span className="text-4xl">💳</span>
          </div>
          <h2 className="text-[10px] font-black text-neutral-400 uppercase tracking-[0.2em] mb-3">Payment Status</h2>
          <span className={`badge text-xs ${order.payment?.status === 'PAID' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'}`}>
            {order.payment?.status ?? 'PENDING'}
          </span>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="elevated-card">
            <h2 className="text-lg font-bold text-neutral-900 mb-6 flex items-center gap-2">
              <span className="w-2 h-6 bg-primary-600 rounded-full"></span>
              Order Items
            </h2>
            <div className="space-y-4">
              {order.items?.map((item, i) => (
                <div key={i} className="flex gap-4 p-3 rounded-2xl hover:bg-neutral-50 transition-colors border border-transparent hover:border-neutral-100 group">
                  <div className="w-20 h-20 bg-neutral-100 rounded-xl overflow-hidden flex-shrink-0 border border-neutral-200 group-hover:shadow-md transition-all">
                    <img
                      src={item.image_url ?? '/placeholder.svg'}
                      alt={item.product_name}
                      className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                    />
                  </div>
                  <div className="flex-1 flex flex-col justify-center">
                    <p className="text-sm font-bold text-neutral-900 line-clamp-1">{item.product_name}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs font-medium text-neutral-500">{item.variant_label}</span>
                      <span className="w-1 h-1 bg-neutral-300 rounded-full"></span>
                      <span className="text-xs font-black text-primary-600">×{item.quantity}</span>
                    </div>
                  </div>
                  <div className="flex flex-col justify-center items-end">
                    <span className="text-sm font-black text-neutral-900">{formatIDR(item.subtotal)}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 pt-6 border-t border-neutral-100 space-y-3">
              <div className="flex justify-between text-sm text-neutral-500">
                <span>Items Subtotal</span>
                <span>{formatIDR(order.subtotal)}</span>
              </div>
              <div className="flex justify-between text-sm text-neutral-500">
                <span>Shipping Fee</span>
                <span>{formatIDR(order.shipping_cost)}</span>
              </div>
              <div className="flex justify-between pt-4 border-t border-neutral-100">
                <span className="text-lg font-bold text-neutral-900">Grand Total</span>
                <span className="text-xl font-black text-primary-600">{formatIDR(order.total)}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          {order.shipping_address && (
            <div className="elevated-card">
              <h2 className="text-lg font-bold text-neutral-900 mb-4 flex items-center gap-2">
                <span className="w-2 h-6 bg-accent-500 rounded-full"></span>
                Shipping Details
              </h2>
              <div className="p-4 bg-neutral-50 rounded-2xl border border-neutral-100">
                <p className="text-sm font-black text-neutral-900 mb-1">{order.shipping_address.name}</p>
                <p className="text-xs font-medium text-primary-600 mb-4">{order.shipping_address.phone}</p>
                <div className="space-y-1">
                  <p className="text-xs text-neutral-600 leading-relaxed italic">"{order.shipping_address.street}"</p>
                  <p className="text-xs text-neutral-500 font-medium">
                    {order.shipping_address.city}, {order.shipping_address.province}
                  </p>
                  <p className="text-[10px] font-black text-neutral-400 mt-2 tracking-widest uppercase">
                    POSTAL CODE: {order.shipping_address.postal_code}
                  </p>
                </div>
              </div>
            </div>
          )}

          <div className="elevated-card bg-primary-600 text-white border-none shadow-xl shadow-primary-200">
            <h2 className="text-sm font-black uppercase tracking-widest mb-4 opacity-80">Admin Note</h2>
            <p className="text-xs leading-relaxed font-medium">
              This order requires priority processing to maintain SLA standards. Ensure items are double-checked before packing.
            </p>
            <button className="mt-4 w-full py-2 bg-white/20 hover:bg-white/30 rounded-xl text-[10px] font-black uppercase tracking-widest transition-colors">
              Add Private Annotation
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
