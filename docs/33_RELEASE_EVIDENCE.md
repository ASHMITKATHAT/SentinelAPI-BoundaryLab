# Release evidence — BoundaryLab 0.2.0

Evidence captured on 2026-09-24 from the release candidate in this repository.

## Automated verification

| Gate | Command | Result |
|---|---|---|
| Service tests | `python -m pytest apps/service/tests -q` | 29 passed |
| Web type safety | `npm run typecheck` | Passed |
| Production bundle | `npm run build` | Passed; 30 modules transformed |
| Production dependency audit | `npm audit --omit=dev` | 0 vulnerabilities reported |
| Pack and contract validation | `python tools/validate_pack.py` | Passed; 7 JSON artifacts, 2 OpenAPI documents, 30 evaluation cases |
| Whitespace check | `git diff --check` | Passed |
| Secret-pattern scan | repository scan excluding dependencies, build output, runtime data and Git metadata | No recognized private-key or common token pattern found |

The optimized web bundle contains a 0.55 kB HTML entry, 21.27 kB CSS file (5.28 kB gzip) and 253.00 kB JavaScript file (77.68 kB gzip).

## Live execution proof

The same CLI gate used by GitHub Actions ran against independent local HTTP fixture processes, not in-process test doubles.

| Target | Cases | Live HTTP requests | Cleanup | Process result |
|---|---:|---:|---|---|
| Correct policy-preserving repair | 12 pass, 0 violation, 0 inconclusive | 26 | complete | exit 0 |
| Vulnerable baseline | 8 pass, 4 violations, 0 inconclusive | 26 | complete | exit 1 |

The negative result proves that a policy violation blocks the gate. The positive result proves that legitimate owner and collaborator paths still work after the repair.

## Browser verification

The compiled React bundle was served through the FastAPI process and exercised at a 720 × 858 viewport:

- passive analysis of the bundled OpenAPI document plus disclosed HAR traffic found 10 operations, proposed 5 review-required ownership candidates and identified 1 undocumented high-risk route;
- HAR query values, headers, cookies and bodies were not persisted;
- the vulnerable live run showed four violations and generated four reason-specific deterministic root-cause cards, repair steps, regression checks and a framework-neutral patch outline;
- AI remediation stayed disabled because no provider key was configured;
- the discovery and remediation workspaces had no document-level horizontal scrolling after responsive fixes.

## Security controls observed

The running `0.2.0` service returned per-request correlation IDs, a restrictive Content Security Policy on the web shell, and a Permissions Policy that disables camera, microphone and geolocation. Session cookies are HTTP-only and same-site strict; state changes require both the session CSRF token and an approved Origin.

## Release boundary

This evidence supports a production-minded local pilot and mentor demo. It is not evidence for public multi-tenant hosting, a penetration-test attestation, a compliance certification, recovery objectives or an AI quality rate. Remote active execution remains limited to explicitly reviewed adapters; the CLI gate accepts loopback origins only.
