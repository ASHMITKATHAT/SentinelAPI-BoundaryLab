# BoundaryLab implementation status

**Verified 25 September 2026.** This record separates working behavior from product plans and production claims.

## Current system

BoundaryLab is a working local, single-operator authorization regression workbench. The React client and FastAPI control plane run on `127.0.0.1:8080`. The process starts with no active target unless the operator supplies a reviewed real-target registry or explicitly enables the disclosed lab fixtures. This prevents packaged or local startup from silently presenting synthetic results as real findings.

Real-target mode binds a fixed OpenAPI `GET` operation to a numeric loopback origin, a fixed resource ID reference, an in-memory proof marker and 2–6 environment-backed identities. It sends one bounded request per identity and evaluates allowed access, denied access and identity-specific forbidden fields. The browser cannot submit a URL, token, resource ID, marker or expected verdict.

Explicit lab mode covers one reviewed permission lifecycle: Alice owns an invoice, Bob receives and later loses a share, and an asynchronous export created during the share is retrieved before and after the declared revocation deadline. Mallory provides the cross-tenant negative case.

## Verified acceptance evidence

| Target build | Pass | Violation | Inconclusive | Requests | Cleanup | Assessment |
|---|---:|---:|---:|---:|---|---|
| `invoice-vulnerable` | 8 | 4 | 0 | 26 | Complete | Blocked |
| `invoice-owner-only` | 7 | 2 | 3 | 21 | Complete | Blocked |
| `invoice-fixed` | 12 | 0 | 0 | 26 | Complete | Pass in scope |

The live comparison shows why a deny-everyone repair is not acceptable. It prevents Bob's valid shared-detail and export flows, which produces two functional policy violations and makes three dependent cases inconclusive. The correct repair preserves those allowed paths and denies retrieval after revocation.

Automated verification covers scenario verdicts, transport bounds and redaction, hashed sessions, restart recovery, queue cancellation, CSRF/Origin enforcement, trusted target selection, discovery bounds, HAR minimization, remediation schema validation, CI failure semantics and safe report rendering. The frontend passes TypeScript checking and a production Vite build. `tools/validate_pack.py` validates contracts, schemas, required cases, expected fixture counts and local documentation links.

The suite now contains 39 passing service tests, including real-target registry validation, OpenAPI operation binding, numeric-loopback enforcement, missing-environment failure, encoded resource IDs, exception-detail suppression, marker/token/resource-ID non-persistence, restricted-field redaction, persisted worker-activity ordering and release-gate regression classification. A browser QA run exercised the real adapter through separate localhost sockets: one allowed identity received the configured marker, one denied identity received 404, and the resulting two-case report passed in scope with marker and bearer values redacted.

Comparison now produces a deterministic release gate from ordered baseline and candidate runs. It reports repaired cases, preserved passes, newly regressed cases and unresolved evidence. A candidate is ready only when every required candidate case passes and no prior pass regresses. The UI states this as a scoped release decision rather than a general security certification.

The local startup helper launches the service in the background, waits for its health endpoint and stores process/log metadata under the ignored runtime directory. Browser requests have bounded timeouts and distinguish an offline service, expired session, validation response and unexpected proxy content. Mutations are not automatically retried.

The Verify workspace now streams persisted worker events instead of presenting a generic spinner. A run visibly moves through queue acceptance, worker claim, safety-scope verification, bounded case execution, evidence sealing and final verdict. Selecting a newly-created run remains stable while the run list refreshes, so live and historical evidence cannot be mixed in one detail panel.

## Generic onboarding without unsafe execution

The Discovery workspace accepts OpenAPI 3.x JSON and optional HAR JSON. It derives operation coverage, flags resource-ID operations as human-reviewed dual-identity candidates and compares observed method/path templates with the contract. It sends no target requests. It does not persist HAR headers, cookies, query strings or bodies, and it generalizes identifier-like path segments.

Candidate governance is implemented as an append-only decision ledger. Approve/reject requests reference a candidate ID from the stored analysis; the server stores its exact snapshot, canonical SHA-256, rationale, reviewer and timestamp. This prevents the browser from substituting an unreviewed rule body and preserves superseded decisions for inspection.

This makes the product useful on an unfamiliar API before an active adapter exists. Real read execution requires a reviewed registry and environment-backed identities; active mutation still requires a trusted adapter defining actors, seed/setup, resource extraction, allowed operations, protected markers and cleanup. Arbitrary remote scanning is intentionally unavailable until isolated runners and DNS/IP pinning exist. The [real-target runbook](37_REAL_TARGET_RUNBOOK.md) documents the supported workflow and limits.

## Remediation and CI

Completed runs provide deterministic root-cause guidance. Optional model-assisted remediation uses schema-constrained output and only failed-case summaries after an explicit operator action. Model output is advisory and cannot alter deterministic results.

`boundarylab.cli gate` runs the same lifecycle against a loopback target and returns a non-zero exit code for configured violations, inconclusive cases or execution errors. The repository workflow builds the client, runs all tests, validates artifacts and gates the live fixed fixture.

## Runtime and evidence controls

- Target origins are selected from a server-owned registry; the browser cannot submit an arbitrary URL.
- HTTP redirects and proxy environment variables are disabled. Concurrency, request rate, total request count and decoded response bytes are bounded.
- Cleanup capacity is reserved even after the main request budget is used.
- Authorization values and unrestricted bodies are removed before evidence persistence.
- Sessions are random opaque values stored only as SHA-256 hashes. Cookies are HTTP-only and same-site strict; mutations require CSRF and Origin validation.
- SQLite uses WAL mode and transactional queue claiming. Running jobs become interrupted after an unclean restart rather than being presented as complete.
- Reports include the build ID, policy version, case denominator, incomplete state and cleanup status. HTML output escapes target-derived values and is downloaded with a restrictive CSP.

## Honest production boundary

The system is production-minded for a controlled local demonstration. It has not passed the gates for a public, multi-tenant service. Before an external deployment, the team must add:

1. TLS termination, SSO/RBAC and managed secret rotation.
2. Postgres migrations and backups instead of a local SQLite file.
3. Isolated runner processes or containers with egress allowlists, DNS resolution pinning and per-tenant quotas.
4. Structured logs, metrics, traces, alerting and audited data-retention deletion.
5. Load, soak, browser end-to-end and disaster-recovery tests in the deployment environment.
6. Dependency/SBOM scanning, threat-model review and an independent security assessment.

A multi-stage Dockerfile and hardened local Compose profile are included for repeatable packaging. Only port 8080 is published on host loopback and default startup has no active target. If the disclosed lab is explicitly enabled, fixture ports remain private. The process is non-root, the root filesystem is read-only and Linux capabilities are dropped. Docker is unavailable on the local verification host. The GitHub workflow therefore owns the actual image-build and hardened runtime smoke-test gate; do not claim that gate until its run succeeds for the release commit.

Until those gates are complete, describe BoundaryLab as a working local pilot or hackathon MVP. Describe a successful scan as **pass in scope**, never as proof that the target is secure in general.

## Mentor demonstration path

1. Open Discovery, load the disclosed traffic sample, show the shadow route and approve one generated candidate with a written rationale.
2. Open Policy and point to the 2,000 ms revocation promise.
3. Queue the three-build proof from Live runs.
4. Open vulnerable evidence and generate deterministic remediation.
5. Compare all three runs to show the leak, broken owner-only repair and correct repair.
6. Export the fixed HTML report and explain its tested-scope boundary.

The entire path uses persisted live-run data. The older file at `design/boundarylab-prototype.html` remains only a labelled design reference.
