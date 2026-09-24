# BoundaryLab service and workbench

This package contains the working BoundaryLab local system: three independent synthetic invoice API modes, a deterministic 12-case authorization lifecycle runner, bounded transport, evidence minimization, SQLite persistence, a single safe worker, control APIs and report generation. The compiled React client in `apps/web/dist` is served by the same origin.

The developer matrix command uses in-process ASGI targets for fast tests. The mentor demo command starts four actual localhost sockets: the control plane on port 8080 and one disclosed fixture build on each of ports 9011–9013.

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

## Start the full workbench

Build the frontend once from the repository root:

```powershell
Push-Location apps/web
npm ci
npm run build
Pop-Location
& '.\.venv\Scripts\python.exe' -m boundarylab.devserver
```

The server prints a random bootstrap secret. Open `http://127.0.0.1:8080`, authenticate, and queue the three-build proof. To use a stable secret and isolated demo database during rehearsal:

```powershell
& '.\.venv\Scripts\python.exe' -m boundarylab.devserver `
  --bootstrap-secret 'mentor-demo-boundary-2026' `
  --data-dir '.\var\rehearsal'
```

The demo binds only to `127.0.0.1`. Do not expose this development launcher directly to a public network.

## Implemented invariants

- Vulnerable fixture produces 8 pass / 4 security violations.
- Owner-only repair produces 7 pass / 2 functional regressions / 3 inconclusive dependent cases.
- Correct repair produces 12 pass and `pass_in_scope`.
- An unavailable active collaborator flow cannot become a revocation pass.
- Unknown operations are rejected before a request; the main request budget preserves cleanup capacity.
- Stored evidence redacts bearer authorization and allowlists response fields.
- Response bodies are streamed with a decoded-size limit.
- Runs and generated artifacts survive restarts; an interrupted active run is explicitly marked incomplete.
- Only server-configured target aliases can be queued through the control API.
- State-changing calls require the session's CSRF token and an approved Origin.
- HTML reports escape target-derived content and downloads carry a restrictive Content Security Policy.

The scanner does not use fixture variant names or the expected-results JSON to decide case outcomes. The hosted-production gaps are tracked in `docs/32_IMPLEMENTATION_STATUS.md` and `docs/28_PRODUCTION_READINESS.md`.
