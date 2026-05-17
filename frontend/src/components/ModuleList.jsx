const DOT = {
  service: 'bg-bob-primary',
  utility: 'bg-bob-accent',
  config: 'bg-bob-warning',
}

export default function ModuleList({ modules, selectedId, onSelect }) {
  return (
    <nav aria-label="Modules" className="flex flex-col gap-2">
      {modules.map((m) => {
        const active = m.id === selectedId
        return (
          <button
            key={m.id}
            type="button"
            onClick={() => onSelect(m.id)}
            className={`flex flex-col gap-2 rounded-input px-3 py-3 text-left transition-all duration-200 ${active
                ? 'bg-bob-bg text-bob-text ring-2 ring-bob-primary shadow-lg'
                : 'text-bob-text/85 hover:bg-bob-bg/80 hover:shadow-md'
              }`}
          >
            <div className="flex items-center gap-2">
              <span
                className={`h-2 w-2 shrink-0 rounded-full ${DOT[m.kind ?? 'service'] ?? 'bg-bob-muted'}`}
                aria-hidden
              />
              <span className="truncate font-semibold text-sm">{m.name}</span>
            </div>
            {m.description && (
              <p className="text-xs text-bob-muted line-clamp-2 leading-relaxed">
                {m.description}
              </p>
            )}
            {m.key_files && m.key_files.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-1">
                {m.key_files.slice(0, 2).map((file) => (
                  <span
                    key={file}
                    className="text-[10px] bg-bob-bg px-1.5 py-0.5 rounded text-bob-muted font-mono truncate max-w-[120px]"
                    title={file}
                  >
                    {file.split('/').pop()}
                  </span>
                ))}
                {m.key_files.length > 2 && (
                  <span className="text-[10px] text-bob-muted">
                    +{m.key_files.length - 2} more
                  </span>
                )}
              </div>
            )}
          </button>
        )
      })}
    </nav>
  )
}
