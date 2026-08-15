import { Link } from 'react-router-dom'

export default function AboutPage() {
  return (
    <div>
      <div className="bg-neutral-100 py-20">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h1 className="text-4xl font-bold text-neutral-900 mb-4">
            About Phoenix 
          </h1>
          <p className="text-lg text-neutral-600 leading-relaxed">
            We are a trusted online store bringing high-quality products directly to you.
          </p>
        </div>
      </div>
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <Link to="/products" className="btn-primary">View Products</Link>
      </div>
    </div>
  )
}
