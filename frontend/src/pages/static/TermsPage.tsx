import Breadcrumb from '../../components/common/Breadcrumb'

export default function TermsPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Breadcrumb items={[{ label: 'Home', href: '/' }, { label: 'Terms & Conditions' }]} />
      <h1 className="text-3xl font-semibold text-neutral-900 mb-8">Terms & Conditions</h1>
      <div className="prose prose-neutral max-w-none text-neutral-600 leading-relaxed space-y-5 text-sm">
        <p>By using our service, you agree to the applicable terms and conditions.</p>
        <h2 className="text-base font-semibold text-neutral-900">1. Use of Service</h2>
        <p>Our service may only be used for lawful purposes in accordance with applicable regulations.</p>
        <h2 className="text-base font-semibold text-neutral-900">2. User Accounts</h2>
        <p>You are responsible for maintaining the confidentiality of your account and password.</p>
        <h2 className="text-base font-semibold text-neutral-900">3. Return Policy</h2>
        <p>Product returns can be made within 30 days of receipt, provided the product is in its original condition.</p>
      </div>
    </div>
  )
}
