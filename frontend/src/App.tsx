import { useEffect } from 'react'
import { RouterProvider } from 'react-router-dom'
import { router } from './routes'
import { useAppDispatch, useAppSelector } from './app/hooks'
import { fetchMe } from './features/auth/authSlice'

function AppInner() {
  const dispatch = useAppDispatch()
  const { token, user } = useAppSelector((s) => s.auth)

  // Re-hydrate user from token on every fresh page load (e.g. after Xendit redirect)
  useEffect(() => {
    if (token && !user) {
      dispatch(fetchMe())
    }
  }, [])

  return <RouterProvider router={router} />
}

export default function App() {
  return <AppInner />
}
