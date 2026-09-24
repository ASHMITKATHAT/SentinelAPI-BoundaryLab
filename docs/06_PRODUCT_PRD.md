# Product requirements

Version 1.0 • 24 September 2026 • planned local MVP. Requirements below are unimplemented until the [readiness gates](28_PRODUCTION_READINESS.md) are evidenced.

## Users and jobs

Backend engineer: reproduce and fix access behavior without leaking credentials into a report. Engineering lead: review the declared permission contract and compare a change. Mentor/judge: inspect whether a result is real and whether the product has a customer. One local operator account serves the MVP; multi-organization roles are later.

## Release scope

| ID | Priority | Requirement and acceptance |
|---|---|---|
| R01 | P0 | Import OpenAPI **3.1 JSON**, local file ≤1 MiB; unique operation IDs; reject external references and unsupported documents with a clear error. Every operation receives supported/unsupported/not-selected coverage status. |
| R02 | P0 | Select a trusted target alias and runtime credential references for Alice, Bob and Mallory. Preflight each identity and target build; mismatches stop dependent tests. Secrets never appear in persisted artifacts. |
| R03 | P0 | Review policy v1: identities, object ownership, active sharing, restricted field and revocation semantics. Explicit approval pins its hash. Unknown policy never becomes a confirmed flaw. |
| R04 | P0 | Test private invoice access under owner, same-tenant non-owner, foreign-tenant and anonymous sessions; use positive controls plus canary equality, not status alone. |
| R05 | P0 | Check `/internal_bank_ref` only on the explicitly shared invoice response where Bob is allowed object access but not that property. Missing business policy returns inconclusive. |
| R06 | P0 | Test Bob's active shared access and queued export, revoke sharing, then probe fresh retrieval after 2,000 ms grace + 200 ms margin. Verify Alice still has access. |
| R07 | P0 | Persist actual sanitized evidence, case verdicts, severity reasons, scope and build/policy/spec/suite versions. Reports survive restart. |
| R08 | P0 | Compare the three fixture variants using compatible policy/spec/suite/fixture-semantics hashes. A failed positive control is a regression or inconclusive result, never a successful repair. |
| R09 | P0 | Export JSON results and a standalone HTML engineer/nontechnical report. Include replay manifest with secret placeholders; no executable arbitrary code from imported data. |
| R10 | P0 | Enforce target/method/path authorization, request/time/body limits, cancellation, redaction and isolated fixture cleanup. Redirects cannot escape scope. |
| R11 | P0 | Persist queue/run states; recover crashed runs as incomplete; distinguish completed evaluation from passing behavior. |
| R12 | P1 | CLI executes the same engine and emits CI exit status: 0 scoped pass, 1 observed violation/regression, 2 incomplete/configuration error. P0 exported replay instructions can use the control API. |
| R13 | P1 | With a reviewed quota contract, test a small configured allowance using bounded sequential requests; otherwise mark rate-limit checks unsupported. |
| R14 | P1 | Optional AI drafts policy/explanations from redacted structured facts; schema validation and human approval required. Core works with no AI key. |

P0 is the two-developer target, with simplified UI/report presentation for a solo developer. P1 starts only after a complete P0 vertical slice. The signature lifecycle and positive-control comparison cannot be cut in favor of AI or extra scan categories.

## Non-goals

No traffic capture, OpenAPI 2/3.0 conversion, GraphQL/gRPC, OAuth login automation, arbitrary workflows generated and executed by an LLM, public-target scanning, CVSS auto-scoring, exploit-chain discovery, background production monitoring, billing, SSO or compliance certification in P0. Listed compatibility limits must appear in onboarding and reports.

## Coverage and semantics

A **case** evaluates one expected behavior; a **finding** records an observed policy violation or functional regression; a **run** executes a fixed suite; a **release assessment** summarizes only its selected scope. “Completed” describes execution and does not mean safe.

Case verdicts: `pass`, `violation`, `inconclusive`, `skipped`. Findings: `security_violation` or `functional_regression`, with category, human-readable severity and evidence. A failed control can create a regression while dependent security tests are inconclusive.

Release assessment: `blocked` if any required case violates policy; otherwise `incomplete` if any required case is inconclusive/skipped or execution did not complete; otherwise `pass_in_scope`. A separately recorded incomplete flag remains visible even when blocked takes precedence. No global “secure” badge.

## Nonfunctional targets—not measured results

Local first scan under 5 minutes after prerequisites are installed; the full small fixture suite under 120 seconds excluding startup; at most 200 target requests/run, 2 requests/second and one in-flight request; response body cap 64 KiB; offline operation after images/dependencies are available. Setup time and suite latency must be measured on the actual demo laptop.

Acceptance additionally requires keyboard-accessible flows, explicit labels for all states, zero credential occurrences in exported synthetic test reports, and failure injection that cannot produce a green result. Supporting setup, budget counters and cleanup traffic count toward total scope/budget accounting.

## Business success hypotheses

At 30 days: 10 interviews, 3 staging pilots, at least 2 explicit paid-pilot discussions. At 60 days: ≥2 paid pilots, an owner maintaining a policy without us, and evidence that recurring testing is valued. These are discovery gates, not traction claims.
