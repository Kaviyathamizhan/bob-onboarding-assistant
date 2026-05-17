import MarkdownRenderer from './MarkdownRenderer'

export default function ModuleDetail({ module }) {
  if (!module) {
    return (
      <div className="rounded-card border border-dashed border-bob-muted/35 bg-bob-bg/50 p-8 text-center text-sm text-bob-muted">
        Select a module in the sidebar to see description, key files, imports, and exports.
      </div>
    )
  }

  const key_files = module.key_files ?? []
  const imports = module.imports ?? []
  const exports = module.exports ?? []

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-mono text-lg font-semibold text-bob-text">{module.name}</h2>
        <div className="mt-2">
          <MarkdownRenderer content={module.description || 'No description available.'} />
        </div>
      </div>
      {/^module-\d+$/i.test(module.id) &&
        !key_files.length &&
        !imports.length &&
        !exports.length &&
        !module.description ? (
        <p className="rounded-card border border-bob-warning/30 bg-bob-warning/10 p-3 text-xs text-bob-warning">
          Bob&apos;s reply was not in the <span className="font-mono">MODULE_ID / KEY_FILES</span> format
          the app expects. Re-run Analyze and ask Bob to follow the prompt template exactly, then submit
          again.
        </p>
      ) : null}
      <section>
        <h3 className="font-mono text-xs font-semibold uppercase tracking-wide text-bob-muted">
          Key files
        </h3>
        <ul className="mt-2 space-y-1 text-sm text-bob-primary">
          {key_files.length === 0 ? (
            <li className="text-xs text-bob-muted">None listed in Bob&apos;s response</li>
          ) : (
            key_files.map((f) => (
              <li key={f} className="truncate font-mono text-xs">
                {f}
              </li>
            ))
          )}
        </ul>
      </section>
      <section className="grid gap-6 sm:grid-cols-2">
        <div>
          <h3 className="font-mono text-xs font-semibold uppercase tracking-wide text-bob-muted">
            Imports
          </h3>
          <ul className="mt-2 space-y-1 text-xs text-bob-muted">
            {imports.map((x) => (
              <li key={x}>{x}</li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="font-mono text-xs font-semibold uppercase tracking-wide text-bob-muted">
            Exports
          </h3>
          <ul className="mt-2 space-y-1 text-xs text-bob-muted">
            {exports.map((x) => (
              <li key={x}>{x}</li>
            ))}
          </ul>
        </div>
      </section>
    </div>
  )
}
