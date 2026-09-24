export type Verdict = 'pass' | 'violation' | 'inconclusive' | 'skipped'
export type RunState = 'queued' | 'running' | 'completed' | 'failed' | 'interrupted' | 'cancelled'

export interface Target {
  alias: string
  label: string
  origin: string
  synthetic_fixture: boolean
  limits: { requests: number; requests_per_second: number; in_flight: number; response_bytes: number }
}

export interface CaseResult {
  case_id: string
  name: string
  verdict: Verdict
  expected: string
  observed: string
  finding_kind: 'security_violation' | 'functional_regression' | null
  evidence_ids: string[]
  reason_code: string
}

export interface Evidence {
  evidence_id: string
  operation_id: string
  identity: string
  method: string
  path: string
  status_code: number | null
  marker_match: boolean | null
  start_offset_ms: number
  duration_ms: number
  request_headers: Record<string, string>
  response_excerpt: unknown
  sha256: string
}

export interface Report {
  target_alias: string
  build_id: string | null
  policy_version: string
  assessment: 'blocked' | 'incomplete' | 'pass_in_scope'
  has_incomplete_cases: boolean
  counts: Record<Verdict, number>
  request_count: number
  cleanup_status: string
  execution_error: string | null
  cases: CaseResult[]
  evidence: Evidence[]
}

export interface Run {
  id: string
  target_alias: string
  state: RunState
  assessment: Report['assessment'] | null
  has_incomplete_cases: boolean
  build_id: string | null
  counts: Record<Verdict, number>
  request_count: number
  cleanup_status: string
  execution_error: string | null
  cancellation_requested: boolean
  created_at: string
  updated_at: string
  started_at: string | null
  completed_at: string | null
  report?: Report | null
}

export interface ComparisonRow {
  case_id: string
  name: string
  outcomes: Array<{ run_id: string; target_alias: string; build_id: string; verdict: Verdict; kind: string | null }>
}

export interface Comparison {
  compatible: boolean
  policy_version: string
  runs: Run[]
  rows: ComparisonRow[]
}
