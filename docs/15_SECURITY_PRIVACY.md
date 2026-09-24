# Security, authorization and privacy

The scanner is a privileged client; its own mistakes can expose secrets or mutate data. The local MVP supports explicitly configured lab targets and narrowly authorized staging adapters. No public-target scanning is implied by uploading OpenAPI.

## Authorization to test

An approved scope identifies target alias, exact origin, permitted addresses, operations/methods, synthetic fixture namespace, credential references, limits and expiry. The trusted operator records authority to test. UI policy approval cannot expand that network scope. Mutation authorization is required for share/export setup and namespace cleanup. The bundled fixture scope is deliberately preconfigured for the lab.

## Threat model and controls

| Threat | Required control | Verification |
|---|---|---|
| SSRF via spec, redirects or links | Do not fetch `servers`/external refs; alias-only transport; connect-address pinning; no redirects; network egress policy | Remote ref, metadata IP, redirect and DNS-change cases |
| Target degradation | 2 RPS, one in-flight request, bounded requests/deadlines/bodies; immediate stop scheduling on cancel | Target counter and cancellation test |
| Cross-run deletion | Namespaced fixture IDs, separate lab token, deletion ownership check | Attempt deletion of another namespace fails |
| Credential disclosure | Runtime secret registry, no raw header/body persistence, sanitizer before write | Seed unique secret sentinels and search DB/logs/reports |
| Data overcollection | Synthetic canary fields, allowlisted pointers, stream cap and content-type checks | Large/binary response is bounded and inconclusive |
| Malicious policy | Strict schema and typed scenario allowlist; no arbitrary code/templates/commands | Unknown operation and script payload rejected |
| Browser injection | Escaped request/model content, no dangerous HTML; restrictive CSP | Script-looking spec descriptions display as text |
| Control API misuse | Operator session, Origin/CSRF controls, loopback binding, no permissive CORS | Unauthorized and cross-origin calls rejected |
| False “fixed” result | Positive controls, build fingerprints, complete case denominators | Owner-only patch cannot pass release assessment |

Private/loopback destinations are only allowed for the exact configured lab aliases. Do not implement a blanket private-network bypass. The local control API itself is excluded from target scope. All HTTP requests, including fixture administration and polls, pass through authorized transport rules.

## Evidence lifecycle

Never persist complete credentials, cookies, bearer URLs or arbitrary response bodies. Store only allowed data needed for the claim. Reports use synthetic names and canary digests. A sanitized request's replay uses named environment placeholders, not pasted secrets. Evidence outside the web root is served by authorized opaque artifact IDs with safe content disposition.

Use local OS/container permissions and a customer-owned volume; at-rest disk encryption is an environment requirement for real pilots and is not implemented merely by hashing evidence. A SHA-256 manifest detects changed bytes but is not a signature, trusted timestamp or compliance certificate.

Default retention proposal is 7-day evidence/30-day metadata with explicit pin/delete. No external telemetry is enabled by default. Optional AI gets redacted facts only, with a separately selected provider configuration. For real pilots, verify applicable customer contracts, privacy obligations, retention and provider terms; this pack makes no legal-compliance certification.

## Release restrictions

Expose only localhost in the event. Before any remote/shared deployment: TLS, stronger identity, tenant isolation, secret rotation, independent review, restoration testing and incident handling must pass. See [production gates](28_PRODUCTION_READINESS.md). The objective is professional engineering discipline, not an unsupported two-day production-ready label.
