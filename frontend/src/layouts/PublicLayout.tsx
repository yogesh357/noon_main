import { Outlet } from 'react-router-dom'
import { useEffect } from 'react'
import { useAppDispatch, useAppSelector } from '../app/hooks'
import { fetchMe } from '../features/auth/authSlice'
import { fetchCartCount } from '../features/cart/cartSlice'
import { setNotificationCount } from '../features/ui/uiSlice'
import { dashboardService } from '../services/api.service'
import Navbar from '../components/common/Navbar'
import Footer from '../components/common/Footer'
import Toast from '../components/common/Toast'

export default function PublicLayout() {
  const dispatch = useAppDispatch()
  const { token, user } = useAppSelector((s) => s.auth)

  useEffect(() => {
    // Hydrate auth and cart on mount
    if (token && !user) {
      dispatch(fetchMe())
    }
    dispatch(fetchCartCount())
  }, [token])

  useEffect(() => {
    // Poll notification count if logged in
    if (!user) return
    const loadCount = async () => {
      try {
        const { data } = await dashboardService.getNotificationCount()
        dispatch(setNotificationCount(data.count))
      } catch { /* ignore */ }
    }
    loadCount()
    const interval = setInterval(loadCount, 60_000)
    return () => clearInterval(interval)
  }, [user])

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
      <Toast />
    </div>
  )
}
