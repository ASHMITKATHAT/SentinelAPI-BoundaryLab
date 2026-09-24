# Testing and evaluation strategy

The [evaluation manifest](../examples/evaluation-cases.json) is an expected-results oracle for implementation tests. It is not a report of tests already run. Product verdicts must come from actual HTTP observations, not lookup by variant name.

## Test layers

Unit tests cover policy parsing, marker/status assertions, state transitions, budget accounting, comparison fingerprints and assessment precedence. Integration tests use the independent fixture API and a temporary SQLite database. Security tests use controlled local adversarial endpoints. One browser end-to-end test covers import → approval → run → evidence → compare → export.

Do not test cosmetic details with brittle snapshots. Spend test effort on errors that could falsely declare a repair successful, escape target scope, replay a mutation or expose secrets.

## Core benchmark: 12 required cases × 3 implementations

| Case | Expected behavior | Vulnerable | Owner-only | Fixed |
|---|---|---|---|---|
| C01 | Alice reads private preview | pass | pass | pass |
| C02 | Bob denied private preview | violation | pass | pass |
| C03 | Mallory denied private preview | violation | pass | pass |
| C04 | Anonymous denied private preview | pass | pass | pass |
| C05 | Bob reads active shared detail | pass | violation | pass |
| C06 | Bob cannot see owner-only field | violation | inconclusive | pass |
| C07 | Alice retains owner-only field | pass | pass | pass |
| C08 | Bob queues export while shared | pass | violation | pass |
| C09 | Bob retrieves ready export before revoke | pass | inconclusive | pass |
| C10 | Bob denied export after revoke deadline | violation | inconclusive | pass |
| C11 | Bob denied invoice detail after revoke | pass | pass | pass |
| C12 | Alice retrieves invoice export as owner | pass | pass | pass |

C08 is an independent active-sharing attempt even if C05 fails. C09/C10 require a successfully queued Bob export and valid pre-revocation retrieval. C11 uses an independently established grant/revoke sequence. C12 uses an Alice-created export, so it remains evaluable on owner-only builds. This keeps the benchmark's dependency graph explicit.

Expected aggregate counts: vulnerable **8 pass / 4 violation**; owner-only **7 pass / 2 violation / 3 inconclusive**; fixed **12 pass**. These are seeded expectations, not detection accuracy claims. The three vulnerable mechanisms generate four case violations because the preview bug affects two non-owner identities.

## Reliability/security suite: 18 additional cases

Expired token, wrong subject, failed grant, failed revoke, export timeout, unexpected 200 body, denial body leaking marker, build change, policy mismatch, worker crash after mutation, cancellation, cleanup failure, oversized body, redirect outside scope, external `$ref`, DNS rebinding attempt, secret sentinel persistence and cross-origin control request. Exact expected behavior is in the manifest; each must exercise actual implementation paths.

## How to measure without gaming the result

- Report outcomes over the finite manifest, with all inconclusive/skipped cases visible.
- For seeded security faults, report detected/eligible seeded faults; do not turn these into a universal precision/recall or zero-day claim.
- Measure legitimate-use regression detection separately from security fault detection.
- Record environment, build, suite hash, repetitions, p50/p95 duration if sample size supports it, request counts and setup time.
- Run each core variant at least three times before demo. Repeat only after meaningful changes or unresolved instability; use the runs to find nondeterminism.
- Add one **held-out fixture variation** after core stability: rename IDs/paths via supported mapping or change export delay within contract. A second real API is post-event work, not a false generality claim.

Required correctness gates: no pass when required context is missing; owner-only patch never passes release assessment; fixed fixture passes valid cases; no sentinel secret in logs/DB/reports; no request reaches a scope-escape endpoint; no mutation replay on crash recovery.

## Integration with original PS

The object preview and restricted-property checks cover the two primary seeded flaw classes. The export lifecycle adds temporal business logic. Anonymous/auth-context controls cover basic auth behavior. Rate-limit testing remains visibly unsupported unless its P1 bounded contract test is actually built. Reports explicitly exclude untested categories.
