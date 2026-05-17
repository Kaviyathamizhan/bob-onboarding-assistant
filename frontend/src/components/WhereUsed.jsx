import { useState } from 'react'
import DependencyGraph from './DependencyGraph'

export default function WhereUsed({ paths, onTrigger, expanded, loading, moduleName }) {
  const [viewMode, setViewMode] = useState('list') // 'list' or 'graph'

  return (
    <div className="rounded-card border border-bob-muted/20 bg-bob-bg p-4">
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={onTrigger}
          disabled={loading}
          className="text-sm font-semibold text-bob-primary hover:underline disabled:opacity-50 transition-all"
        >
          {loading ? 'Searching…' : 'Where is this used?'}
        </button>

        {expanded && paths.length > 0 && (
          <div className="flex gap-1 rounded-input bg-bob-surface p-1">
            <button
              type="button"
              onClick={() => setViewMode('list')}
              className={`px-3 py-1 text-xs font-medium rounded transition-all ${viewMode === 'list'
                  ? 'bg-bob-primary text-white'
                  : 'text-bob-muted hover:text-bob-text'
                }`}
            >
              List
            </button>
            <button
              type="button"
              onClick={() => setViewMode('graph')}
              className={`px-3 py-1 text-xs font-medium rounded transition-all ${viewMode === 'graph'
                  ? 'bg-bob-primary text-white'
                  : 'text-bob-muted hover:text-bob-text'
                }`}
            >
              Graph
            </button>
          </div>
        )}
      </div>

      {expanded ? (
        paths.length === 0 ? (
          <p className="mt-3 text-xs text-bob-warning">No importing files found.</p>
        ) : (
          <>
            {viewMode === 'graph' ? (
              <DependencyGraph moduleName={moduleName || 'Module'} importingFiles={paths} />
            ) : (
              <ul className="mt-3 max-h-48 space-y-1 overflow-y-auto text-xs text-bob-muted">
                {paths.slice(0, 10).map((p) => (
                  <li key={p} className="truncate font-mono hover:text-bob-text transition-colors">
                    {p}
                  </li>
                ))}
                {paths.length > 10 && (
                  <li className="text-bob-warning italic">
                    +{paths.length - 10} more files...
                  </li>
                )}
              </ul>
            )}
          </>
        )
      ) : (
        <p className="mt-2 text-xs text-bob-muted">Search import references across scanned files.</p>
      )}
    </div>
  )
}
