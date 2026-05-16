import { apiClient } from './client'

export async function analyzeRepo(repoUrl) {
  const { data } = await apiClient.post('/api/analyze', { repo_url: repoUrl })
  return data
}

export async function submitBobResponse(repoUrl, bobResponse) {
  const { data } = await apiClient.post('/api/submit-bob-response', {
    repo_url: repoUrl,
    bob_response: bobResponse,
  })
  return data
}

export async function getResult() {
  const { data } = await apiClient.get('/api/result')
  return data
}

export async function getGuide() {
  const { data } = await apiClient.get('/api/guide')
  return data
}

export async function getWhereUsed(moduleId) {
  const { data } = await apiClient.get(`/api/where-used/${moduleId}`)
  return data
}
