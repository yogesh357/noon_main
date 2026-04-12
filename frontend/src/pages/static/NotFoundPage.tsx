import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center text-center px-4 py-20">
      <p className="text-8xl font-bold text-neutral-200 mb-4">404</p>
      <h1 className="text-2xl font-semibold text-neutral-900 mb-2">Page Not Found</h1>
      <p className="text-neutral-500 mb-8">The page you're looking for doesn't exist.</p>
      <Link to="/" className="btn-primary">Go Home</Link>
    </div>
  )
}
