import MarkdownRenderer from './MarkdownRenderer'

export default function ArchOverview({ architecture_summary }) {
  return (
    <div className="rounded-card border border-bob-muted/20 bg-bob-bg p-6">
      <h2 className="font-mono text-sm font-semibold uppercase tracking-wide text-bob-muted mb-4">
        Architecture overview
      </h2>
      <div className="mt-4">
        <MarkdownRenderer
          content={architecture_summary || 'No architecture summary available.'}
        />
      </div>
    </div>
  )
}
