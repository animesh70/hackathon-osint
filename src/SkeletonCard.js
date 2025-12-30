export default function SkeletonCard() {
  return (
    <div className="animate-pulse bg-black/40 border border-purple-500/20 rounded-lg p-4 space-y-3">
      <div className="h-4 bg-gray-700 rounded w-1/3"></div>
      <div className="h-3 bg-gray-700 rounded w-full"></div>
      <div className="h-3 bg-gray-700 rounded w-5/6"></div>
    </div>
  );
}
