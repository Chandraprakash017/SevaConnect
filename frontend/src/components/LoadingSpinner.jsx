/**
 * LoadingSpinner — full-page or inline 3D loading indicator.
 */

export default function LoadingSpinner({ text = 'Loading...', fullPage = true }) {
  if (fullPage) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 animate-fade-in">
        <div className="spinner-3d" />
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{text}</p>
      </div>
    )
  }

  return (
    <div className="flex items-center justify-center gap-3 py-8">
      <div className="spinner-3d" style={{ width: 30, height: 30 }} />
      <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{text}</p>
    </div>
  )
}
