import { useEffect } from 'react'
import { useAppDispatch, useAppSelector } from '../../app/hooks'
import { clearToast } from '../../features/ui/uiSlice'

export default function Toast() {
  const dispatch = useAppDispatch()
  const toast = useAppSelector((s) => s.ui.toast)

  useEffect(() => {
    if (!toast) return
    const timer = setTimeout(() => dispatch(clearToast()), 3500)
    return () => clearTimeout(timer)
  }, [toast, dispatch])

  if (!toast) return null

  const colors = {
    success: 'bg-green-600',
    error: 'bg-red-600',
    info: 'bg-neutral-800',
  }

  return (
    <div className={`fixed bottom-6 right-6 z-[100] flex items-center gap-3 px-5 py-3.5 rounded-xl text-white text-sm shadow-xl ${colors[toast.type]} animate-in slide-in-from-bottom-4`}>
      {toast.type === 'success' && (
        <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      )}
      {toast.type === 'error' && (
        <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      )}
      <span>{toast.message}</span>
      <button onClick={() => dispatch(clearToast())} className="ml-2 opacity-70 hover:opacity-100">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  )
}
