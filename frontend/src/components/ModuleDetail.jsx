export default function ModuleDetail({ module }) {
  if (!module) {
    return (
      <div className="rounded-card border border-dashed border-bob-muted/35 bg-bob-bg/50 p-8 text-center text-sm text-bob-muted">
        Select a module in the sidebar to see description, key files, imports, and exports.
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-mono text-lg font-semibold text-bob-text">{module.name}</h2>
        <p className="mt-2 text-sm leading-relaxed text-bob-text/90">{module.description}</p>
      </div>
      <section>
        <h3 className="font-mono text-xs font-semibold uppercase tracking-wide text-bob-muted">
          Key files
        </h3>
        <ul className="mt-2 space-y-1 text-sm text-bob-primary">
          {module.keyFiles.map((f) => (
            <li key={f} className="truncate font-mono text-xs">
              {f}
            </li>
          ))}
        </ul>
      </section>
      <section className="grid gap-6 sm:grid-cols-2">
        <div>
          <h3 className="font-mono text-xs font-semibold uppercase tracking-wide text-bob-muted">
            Imports
          </h3>
          <ul className="mt-2 space-y-1 text-xs text-bob-muted">
            {module.imports.map((x) => (
              <li key={x}>{x}</li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="font-mono text-xs font-semibold uppercase tracking-wide text-bob-muted">
            Exports
          </h3>
          <ul className="mt-2 space-y-1 text-xs text-bob-muted">
            {module.exports.map((x) => (
              <li key={x}>{x}</li>
            ))}
          </ul>
        </div>
      </section>
    </div>
  )
}
