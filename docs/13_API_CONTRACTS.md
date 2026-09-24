# API contracts and adapter boundary

Machine sources: [control API OpenAPI](../contracts/control-api.openapi.json), [fixture API OpenAPI](../contracts/demo-api.openapi.json), [policy schema](../contracts/policy.schema.json). These are contract artifacts, not running endpoints.

## Control plane `/api/v1`

| Method and route | Behavior |
|---|---|
| POST `/session` | Exchange local bootstrap secret for opaque operator session; never log request body |
| DELETE `/session` | Invalidate current session |
| GET `/targets` | Return trusted aliases, scope hashes and safe limits; never credentials |
| POST `/specs` | Import JSON object in a typed request; return normalized hash and operation coverage |
| POST `/policies` | Validate a policy against schema and selected spec; create immutable version |
| POST `/policies/{policy_id}/approval` | Approve exact hash with recorded policy-owner attestation |
| POST `/runs` | Require approved policy/scope; create queued run, 202 |
| GET `/runs` | Bounded recent run list for comparisons |
| GET `/runs/{run_id}` | Return state, scope, case counts, assessment and cleanup state |
| GET `/runs/{run_id}/events` | Cursor-based ordered events, max 100 per page |
| GET `/runs/{run_id}/results` | Case results, findings and evidence references |
| POST `/runs/{run_id}/cancel` | Idempotent cancellation request; terminal runs return their existing state |
| POST `/comparisons` | Compare 2–3 compatible completed runs; return mismatch details on 409 |
| POST `/runs/{run_id}/artifacts` | Generate `report_html` or `results_json` plus replay manifest |
| GET `/artifacts/{artifact_id}` | Authorized binary/text download by opaque ID |

GET routes require the operator cookie. Mutating routes except session creation also require `X-CSRF-Token`, and all browser requests enforce approved Origin. Session creation checks origin and rate limits. Implementation uses appropriate Secure cookie settings for HTTPS; the explicit local HTTP development profile cannot claim transport encryption.

POST `/runs` accepts `Idempotency-Key`. Repeating the same key and canonical body returns the same run; changed body returns 409. Retain key mapping for 24 hours in P0. Creating a second run may queue it; only one executes at a time. Queue length cap 10; overflow 429 with retry guidance.

Errors use `{error:{code,message,request_id,details}}`; never include exception stacks or credential values. Important codes: `INVALID_SPEC`, `UNSUPPORTED_SPEC`, `POLICY_NOT_APPROVED`, `POLICY_SPEC_MISMATCH`, `SCOPE_DENIED`, `IDENTITY_MISMATCH`, `NON_COMPARABLE_RUNS`, `BUDGET_EXCEEDED`, `ARTIFACT_UNAVAILABLE`. Use 422 for invalid policy, 413 for oversized input, 401/403 for control-plane auth, 409 for state/hash conflicts and 503 for unavailable worker.

## Target adapter

Required operation IDs: `health`, `getMe`, `listInvoices`, `getInvoice`, `getInvoicePreview`, `grantShare`, `revokeShare`, `queueExport`, `getExport`, `getExportContent`. The ordinary OpenAPI contract excludes lab administration.

The **internal demo adapter only** supports `POST /__lab/fixtures` and `DELETE /__lab/fixtures/{namespace}` with a distinct lab token. Factory input is `{run_id, fixture_semantics_version}`; output contains a namespace, identity bindings, object IDs, secret-reference bindings and expected synthetic markers. Secret values are obtained separately from the runtime registry. Namespace deletion is idempotent and cannot reset other runs.

Each adapter implements `prepare`, `preflight`, `resolve_object`, `cleanup` and `read_build_id`. A future custom staging adapter requires explicit fixture provisioning and permissions; an arbitrary OpenAPI file alone is insufficient to infer business ownership or reset remote data.

## Severity and evidence contract

Object or export exposure of a protected synthetic marker is `high` under this fixture's declared impact. Owner-only field leakage is `medium` here; a real deployment may justify a different assessment. Functional regression has severity `medium` and kind `functional_regression`, not a fabricated CVE. No numeric CVSS is emitted without a justified vector and review.

Evidence contains operation, method, templated path, identity label, response status, permitted body pointers, marker-match boolean/digest, rule and time offsets. Authorization/Cookie/Set-Cookie, tokens in URL/body and disallowed fields are removed before storage. A response status alone cannot establish object exposure.
