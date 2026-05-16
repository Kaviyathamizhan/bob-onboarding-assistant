export default function WhereUsed({ paths, onTrigger, expanded, loading }) {
  return (
    <div className="rounded-card border border-bob-muted/20 bg-bob-bg p-4">
      <button
        type="button"
        onClick={onTrigger}
        disabled={loading}
        className="text-sm font-semibold text-bob-primary hover:underline disabled:opacity-50"
      >
        {loading ? 'Searching…' : 'Where is this used?'}
      </button>
      {expanded ? (
        <ul className="mt-3 max-h-48 space-y-1 overflow-y-auto text-xs text-bob-muted">
          {paths.length === 0 ? (
            <li className="text-bob-warning">No importing files found.</li>
          ) : (
            paths.slice(0, 10).map((p) => (
              <li key={p} className="truncate font-mono">
                {p}
              </li>
            ))
          )}
        </ul>
      ) : (
        <p className="mt-2 text-xs text-bob-muted">Search import references across scanned files.</p>
      )}
    </div>
  )
}
