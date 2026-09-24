# API contracts and adapter boundary

Machine sources: [control API OpenAPI](../contracts/control-api.openapi.json), [fixture API OpenAPI](../contracts/demo-api.openapi.json), [policy schema](../contracts/policy.schema.json). The first two describe the implemented local services; the policy schema remains the authoritative supported invoice scenario.

## Control plane `/api/v1`

| Method and route | Behavior |
|---|---|
| POST `/session` | Exchange local bootstrap secret for opaque operator session; never log request body |
| GET `/session` | Restore session and its CSRF token after a browser reload |
| DELETE `/session` | Invalidate current session |
| GET `/targets` | Return trusted aliases and safe execution limits; never credentials |
| GET `/capabilities` | Disclose passive discovery, trusted-adapter execution and configured remediation modes |
| GET `/policy` | Return the bundled reviewed policy and canonical SHA-256 |
| GET `/spec` | Return the bundled fixture contract and operation inventory |
| POST `/discovery/analyses` | Passively analyze OpenAPI 3.x plus optional HAR; persist derived metadata only |
| GET `/discovery/analyses` | Return recent persisted discovery results |
| POST `/runs` | Require a trusted target alias; create queued run, 202 |
| GET `/runs` | Bounded recent run list for comparisons |
| GET `/runs/{run_id}` | Return state, scope, case counts, assessment and cleanup state |
| GET `/runs/{run_id}/events` | Cursor-based ordered events, max 100 per page |
| POST `/runs/{run_id}/cancel` | Idempotent cancellation request; terminal runs return their existing state |
| POST `/comparisons` | Compare 2–3 compatible completed runs; return mismatch details on 409 |
| POST `/runs/{run_id}/artifacts` | Generate `report_html` or `results_json` plus replay manifest |
| POST `/runs/{run_id}/explanations` | Generate persisted deterministic or explicitly requested AI remediation |
| GET `/artifacts/{artifact_id}` | Authorized binary/text download by opaque ID |

GET routes require the operator cookie. Mutating routes except session creation also require `X-CSRF-Token`, and all browser requests enforce approved Origin. Session creation checks Origin. Cookies are HTTP-only and same-site strict. Secure cookies are enabled by configuration for HTTPS; the explicit local HTTP development profile cannot claim transport encryption.

Only one run executes at a time. Queue length is capped at 10 and overflow returns 429. Idempotency-key persistence is a staging-pilot requirement and is not claimed by the current local API.

Errors use `{error:{code,message,request_id}}`; never include exception stacks or credential values. Use 422 for invalid documents, 413 for oversized discovery input, 401/403 for control-plane auth, 409 for state/capability conflicts, 429 for queue pressure and 502 for a failed optional remediation provider.

Discovery requests are capped at 2 MB, 500 OpenAPI paths, 2,000 operations and 5,000 HAR entries. External `$ref` values are rejected without network access. HAR headers, cookies, query strings and bodies are not stored. Candidate invariants are marked for review and cannot initiate active traffic.

## Target adapter

Required operation IDs: `health`, `getMe`, `listInvoices`, `getInvoice`, `getInvoicePreview`, `grantShare`, `revokeShare`, `queueExport`, `getExport`, `getExportContent`. The ordinary OpenAPI contract excludes lab administration.

The **internal demo adapter only** supports `POST /__lab/fixtures` and `DELETE /__lab/fixtures/{namespace}` with a distinct lab token. Factory input is `{run_id, fixture_semantics_version}`; output contains a namespace, identity bindings, object IDs, secret-reference bindings and expected synthetic markers. Secret values are obtained separately from the runtime registry. Namespace deletion is idempotent and cannot reset other runs.

Each adapter implements `prepare`, `preflight`, `resolve_object`, `cleanup` and `read_build_id`. A future custom staging adapter requires explicit fixture provisioning and permissions; an arbitrary OpenAPI file alone is insufficient to infer business ownership or reset remote data.

## Severity and evidence contract

Object or export exposure of a protected synthetic marker is `high` under this fixture's declared impact. Owner-only field leakage is `medium` here; a real deployment may justify a different assessment. Functional regression has severity `medium` and kind `functional_regression`, not a fabricated CVE. No numeric CVSS is emitted without a justified vector and review.

Evidence contains operation, method, templated path, identity label, response status, permitted body pointers, marker-match boolean/digest, rule and time offsets. Authorization/Cookie/Set-Cookie, tokens in URL/body and disallowed fields are removed before storage. A response status alone cannot establish object exposure.
