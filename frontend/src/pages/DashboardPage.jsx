import { useEffect, useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import ArchOverview from '../components/ArchOverview'
import ModuleDetail from '../components/ModuleDetail'
import ModuleList from '../components/ModuleList'
import WhereUsed from '../components/WhereUsed'
import { getResult, getWhereUsed } from '../api/repo'

export default function DashboardPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [analysis, setAnalysis] = useState(location.state?.analysis ?? null)
  const [loading, setLoading] = useState(!location.state?.analysis)
  const [selectedId, setSelectedId] = useState(null)
  const [whereUsedOpen, setWhereUsedOpen] = useState(false)
  const [whereUsedFiles, setWhereUsedFiles] = useState([])
  const [whereUsedLoading, setWhereUsedLoading] = useState(false)

  useEffect(() => {
    if (analysis) return
    getResult()
      .then((data) => setAnalysis(data))
      .catch(() => navigate('/', { replace: true }))
      .finally(() => setLoading(false))
  }, [analysis, navigate])

  useEffect(() => {
    if (analysis?.modules?.length && !selectedId) {
      setSelectedId(analysis.modules[0].id)
    }
  }, [analysis, selectedId])

  const selected = useMemo(
    () => analysis?.modules?.find((m) => m.id === selectedId) ?? null,
    [analysis, selectedId],
  )

  async function handleWhereUsed() {
    if (!selectedId) return
    if (whereUsedOpen) {
      setWhereUsedOpen(false)
      return
    }
    setWhereUsedLoading(true)
    try {
      const data = await getWhereUsed(selectedId)
      setWhereUsedFiles(data.files ?? [])
      setWhereUsedOpen(true)
    } catch {
      setWhereUsedFiles([])
      setWhereUsedOpen(true)
    } finally {
      setWhereUsedLoading(false)
    }
  }

  if (loading || !analysis) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-bob-bg">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-bob-muted/30 border-t-bob-primary" />
      </div>
    )
  }

  const { repo_url, repo_name, tech_stack, architecture_summary, modules, file_count, onboarding_guide } =
    analysis

  return (
    <div className="flex min-h-screen flex-col bg-bob-bg">
      <header className="flex flex-wrap items-center justify-between gap-4 border-b border-bob-surface bg-bob-surface px-6 py-4">
        <div className="min-w-0">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="text-xs font-medium text-bob-primary hover:underline"
          >
            ← New analysis
          </button>
          <h1 className="mt-1 truncate font-mono text-lg font-semibold text-bob-text" title={repo_url}>
            {repo_name}
          </h1>
          <p className="truncate font-mono text-xs text-bob-muted" title={repo_url}>
            {repo_url}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {tech_stack.map((tech) => (
            <span
              key={tech}
              className="rounded-full border border-bob-primary/40 bg-bob-bg px-2.5 py-0.5 font-mono text-xs text-bob-text"
            >
              {tech}
            </span>
          ))}
          <button
            type="button"
            onClick={() => navigate('/guide', { state: { guide: onboarding_guide, repo_name } })}
            className="rounded-input bg-bob-primary px-4 py-2 text-xs font-semibold text-white hover:brightness-110"
          >
            View onboarding guide
          </button>
        </div>
      </header>

      {file_count >= 100 ? (
        <p className="border-b border-bob-warning/40 bg-bob-warning/10 px-6 py-2 text-center text-xs text-bob-warning">
          Analyzing first 100 files of this repo.
        </p>
      ) : null}

      <div className="flex min-h-0 flex-1">
        <aside className="w-[280px] shrink-0 border-r border-bob-surface bg-bob-surface p-4">
          <p className="font-mono text-xs font-semibold uppercase tracking-wide text-bob-muted">
            Modules
          </p>
          <div className="mt-4">
            <ModuleList
              modules={modules}
              selectedId={selectedId}
              onSelect={(id) => {
                setSelectedId(id)
                setWhereUsedOpen(false)
                setWhereUsedFiles([])
              }}
            />
          </div>
        </aside>

        <main className="min-w-0 flex-1 overflow-y-auto p-6">
          <div className="mx-auto max-w-4xl space-y-6">
            <ArchOverview architecture_summary={architecture_summary} />
            {selected ? <ModuleDetail module={selected} /> : null}
            <WhereUsed
              paths={whereUsedFiles}
              expanded={whereUsedOpen}
              loading={whereUsedLoading}
              onTrigger={handleWhereUsed}
            />
          </div>
        </main>
      </div>
    </div>
  )
}
