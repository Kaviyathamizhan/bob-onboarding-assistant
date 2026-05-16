import { useNavigate } from 'react-router-dom'
import RepoInput from '../components/RepoInput'

export default function HomePage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-16">
      <header className="mb-10 max-w-lg text-center">
        <p className="font-mono text-xs font-semibold uppercase tracking-widest text-bob-primary">
          BobOnboard
        </p>
        <h1 className="mt-3 font-mono text-2xl font-semibold text-bob-text sm:text-3xl">
          Codebase onboarding assistant
        </h1>
        <p className="mt-3 text-sm text-bob-muted">
          Paste a public GitHub URL. We scan the repo, build a Bob prompt, and you run analysis in IBM Bob
          IDE — then paste Bob&apos;s response back for your dashboard.
        </p>
      </header>
      <RepoInput onAnalyze={(url) => navigate('/analyzing', { state: { repoUrl: url } })} />
    </div>
  )
}
