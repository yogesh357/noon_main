import { useState } from 'react'
import { useAppDispatch, useAppSelector } from '../../app/hooks'
import { setUser } from '../../features/auth/authSlice'
import { showToast } from '../../features/ui/uiSlice'
import { dashboardService } from '../../services/api.service'

export default function DashboardProfilePage() {
  const dispatch = useAppDispatch()
  const { user } = useAppSelector((s) => s.auth)
  const { language } = useAppSelector((s) => s.ui)
  const [form, setForm] = useState({ full_name: user?.full_name ?? '', phone: user?.phone ?? '' })
  const [saving, setSaving] = useState(false)

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    try {
      const formData = new FormData()
      Object.entries(form).forEach(([k, v]) => formData.append(k, v))
      const { data } = await dashboardService.updateProfile(formData)
      dispatch(setUser(data))
      dispatch(showToast({ message: 'Profile updated', type: 'success' }))
    } catch {
      dispatch(showToast({ message: 'Failed to update profile', type: 'error' }))
    } finally {
      setSaving(false)
    }
  }

  if (!user) return null

  return (
    <div className="space-y-5 max-w-lg">
      <h1 className="text-xl font-semibold text-neutral-900">Profile Settings</h1>

      <div className="card">
        {/* Avatar */}
        <div className="flex items-center gap-4 mb-6 pb-6 border-b border-neutral-100">
          {user.avatar_url ? (
            <img src={user.avatar_url} alt={user.full_name} className="w-16 h-16 rounded-full object-cover" />
          ) : (
            <div className="w-16 h-16 rounded-full bg-brand-red text-white flex items-center justify-center text-2xl font-semibold">
              {user.full_name.charAt(0).toUpperCase()}
            </div>
          )}
          <div>
            <p className="font-semibold text-neutral-900">{user.full_name}</p>
            <p className="text-sm text-neutral-500">{user.email}</p>
            <p className="text-xs text-neutral-400 mt-0.5 capitalize">Role: {user.role.toLowerCase()}</p>
          </div>
        </div>

        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="label">Full Name</label>
            <input type="text" value={form.full_name}
              onChange={(e) => setForm((p) => ({ ...p, full_name: e.target.value }))}
              className="input" required />
          </div>
          <div>
            <label className="label">Email</label>
            <input type="email" value={user.email} className="input bg-neutral-50 cursor-not-allowed" readOnly />
            <p className="text-xs text-neutral-400 mt-1">Email cannot be changed</p>
          </div>
          <div>
            <label className="label">Phone</label>
            <input type="tel" value={form.phone}
              onChange={(e) => setForm((p) => ({ ...p, phone: e.target.value }))}
              className="input" placeholder="+62 812 3456 7890" />
          </div>
          <div>
            <label className="label">Language Preference</label>
            <select className="input" value={language} disabled>
              <option value="id">Bahasa Indonesia</option>
              <option value="en">English</option>
            </select>
            <p className="text-xs text-neutral-400 mt-1">Change via the language toggle in the header</p>
          </div>

          <button type="submit" disabled={saving} className="btn-primary">
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </form>
      </div>
    </div>
  )
}
