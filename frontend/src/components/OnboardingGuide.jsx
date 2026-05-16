import { useState } from 'react'

export default function OnboardingGuide({ guide, repoName }) {
  const [copied, setCopied] = useState(false)

  async function handleCopy() {
    await navigator.clipboard.writeText(guide ?? '')
    setCopied(true)
    window.setTimeout(() => setCopied(false), 2000)
  }

  const sections = parseGuideSections(guide ?? '')

  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="font-mono text-xs text-bob-muted">Onboarding guide</p>
          <h1 className="font-mono text-xl font-semibold text-bob-text">{repoName}</h1>
        </div>
        <button
          type="button"
          onClick={handleCopy}
          className="rounded-input bg-bob-primary px-4 py-2 text-sm font-semibold text-white"
        >
          {copied ? 'Copied!' : 'Copy guide'}
        </button>
      </div>

      <div className="mt-8 space-y-8">
        {sections.length > 0 ? (
          sections.map((section) => (
            <section key={section.title} className="rounded-card border border-bob-muted/20 bg-bob-surface p-6">
              <h2 className="font-mono text-sm font-semibold text-bob-primary">{section.title}</h2>
              <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-bob-text/90">
                {section.body}
              </p>
            </section>
          ))
        ) : (
          <pre className="whitespace-pre-wrap rounded-card border border-bob-muted/20 bg-bob-surface p-6 text-sm text-bob-text/90">
            {guide}
          </pre>
        )}
      </div>
    </div>
  )
}

function parseGuideSections(text) {
  const lines = text.split('\n')
  const sections = []
  let current = null

  for (const line of lines) {
    const heading = line.match(/^#{1,3}\s+(.+)$/) || line.match(/^\d+\.\s+(.+)$/)
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
