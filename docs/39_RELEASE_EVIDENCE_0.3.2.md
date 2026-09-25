# Release evidence — BoundaryLab 0.3.2

Evidence captured on 25 September 2026 from the release candidate in this repository.

## Problem corrected

A browser tab could remain visible after the local service stopped. The next Discovery action then displayed the browser's generic `Failed to fetch` text, which did not tell the operator whether the input, session or server had failed.

Version 0.3.2 adds a persistent Windows launcher with an explicit health wait and connection-aware browser behavior. Network failure, timeout, session expiry, validation rejection and an unexpected proxy response now have separate messages. The interface exposes an offline banner and reconnect action. Mutation requests are not automatically replayed after uncertain network failures.

The login now trims accidental surrounding whitespace, keeps a visible progress panel on screen while the local session is created and explains an incorrect secret as a mismatch with the currently running server. Verification actions expose queue creation, active build names and queued/running state in a persistent progress panel until the worker finishes.

## New release gate

The Compare workspace now accepts an ordered baseline and release candidate. The server uses only persisted, compatible case evidence and returns:

- fixed cases that failed before and pass now;
- preserved cases that pass in both builds;
- regressions that passed before and fail or become inconclusive now;
- unresolved cases that still lack passing evidence;
- a deterministic `ready`, `blocked` or `needs_evidence` decision with reasons.

This answers the mentor and buyer question directly: did the security fix close the declared boundary without breaking legitimate product behavior?

## Mentor walkthrough

The authenticated workspace now opens on a mentor-facing overview instead of dropping directly into a dense run screen. It explains the breach in four plain-language moments, exposes the complete feature inventory and links five working stages in order: Discover, Define, Verify, Compare and Handoff. Every stage carries its own mentor question, the proof to point at and a direct next-step action. Fixture identities are presented as business roles so the security model remains understandable without fictional names.

## Verification gates

| Gate | Result |
|---|---|
| Service tests | 39 passed |
| Frontend TypeScript | Passed |
| Production Vite bundle | Passed; 31 modules transformed |
| Static pack and contract validation | Passed |
| PowerShell launcher syntax | Passed |
| Discovery browser flow | Passed; 10 operations, 5 candidates and 1 disclosed shadow route |
| Release gate browser flow | Passed; 4 fixed, 8 preserved, 0 regressed, 0 unresolved |
| Disconnect and reconnect browser flow | Passed; clear uncertain-mutation message and stale error removed after reconnect |
| Mentor walkthrough | Passed; Overview and all five guided stages navigated at 569 px without horizontal overflow |
| Login recovery | Passed; incorrect secret explained, surrounding whitespace normalized and progress visibly rendered |
| Verification progress | Passed; fixed build shown from queue creation through running state to pass-in-scope completion |
| Worker execution trace | Passed; 6 persisted stages from run acceptance through evidence sealing and scoped verdict |
| Browser console | 0 warnings or errors |
| Git whitespace check | Passed |

Production bundle output after the execution-trace polish: 0.55 kB HTML, 47.21 kB CSS (9.68 kB gzip) and 285.59 kB JavaScript (86.91 kB gzip). The release gate remains scoped to compatible persisted cases and does not certify behavior outside the declared policy.
