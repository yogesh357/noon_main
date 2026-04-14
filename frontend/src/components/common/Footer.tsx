import { Link } from 'react-router-dom'
import { useAppSelector } from '../../app/hooks'
import { t } from '../../utils/i18n'

export default function Footer() {
  const { language } = useAppSelector((s) => s.ui)
  const year = new Date().getFullYear()

  return (
    <footer className="bg-neutral-900 text-neutral-400">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div>
            <span className="text-lg font-bold text-white tracking-tight">NOON</span>
            <p className="mt-3 text-sm leading-relaxed">
              {language === 'id'
                ? 'Toko online terpercaya untuk produk berkualitas.'
                : 'Your trusted online store for quality products.'}
            </p>
          </div>

          {/* Shop */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">{t('Shop', language)}</h3>
            <ul className="space-y-2.5 text-sm">
              <li><Link to="/products" className="hover:text-white transition-colors">{t('All Products', language)}</Link></li>
              <li><Link to="/products?sort=newest" className="hover:text-white transition-colors">{t('New Arrivals', language)}</Link></li>
              <li><Link to="/search" className="hover:text-white transition-colors">{t('Search', language)}</Link></li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">{t('Support', language)}</h3>
            <ul className="space-y-2.5 text-sm">
              <li><Link to="/faq" className="hover:text-white transition-colors">{t('FAQ', language)}</Link></li>
              <li><Link to="/contact" className="hover:text-white transition-colors">{t('Contact Us', language)}</Link></li>
              <li><Link to="/terms" className="hover:text-white transition-colors">{t('Terms & Conditions', language)}</Link></li>
              <li><Link to="/disclaimer" className="hover:text-white transition-colors">{t('Disclaimer', language)}</Link></li>
            </ul>
          </div>

          {/* Account */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">{t('Account', language)}</h3>
            <ul className="space-y-2.5 text-sm">
              <li><Link to="/auth/login" className="hover:text-white transition-colors">{t('Login', language)}</Link></li>
              <li><Link to="/auth/register" className="hover:text-white transition-colors">{t('Register', language)}</Link></li>
              <li><Link to="/dashboard" className="hover:text-white transition-colors">{t('My Dashboard', language)}</Link></li>
            </ul>
          </div>
        </div>

        <div className="mt-10 pt-8 border-t border-neutral-800 text-sm text-center">
          &copy; {year} Noon. All rights reserved.
        </div>
      </div>
    </footer>
  )
}
