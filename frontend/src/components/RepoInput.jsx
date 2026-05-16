import { useState } from 'react'

const EXAMPLE_REPOS = [
  'https://github.com/pallets/flask',
  'https://github.com/vitejs/vite',
  'https://github.com/fastapi/fastapi',
]

function isPublicGithubRepoUrl(value) {
  try {
    const u = new URL(value.trim())
    if (u.protocol !== 'https:' && u.protocol !== 'http:') return false
    const host = u.hostname.replace(/^www\./, '')
    if (host !== 'github.com') return false
    const parts = u.pathname.split('/').filter(Boolean)
    return parts.length >= 2
  } catch {
    return false
  }
}

export default function RepoInput({ onAnalyze }) {
  const [url, setUrl] = useState('')
  const [error, setError] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    const trimmed = url.trim()
    if (!trimmed) {
      setError('Please enter a valid GitHub URL')
      return
    }
    if (!isPublicGithubRepoUrl(trimmed)) {
      setError('Please enter a valid public GitHub repository URL')
      return
    }
    setError('')
    onAnalyze(trimmed.startsWith('http') ? trimmed : `https://${trimmed}`)
  }

  function tryExample(href) {
    setUrl(href)
    setError('')
  }

  return (
    <div className="w-full max-w-xl rounded-card border border-bob-surface bg-bob-surface p-6 shadow-lg">
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <label htmlFor="repo-url" className="block text-sm font-medium text-bob-muted">
          GitHub repository URL
        </label>
        <input
          id="repo-url"
          name="repo-url"
          type="text"
          autoComplete="off"
          placeholder="https://github.com/org/repo"
          value={url}
          onChange={(e) => {
            setUrl(e.target.value)
            if (error) setError('')
          }}
          className="w-full rounded-input border border-bob-muted/40 bg-bob-bg px-3 py-2.5 text-sm text-bob-text outline-none ring-0 placeholder:text-bob-muted/60 focus:border-bob-primary focus:ring-1 focus:ring-bob-primary"
        />
        {error ? (
          <p className="text-sm text-bob-warning" role="alert">
            {error}
          </p>
        ) : null}
        <button
          type="submit"
          className="w-full rounded-input bg-bob-primary py-2.5 text-sm font-semibold text-white transition hover:brightness-110 active:brightness-95"
        >
          Analyze with Bob
        </button>
      </form>
      <p className="mt-6 text-center text-xs text-bob-muted">or try an example repo</p>
      <ul className="mt-3 flex flex-col gap-2">
        {EXAMPLE_REPOS.map((href) => (
          <li key={href}>
            <button
              type="button"
              onClick={() => tryExample(href)}
              className="w-full rounded-input border border-bob-muted/25 bg-bob-bg px-3 py-2 text-left text-xs text-bob-primary transition hover:border-bob-primary/50"
            >
              {href.replace('https://github.com/', '')}
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
