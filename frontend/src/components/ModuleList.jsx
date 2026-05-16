const DOT = {
  service: 'bg-bob-primary',
  utility: 'bg-bob-accent',
  config: 'bg-bob-warning',
}

export default function ModuleList({ modules, selectedId, onSelect }) {
  return (
    <nav aria-label="Modules" className="flex flex-col gap-1">
      {modules.map((m) => {
        const active = m.id === selectedId
        return (
          <button
            key={m.id}
            type="button"
            onClick={() => onSelect(m.id)}
            className={`flex w-full items-center gap-2 rounded-input px-3 py-2 text-left text-sm transition ${
              active
                ? 'bg-bob-bg text-bob-text ring-1 ring-bob-primary'
                : 'text-bob-text/85 hover:bg-bob-bg/80'
            }`}
          >
            <span className={`h-2 w-2 shrink-0 rounded-full ${DOT[m.kind] ?? 'bg-bob-muted'}`} aria-hidden />
            <span className="truncate font-medium">{m.name}</span>
          </button>
        )
      })}
    </nav>
  )
}
