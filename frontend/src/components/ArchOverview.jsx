export default function ArchOverview({ architecture_summary }) {
  return (
    <div className="rounded-card border border-bob-muted/20 bg-bob-bg p-6">
      <h2 className="font-mono text-sm font-semibold uppercase tracking-wide text-bob-muted">
        Architecture overview
      </h2>
      <p className="mt-4 whitespace-pre-wrap text-sm leading-relaxed text-bob-text/90">
        {architecture_summary || 'No architecture summary available.'}
      </p>
    </div>
  )
}
