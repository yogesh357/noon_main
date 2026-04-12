import { useEffect, useState } from 'react'
import { useAppDispatch, useAppSelector } from '../../app/hooks'
import { dashboardService } from '../../services/api.service'
import { setNotificationCount } from '../../features/ui/uiSlice'
import type { Notification } from '../../types'

export default function DashboardNotificationsPage() {
  const dispatch = useAppDispatch()
  const { language } = useAppSelector((s) => s.ui)
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)

  const load = async () => {
    const { data } = await dashboardService.getNotifications()
    setNotifications(data)
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  const markRead = async (id: number) => {
    await dashboardService.markRead(id)
    setNotifications((prev) => prev.map((n) => n.id === id ? { ...n, is_read: true } : n))
    dispatch(setNotificationCount(notifications.filter((n) => !n.is_read && n.id !== id).length))
  }

  const markAllRead = async () => {
    await dashboardService.markAllRead()
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })))
    dispatch(setNotificationCount(0))
  }

  const unreadCount = notifications.filter((n) => !n.is_read).length

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-neutral-900">Notifications</h1>
        {unreadCount > 0 && (
          <button onClick={markAllRead} className="text-sm text-brand-red hover:text-brand-red-dark font-medium">
            Mark all read
          </button>
        )}
      </div>

      {loading ? (
        <div className="space-y-3">{[...Array(4)].map((_, i) => <div key={i} className="skeleton h-16 rounded-xl" />)}</div>
      ) : notifications.length === 0 ? (
        <div className="card text-center py-12 text-neutral-400">No notifications yet</div>
      ) : (
        <div className="space-y-2">
          {notifications.map((n) => (
            <div key={n.id}
              className={`card cursor-pointer transition-colors ${!n.is_read ? 'bg-brand-red/5 border-brand-red/20' : 'hover:border-neutral-300'}`}
              onClick={() => !n.is_read && markRead(n.id)}>
              <div className="flex gap-3">
                <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${n.is_read ? 'bg-neutral-200' : 'bg-brand-red'}`} />
                <div className="min-w-0">
                  <p className={`text-sm font-medium ${n.is_read ? 'text-neutral-600' : 'text-neutral-900'}`}>
                    {language === 'en' ? n.title_en : n.title_id}
                  </p>
                  <p className="text-xs text-neutral-500 mt-0.5 line-clamp-2">
                    {language === 'en' ? n.message_en : n.message_id}
                  </p>
                  <p className="text-xs text-neutral-400 mt-1">
                    {new Date(n.created_at).toLocaleString('id-ID')}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
