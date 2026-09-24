# Release evidence — BoundaryLab 0.3.2

Evidence captured on 25 September 2026 from the release candidate in this repository.

## Problem corrected

A browser tab could remain visible after the local service stopped. The next Discovery action then displayed the browser's generic `Failed to fetch` text, which did not tell the operator whether the input, session or server had failed.

Version 0.3.2 adds a persistent Windows launcher with an explicit health wait and connection-aware browser behavior. Network failure, timeout, session expiry, validation rejection and an unexpected proxy response now have separate messages. The interface exposes an offline banner and reconnect action. Mutation requests are not automatically replayed after uncertain network failures.

## New release gate

The Compare workspace now accepts an ordered baseline and release candidate. The server uses only persisted, compatible case evidence and returns:

- fixed cases that failed before and pass now;
- preserved cases that pass in both builds;
- regressions that passed before and fail or become inconclusive now;
- unresolved cases that still lack passing evidence;
- a deterministic `ready`, `blocked` or `needs_evidence` decision with reasons.

This answers the mentor and buyer question directly: did the security fix close the declared boundary without breaking legitimate product behavior?

## Verification gates

| Gate | Result |
|---|---|
| Service tests | 38 passed |
| Frontend TypeScript | Passed |
| Production Vite bundle | Passed; 31 modules transformed |
| Static pack and contract validation | Passed |
| PowerShell launcher syntax | Passed |
| Discovery browser flow | Passed; 10 operations, 5 candidates and 1 disclosed shadow route |
| Release gate browser flow | Passed; 4 fixed, 8 preserved, 0 regressed, 0 unresolved |
| Disconnect and reconnect browser flow | Passed; clear uncertain-mutation message and stale error removed after reconnect |
| Browser console | 0 warnings or errors |
| Git whitespace check | Passed |

Production bundle output: 0.55 kB HTML, 35.96 kB CSS (7.82 kB gzip) and 271.69 kB JavaScript (83.02 kB gzip). The release gate remains scoped to compatible persisted cases and does not certify behavior outside the declared policy.
