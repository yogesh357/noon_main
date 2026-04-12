import { Link, Outlet } from 'react-router-dom'
import Toast from '../components/common/Toast'

export default function CheckoutLayout() {
  return (
    <div className="min-h-screen flex flex-col bg-neutral-50">
      {/* Minimal header */}
      <header className="bg-white border-b border-neutral-200">
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/" className="text-xl font-bold tracking-tight text-neutral-900">
            PHOENIX
          </Link>
          <div className="flex items-center gap-2 text-sm text-neutral-500">
            <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            Secure Checkout
          </div>
        </div>
      </header>

      <main className="flex-1 py-8">
        <div className="max-w-3xl mx-auto px-4">
          <Outlet />
        </div>
      </main>
      <Toast />
    </div>
  )
}
