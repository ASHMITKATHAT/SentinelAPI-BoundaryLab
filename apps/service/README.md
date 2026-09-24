# BoundaryLab service — Developer 1 vertical slice

This directory contains the first implemented security core: three independent synthetic invoice API modes, a deterministic 12-case authorization lifecycle runner, bounded operation transport, evidence minimization and tests.

It is not yet the full product. The current integration uses HTTPX's ASGI transport in one process. It exercises real ASGI HTTP requests and independent server behavior without a live socket. Fixed-origin network/DNS pinning, persistence, the control API, containers and UI integration remain to be implemented before the full MVP claim in the root documentation.

## Setup on Windows PowerShell

From the repository root:

```powershell
& '<python-3.12-path>' -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install -e '.\apps\service[dev]'
```

Run the meaningful suite. This workspace currently disables pytest's cache plugin because it hangs at shutdown on the event filesystem; test collection and results are unaffected.

```powershell
Set-Location apps/service
& '..\..\.venv\Scripts\python.exe' -m pytest -q -p no:cacheprovider
```

Run the three-variant development matrix:

```powershell
& '..\..\.venv\Scripts\python.exe' -m boundarylab.cli matrix --fast
```

`--fast` shortens the policy timing for developer feedback and clearly labels the output as a local ASGI fixture matrix. Omit it to execute the documented 2,000 ms grace plus 200 ms probe margin, still against the in-process fixture.

## Implemented invariants

- Vulnerable fixture produces 8 pass / 4 security violations.
- Owner-only repair produces 7 pass / 2 functional regressions / 3 inconclusive dependent cases.
- Correct repair produces 12 pass and `pass_in_scope`.
- An unavailable active collaborator flow cannot become a revocation pass.
- Unknown operations are rejected before a request; the main request budget preserves cleanup capacity.
- Stored evidence redacts bearer authorization and allowlists response fields.
- Response bodies are streamed with a decoded-size limit.

The scanner does not use fixture variant names or the expected-results JSON to decide case outcomes.
