import { useState } from 'react'

import Breadcrumb from '../../components/common/Breadcrumb'

const FAQS = [
  { q: 'How can I track my order?', a: 'Once your order is shipped, you can track it through your account dashboard under "Track Shipment".' },
  { q: 'What payment methods are available?', a: 'We accept Virtual Account, E-wallets (OVO, GoPay, DANA), QRIS, Credit Card, and retail outlets.' },
  { q: 'How long does delivery take?', a: 'Regular delivery takes 2-4 business days. Same-day delivery is available in selected areas.' },
  { q: 'How do I request a return?', a: 'Go to "Disputes" in your dashboard and select the order you want to return.' },
  { q: 'Is product authenticity guaranteed?', a: 'Yes, all our products are 100% authentic and sourced directly from official distributors.' },
]

export default function FAQPage() {
  const [open, setOpen] = useState<number | null>(null)

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Breadcrumb items={[{ label: 'Home', href: '/' }, { label: 'FAQ' }]} />
      <h1 className="text-3xl font-semibold text-neutral-900 mb-2">FAQ</h1>
      <p className="text-neutral-500 mb-10">Frequently asked questions</p>

      <div className="space-y-3">
        {FAQS.map((faq, i) => (
          <div key={i} className="border border-neutral-200 rounded-xl overflow-hidden">
            <button onClick={() => setOpen(open === i ? null : i)}
              className="w-full flex items-center justify-between px-5 py-4 text-left">
              <span className="font-medium text-neutral-900 text-sm pr-4">
                {faq.q}
              </span>
              <svg className={`w-5 h-5 text-neutral-400 flex-shrink-0 transition-transform ${open === i ? 'rotate-180' : ''}`}
                fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {open === i && (
              <div className="px-5 pb-5 text-sm text-neutral-600 leading-relaxed border-t border-neutral-100">
                <div className="pt-4">{faq.a}</div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
