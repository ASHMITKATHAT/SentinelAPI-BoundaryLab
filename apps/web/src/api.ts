import type { CandidateReview, Capabilities, Comparison, DiscoveryAnalysis, Explanation, GitHubImportResult, PolicySummary, Run, RunEvent, SpecSummary, Target } from './types'
import { ApiError, requestJson } from './http'

let csrfToken = ''
let status = { connection: 'unknown' as 'unknown' | 'connected' | 'offline', sessionExpired: false }
const listeners = new Set<() => void>()
export const getApiStatus = () => status
export const subscribeApiStatus = (listener: () => void) => { listeners.add(listener); return () => { listeners.delete(listener) } }
function updateStatus(update: Partial<typeof status>) {
  const next = { ...status, ...update }
  if (next.connection === status.connection && next.sessionExpired === status.sessionExpired) return
  status = next
  listeners.forEach(listener => listener())
}

async function request<T>(path: string, init: RequestInit = {}, timeoutMs?: number): Promise<T> {
  const headers = new Headers(init.headers)
  if (init.body) headers.set('Content-Type', 'application/json')
  if (init.method && init.method !== 'GET' && csrfToken) headers.set('X-CSRF-Token', csrfToken)
  try {
    const result = await requestJson<T>(path, { ...init, headers }, timeoutMs)
    updateStatus({ connection: 'connected' })
    return result
  } catch (error) {
    if (error instanceof ApiError) {
      if (['network', 'timeout', 'protocol'].includes(error.kind)) updateStatus({ connection: 'offline' })
      else updateStatus({ connection: 'connected' })
      if (error.kind === 'session' && !(path === '/api/v1/session' && init.method === 'POST')) {
        csrfToken = ''
        updateStatus({ sessionExpired: true })
      }
    }
    throw error
  }
}

export const api = {
  health: () => requestJson<{ status: string; service: string; version: string }>('/api/healthz', {}, 4_000),
  async restoreSession() {
    const session = await request<{ csrf_token: string }>('/api/v1/session')
    csrfToken = session.csrf_token
    updateStatus({ sessionExpired: false })
  },
  async login(bootstrapSecret: string) {
    const session = await request<{ csrf_token: string }>('/api/v1/session', {
      method: 'POST', body: JSON.stringify({ bootstrap_secret: bootstrapSecret }),
    })
    csrfToken = session.csrf_token
    updateStatus({ sessionExpired: false })
  },
  async logout() {
    await request<void>('/api/v1/session', { method: 'DELETE' })
    csrfToken = ''
    updateStatus({ sessionExpired: false })
  },
  targets: () => request<Target[]>('/api/v1/targets'),
  capabilities: () => request<Capabilities>('/api/v1/capabilities'),
  importGitHubOpenApi: (repository: string, ref: string, path: string) => request<GitHubImportResult>('/api/v1/integrations/github/import', {
    method: 'POST', body: JSON.stringify({ repository: repository.trim(), ref: ref.trim(), path: path.trim() }),
  }, 20_000),
  policy: (targetAlias?: string) => request<PolicySummary>(`/api/v1/policy${targetAlias ? `?target_alias=${encodeURIComponent(targetAlias)}` : ''}`),
  spec: (targetAlias?: string) => request<SpecSummary>(`/api/v1/spec${targetAlias ? `?target_alias=${encodeURIComponent(targetAlias)}` : ''}`),
  analyze: (label: string, document: Record<string, unknown>, har: Record<string, unknown> | null) => {
    const body = JSON.stringify({ label: label.trim(), document, har })
    if (new TextEncoder().encode(body).byteLength > 2_000_000) {
      return Promise.reject(new Error('OpenAPI and HAR together exceed the 2 MB request limit. Remove the traffic sample or use smaller files.'))
    }
    return request<DiscoveryAnalysis>('/api/v1/discovery/analyses', { method: 'POST', body })
  },
  analyses: () => request<DiscoveryAnalysis[]>('/api/v1/discovery/analyses?limit=20'),
  candidateReviews: (analysisId: string) =>
    request<CandidateReview[]>(`/api/v1/discovery/analyses/${analysisId}/reviews`),
  reviewCandidate: (analysisId: string, candidateId: string, decision: 'approved' | 'rejected', rationale: string) =>
    request<CandidateReview>(`/api/v1/discovery/analyses/${analysisId}/reviews`, {
      method: 'POST', body: JSON.stringify({ candidate_id: candidateId, decision, rationale }),
    }),
  runs: () => request<Run[]>('/api/v1/runs?limit=50'),
  run: (id: string) => request<Run>(`/api/v1/runs/${id}`),
  runEvents: (id: string) => request<{ events: RunEvent[]; next_cursor: number }>(`/api/v1/runs/${id}/events?after=0&limit=100`),
  startRun: (targetAlias: string) => request<Run>('/api/v1/runs', { method: 'POST', body: JSON.stringify({ target_alias: targetAlias }) }),
  cancelRun: (id: string) => request<Run>(`/api/v1/runs/${id}/cancel`, { method: 'POST' }),
  compare: (runIds: string[]) => request<Comparison>('/api/v1/comparisons', { method: 'POST', body: JSON.stringify({ run_ids: runIds }) }),
  explain: (runId: string, mode: 'deterministic' | 'ai') => request<Explanation>(`/api/v1/runs/${runId}/explanations`, {
    method: 'POST', body: JSON.stringify({ mode }),
  }, mode === 'ai' ? 60_000 : 20_000),
  async artifact(runId: string, format: 'report_html' | 'results_json') {
    return request<{ download_path: string; sha256: string }>(`/api/v1/runs/${runId}/artifacts`, {
      method: 'POST', body: JSON.stringify({ format }),
    })
  },
}
