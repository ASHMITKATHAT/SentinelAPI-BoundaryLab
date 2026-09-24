# Production-readiness gates

**Current status: local event MVP gates are implemented and verified; staging and hosted-production gates remain open.** This status is limited to the repository's automated tests and local live run. It is not an external security certification.

| Gate | Local event MVP | Authorized staging pilot | Public/hosted production |
|---|---|---|---|
| Functional evidence | **Passed:** 12 cases × 3 live variants; restart persistence; repair comparison | Independent customer fixture and maintained policy | Cross-version regression and supported compatibility matrix |
| Network safety | **Passed locally:** trusted aliases, loopback CI gate, budgets, no redirects | Reviewed remote pinning/TLS/egress and written scope | Isolated runners, tenant/job boundary review and abuse controls |
| Credentials | **Passed locally:** hashed sessions and redacted persisted evidence | Customer-approved secret storage/rotation | Managed secret lifecycle, access audit and isolation |
| Identity/access | **Passed locally:** one operator, CSRF, Origin and Trusted Host checks | Appropriate customer access controls | SSO/RBAC/tenant authorization and negative tests |
| Reliability | **Passed locally:** crash/cancel/cleanup semantics and restart persistence | Backup/restore rehearsal, defined retention | Recovery objectives, monitoring, incident response and tested restores |
| Evidence | **Passed locally:** bounded sanitized evidence, report escaping and hashes | Customer-reviewed data handling and deletion | Enforced retention, access logs, export controls and contractual terms |
| Deployment | **Passed locally:** lockfile, repeatable setup and CI workflow | Update/rollback documentation and security review | Hardened images, patch process, capacity tests and operational ownership |
| Claims | **Passed:** tested-scope language and seeded-fixture disclosure | Measured pilot outcomes only | Supported service commitments based on measured capability |

## Proposed SLOs to validate later

For the small local suite: finish within the 120-second budget or produce an explicit incomplete result, persist reports across process restart, and honor cancellation without new test requests after the active request/deadline boundary. These are acceptance targets, not hosted uptime promises.

A future pilot may choose recovery point/time objectives based on customer needs; no arbitrary 99.99% availability claim belongs in the hackathon deck. There is no compliance certification, penetration-test attestation or audited security guarantee from this pack.

## Release evidence checklist

Record application commit, dependency lock hashes, environment, completed tests and failures, actual run IDs, policy/suite/fixture hashes, known unsupported operations and operator instructions. A release owner signs off on any unresolved risk. Never promote a design prototype into production by removing its label.

The sensible two-day promise is **a complete, inspectable local workflow built with production-minded boundaries**. Broader production readiness takes additional implementation, independent usage and review.
