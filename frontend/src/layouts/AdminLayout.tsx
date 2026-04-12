import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useAppSelector } from '../app/hooks'
import Navbar from '../components/common/Navbar'
import Toast from '../components/common/Toast'
import { 
  LayoutDashboard, 
  ShoppingCart, 
  Repeat, 
  AlertTriangle, 
  ShieldCheck,
  PackageSearch
} from 'lucide-react'

const navItems = [
  { to: '/admin-panel', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/admin-panel/orders', label: 'Orders', icon: ShoppingCart },
  { to: '/admin-panel/marketplace-orders', label: 'Marketplace', icon: PackageSearch },
  { to: '/admin-panel/disputes', label: 'Disputes', icon: AlertTriangle },
]

export default function AdminLayout() {
  const navigate = useNavigate()
  const { user } = useAppSelector((s) => s.auth)

  useEffect(() => {
    if (!user) navigate('/auth/login', { replace: true })
    else if (user.role !== 'ADMIN') navigate('/', { replace: true })
  }, [user])

  return (
    <div className="min-h-screen flex flex-col bg-neutral-50/50">
      <Navbar />
      <div className="flex-1 flex max-w-[1440px] mx-auto w-full">
        {/* Sidebar */}
        <aside className="hidden lg:flex w-64 flex-shrink-0 flex-col border-r border-neutral-100 bg-white/50 backdrop-blur-xl sticky top-20 h-[calc(100vh-5rem)]">
          <div className="p-6 flex flex-col h-full">
            <div className="flex items-center gap-3 px-2 mb-8 group cursor-default">
              <div className="w-10 h-10 rounded-xl bg-primary-600 flex items-center justify-center shadow-lg shadow-primary-200 transition-transform group-hover:scale-110 duration-300">
                <ShieldCheck className="text-white" size={20} />
              </div>
              <div>
                <p className="text-xs font-black text-neutral-900 uppercase tracking-widest">Admin Panel</p>
                <p className="text-[10px] text-primary-600 font-bold uppercase tracking-tighter">System Oversight</p>
              </div>
            </div>

            <nav className="flex-1 space-y-1.5">
              {navItems.map((item) => {
                const Icon = item.icon
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.end}
                    className={({ isActive }) => `sidebar-link ${isActive ? 'active shadow-lg shadow-primary-100' : 'hover:translate-x-1'}`}
                  >
                    <Icon size={18} className="transition-transform group-hover:scale-110" />
                    <span className="font-semibold">{item.label}</span>
                  </NavLink>
                )
              })}
            </nav>

            <div className="mt-auto pt-6 border-t border-neutral-100">
              <div className="p-4 rounded-2xl bg-gradient-to-br from-primary-50 to-accent-50 border border-primary-100">
                <p className="text-[10px] font-black text-primary-700 uppercase tracking-widest mb-1">System Health</p>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                  <span className="text-[10px] font-bold text-neutral-600">All systems operational</span>
                </div>
              </div>
            </div>
          </div>
        </aside>

        {/* Mobile bottom nav */}
        <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-white/80 backdrop-blur-xl border-t border-neutral-100 z-40 flex px-2 py-1 shadow-[0_-8px_30px_rgb(0,0,0,0.04)]">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `flex-1 flex flex-col items-center py-2 text-[10px] gap-1 transition-all duration-300 ${
                    isActive 
                      ? 'text-primary-600 font-black scale-110' 
                      : 'text-neutral-400 font-bold hover:text-neutral-600'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon size={20} strokeWidth={isActive ? 2.5 : 2} />
                    <span className="uppercase tracking-[0.05em]">{item.label}</span>
                  </>
                )}
              </NavLink>
            )
          })}
        </div>

        {/* Content */}
        <main className="flex-1 overflow-auto pb-20 lg:pb-0">
          <div className="max-w-full lg:p-8 p-4">
            <Outlet />
          </div>
        </main>
      </div>
      <Toast />
    </div>
  )
}
