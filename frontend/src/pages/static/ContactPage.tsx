import { useState } from 'react'
import { useAppSelector } from '../../app/hooks'
import Breadcrumb from '../../components/common/Breadcrumb'

export default function ContactPage() {
  const { language } = useAppSelector((s) => s.ui)
  const [sent, setSent] = useState(false)
  const [form, setForm] = useState({ name: '', email: '', message: '' })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setSent(true)
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Breadcrumb items={[{ label: 'Home', href: '/' }, { label: language === 'id' ? 'Hubungi Kami' : 'Contact Us' }]} />
      <h1 className="text-3xl font-semibold text-neutral-900 mb-2">{language === 'id' ? 'Hubungi Kami' : 'Contact Us'}</h1>
      <p className="text-neutral-500 mb-10">{language === 'id' ? 'Kami siap membantu Anda' : 'We\'re here to help'}</p>

      <div className="grid md:grid-cols-2 gap-10">
        <div className="space-y-6">
          {[
            { icon: '📧', label: 'Email', val: 'support@projectphoenix.id' },
            { icon: '📱', label: 'WhatsApp', val: '+62 812 3456 7890' },
            { icon: '⏰', label: language === 'id' ? 'Jam Operasional' : 'Business Hours', val: language === 'id' ? 'Senin–Jumat, 09.00–17.00 WIB' : 'Mon–Fri, 9AM–5PM WIB' },
          ].map((item) => (
            <div key={item.label} className="flex gap-4">
              <span className="text-2xl">{item.icon}</span>
              <div>
                <p className="font-medium text-neutral-900 text-sm">{item.label}</p>
                <p className="text-neutral-500 text-sm">{item.val}</p>
              </div>
            </div>
          ))}
        </div>

        {sent ? (
          <div className="card text-center py-12">
            <div className="text-4xl mb-3">✅</div>
            <p className="font-medium text-neutral-900">{language === 'id' ? 'Pesan terkirim!' : 'Message sent!'}</p>
            <p className="text-sm text-neutral-500 mt-1">{language === 'id' ? 'Kami akan merespons dalam 1x24 jam.' : 'We\'ll respond within 24 hours.'}</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">{language === 'id' ? 'Nama' : 'Name'}</label>
              <input type="text" value={form.name} onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
                className="input" required />
            </div>
            <div>
              <label className="label">Email</label>
              <input type="email" value={form.email} onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))}
                className="input" required />
            </div>
            <div>
              <label className="label">{language === 'id' ? 'Pesan' : 'Message'}</label>
              <textarea rows={4} value={form.message} onChange={(e) => setForm((p) => ({ ...p, message: e.target.value }))}
                className="input resize-none" required />
            </div>
            <button type="submit" className="btn-primary w-full">{language === 'id' ? 'Kirim Pesan' : 'Send Message'}</button>
          </form>
        )}
      </div>
    </div>
  )
}
