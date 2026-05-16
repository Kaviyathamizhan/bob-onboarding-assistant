import { useEffect, useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

const STEPS = [
  { key: 'clone', label: 'Cloning repo…' },
  { key: 'scan', label: 'Scanning files…' },
  { key: 'bob', label: 'Analyzing with Bob…' },
  { key: 'guide', label: 'Generating onboarding guide…' },
]

export default function AnalyzingPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const repoUrl = location.state?.repoUrl

  const fileCount = useMemo(() => 12 + Math.floor(Math.random() * 75), [])

  const [stepIndex, setStepIndex] = useState(0)

  useEffect(() => {
    if (!repoUrl) {
      navigate('/', { replace: true })
    }
  }, [repoUrl, navigate])

  useEffect(() => {
    if (!repoUrl) return undefined
    if (stepIndex >= STEPS.length - 1) {
      const t = window.setTimeout(() => {
        navigate('/dashboard', { replace: true, state: { repoUrl } })
      }, 900)
      return () => window.clearTimeout(t)
    }
    const t = window.setTimeout(() => setStepIndex((i) => i + 1), 1100)
    return () => window.clearTimeout(t)
  }, [repoUrl, stepIndex, navigate])

  if (!repoUrl) return null

  const repoLabel = repoUrl.replace(/^https?:\/\/github\.com\//i, '')

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4">
      <div className="w-full max-w-md rounded-card border border-bob-surface bg-bob-surface p-8">
        <p className="font-mono text-xs text-bob-muted">Analyzing</p>
        <h1 className="mt-1 font-mono text-lg font-semibold text-bob-text">{repoLabel}</h1>
        <p className="mt-2 truncate text-xs text-bob-primary" title={repoUrl}>
          {repoUrl}
        </p>

        <div
          className="mt-8 flex justify-center"
          role="status"
          aria-live="polite"
          aria-label="Analysis progress"
        >
          <div className="h-10 w-10 animate-spin rounded-full border-2 border-bob-muted/30 border-t-bob-primary" />
        </div>

        <ol className="mt-8 space-y-3">
          {STEPS.map((step, i) => {
            const done = i < stepIndex
            const active = i === stepIndex
            const label =
              step.key === 'scan' && active
                ? `Scanning ${fileCount} files…`
                : step.key === 'scan' && done
                  ? `Scanned ${fileCount} files`
                  : step.label
            return (
              <li
                key={step.key}
                className={`flex items-center gap-3 text-sm ${
                  done ? 'text-bob-accent' : active ? 'text-bob-text' : 'text-bob-muted'
                }`}
              >
                <span
                  className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full border text-xs font-mono ${
                    done
                      ? 'border-bob-accent bg-bob-accent/15 text-bob-accent'
                      : active
                        ? 'border-bob-primary text-bob-primary'
                        : 'border-bob-muted/40 text-bob-muted'
                  }`}
                  aria-hidden
                >
                  {done ? '✓' : i + 1}
                </span>
                <span>{label}</span>
              </li>
            )
          })}
        </ol>

        <p className="mt-8 text-center text-xs leading-relaxed text-bob-muted">
          No live Bob API call — this screen simulates progress for UI work. Your teammate can swap the
          timer for real job status later.
        </p>
      </div>
    </div>
  )
}
