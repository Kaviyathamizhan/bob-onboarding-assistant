import MarkdownRenderer from './MarkdownRenderer'
import OnboardingTimeline from './OnboardingTimeline'
import { useState } from 'react'

export default function OnboardingGuide({ guide, repoName }) {
  const [copied, setCopied] = useState(false)

  async function handleCopy() {
    await navigator.clipboard.writeText(guide ?? '')
    setCopied(true)
    window.setTimeout(() => setCopied(false), 2000)
  }

  function handleDownload() {
    const blob = new Blob([guide ?? ''], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${repoName.replace(/[^a-z0-9]/gi, '-').toLowerCase()}-onboarding-guide.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const sections = parseGuideSections(guide ?? '')
  const timelineSteps = parseTimelineSteps(guide ?? '')

  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="font-mono text-xs text-bob-muted">Onboarding guide</p>
          <h1 className="font-mono text-xl font-semibold text-bob-text">{repoName}</h1>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleCopy}
            className="rounded-input bg-bob-primary px-4 py-2 text-sm font-semibold text-white hover:brightness-110 transition-all"
          >
            {copied ? 'Copied!' : 'Copy guide'}
          </button>
          <button
            type="button"
            onClick={handleDownload}
            className="rounded-input bg-bob-accent px-4 py-2 text-sm font-semibold text-white hover:brightness-110 transition-all"
          >
            Download .md
          </button>
        </div>
      </div>

      <div className="mt-8 space-y-8">
        {timelineSteps.length > 0 && (
          <section className="rounded-card border border-bob-muted/20 bg-bob-surface p-6">
            <div className="flex items-center gap-2 mb-6">
              <h2 className="font-mono text-sm font-semibold text-bob-primary">Start Here</h2>
              <span className="text-xs text-bob-muted">⏱ Estimated Time: 2-3 hours</span>
            </div>
            <OnboardingTimeline steps={timelineSteps} />
          </section>
        )}

        {sections.length > 0 ? (
          sections.map((section) => (
            <section key={section.title} className="rounded-card border border-bob-muted/20 bg-bob-surface p-6">
              <h2 className="font-mono text-sm font-semibold text-bob-primary">{section.title}</h2>
              <div className="mt-3">
                <MarkdownRenderer content={section.body} />
              </div>
            </section>
          ))
        ) : !timelineSteps.length ? (
          <pre className="whitespace-pre-wrap rounded-card border border-bob-muted/20 bg-bob-surface p-6 text-sm text-bob-text/90">
            {guide}
          </pre>
        ) : null}
      </div>
    </div>
  )
}

function parseGuideSections(text) {
  const lines = text.split('\n')
  const sections = []
  let current = null

  for (const line of lines) {
    const heading = line.match(/^#{1,3}\s+(.+)$/)
    if (heading) {
      if (current) sections.push(current)
      current = { title: heading[1].trim(), body: '' }
    } else if (current) {
      current.body += (current.body ? '\n' : '') + line
    }
  }
  if (current) sections.push(current)
  return sections
}

function parseTimelineSteps(text) {
  const lines = text.split('\n')
  const steps = []
  let currentStep = null

  for (const line of lines) {
    const match = line.match(/^(\d+)\.\s+(.+)$/)
    if (match) {
      if (currentStep) {
        steps.push(currentStep)
      }
      currentStep = {
        title: match[2].trim(),
        description: ''
      }
    } else if (currentStep && line.trim()) {
      currentStep.description += (currentStep.description ? '\n' : '') + line.trim()
    }
  }
  if (currentStep) {
    steps.push(currentStep)
  }
  return steps
}
