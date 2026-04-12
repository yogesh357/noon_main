import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAppDispatch } from '../../app/hooks'
import { clearCart } from '../../features/cart/cartSlice'
import { checkoutService } from '../../services/api.service'
import { formatIDR } from '../../utils/currency'
import type { Order } from '../../types'

export default function OrderSuccessPage() {
  const { orderNumber } = useParams<{ orderNumber: string }>()
  const dispatch = useAppDispatch()
  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    dispatch(clearCart())
    if (orderNumber) {
      checkoutService.getOrderSuccess(orderNumber)
        .then(({ data }) => setOrder(data))
        .finally(() => setLoading(false))
    }
  }, [orderNumber])

  if (loading) return <div className="flex justify-center py-12"><div className="skeleton w-full max-w-md h-64 rounded-xl" /></div>

  return (
    <div className="max-w-md mx-auto text-center py-8 px-4">
      {/* Success icon */}
      <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      </div>

      <h1 className="text-2xl font-semibold text-neutral-900 mb-2">Order Placed!</h1>
      <p className="text-neutral-500 text-sm mb-1">Your order has been received</p>
      <p className="text-sm font-medium text-neutral-700">Order #{order?.order_number ?? orderNumber}</p>

      {order?.payment?.payment_url && order.payment.status === 'PENDING' && (
        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-xl">
          <p className="text-sm text-yellow-800 font-medium mb-3">Complete your payment</p>
          <a href={order.payment.payment_url} className="btn-primary bg-yellow-500 hover:bg-yellow-600 w-full">
            Pay Now
          </a>
        </div>
      )}

      {order && (
        <div className="mt-6 card text-left">
          <h2 className="font-semibold text-neutral-900 mb-3 text-sm">Order Summary</h2>
          <div className="space-y-2 mb-3">
            {order.items?.map((item, i) => (
              <div key={i} className="flex justify-between text-sm">
                <span className="text-neutral-600">{item.product_name} × {item.quantity}</span>
                <span className="font-medium">{formatIDR(item.subtotal)}</span>
              </div>
            ))}
          </div>
          <div className="border-t border-neutral-100 pt-3 flex justify-between font-semibold">
            <span>Total</span>
            <span>{formatIDR(order.total)}</span>
          </div>
        </div>
      )}

      <div className="mt-6 space-y-3">
        <Link to="/dashboard/orders" className="btn-primary w-full">View My Orders</Link>
        <Link to="/products" className="btn-secondary w-full">Continue Shopping</Link>
      </div>
    </div>
  )
}
