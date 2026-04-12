import { useAppSelector } from '../../app/hooks'
import Breadcrumb from '../../components/common/Breadcrumb'

export default function DisclaimerPage() {
  const { language } = useAppSelector((s) => s.ui)
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Breadcrumb items={[{ label: 'Home', href: '/' }, { label: 'Disclaimer' }]} />
      <h1 className="text-3xl font-semibold text-neutral-900 mb-8">Disclaimer</h1>
      <div className="text-neutral-600 leading-relaxed space-y-5 text-sm">
        <p>{language === 'id'
          ? 'Informasi yang disediakan di platform ini hanya untuk keperluan informasi umum. Kami berupaya menjaga informasi tetap akurat dan terkini, namun tidak memberikan jaminan atas kelengkapan, keakuratan, atau kesesuaiannya.'
          : 'The information provided on this platform is for general information purposes only. We strive to keep the information accurate and up-to-date, but we make no representations or warranties of any kind.'}</p>
        <p>{language === 'id'
          ? 'Harga dan ketersediaan produk dapat berubah sewaktu-waktu tanpa pemberitahuan sebelumnya.'
          : 'Product prices and availability are subject to change without prior notice.'}</p>
      </div>
    </div>
  )
}
