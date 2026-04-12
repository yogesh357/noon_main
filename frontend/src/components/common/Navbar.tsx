import { useState, useRef, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../../app/hooks'
import { logout } from '../../features/auth/authSlice'
import { toggleLanguage, setSearchOpen } from '../../features/ui/uiSlice'
import { t } from '../../utils/i18n'

export default function Navbar() {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const { user } = useAppSelector((s) => s.auth)
  const { language, notificationCount } = useAppSelector((s) => s.ui)
  const cartCount = useAppSelector((s) => s.cart.count)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchVisible, setSearchVisible] = useState(false)
  const searchRef = useRef<HTMLInputElement>(null)

  // Close dropdowns on outside click
  useEffect(() => {
    const handler = () => setProfileOpen(false)
    document.addEventListener('click', handler)
    return () => document.removeEventListener('click', handler)
  }, [])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`)
      setSearchVisible(false)
      setSearchQuery('')
    }
  }

  const handleLogout = () => {
    dispatch(logout())
    navigate('/')
  }

  const getDashboardLink = () => {
    if (!user) return '/auth/login'
    if (user.role === 'ADMIN') return '/admin-panel'
    if (user.role === 'WAREHOUSE') return '/warehouse'
    return '/dashboard'
  }

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-neutral-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 lg:h-20">

          {/* Logo */}
          <Link to="/" className="flex-shrink-0">
            <span className="text-xl font-bold tracking-tight text-neutral-900">PHOENIX</span>
          </Link>

          {/* Desktop Nav */}
          {!searchVisible && (
            <nav className="hidden lg:flex items-center space-x-8">
              <Link to="/products" className="text-sm font-medium text-neutral-600 hover:text-neutral-900 transition-colors">
                {t('Products', language)}
              </Link>
              <Link to="/about" className="text-sm font-medium text-neutral-600 hover:text-neutral-900 transition-colors">
                {t('About Us', language)}
              </Link>
              <Link to="/faq" className="text-sm font-medium text-neutral-600 hover:text-neutral-900 transition-colors">
                {t('FAQ', language)}
              </Link>
              <Link to="/contact" className="text-sm font-medium text-neutral-600 hover:text-neutral-900 transition-colors">
                {t('Contact', language)}
              </Link>
            </nav>
          )}

          {/* Search input (expanded) */}
          {searchVisible && (
            <form onSubmit={handleSearch} className="flex-1 mx-8 hidden lg:block">
              <div className="relative">
                <input
                  ref={searchRef}
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={t('Search products...', language)}
                  className="w-full px-4 py-2.5 pl-10 border border-neutral-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-red/20 focus:border-brand-red"
                  autoFocus
                />
                <svg className="absolute left-3 top-3 w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <button type="button" onClick={() => setSearchVisible(false)}
                  className="absolute right-3 top-2.5 text-neutral-400 hover:text-neutral-700">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </form>
          )}

          {/* Right Controls */}
          <div className="flex items-center space-x-1 sm:space-x-2">
            {/* Search toggle */}
            <button onClick={() => { setSearchVisible(!searchVisible); setMobileOpen(false) }}
              className="p-2 text-neutral-600 hover:text-neutral-900 transition-colors rounded-lg hover:bg-neutral-100"
              aria-label="Search">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>

            {/* Language toggle */}
            <button
              onClick={() => dispatch(toggleLanguage())}
              className="hidden sm:inline-flex items-center px-2.5 py-1.5 text-xs font-medium text-neutral-600 border border-neutral-300 rounded-lg hover:bg-neutral-50 transition-colors"
            >
              {language === 'id' ? 'EN' : 'ID'}
            </button>

            {/* Account / Profile */}
            {user ? (
              <div className="relative" onClick={(e) => e.stopPropagation()}>
                <button onClick={() => setProfileOpen(!profileOpen)}
                  className="flex items-center gap-2 p-2 text-neutral-600 hover:text-neutral-900 rounded-lg hover:bg-neutral-100 transition-colors">
                  {user.avatar_url ? (
                    <img src={user.avatar_url} alt={user.full_name} className="w-7 h-7 rounded-full object-cover" />
                  ) : (
                    <div className="w-7 h-7 rounded-full bg-brand-red text-white flex items-center justify-center text-xs font-semibold">
                      {user.full_name.charAt(0).toUpperCase()}
                    </div>
                  )}
                  {notificationCount > 0 && (
                    <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-brand-red text-white text-[10px] rounded-full flex items-center justify-center">
                      {notificationCount > 9 ? '9+' : notificationCount}
                    </span>
                  )}
                </button>
                {profileOpen && (
                  <div className="absolute right-0 mt-2 w-52 bg-white rounded-xl shadow-lg border border-neutral-200 py-1 z-50">
                    <div className="px-4 py-2.5 border-b border-neutral-100">
                      <p className="text-sm font-medium text-neutral-900 truncate">{user.full_name}</p>
                      <p className="text-xs text-neutral-500 truncate">{user.email}</p>
                    </div>
                    <Link to={getDashboardLink()} className="flex items-center gap-2 px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-50">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6z" /></svg>
                      {t('My Dashboard', language)}
                    </Link>
                    <Link to="/dashboard/orders" className="flex items-center gap-2 px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-50">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2" /></svg>
                      {t('Orders', language)}
                    </Link>
                    <Link to="/dashboard/notifications" className="flex items-center gap-2 px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-50">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>
                      {t('Notifications', language)}
                      {notificationCount > 0 && (
                        <span className="ml-auto bg-brand-red text-white text-xs px-1.5 py-0.5 rounded-full">{notificationCount}</span>
                      )}
                    </Link>
                    <div className="border-t border-neutral-100 mt-1">
                      <button onClick={handleLogout}
                        className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
                        {t('Logout', language)}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <Link to="/auth/login" className="p-2 text-neutral-600 hover:text-neutral-900 transition-colors rounded-lg hover:bg-neutral-100">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </Link>
            )}

            {/* Cart */}
            <Link to="/cart" className="relative p-2 text-neutral-600 hover:text-neutral-900 transition-colors rounded-lg hover:bg-neutral-100" aria-label="Cart">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
              </svg>
              {cartCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 bg-brand-red text-white text-[10px] w-4 h-4 rounded-full flex items-center justify-center font-medium">
                  {cartCount > 9 ? '9+' : cartCount}
                </span>
              )}
            </Link>

            {/* Mobile menu */}
            <button onClick={() => setMobileOpen(!mobileOpen)}
              className="lg:hidden p-2 text-neutral-600 rounded-lg hover:bg-neutral-100">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {mobileOpen
                  ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" />
                  : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 6h16M4 12h16M4 18h16" />
                }
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile search */}
      {searchVisible && (
        <div className="lg:hidden px-4 pb-3">
          <form onSubmit={handleSearch}>
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={t('Search products...', language)}
                className="w-full px-4 py-2.5 pl-10 border border-neutral-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-red/20 focus:border-brand-red"
                autoFocus
              />
              <svg className="absolute left-3 top-3 w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </form>
        </div>
      )}

      {/* Mobile Nav */}
      {mobileOpen && (
        <div className="lg:hidden border-t border-neutral-200 bg-white">
          <nav className="max-w-7xl mx-auto px-4 py-4 space-y-1">
            <Link to="/products" onClick={() => setMobileOpen(false)} className="block py-2.5 px-3 rounded-lg text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 text-sm font-medium">
              {t('Products', language)}
            </Link>
            <Link to="/about" onClick={() => setMobileOpen(false)} className="block py-2.5 px-3 rounded-lg text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 text-sm font-medium">
              {t('About Us', language)}
            </Link>
            <Link to="/faq" onClick={() => setMobileOpen(false)} className="block py-2.5 px-3 rounded-lg text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 text-sm font-medium">
              {t('FAQ', language)}
            </Link>
            <Link to="/contact" onClick={() => setMobileOpen(false)} className="block py-2.5 px-3 rounded-lg text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 text-sm font-medium">
              {t('Contact', language)}
            </Link>
            <div className="pt-2 border-t border-neutral-100">
              <button onClick={() => { dispatch(toggleLanguage()); setMobileOpen(false) }}
                className="block py-2.5 px-3 text-sm text-neutral-600">
                {language === 'id' ? '🌐 English' : '🌐 Indonesia'}
              </button>
            </div>
          </nav>
        </div>
      )}
    </header>
  )
}
