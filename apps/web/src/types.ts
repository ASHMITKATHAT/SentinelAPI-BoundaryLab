export type Verdict = 'pass' | 'violation' | 'inconclusive' | 'skipped'
export type RunState = 'queued' | 'running' | 'completed' | 'failed' | 'interrupted' | 'cancelled'

export interface Target {
  alias: string
  label: string
  origin: string
  synthetic_fixture: boolean
  mode: 'temporal_lab' | 'real_read_probe'
  ready: boolean
  missing_environment: string[]
  case_count: number
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
  outcomes: Array<{ run_id: string; target_alias: string; build_id: string | null; verdict: Verdict; kind: string | null }>
}

export interface Comparison {
  compatible: boolean
  policy_version: string
  runs: Run[]
  rows: ComparisonRow[]
  gate: {
    decision: 'ready' | 'blocked' | 'needs_evidence'
    baseline_run_id: string
    candidate_run_id: string
    fixed: number
    regressed: number
    preserved: number
    unresolved: number
    reasons: string[]
    changes: Array<{
      case_id: string
      name: string
      before: Verdict
      after: Verdict
      classification: 'fixed' | 'regressed' | 'preserved' | 'unresolved'
    }>
  }
}

export interface SpecSummary {
  configured: boolean
  title: string
  version: string
  openapi: string
  operation_count: number
  operations: string[]
  document: Record<string, unknown> | null
}

export interface PolicySummary {
  approved: boolean
  sha256: string
  document: Record<string, unknown>
}

export interface Capabilities {
  discovery: { openapi: boolean; har: boolean; active_replay: string; candidate_reviews: string }
  runtime: { configured_targets: number; real_targets: number; lab_targets: number; remote_network: string }
  remediation: { deterministic: boolean; ai_configured: boolean; model: string | null; data_sent: string }
}

export interface DiscoveryAnalysis {
  id: string
  label: string
  created_at: string
  analysis_version: string
  spec: { title: string; version: string; openapi: string; sha256: string }
  summary: {
    documented_paths: number
    documented_operations: number
    ownership_candidates: number
    authenticated_operations: number
    shadow_operations: number
    har_entries: number
  }
  invariant_candidates: Array<{
    id: string
    kind: string
    operation_id: string
    method: string
    path: string
    resource_parameter: string
    confidence: string
    proposed_rule: string
    required_setup: string
    review_required: boolean
  }>
  traffic_diff: {
    provided: boolean
    documented_operations_observed: number
    shadow_operations: Array<{ method: string; path: string; sample_count: number; risk: string }>
    unobserved_documented_operations: Array<{ method: string; path: string }>
  }
  safety: Record<string, boolean>
  limitations: string[]
}

export interface CandidateReview {
  id: string
  analysis_id: string
  candidate_id: string
  decision: 'approved' | 'rejected'
  rationale: string
  reviewer: string
  candidate_sha256: string
  created_at: string
  candidate: DiscoveryAnalysis['invariant_candidates'][number]
}

export interface Explanation {
  id: string
  run_id: string
  mode: 'deterministic' | 'openai_structured'
  model: string | null
  provider_status: string
  summary: string
  risk: 'critical' | 'high' | 'medium' | 'low' | 'none'
  root_causes: Array<{ case_id: string; category: string; explanation: string; recommended_guard: string }>
  remediation_steps: string[]
  regression_checks: string[]
  patch_outline: string
  limitations: string[]
}
