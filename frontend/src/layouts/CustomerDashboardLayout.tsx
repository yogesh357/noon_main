import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useAppSelector } from '../app/hooks'
import Navbar from '../components/common/Navbar'
import Footer from '../components/common/Footer'
import Toast from '../components/common/Toast'
import { 
  LayoutGrid, 
  ShoppingBag, 
  Truck, 
  AlertCircle, 
  MapPin, 
  CreditCard, 
  Heart, 
  User, 
  Bell 
} from 'lucide-react'

const navItems = [
  { to: '/dashboard', label: 'Overview', icon: LayoutGrid, end: true },
  { to: '/dashboard/orders', label: 'Orders', icon: ShoppingBag },
  { to: '/dashboard/tracking', label: 'Track Shipment', icon: Truck },
  { to: '/dashboard/disputes', label: 'Disputes', icon: AlertCircle },
  { to: '/dashboard/addresses', label: 'Addresses', icon: MapPin },
  { to: '/dashboard/payments', label: 'Payments', icon: CreditCard },
  { to: '/dashboard/wishlist', label: 'Wishlist', icon: Heart },
  { to: '/dashboard/profile', label: 'Profile', icon: User },
  { to: '/dashboard/notifications', label: 'Notifications', icon: Bell },
]

export default function CustomerDashboardLayout() {
  const navigate = useNavigate()
  const { user } = useAppSelector((s) => s.auth)
  const notificationCount = useAppSelector((s) => s.ui.notificationCount)

  useEffect(() => {
    if (!user) navigate('/auth/login', { replace: true })
    else if (user.role !== 'CUSTOMER') navigate('/', { replace: true })
  }, [user])

  return (
    <div className="min-h-screen flex flex-col bg-neutral-50/50">
      <Navbar />
      <main className="flex-1 max-w-[1440px] mx-auto w-full">
        <div className="px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Sidebar */}
            <aside className="w-full lg:w-64 flex-shrink-0">
              <div className="elevated-card p-2 sticky top-24">
                {/* User info */}
                {user && (
                  <div className="relative overflow-hidden p-4 mb-4 rounded-xl bg-gradient-to-br from-primary-600 to-indigo-700 text-white shadow-lg shadow-primary-200">
                    <div className="relative z-10">
                      <p className="text-xs font-black uppercase tracking-widest opacity-80 mb-1">Customer Account</p>
                      <p className="text-base font-bold truncate">{user.full_name}</p>
                      <p className="text-[10px] opacity-70 truncate font-medium">{user.email}</p>
                    </div>
                    <div className="absolute -right-4 -bottom-4 opacity-10 group-hover:scale-125 transition-transform duration-500">
                      <User size={80} />
                    </div>
                  </div>
                )}
                
                <nav className="space-y-1">
                  <h3 className="text-[10px] font-black text-neutral-400 uppercase tracking-[0.2em] mb-3 ml-3">Navigation</h3>
                  {navItems.map((item) => {
                    const Icon = item.icon
                    return (
                      <NavLink
                        key={item.to}
                        to={item.to}
                        end={item.end}
                        className={({ isActive }) =>
                          `sidebar-link group ${isActive ? 'active' : 'hover:translate-x-1'}`
                        }
                      >
                        <Icon size={18} className="transition-transform group-hover:scale-110" />
                        <span className="font-semibold">{item.label}</span>
                        {item.label === 'Notifications' && notificationCount > 0 && (
                          <span className="ml-auto bg-rose-500 text-white text-[10px] px-2 py-0.5 rounded-full font-black shadow-sm group-hover:animate-bounce">
                            {notificationCount}
                          </span>
                        )}
                      </NavLink>
                    )
                  })}
                </nav>
              </div>
            </aside>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <Outlet />
            </div>
          </div>
        </div>
      </main>
      <Footer />
      <Toast />
    </div>
  )
}
