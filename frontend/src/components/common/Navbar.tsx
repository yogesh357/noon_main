import { useState, useRef, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../../app/hooks'
import { logout } from '../../features/auth/authSlice'
import { toggleLanguage, setSearchOpen } from '../../features/ui/uiSlice'
import { t } from '../../utils/i18n'
import { 
  Search, 
  Languages, 
  User, 
  ShoppingBag, 
  Menu, 
  X, 
  LogOut, 
  LayoutDashboard, 
  Bell,
  ShoppingCart,
  ChevronDown
} from 'lucide-react'

export default function Navbar({ fluid = false }: { fluid?: boolean }) {
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
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-neutral-100 shadow-sm">
      <div className={fluid ? "px-4 sm:px-6 lg:px-10" : "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"}>
        <div className="flex items-center justify-between h-16 lg:h-20">

          {/* Logo */}
          <Link to="/" className="flex-shrink-0 group flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-neutral-900 flex items-center justify-center transition-transform group-hover:rotate-12">
              <span className="text-white text-lg font-black italic">N</span>
            </div>
            <span className="text-xl font-black tracking-tighter text-neutral-900 uppercase">NOON</span>
          </Link>

          {/* Desktop Nav */}
          {!searchVisible && (
            <nav className="hidden lg:flex items-center space-x-1">
              {[
                { label: 'Products', to: '/products' },
                { label: 'About Us', to: '/about' },
                { label: 'FAQ', to: '/faq' },
                { label: 'Contact', to: '/contact' }
              ].map((item) => (
                <Link 
                  key={item.to}
                  to={item.to} 
                  className="px-4 py-2 text-sm font-bold text-neutral-500 hover:text-neutral-900 hover:bg-neutral-50 rounded-xl transition-all"
                >
                  {t(item.label, language)}
                </Link>
              ))}
            </nav>
          )}

          {/* Search input (expanded) */}
          {searchVisible && (
            <form onSubmit={handleSearch} className="flex-1 mx-8 hidden lg:block transition-all animate-in fade-in slide-in-from-top-2">
              <div className="relative">
                <input
                  ref={searchRef}
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={t('Search products...', language)}
                  className="w-full px-5 py-3 pl-12 bg-neutral-100 border-none rounded-2xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:bg-white transition-all shadow-inner"
                  autoFocus
                />
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                <button 
                  type="button" 
                  onClick={() => setSearchVisible(false)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-900 transition-colors p-1"
                >
                  <X size={16} />
                </button>
              </div>
            </form>
          )}

          {/* Right Controls */}
          <div className="flex items-center space-x-1 sm:space-x-2">
            {/* Search toggle */}
            {!searchVisible && (
              <button 
                onClick={() => { setSearchVisible(true); setMobileOpen(false) }}
                className="p-2.5 text-neutral-500 hover:text-neutral-900 rounded-xl hover:bg-neutral-50 transition-all active:scale-95"
                aria-label="Search"
              >
                <Search size={20} />
              </button>
            )}

            {/* Language toggle */}
            <button
              onClick={() => dispatch(toggleLanguage())}
              className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-black text-neutral-500 border border-neutral-200 rounded-xl hover:bg-neutral-50 hover:border-neutral-300 transition-all active:scale-95"
              title={language === 'id' ? 'Switch to English' : 'Ganti ke Bahasa Indonesia'}
            >
              <Languages size={14} className="opacity-50" />
              {language === 'id' ? 'EN' : 'Bahasa'}
            </button>

            {/* Account / Profile */}
            {user ? (
              <div className="relative" onClick={(e) => e.stopPropagation()}>
                <button 
                  onClick={() => setProfileOpen(!profileOpen)}
                  className="flex items-center gap-2 p-1.5 pr-2.5 bg-neutral-100 hover:bg-neutral-200 rounded-2xl transition-all group active:scale-95"
                >
                  {user.avatar_url ? (
                    <img src={user.avatar_url} alt={user.full_name} className="w-8 h-8 rounded-xl object-cover shadow-sm" />
                  ) : (
                    <div className="w-8 h-8 rounded-xl bg-primary-600 text-white flex items-center justify-center text-xs font-black shadow-lg shadow-primary-200">
                      {user.full_name.charAt(0).toUpperCase()}
                    </div>
                  )}
                  <ChevronDown size={14} className={`text-neutral-400 transition-transform duration-300 ${profileOpen ? 'rotate-180' : ''}`} />
                  {notificationCount > 0 && (
                    <span className="absolute -top-1 -right-1 w-5 h-5 bg-rose-500 text-white text-[10px] rounded-full flex items-center justify-center font-black border-2 border-white animate-bounce">
                      {notificationCount > 9 ? '9+' : notificationCount}
                    </span>
                  )}
                </button>
                {profileOpen && (
                  <div className="absolute right-0 mt-3 w-64 bg-white/90 backdrop-blur-xl rounded-2xl shadow-2xl border border-neutral-100 p-2 z-50 animate-in fade-in zoom-in-95 font-sans">
                    <div className="px-4 py-3 mb-1 bg-neutral-50/50 rounded-xl border border-neutral-100">
                      <p className="text-sm font-black text-neutral-900 truncate">{user.full_name}</p>
                      <p className="text-[10px] text-neutral-500 truncate font-bold uppercase tracking-widest">{user.email}</p>
                    </div>
                    
                    <div className="grid grid-cols-1 gap-0.5">
                      <Link to={getDashboardLink()} className="flex items-center gap-3 px-3 py-2.5 text-sm font-bold text-neutral-600 hover:bg-primary-50 hover:text-primary-700 rounded-xl transition-colors group">
                        <LayoutDashboard size={18} className="opacity-50 group-hover:opacity-100 transition-opacity" />
                        {t('My Dashboard', language)}
                      </Link>
                      <Link to="/dashboard/orders" className="flex items-center gap-3 px-3 py-2.5 text-sm font-bold text-neutral-600 hover:bg-primary-50 hover:text-primary-700 rounded-xl transition-colors group">
                        <ShoppingCart size={18} className="opacity-50 group-hover:opacity-100 transition-opacity" />
                        {t('Orders', language)}
                      </Link>
                      <Link to="/dashboard/notifications" className="flex items-center justify-between px-3 py-2.5 text-sm font-bold text-neutral-600 hover:bg-primary-50 hover:text-primary-700 rounded-xl transition-colors group">
                        <div className="flex items-center gap-3">
                          <Bell size={18} className="opacity-50 group-hover:opacity-100 transition-opacity" />
                          {t('Notifications', language)}
                        </div>
                        {notificationCount > 0 && (
                          <span className="bg-rose-500 text-white text-[10px] px-2 py-0.5 rounded-full font-black">{notificationCount}</span>
                        )}
                      </Link>
                    </div>

                    <div className="mt-2 pt-2 border-t border-neutral-50">
                      <button 
                        onClick={handleLogout}
                        className="w-full flex items-center gap-3 px-3 py-2.5 text-sm font-black text-rose-500 hover:bg-rose-50 rounded-xl transition-colors group"
                      >
                        <LogOut size={18} className="group-hover:translate-x-1 transition-transform" />
                        {t('Logout', language)}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <Link 
                to="/auth/login" 
                className="p-2.5 text-neutral-500 hover:text-neutral-900 rounded-xl hover:bg-neutral-50 transition-all active:scale-95"
              >
                <User size={20} />
              </Link>
            )}

            {/* Cart */}
            <Link 
              to="/cart" 
              className="relative p-2.5 text-neutral-500 hover:text-neutral-900 rounded-xl hover:bg-neutral-50 transition-all group active:scale-95" 
              aria-label="Cart"
            >
              <ShoppingBag size={20} className="group-hover:rotate-6 transition-transform" />
              {cartCount > 0 && (
                <span className="absolute top-1 right-1 bg-primary-600 text-white text-[10px] w-5 h-5 rounded-full flex items-center justify-center font-black border-2 border-white shadow-sm">
                  {cartCount > 9 ? '9+' : cartCount}
                </span>
              )}
            </Link>

            {/* Mobile menu toggle */}
            <button 
              onClick={() => setMobileOpen(!mobileOpen)}
              className="lg:hidden p-2.5 text-neutral-500 hover:text-neutral-900 rounded-xl hover:bg-neutral-50 transition-all active:scale-95"
            >
              {mobileOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Nav */}
      {mobileOpen && (
        <div className="lg:hidden border-t border-neutral-100 bg-white/95 backdrop-blur-xl animate-in fade-in slide-in-from-top-4">
          <nav className="px-4 py-6 space-y-1">
            {[
              { label: 'Products', to: '/products' },
              { label: 'About Us', to: '/about' },
              { label: 'FAQ', to: '/faq' },
              { label: 'Contact', to: '/contact' }
            ].map((item) => (
              <Link 
                key={item.to}
                to={item.to} 
                onClick={() => setMobileOpen(false)} 
                className="block py-3 px-4 rounded-2xl text-base font-black text-neutral-600 hover:bg-primary-50 hover:text-primary-700 transition-all"
              >
                {t(item.label, language)}
              </Link>
            ))}
            
            <div className="pt-4 mt-4 border-t border-neutral-50">
              <button 
                onClick={() => { dispatch(toggleLanguage()); setMobileOpen(false) }}
                className="w-full flex items-center justify-between py-3 px-4 bg-neutral-50 rounded-2xl text-sm font-black text-neutral-600"
              >
                <div className="flex items-center gap-2">
                  <Languages size={18} className="opacity-50" />
                  {language === 'id' ? 'Switch to English' : 'Ganti ke Bahasa Indonesia'}
                </div>
                <span className="text-primary-600 font-bold">{language === 'id' ? '→ EN' : '→ Bahasa'}</span>
              </button>
            </div>
          </nav>
        </div>
      )}
    </header>
  )
}
