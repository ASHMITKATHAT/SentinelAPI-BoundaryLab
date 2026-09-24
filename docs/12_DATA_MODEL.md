# Data model and invariants

All IDs are opaque server-generated strings. UTC timestamps support display; local monotonic durations support within-process timing. Never compare monotonic values from different processes or resumed runs. Store amounts of time as integer milliseconds.

| Entity | Key fields | Invariants |
|---|---|---|
| `projects` | id, name, created_at | One seeded local project is sufficient in P0 |
| `specs` | id, project_id, canonical_json, sha256, operation_summary | Immutable after import; ≤1 MiB; no remote references |
| `target_scopes` | id, project_id, alias, origin, addresses, allowed_operations, limits, hash, approved_at | Provisioned by trusted operator config; UI cannot expand origin or methods |
| `policies` | id, project_id, spec_id, version, document_json, hash, approved_at | Only schema-valid documents; approval pins canonical hash |
| `runs` | id, project_id, spec_id, policy_id, target_scope_id, fingerprints, state, assessment, has_incomplete_cases, timestamps, deadline, request_count, cancellation_requested | Immutable input references; one global active lease; completed does not imply pass |
| `worker_leases` | singleton key, run_id, worker_id, expires_at, heartbeat_at | Transactional claim and renewal; never auto-replay interrupted writes |
| `case_results` | id, run_id, case_id, required, verdict, reason_code, expected_json, observed_json, control_ids | Unique `(run_id, case_id)`; no verdict derived from target variant |
| `steps` | id, run_id, sequence, operation_id, identity_ref, start_offset_ms, duration_ms, state, evidence_id | Monotonic sequence; record start before mutation |
| `findings` | id, run_id, case_result_id, kind, category, severity, rule_id, explanation, evidence_ids | Only observed policy violations/regressions; no finding from missing context alone |
| `evidence` | id, run_id, relative_path, sha256, size_bytes, redaction_version | Path is generated internally; no credentials or unrestricted raw body |
| `artifacts` | id, run_id, type, relative_path, sha256, created_at | Authenticated download; safe MIME/disposition; no arbitrary filesystem lookup |
| `fixture_namespaces` | id, run_id, target_scope_id, semantics_hash, status, cleanup_error | Delete only resources belonging to this namespace |
| `audit_events` | id, run_id nullable, event_type, actor, sanitized_payload, created_at | Approvals, state changes, cancellations and artifact creation; secrets excluded |

`comparisons` may be computed from immutable runs rather than stored. Operator sessions are random opaque IDs stored as hashes with expiry; one bootstrap operator secret is managed outside this database. Credential values are never a column; approved symbolic references resolve in the worker.

## State machines

Run states: `queued → preflight → running → finalizing → completed`. From a nonterminal state, infrastructure failure can lead to `failed`, a worker interruption to `interrupted`, or a cancellation to `cancelled`. Finalization attempts cleanup before committing a terminal state. Recovery can move an abandoned active run directly to interrupted with cleanup pending.

Step states: `pending`, `started`, `recorded`, `failed`, `skipped`. A started mutation without a recorded result is ambiguous and cannot be replayed automatically.

Case verdicts and release assessment follow the [PRD](06_PRODUCT_PRD.md). `violation` covers a required behavior mismatch; finding `kind` distinguishes data/security harm from legitimate-use regression. `inconclusive` is not a severity. `skipped` includes intentionally out-of-scope cases; a required skipped case still prevents a pass.

## Indexes and transactions

Index runs by project/created_at, events by run/id, steps by run/sequence and results by run/case. Enforce foreign keys and unique version constraints. Run claim uses a short write transaction on the lease row. Evidence is written to a temporary generated path, flushed and renamed, then referenced by a short DB transaction. Recovery handles orphan files and missing artifacts explicitly; it never fabricates evidence.

Canonical hashes: sorted-key UTF-8 JSON with compact separators, no NaN/Infinity. Exclude approval timestamps from policy content; include the business rules, scenario version and budgets. Preserve the exact imported spec and a separate normalized form. Fingerprints use normalized spec plus engine version so normalization changes cannot silently alter comparisons.

Default local retention proposal: 7 days for redacted evidence, 30 days for aggregate metadata, manually configurable. Pinning a run keeps its evidence and is explicit. These are product defaults to implement, not legal retention requirements. Deletion removes associated local files; no remote customer data is stored in the MVP.
