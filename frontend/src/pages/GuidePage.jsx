import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import OnboardingGuide from '../components/OnboardingGuide'
import { getGuide } from '../api/repo'

export default function GuidePage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [guide, setGuide] = useState(location.state?.guide ?? '')
  const repoName = location.state?.repo_name ?? 'Repository'

  useEffect(() => {
    if (guide) return
    getGuide()
      .then((data) => setGuide(data.guide ?? ''))
      .catch(() => navigate('/dashboard', { replace: true }))
  }, [guide, navigate])

  return (
    <div className="min-h-screen bg-bob-bg">
      <div className="border-b border-bob-surface bg-bob-surface px-6 py-4">
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="text-sm font-medium text-bob-primary hover:underline"
        >
          ← Back to dashboard
        </button>
      </div>
      <OnboardingGuide guide={guide} repoName={repoName} />
    </div>
  )
}
