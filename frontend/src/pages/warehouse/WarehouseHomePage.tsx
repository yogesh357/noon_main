import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { warehouseService } from '../../services/api.service'

export default function WarehouseHomePage() {
  const [data, setData] = useState<{
    pending_picking?: number; pending_packing?: number; pending_handover?: number
  }>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    warehouseService.getHome().then(({ data }) => setData(data)).finally(() => setLoading(false))
  }, [])

  const cards = [
    { label: 'Pending Picking', value: data.pending_picking ?? 0, to: '/warehouse/picking', icon: '📋', color: 'bg-blue-500' },
    { label: 'Pending Packing', value: data.pending_packing ?? 0, to: '/warehouse/packing', icon: '📦', color: 'bg-orange-500' },
    { label: 'Pending Handover', value: data.pending_handover ?? 0, to: '/warehouse/handover', icon: '🚚', color: 'bg-green-500' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-white">Warehouse Dashboard</h1>
        <p className="text-neutral-400 text-sm mt-0.5">{new Date().toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'long' })}</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {cards.map((card) => (
          <Link key={card.to} to={card.to}
            className="bg-neutral-800 rounded-xl p-5 hover:bg-neutral-700 transition-colors">
            <div className={`w-10 h-10 ${card.color} rounded-xl flex items-center justify-center text-xl mb-3`}>
              {card.icon}
            </div>
            {loading ? (
              <div className="skeleton h-8 w-12 rounded mb-1 bg-neutral-700" />
            ) : (
              <p className="text-3xl font-bold text-white">{card.value}</p>
            )}
            <p className="text-neutral-400 text-sm mt-0.5">{card.label}</p>
          </Link>
        ))}
      </div>

      <div className="bg-neutral-800 rounded-xl p-5">
        <h2 className="text-sm font-semibold text-neutral-300 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 gap-3">
          <Link to="/warehouse/picking" className="bg-neutral-700 hover:bg-neutral-600 rounded-lg p-4 text-center transition-colors">
            <p className="text-2xl mb-1">📋</p>
            <p className="text-sm font-medium text-white">Start Picking</p>
          </Link>
          <Link to="/warehouse/packing" className="bg-neutral-700 hover:bg-neutral-600 rounded-lg p-4 text-center transition-colors">
            <p className="text-2xl mb-1">📦</p>
            <p className="text-sm font-medium text-white">Start Packing</p>
          </Link>
        </div>
      </div>
    </div>
  )
}
