# BoundaryLab implementation status

**Verified 24 September 2026.** This record separates working behavior from product plans and production claims.

## Current system

BoundaryLab is a working local, single-operator authorization regression workbench. The React client and FastAPI control plane run on `127.0.0.1:8080`. Three independent synthetic invoice services run on ports 9011–9013. The control worker calls those services through real localhost HTTP connections, persists results in SQLite and returns only evidence produced by the run.

The product currently covers one reviewed permission lifecycle: Alice owns an invoice, Bob receives and later loses a share, and an asynchronous export created during the share is retrieved before and after the declared revocation deadline. Mallory provides the cross-tenant negative case.

## Verified acceptance evidence

| Target build | Pass | Violation | Inconclusive | Requests | Cleanup | Assessment |
|---|---:|---:|---:|---:|---|---|
| `invoice-vulnerable` | 8 | 4 | 0 | 26 | Complete | Blocked |
| `invoice-owner-only` | 7 | 2 | 3 | 21 | Complete | Blocked |
| `invoice-fixed` | 12 | 0 | 0 | 26 | Complete | Pass in scope |

The live comparison shows why a deny-everyone repair is not acceptable. It prevents Bob's valid shared-detail and export flows, which produces two functional policy violations and makes three dependent cases inconclusive. The correct repair preserves those allowed paths and denies retrieval after revocation.

Automated verification covers scenario verdicts, transport bounds and redaction, hashed sessions, restart recovery, queue cancellation, CSRF/Origin enforcement, trusted target selection, discovery bounds, HAR minimization, remediation schema validation, CI failure semantics and safe report rendering. The frontend passes TypeScript checking and a production Vite build. `tools/validate_pack.py` validates contracts, schemas, required cases, expected fixture counts and local documentation links.

## Generic onboarding without unsafe execution

The Discovery workspace accepts OpenAPI 3.x JSON and optional HAR JSON. It derives operation coverage, flags resource-ID operations as human-reviewed dual-identity candidates and compares observed method/path templates with the contract. It sends no target requests. It does not persist HAR headers, cookies, query strings or bodies, and it generalizes identifier-like path segments.

Candidate governance is implemented as an append-only decision ledger. Approve/reject requests reference a candidate ID from the stored analysis; the server stores its exact snapshot, canonical SHA-256, rationale, reviewer and timestamp. This prevents the browser from substituting an unreviewed rule body and preserves superseded decisions for inspection.

This makes the product useful on an unfamiliar API before an active adapter exists. Active execution still requires a trusted adapter defining actors, seed/setup, resource extraction, allowed operations, protected markers and cleanup. Arbitrary remote scanning is intentionally unavailable until isolated runners and DNS/IP pinning exist.

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

A multi-stage Dockerfile and hardened local Compose profile are included for repeatable packaging. Only port 8080 is published on host loopback; fixture ports remain private, the process is non-root, the root filesystem is read-only and Linux capabilities are dropped. Docker is unavailable on the local verification host. The GitHub workflow therefore owns the actual image-build and hardened runtime smoke-test gate; do not claim that gate until its run succeeds for the release commit.

Until those gates are complete, describe BoundaryLab as a working local pilot or hackathon MVP. Describe a successful scan as **pass in scope**, never as proof that the target is secure in general.

## Mentor demonstration path

1. Open Discovery, load the disclosed traffic sample, show the shadow route and approve one generated candidate with a written rationale.
2. Open Policy and point to the 2,000 ms revocation promise.
3. Queue the three-build proof from Live runs.
4. Open vulnerable evidence and generate deterministic remediation.
5. Compare all three runs to show the leak, broken owner-only repair and correct repair.
6. Export the fixed HTML report and explain its tested-scope boundary.

The entire path uses persisted live-run data. The older file at `design/boundarylab-prototype.html` remains only a labelled design reference.
