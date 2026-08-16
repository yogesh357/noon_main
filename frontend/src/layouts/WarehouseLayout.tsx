import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useAppSelector } from '../app/hooks'
import Toast from '../components/common/Toast'
import {
  Home,

  ListChecks,
  Package,
  Handshake,
  Box,
  Truck
} from 'lucide-react'

const navItems = [
  { to: '/warehouse', label: 'Dashboard', icon: Home, end: true },
  { to: '/warehouse/picking', label: 'Picking', icon: ListChecks },
  { to: '/warehouse/packing', label: 'Packing', icon: Package },
  { to: '/warehouse/handover', label: 'Handover', icon: Handshake },
]

export default function WarehouseLayout() {
  const navigate = useNavigate()
  const { user, loading } = useAppSelector((s) => s.auth)

  useEffect(() => {
    if (loading) return
    if (!user) navigate('/auth/login', { replace: true })
    else if (user.role !== 'WAREHOUSE' && user.role !== 'ADMIN') navigate('/', { replace: true })
  }, [user, loading])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-950">
        <div className="w-8 h-8 border-4 border-neutral-800 border-t-rose-500 rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-white flex flex-col font-sans selection:bg-primary-500/30">
      {/* Warehouse Header */}

      <header className="bg-neutral-900/50 backdrop-blur-md border-b border-white/5 px-6 py-4 sticky top-0 z-50">
        <div className="flex items-center justify-between max-w-[1440px] mx-auto w-full">
          <div className="flex items-center gap-4 group cursor-default">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-rose-500 to-rose-600 flex items-center justify-center shadow-lg shadow-rose-900/20 transition-transform group-hover:rotate-12 duration-300">
              <Box className="text-white" size={20} />
            </div>
            <div>
              <p className="text-xs font-black text-white uppercase tracking-widest">Warehouse Ops</p>
              <p className="text-[10px] text-neutral-500 font-bold uppercase tracking-tighter">Phoenix  WMS</p>
            </div>
          </div>
          {user && (
            <div className="flex items-center gap-4 bg-white/5 p-1.5 pr-4 rounded-xl border border-white/10 group">
              <div className="w-8 h-8 rounded-lg bg-neutral-800 flex items-center justify-center text-xs font-black text-rose-500 group-hover:bg-rose-500 group-hover:text-white transition-all duration-300">
                {user.full_name?.charAt(0).toUpperCase()}
              </div>
              <div className="text-right hidden sm:block">
                <p className="text-xs font-black text-white">{user.full_name}</p>
                <p className="text-[10px] text-neutral-500 font-bold uppercase tracking-[0.05em]">Logistics Staff</p>
              </div>
            </div>
          )}
        </div>
      </header>

      <div className="flex flex-1 w-full">
        {/* Sidebar */}
        <aside className="hidden lg:flex w-64 flex-shrink-0 flex-col bg-neutral-950 border-r border-white/5 p-6">
          <nav className="space-y-1.5 flex-1">
            <h3 className="text-[10px] font-black text-neutral-600 uppercase tracking-[0.2em] mb-4 ml-2">Main Controls</h3>
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold transition-all duration-300 group ${isActive
                      ? 'bg-rose-600 text-white shadow-lg shadow-rose-900/20 translate-x-1'
                      : 'text-neutral-500 hover:bg-white/5 hover:text-white'
                    }`
                  }
                >
                  <Icon size={18} className="transition-transform group-hover:scale-110" />
                  <span>{item.label}</span>
                </NavLink>
              )
            })}
          </nav>

          <div className="mt-auto">
            <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
              <div className="flex items-center gap-2 mb-2">
                <Truck size={14} className="text-rose-500" />
                <span className="text-[10px] font-black text-neutral-400 uppercase tracking-widest">Quick Report</span>
              </div>
              <p className="text-[11px] text-neutral-500 leading-relaxed">
                Report any equipment issues or inventory discrepancies immediately.
              </p>
            </div>
          </div>
        </aside>

        {/* Content */}
        <main className="flex-1 p-6 lg:p-8 pb-24 lg:pb-8 bg-neutral-950/40 backdrop-blur-sm">
          <Outlet />
        </main>
      </div>

      {/* Mobile Bottom Nav */}
      <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-neutral-900/90 backdrop-blur-xl border-t border-white/5 flex z-40 px-2 py-1.5 shadow-[0_-8px_30px_rgb(0,0,0,0.5)]">
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `flex-1 flex flex-col items-center py-2 text-[10px] gap-1 transition-all duration-300 ${isActive
                  ? 'text-rose-500 font-black scale-110'
                  : 'text-neutral-500 font-bold'
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
        })}</nav>
      <Toast />
    </div>
  )
}
