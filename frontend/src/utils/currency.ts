/**
 * Format a number as Indonesian Rupiah
 * e.g. 150000 → "Rp 150.000"
 */
export function formatIDR(amount: number): string {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

/**
 * Format compact IDR for badges
 * e.g. 1500000 → "Rp 1,5 jt"
 */
export function formatIDRCompact(amount: number): string {
  if (amount >= 1_000_000) {
    return `Rp ${(amount / 1_000_000).toFixed(1).replace('.', ',')} jt`
  }
  if (amount >= 1_000) {
    return `Rp ${(amount / 1_000).toFixed(0)}rb`
  }
  return formatIDR(amount)
}
