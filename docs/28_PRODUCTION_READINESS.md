# Production-readiness gates

**Current status: specification and design only. No product gate below has passed yet.** Artifact validation checks the handoff's structure; it does not certify scanner behavior.

| Gate | Local event MVP | Authorized staging pilot | Public/hosted production |
|---|---|---|---|
| Functional evidence | 12 required cases × 3 actual variants; real report persistence | Independent customer fixture and maintained policy | Cross-version regression and supported compatibility matrix |
| Network safety | Local target aliases, budgets, no scope escape | Reviewed remote-target pinning/TLS/egress and written scope | Isolated runners, tenant/job boundary review and abuse controls |
| Credentials | Runtime refs and sentinel redaction tests | Customer-approved secret storage/rotation | Managed secret lifecycle, access audit and isolation |
| Identity/access | One local operator, CSRF/origin | Appropriate customer access controls | SSO/RBAC/tenant authorization and negative tests |
| Reliability | Crash/cancel/cleanup behavior, restart persistence | Backup/restore rehearsal, defined retention | Recovery objectives, monitoring, incident response and tested restores |
| Evidence | Bounded sanitized evidence with hashes | Customer-reviewed data handling and deletion | Enforced retention, access logs, export controls and appropriate contractual terms |
| Deployment | Repeatable local setup, pinned dependencies | Update/rollback documentation and security review | Hardened images, patch process, capacity tests and operational ownership |
| Claims | Tested-scope result, seeded-fixture disclosure | Measured pilot outcomes only | Supported service commitments based on measured capability |

## Proposed SLOs to validate later

For the small local suite: finish within the 120-second budget or produce an explicit incomplete result, persist reports across process restart, and honor cancellation without new test requests after the active request/deadline boundary. These are acceptance targets, not hosted uptime promises.

A future pilot may choose recovery point/time objectives based on customer needs; no arbitrary 99.99% availability claim belongs in the hackathon deck. There is no compliance certification, penetration-test attestation or audited security guarantee from this pack.

## Release evidence checklist

Record application commit, dependency lock hashes, environment, completed tests and failures, actual run IDs, policy/suite/fixture hashes, known unsupported operations and operator instructions. A release owner signs off on any unresolved risk. Never promote a design prototype into production by removing its label.

The sensible two-day promise is **a complete, inspectable local workflow built with production-minded boundaries**. Broader production readiness takes additional implementation, independent usage and review.
