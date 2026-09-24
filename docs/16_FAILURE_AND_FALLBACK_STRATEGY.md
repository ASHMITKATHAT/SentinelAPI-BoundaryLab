# Failure handling and honest fallbacks

| Failure | Product response | Continue / recovery |
|---|---|---|
| Invalid or unsupported OpenAPI | Show path-specific validation and supported format | No requests; import corrected spec |
| No business policy | Needs-policy state | Draft/review policy before tests |
| Wrong identity or expired token | Authentication context invalid | Dependent cases inconclusive; new run after repair |
| Active collaborator denied | Functional regression with evidence | Dependent export cases inconclusive, independent owner/object tests may continue |
| Export never ready | Timeout with poll count and bounded trace | No revocation conclusion; namespace cleanup |
| Revoke request fails | Preconditions incomplete | Do not label later access a post-revocation leak |
| 200 response without expected canary | Unexpected representation | Inconclusive, inspect contract rather than inventing exposure |
| 403/404 with protected marker body | Data exposure despite denial status | Policy violation if context/control and marker are valid |
| Network timeout/429/5xx | Transport or target-capacity evidence | No security pass; stop or skip dependent steps |
| Body exceeds cap / unknown type | Bounded read, discard unapproved content | Inconclusive; no arbitrary file parser |
| Request/time budget exhausted | Stop scheduling | Preserve evidence, cleanup reserve, incomplete required cases |
| Worker crashes after mutation | Interrupted run, ambiguous step | No replay; fresh run and separately tracked old cleanup |
| Database temporarily busy | Bounded short retry for DB operation only | Never retry the preceding target mutation |
| Cancellation | Stop test traffic and attempt authorized cleanup | Terminal cancelled; retain prior observed violations |
| Cleanup fails | Prominent cleanup-pending warning | Do not delete broadly; retry only known namespace |
| Build changes during run | Invalid comparison context | Incomplete; rerun on stable build |
| Hashes differ across runs | Comparison rejected | Select compatible runs; no normalized-away policy changes |
| AI unavailable | Deterministic explanation template | All P0 scans and reports still operate |
| Demo internet unavailable | Local fixtures, local images and app | Works once dependencies are preloaded |

## Presentation fallback ladder

1. Repair/restart the actual local app, preserve its failed-run evidence and rerun a fresh namespace.
2. If the UI fails but the engine works, use its real API/CLI results and saved report, identifying the UI failure.
3. If the runtime cannot be restored, show a **labelled previously recorded run/video** with its build/date and explain that it is not live.
4. If no working run exists, show the design prototype as a design prototype. Do not call synthetic evidence a test result.

Have a local screen recording, exported report, checksum manifest and setup notes ready after a successful implemented run. Those fallback artifacts do not exist in this specification pack yet and must be produced during implementation.

## Recovery invariants

No failed prerequisite is converted to pass. No counter resets after retries to hide exceeded budgets. No resumed run reuses an uncertain mutation. No cached report is silently substituted for a new run. A report includes why evidence is missing and what a user can do next.
