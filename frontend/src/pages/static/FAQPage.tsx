import { useState } from 'react'
import { useAppSelector } from '../../app/hooks'
import Breadcrumb from '../../components/common/Breadcrumb'

const FAQS = [
  { q_id: 'Bagaimana cara melacak pesanan saya?', q_en: 'How can I track my order?', a_id: 'Setelah pesanan dikirim, Anda dapat melacak pengiriman melalui dashboard akun Anda di menu "Lacak Pengiriman".', a_en: 'Once your order is shipped, you can track it through your account dashboard under "Track Shipment".' },
  { q_id: 'Metode pembayaran apa saja yang tersedia?', q_en: 'What payment methods are available?', a_id: 'Kami menerima Virtual Account, E-wallet (OVO, GoPay, DANA), QRIS, Kartu Kredit, dan Indomaret/Alfamart.', a_en: 'We accept Virtual Account, E-wallets (OVO, GoPay, DANA), QRIS, Credit Card, and retail outlets.' },
  { q_id: 'Berapa lama proses pengiriman?', q_en: 'How long does delivery take?', a_id: 'Pengiriman reguler 2-4 hari kerja. Pengiriman same-day tersedia untuk area tertentu.', a_en: 'Regular delivery takes 2-4 business days. Same-day delivery is available in selected areas.' },
  { q_id: 'Bagaimana cara mengajukan pengembalian?', q_en: 'How do I request a return?', a_id: 'Buka halaman "Sengketa" di dashboard Anda dan pilih pesanan yang ingin dikembalikan.', a_en: 'Go to "Disputes" in your dashboard and select the order you want to return.' },
  { q_id: 'Apakah ada jaminan keaslian produk?', q_en: 'Is product authenticity guaranteed?', a_id: 'Ya, semua produk kami 100% original dan bersumber langsung dari distributor resmi.', a_en: 'Yes, all our products are 100% authentic and sourced directly from official distributors.' },
]

export default function FAQPage() {
  const { language } = useAppSelector((s) => s.ui)
  const [open, setOpen] = useState<number | null>(null)

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Breadcrumb items={[{ label: 'Home', href: '/' }, { label: 'FAQ' }]} />
      <h1 className="text-3xl font-semibold text-neutral-900 mb-2">FAQ</h1>
      <p className="text-neutral-500 mb-10">{language === 'id' ? 'Pertanyaan yang sering ditanyakan' : 'Frequently asked questions'}</p>

      <div className="space-y-3">
        {FAQS.map((faq, i) => (
          <div key={i} className="border border-neutral-200 rounded-xl overflow-hidden">
            <button onClick={() => setOpen(open === i ? null : i)}
              className="w-full flex items-center justify-between px-5 py-4 text-left">
              <span className="font-medium text-neutral-900 text-sm pr-4">
                {language === 'id' ? faq.q_id : faq.q_en}
              </span>
              <svg className={`w-5 h-5 text-neutral-400 flex-shrink-0 transition-transform ${open === i ? 'rotate-180' : ''}`}
                fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {open === i && (
              <div className="px-5 pb-5 text-sm text-neutral-600 leading-relaxed border-t border-neutral-100">
                <div className="pt-4">{language === 'id' ? faq.a_id : faq.a_en}</div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
