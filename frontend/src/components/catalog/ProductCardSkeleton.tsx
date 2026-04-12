export default function ProductCardSkeleton() {
  return (
    <div className="bg-white rounded-xl border border-neutral-100 overflow-hidden">
      {/* Image placeholder */}
      <div className="aspect-square skeleton" />
      {/* Info */}
      <div className="p-3.5 space-y-2.5">
        <div className="skeleton h-4 w-full rounded" />
        <div className="skeleton h-4 w-2/3 rounded" />
        <div className="skeleton h-4 w-1/2 rounded" />
        <div className="flex gap-1.5 mt-1">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton w-3.5 h-3.5 rounded-full" />
          ))}
        </div>
      </div>
    </div>
  )
}
