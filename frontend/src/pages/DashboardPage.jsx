import { useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import ArchOverview from '../components/ArchOverview'
import ModuleDetail from '../components/ModuleDetail'
import ModuleList from '../components/ModuleList'
import WhereUsed from '../components/WhereUsed'

const PLACEHOLDER_MODULES = [
  {
    id: 'web-layer',
    name: 'Web layer',
    kind: 'service',
    description:
      'Placeholder module — replace with Bob’s module breakdown once analysis JSON is wired from the backend.',
    keyFiles: ['src/routes/index.ts', 'src/middleware/auth.ts'],
    imports: ['service:api', 'pkg:express'],
    exports: ['createServer', 'registerRoutes'],
  },
  {
    id: 'data-layer',
    name: 'Data layer',
    kind: 'utility',
    description: 'Skeleton entry for persistence and models discovered in the repository.',
    keyFiles: ['db/client.py', 'models/user.py'],
    imports: ['pkg:sqlalchemy'],
    exports: ['Session', 'User'],
  },
  {
    id: 'config',
    name: 'Configuration',
    kind: 'config',
    description: 'Environment, build, and deployment configuration surfaces.',
    keyFiles: ['pyproject.toml', 'docker-compose.yml'],
    imports: [],
    exports: [],
  },
]

const PLACEHOLDER_WHERE_USED = {
  'web-layer': ['src/cli/main.ts', 'tests/test_server.js'],
  'data-layer': ['src/services/users.py'],
  config: [],
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const repoUrl = location.state?.repoUrl ?? 'https://github.com/example/demo-repo'

  const [selectedId, setSelectedId] = useState(PLACEHOLDER_MODULES[0].id)
  const [whereUsedOpen, setWhereUsedOpen] = useState(false)

  const selected = useMemo(
    () => PLACEHOLDER_MODULES.find((m) => m.id === selectedId) ?? null,
    [selectedId],
  )

  const repoName = repoUrl.replace(/^https?:\/\/github\.com\//i, '').split('/')[1] ?? 'repository'

  return (
    <div className="min-h-screen flex flex-col bg-bob-bg">
      <header className="flex flex-wrap items-center justify-between gap-4 border-b border-bob-surface bg-bob-surface px-6 py-4">
        <div className="min-w-0">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="text-xs font-medium text-bob-primary hover:underline"
          >
            ← New analysis
          </button>
          <h1 className="mt-1 truncate font-mono text-lg font-semibold text-bob-text" title={repoUrl}>
            {repoName}
          </h1>
          <p className="truncate font-mono text-xs text-bob-muted" title={repoUrl}>
            {repoUrl}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {['Python', 'FastAPI', 'Docker'].map((tech) => (
            <span
              key={tech}
              className="rounded-full border border-bob-primary/40 bg-bob-bg px-2.5 py-0.5 font-mono text-xs text-bob-text"
            >
              {tech}
            </span>
          ))}
          <button
            type="button"
            disabled
            title="Available when onboarding guide is wired to the API"
            className="rounded-input border border-bob-muted/40 bg-bob-bg px-4 py-2 text-xs font-semibold text-bob-muted"
          >
            View onboarding guide
          </button>
        </div>
      </header>

      <p className="border-b border-bob-warning/40 bg-bob-warning/10 px-6 py-2 text-center text-xs text-bob-warning">
        Analyzing first 100 files of this repo. (Notice placeholder — matches PRD edge-state pattern.)
      </p>

      <div className="flex min-h-0 flex-1">
        <aside className="w-[280px] shrink-0 border-r border-bob-surface bg-bob-surface p-4">
          <p className="font-mono text-xs font-semibold uppercase tracking-wide text-bob-muted">
            Modules
          </p>
          <div className="mt-4">
            <ModuleList
              modules={PLACEHOLDER_MODULES}
              selectedId={selectedId}
              onSelect={(id) => {
                setSelectedId(id)
                setWhereUsedOpen(false)
              }}
            />
          </div>
        </aside>

        <main className="min-w-0 flex-1 overflow-y-auto p-6">
          <div className="mx-auto max-w-4xl space-y-6">
            <ArchOverview />
            {selected ? <ModuleDetail module={selected} /> : null}
            <WhereUsed
              paths={PLACEHOLDER_WHERE_USED[selectedId] ?? []}
              expanded={whereUsedOpen}
              onTrigger={() => setWhereUsedOpen((v) => !v)}
            />
          </div>
        </main>
      </div>
    </div>
  )
}
