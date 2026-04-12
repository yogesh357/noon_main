import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../../app/hooks'
import { register, clearError } from '../../features/auth/authSlice'
import { showToast } from '../../features/ui/uiSlice'

export default function RegisterPage() {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const { loading, error, user } = useAppSelector((s) => s.auth)
  const [form, setForm] = useState({ full_name: '', email: '', phone: '', password: '', confirm: '' })
  const [showPw, setShowPw] = useState(false)

  useEffect(() => { if (user) navigate('/dashboard', { replace: true }) }, [user])
  useEffect(() => { return () => { dispatch(clearError()) } }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (form.password !== form.confirm) {
      dispatch(showToast({ message: 'Passwords do not match', type: 'error' }))
      return
    }
    const result = await dispatch(register({
      full_name: form.full_name,
      email: form.email,
      phone: form.phone || undefined,
      password: form.password,
    }))
    if (register.fulfilled.match(result)) {
      dispatch(showToast({ message: 'Account created! Please sign in.', type: 'success' }))
      navigate('/auth/login')
    }
  }

  const update = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }))

  return (
    <div className="min-h-[70vh] flex items-center justify-center py-12 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-semibold text-neutral-900">Create Account</h1>
          <p className="text-neutral-500 mt-2 text-sm">Join us today</p>
        </div>

        {error && (
          <div className="mb-5 p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Full Name</label>
            <input type="text" value={form.full_name} onChange={update('full_name')} className="input" placeholder="John Doe" required />
          </div>
          <div>
            <label className="label">Email</label>
            <input type="email" value={form.email} onChange={update('email')} className="input" placeholder="email@example.com" required />
          </div>
          <div>
            <label className="label">Phone (optional)</label>
            <input type="tel" value={form.phone} onChange={update('phone')} className="input" placeholder="+62 812 3456 7890" />
          </div>
          <div>
            <label className="label">Password</label>
            <div className="relative">
              <input type={showPw ? 'text' : 'password'} value={form.password} onChange={update('password')}
                className="input pr-10" placeholder="Min. 8 characters" required minLength={8} />
              <button type="button" onClick={() => setShowPw(!showPw)}
                className="absolute right-3 top-3 text-neutral-400 hover:text-neutral-700">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
            </div>
          </div>
          <div>
            <label className="label">Confirm Password</label>
            <input type="password" value={form.confirm} onChange={update('confirm')}
              className={`input ${form.confirm && form.password !== form.confirm ? 'input-error' : ''}`}
              placeholder="••••••••" required />
            {form.confirm && form.password !== form.confirm && (
              <p className="text-xs text-red-500 mt-1">Passwords do not match</p>
            )}
          </div>

          <button type="submit" disabled={loading} className="btn-primary w-full py-3.5 text-base mt-2">
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-neutral-600">
          Already have an account?{' '}
          <Link to="/auth/login" className="text-brand-red hover:text-brand-red-dark font-medium">Sign In</Link>
        </p>
      </div>
    </div>
  )
}
