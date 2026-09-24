# Release evidence — BoundaryLab 0.3.1

Evidence captured on 25 September 2026 from the release candidate in this repository.

## Change under test

Version 0.3.1 separates the disclosed three-build lab from real-target operation. Default startup has no active target. A reviewed registry can bind an OpenAPI `GET` operation, fixed numeric-loopback origin, environment-backed identities, resource proof and forbidden fields without exposing those runtime values to the browser.

## Automated verification

| Gate | Result |
|---|---|
| Service tests | 37 passed |
| Frontend TypeScript | Passed |
| Production Vite bundle | Passed; 30 modules transformed |
| Static pack/contract validation | Passed; 9 JSON artifacts, 3 OpenAPI documents, 30 evaluation cases |
| Git whitespace check | Passed |

Production bundle output: 0.55 kB HTML, 33.17 kB CSS (7.37 kB gzip) and 267.14 kB JavaScript (81.60 kB gzip).

## Real-adapter end-to-end proof

A separate loopback staging process and the BoundaryLab control process ran on independent sockets. The reviewed registry bound `GET /v1/orders/{resource_id}` to one allowed and one denied identity.

Observed result:

- allowed identity: HTTP 200 with in-memory marker match;
- denied identity: HTTP 404 without marker;
- assessment: 2 pass, 0 violations, 0 inconclusive, `pass_in_scope`;
- persisted request path: reviewed template only;
- persisted Authorization header: `<REDACTED>`;
- persisted proof: `<MATCHED_PROTECTED_MARKER>`;
- browser console: no warning or error entries.

This was a controlled QA target that exercised the real adapter over HTTP. It is not a customer system or an independent vulnerability discovery.

## Explicit lab proof

Browser QA queued the full three-build matrix from the production bundle:

| Build | Result |
|---|---|
| Vulnerable | 8 pass, 4 violations, blocked |
| Owner-only repair | 7 pass, 2 violations, 3 inconclusive, blocked |
| Correct repair | 12 pass, 0 violations, 0 inconclusive, pass in scope |

Evidence drawer, deterministic remediation, compatible-run comparison and JSON artifact generation all completed through the UI. Browser console inspection returned no warnings or errors.

## Safety evidence

- Real registries accept only numeric loopback HTTP(S) origins and OpenAPI-matching `GET` operations.
- Resource path values are percent-encoded before request construction.
- Missing environment references reject run creation.
- Marker values, bearer tokens, resource IDs and configured restricted-field values are absent from persisted real-probe reports.
- Redirects, proxy environment variables, arbitrary operations and browser-supplied target values remain blocked.
- Results use `pass_in_scope`; reports adapt their scope statement and case denominator to the actual policy.

## Remaining production boundary

The release is suitable for an authorized local/staging pilot. It is not an internet-facing multi-tenant service. Hosted deployment still requires SSO/RBAC, managed secrets, Postgres/backups, isolated runners with DNS/IP pinning and egress policy, observability, load/DR testing and independent security review. Automated mutation of an external grant/revoke/background-job lifecycle still requires a product-specific setup and cleanup adapter.
