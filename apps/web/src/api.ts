import type { CandidateReview, Capabilities, Comparison, DiscoveryAnalysis, Explanation, PolicySummary, Run, SpecSummary, Target } from './types'

let csrfToken = sessionStorage.getItem('boundarylab-csrf') || ''

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  if (init.body) headers.set('Content-Type', 'application/json')
  if (init.method && init.method !== 'GET' && csrfToken) headers.set('X-CSRF-Token', csrfToken)
  const response = await fetch(path, { ...init, headers, credentials: 'same-origin' })
  if (!response.ok) {
    const payload = await response.json().catch(() => null)
    throw new Error(payload?.error?.message || `Request failed (${response.status})`)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export const api = {
  async restoreSession() {
    const session = await request<{ csrf_token: string }>('/api/v1/session')
    csrfToken = session.csrf_token
    sessionStorage.setItem('boundarylab-csrf', csrfToken)
  },
  async login(bootstrapSecret: string) {
    const session = await request<{ csrf_token: string }>('/api/v1/session', {
      method: 'POST', body: JSON.stringify({ bootstrap_secret: bootstrapSecret }),
    })
    csrfToken = session.csrf_token
    sessionStorage.setItem('boundarylab-csrf', csrfToken)
  },
  async logout() {
    await request<void>('/api/v1/session', { method: 'DELETE' })
    csrfToken = ''
    sessionStorage.removeItem('boundarylab-csrf')
  },
  targets: () => request<Target[]>('/api/v1/targets'),
  capabilities: () => request<Capabilities>('/api/v1/capabilities'),
  policy: (targetAlias?: string) => request<PolicySummary>(`/api/v1/policy${targetAlias ? `?target_alias=${encodeURIComponent(targetAlias)}` : ''}`),
  spec: (targetAlias?: string) => request<SpecSummary>(`/api/v1/spec${targetAlias ? `?target_alias=${encodeURIComponent(targetAlias)}` : ''}`),
  analyze: (label: string, document: Record<string, unknown>, har: Record<string, unknown> | null) =>
    request<DiscoveryAnalysis>('/api/v1/discovery/analyses', {
      method: 'POST', body: JSON.stringify({ label, document, har }),
    }),
  analyses: () => request<DiscoveryAnalysis[]>('/api/v1/discovery/analyses?limit=20'),
  candidateReviews: (analysisId: string) =>
    request<CandidateReview[]>(`/api/v1/discovery/analyses/${analysisId}/reviews`),
  reviewCandidate: (analysisId: string, candidateId: string, decision: 'approved' | 'rejected', rationale: string) =>
    request<CandidateReview>(`/api/v1/discovery/analyses/${analysisId}/reviews`, {
      method: 'POST', body: JSON.stringify({ candidate_id: candidateId, decision, rationale }),
    }),
  runs: () => request<Run[]>('/api/v1/runs?limit=50'),
  run: (id: string) => request<Run>(`/api/v1/runs/${id}`),
  startRun: (targetAlias: string) => request<Run>('/api/v1/runs', { method: 'POST', body: JSON.stringify({ target_alias: targetAlias }) }),
  cancelRun: (id: string) => request<Run>(`/api/v1/runs/${id}/cancel`, { method: 'POST' }),
  compare: (runIds: string[]) => request<Comparison>('/api/v1/comparisons', { method: 'POST', body: JSON.stringify({ run_ids: runIds }) }),
  explain: (runId: string, mode: 'deterministic' | 'ai') => request<Explanation>(`/api/v1/runs/${runId}/explanations`, {
    method: 'POST', body: JSON.stringify({ mode }),
  }),
  async artifact(runId: string, format: 'report_html' | 'results_json') {
    return request<{ download_path: string; sha256: string }>(`/api/v1/runs/${runId}/artifacts`, {
      method: 'POST', body: JSON.stringify({ format }),
    })
  },
}
