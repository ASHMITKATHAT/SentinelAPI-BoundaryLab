# Release evidence — BoundaryLab 0.3.0

Evidence captured on 2026-09-24 for the policy-governance and deployment increment. This supplements, rather than rewrites, the [0.2.0 evidence](33_RELEASE_EVIDENCE.md).

## Policy Decision Ledger

The OpenAPI/HAR analyzer still treats inferred authorization invariants as review candidates. Version 0.3.0 adds the missing human governance step:

- the browser submits only a persisted candidate ID, approve/reject decision and written rationale;
- the server resolves the candidate from the saved analysis, so the client cannot substitute a different rule body;
- each entry stores the reviewer, timestamp, exact candidate snapshot and canonical SHA-256;
- later decisions append records and preserve earlier decisions;
- an approval never triggers target traffic and does not bypass the trusted-adapter boundary.

The live compiled UI analyzed the bundled specification and disclosed traffic, produced five ownership candidates and one shadow route, then approved `GET /v1/exports/{export_id}` with a rationale. The screen showed one ledger decision, the local operator and the candidate hash prefix. At a 720-pixel viewport there was no document-level horizontal overflow.

## Automated verification

| Gate | Result |
|---|---|
| Service tests | 30 passed |
| Frontend typecheck | Passed |
| Optimized frontend build | Passed; 30 modules transformed |
| Pack, contract and local-link validation | Passed |
| Static container policy controls | Passed |
| Whitespace/error check | Passed |

The frontend bundle contains a 0.55 kB HTML entry, 22.52 kB CSS file (5.48 kB gzip) and 254.63 kB JavaScript file (78.13 kB gzip).

## Container gate

The multi-stage image builds the client separately and runs the Python service as an unprivileged user. Compose publishes only `127.0.0.1:8080`; the seeded fixture ports stay on container loopback. Its root filesystem is read-only, Linux capabilities are dropped, privilege escalation is disabled and SQLite data uses a dedicated volume.

Docker is not installed on the local verification host. The GitHub Actions release gate therefore performs the actual image build and starts the image with the same read-only, capability-drop and no-new-privileges controls. It must observe the `0.3.0` health response before the workflow can pass.

## Remaining boundary

This release improves a controlled local pilot. It does not add internet-facing tenancy, SSO, remote target egress, managed secrets, backups, observability or an independent security assessment. Candidate approval is an audit record, not proof that the inferred policy is correct.
