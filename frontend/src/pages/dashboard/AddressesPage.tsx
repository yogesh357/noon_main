import { useEffect, useState } from 'react'
import { dashboardService } from '../../services/api.service'
import { showToast } from '../../features/ui/uiSlice'
import { useAppDispatch } from '../../app/hooks'
import type { Address, AddressPayload } from '../../types'

const EMPTY: AddressPayload = { name: '', phone: '', street: '', city: '', province: '', postal_code: '', country: 'Indonesia' }

export default function DashboardAddressesPage() {
  const dispatch = useAppDispatch()
  const [addresses, setAddresses] = useState<Address[]>([])
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState<Address | null>(null)
  const [creating, setCreating] = useState(false)
  const [form, setForm] = useState<AddressPayload>(EMPTY)
  const [saving, setSaving] = useState(false)

  const load = () => dashboardService.getAddresses().then(({ data }) => setAddresses(data)).finally(() => setLoading(false))
  useEffect(() => { load() }, [])

  const openEdit = (addr: Address) => { setEditing(addr); setForm({ name: addr.name, phone: addr.phone, street: addr.street, city: addr.city, province: addr.province, postal_code: addr.postal_code, country: addr.country }); setCreating(false) }
  const openCreate = () => { setEditing(null); setForm(EMPTY); setCreating(true) }
  const closeForm = () => { setEditing(null); setCreating(false) }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    try {
      if (editing) await dashboardService.updateAddress(editing.id, form)
      else await dashboardService.createAddress(form)
      dispatch(showToast({ message: editing ? 'Address updated' : 'Address added', type: 'success' }))
      closeForm()
      load()
    } catch {
      dispatch(showToast({ message: 'Failed to save address', type: 'error' }))
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this address?')) return
    await dashboardService.deleteAddress(id)
    dispatch(showToast({ message: 'Address deleted', type: 'success' }))
    load()
  }

  const handleSetDefault = async (id: number) => {
    await dashboardService.setDefaultAddress(id)
    dispatch(showToast({ message: 'Default address updated', type: 'success' }))
    load()
  }

  const upd = (field: keyof AddressPayload) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((p) => ({ ...p, [field]: e.target.value }))

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-neutral-900">My Addresses</h1>
        <button onClick={openCreate} className="btn-primary text-sm py-2 px-4">+ Add Address</button>
      </div>

      {loading ? (
        <div className="space-y-3">{[...Array(2)].map((_, i) => <div key={i} className="skeleton h-24 rounded-xl" />)}</div>
      ) : addresses.length === 0 && !creating ? (
        <div className="card text-center py-10">
          <p className="text-neutral-400 mb-4">No addresses yet</p>
          <button onClick={openCreate} className="btn-primary text-sm">Add Your First Address</button>
        </div>
      ) : (
        <div className="space-y-3">
          {addresses.map((addr) => (
            <div key={addr.id} className={`card ${addr.is_default ? 'border-brand-red/30 bg-brand-red/5' : ''}`}>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-0.5">
                    <p className="font-medium text-neutral-900 text-sm">{addr.name}</p>
                    {addr.is_default && <span className="badge bg-brand-red/10 text-brand-red text-[10px]">Default</span>}
                  </div>
                  <p className="text-sm text-neutral-500">{addr.phone}</p>
                  <p className="text-sm text-neutral-500">{addr.street}, {addr.city}, {addr.province} {addr.postal_code}</p>
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  {!addr.is_default && (
                    <button onClick={() => handleSetDefault(addr.id)} className="text-xs text-neutral-500 hover:text-neutral-900">Set Default</button>
                  )}
                  <button onClick={() => openEdit(addr)} className="text-xs text-brand-red hover:text-brand-red-dark">Edit</button>
                  <button onClick={() => handleDelete(addr.id)} className="text-xs text-red-400 hover:text-red-600">Delete</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Form */}
      {(creating || editing) && (
        <div className="card">
          <h2 className="font-semibold text-neutral-900 mb-4">{editing ? 'Edit Address' : 'New Address'}</h2>
          <form onSubmit={handleSave} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {[
              { field: 'name', label: 'Name', ph: 'John Doe' },
              { field: 'phone', label: 'Phone', ph: '+62 812 3456 7890' },
              { field: 'street', label: 'Street', ph: 'Jl. Sudirman No. 1' },
              { field: 'city', label: 'City', ph: 'Jakarta' },
              { field: 'province', label: 'Province', ph: 'DKI Jakarta' },
              { field: 'postal_code', label: 'Postal Code', ph: '10110' },
            ].map((f) => (
              <div key={f.field} className={f.field === 'street' ? 'sm:col-span-2' : ''}>
                <label className="label">{f.label}</label>
                <input type="text" value={form[f.field as keyof AddressPayload] as string}
                  onChange={upd(f.field as keyof AddressPayload)} className="input" placeholder={f.ph} required />
              </div>
            ))}
            <div className="sm:col-span-2 flex gap-3 mt-2">
              <button type="submit" disabled={saving} className="btn-primary">{saving ? 'Saving...' : 'Save'}</button>
              <button type="button" onClick={closeForm} className="btn-secondary">Cancel</button>
            </div>
          </form>
        </div>
      )}
    </div>
  )
}
