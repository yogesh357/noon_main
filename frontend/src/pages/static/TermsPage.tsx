import { useAppSelector } from '../../app/hooks'
import Breadcrumb from '../../components/common/Breadcrumb'

export default function TermsPage() {
  const { language } = useAppSelector((s) => s.ui)
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Breadcrumb items={[{ label: 'Home', href: '/' }, { label: language === 'id' ? 'Syarat & Ketentuan' : 'Terms & Conditions' }]} />
      <h1 className="text-3xl font-semibold text-neutral-900 mb-8">{language === 'id' ? 'Syarat & Ketentuan' : 'Terms & Conditions'}</h1>
      <div className="prose prose-neutral max-w-none text-neutral-600 leading-relaxed space-y-5 text-sm">
        <p>{language === 'id' ? 'Dengan menggunakan layanan kami, Anda menyetujui syarat dan ketentuan yang berlaku.' : 'By using our service, you agree to the applicable terms and conditions.'}</p>
        <h2 className="text-base font-semibold text-neutral-900">{language === 'id' ? '1. Penggunaan Layanan' : '1. Use of Service'}</h2>
        <p>{language === 'id' ? 'Layanan kami hanya boleh digunakan untuk tujuan yang sah dan sesuai dengan peraturan yang berlaku.' : 'Our service may only be used for lawful purposes in accordance with applicable regulations.'}</p>
        <h2 className="text-base font-semibold text-neutral-900">{language === 'id' ? '2. Akun Pengguna' : '2. User Accounts'}</h2>
        <p>{language === 'id' ? 'Anda bertanggung jawab menjaga kerahasiaan akun dan kata sandi Anda.' : 'You are responsible for maintaining the confidentiality of your account and password.'}</p>
        <h2 className="text-base font-semibold text-neutral-900">{language === 'id' ? '3. Kebijakan Pengembalian' : '3. Return Policy'}</h2>
        <p>{language === 'id' ? 'Pengembalian produk dapat dilakukan dalam 30 hari setelah diterima, dengan syarat produk dalam kondisi original.' : 'Product returns can be made within 30 days of receipt, provided the product is in its original condition.'}</p>
      </div>
    </div>
  )
}
