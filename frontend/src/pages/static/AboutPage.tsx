import { useAppSelector } from '../../app/hooks'
import { Link } from 'react-router-dom'

export default function AboutPage() {
  const { language } = useAppSelector((s) => s.ui)
  return (
    <div>
      <div className="bg-neutral-100 py-20">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h1 className="text-4xl font-bold text-neutral-900 mb-4">
            {language === 'id' ? 'Tentang Noon' : 'About Noon'}
          </h1>
          <p className="text-lg text-neutral-600 leading-relaxed">
            {language === 'id'
              ? 'Kami adalah toko online terpercaya yang menghadirkan produk berkualitas tinggi untuk Anda.'
              : 'We are a trusted online store bringing high-quality products directly to you.'}
          </p>
        </div>
      </div>
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <Link to="/products" className="btn-primary">{language === 'id' ? 'Lihat Produk' : 'View Products'}</Link>
      </div>
    </div>
  )
}
