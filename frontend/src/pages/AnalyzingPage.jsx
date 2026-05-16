import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { analyzeRepo, submitBobResponse } from '../api/repo'

const STEPS = [
  { key: 'clone', label: 'Cloning repo…' },
  { key: 'scan', label: 'Scanning files…' },
  { key: 'prompt', label: 'Building Bob prompt…' },
]

function apiErrorMessage(err) {
  const detail = err.response?.data?.detail
  if (Array.isArray(detail)) return detail.map((m) => m.msg ?? m).join(', ')
  if (detail) return String(detail)
  return err.message || 'Request failed'
}

export default function AnalyzingPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const repoUrl = location.state?.repoUrl

  const [phase, setPhase] = useState('loading')
  const [stepIndex, setStepIndex] = useState(0)
  const [error, setError] = useState('')
  const [promptData, setPromptData] = useState(null)
  const [bobResponse, setBobResponse] = useState('')
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (!repoUrl) navigate('/', { replace: true })
  }, [repoUrl, navigate])

  useEffect(() => {
    if (!repoUrl || phase !== 'loading') return undefined

    let cancelled = false
    const timers = STEPS.map((_, i) =>
      window.setTimeout(() => {
        if (!cancelled) setStepIndex(i)
      }, i * 400),
    )

    analyzeRepo(repoUrl)
      .then((data) => {
        if (cancelled) return
        setStepIndex(STEPS.length)
        setPromptData(data)
        setPhase('prompt')
      })
      .catch((err) => {
        if (cancelled) return
        setError(apiErrorMessage(err))
        setPhase('error')
      })

    return () => {
      cancelled = true
      timers.forEach(clearTimeout)
    }
  }, [repoUrl, phase])

  async function handleCopyPrompt() {
    if (!promptData?.prompt) return
    await navigator.clipboard.writeText(promptData.prompt)
    setCopied(true)
    window.setTimeout(() => setCopied(false), 2000)
  }

  async function handleSubmitBob() {
    if (!bobResponse.trim()) {
      setError('Paste Bob’s response from the IDE before continuing.')
      return
    }
    setError('')
    setPhase('submitting')
    try {
      const analysis = await submitBobResponse(repoUrl, bobResponse)
      navigate('/dashboard', { replace: true, state: { analysis } })
    } catch (err) {
      setError(apiErrorMessage(err))
      setPhase('prompt')
    }
  }

  if (!repoUrl) return null

  const repoLabel = repoUrl.replace(/^https?:\/\/github\.com\//i, '')

  if (phase === 'loading' || phase === 'submitting') {
    return (
      <PageShell repoLabel={repoLabel} repoUrl={repoUrl}>
        <Spinner />
        <ol className="mt-8 space-y-3">
          {STEPS.map((step, i) => {
            const done = phase === 'submitting' || i < stepIndex
            const active = phase === 'loading' && i === stepIndex
            let label = step.label
            if (step.key === 'scan' && promptData?.file_count) {
              label = done
                ? `Scanned ${promptData.file_count} files`
                : `Scanning ${promptData.file_count} files…`
            }
            return <StepRow key={step.key} done={done} active={active} index={i + 1} label={label} />
          })}
          {phase === 'submitting' ? (
            <StepRow done={false} active index="…" label="Parsing Bob response…" />
          ) : null}
        </ol>
      </PageShell>
    )
  }

  if (phase === 'error' && !promptData) {
    return (
      <PageShell repoLabel={repoLabel} repoUrl={repoUrl}>
        <p className="mt-6 text-sm text-bob-warning" role="alert">
          {error}
        </p>
        <button
          type="button"
          onClick={() => navigate('/')}
          className="mt-6 w-full rounded-input bg-bob-primary py-2.5 text-sm font-semibold text-white"
        >
          Back to home
        </button>
      </PageShell>
    )
  }

  return (
    <PageShell repoLabel={repoLabel} repoUrl={repoUrl} wide>
      <p className="font-mono text-xs text-bob-accent">
        Step 1 complete — {promptData?.file_count} files scanned
      </p>
      <h2 className="mt-4 font-mono text-base font-semibold text-bob-text">Copy prompt into IBM Bob IDE</h2>
      <p className="mt-2 text-sm text-bob-muted">
        Paste the prompt below into Bob in VS Code. When Bob finishes, copy its full response and paste it
        below.
      </p>

      <button
        type="button"
        onClick={handleCopyPrompt}
        className="mt-4 rounded-input bg-bob-primary px-4 py-2 text-sm font-semibold text-white hover:brightness-110"
      >
        {copied ? 'Copied!' : 'Copy prompt'}
      </button>

      <label className="mt-4 block text-xs font-medium text-bob-muted" htmlFor="bob-prompt">
        Bob prompt (read-only)
      </label>
      <textarea
        id="bob-prompt"
        readOnly
        value={promptData?.prompt ?? ''}
        className="mt-2 h-48 w-full resize-y rounded-input border border-bob-muted/40 bg-bob-bg p-3 font-mono text-xs text-bob-text"
      />

      <label className="mt-6 block text-xs font-medium text-bob-muted" htmlFor="bob-response">
        Paste Bob&apos;s response here
      </label>
      <textarea
        id="bob-response"
        value={bobResponse}
        onChange={(e) => setBobResponse(e.target.value)}
        placeholder="Paste the full structured response from IBM Bob…"
        className="mt-2 h-40 w-full resize-y rounded-input border border-bob-muted/40 bg-bob-bg p-3 text-sm text-bob-text placeholder:text-bob-muted/60 focus:border-bob-primary focus:ring-1 focus:ring-bob-primary"
      />

      {error ? (
        <p className="mt-3 text-sm text-bob-warning" role="alert">
          {error}
        </p>
      ) : null}

      <button
        type="button"
        onClick={handleSubmitBob}
        disabled={!bobResponse.trim()}
        className="mt-6 w-full rounded-input bg-bob-primary py-2.5 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
      >
        Submit Bob response → Dashboard
      </button>
    </PageShell>
  )
}

function PageShell({ repoLabel, repoUrl, wide, children }) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4 py-10">
      <div
        className={`w-full rounded-card border border-bob-surface bg-bob-surface p-8 ${
          wide ? 'max-w-3xl' : 'max-w-md'
        }`}
      >
        <p className="font-mono text-xs text-bob-muted">Analyzing</p>
        <h1 className="mt-1 font-mono text-lg font-semibold text-bob-text">{repoLabel}</h1>
        <p className="mt-2 truncate text-xs text-bob-primary" title={repoUrl}>
          {repoUrl}
        </p>
        {children}
      </div>
    </div>
  )
}

function Spinner() {
  return (
    <div className="mt-8 flex justify-center" role="status" aria-live="polite">
      <div className="h-10 w-10 animate-spin rounded-full border-2 border-bob-muted/30 border-t-bob-primary" />
    </div>
  )
}

function StepRow({ done, active, index, label }) {
  return (
    <li
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
        {done ? '✓' : index}
      </span>
      <span>{label}</span>
    </li>
  )
}
