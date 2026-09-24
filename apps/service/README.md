# BoundaryLab service and workbench

This package contains the working BoundaryLab local system: three independent synthetic invoice API modes, a deterministic 12-case authorization lifecycle runner, bounded transport, evidence minimization, SQLite persistence, a single safe worker, passive API discovery, remediation analysis, control APIs and report generation. The compiled React client in `apps/web/dist` is served by the same origin.

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

## Passive discovery and shadow-route evidence

Use the **Discovery** screen to import OpenAPI 3.x JSON and an optional HAR export. The analyzer stores derived operation metadata only. HAR headers, cookies, query strings and bodies are discarded. It reports observed method/path templates absent from the contract and proposes review-required ownership invariants for resource-ID operations. It sends no active traffic and does not describe an unobserved route as a zombie API.

Each candidate can be approved or rejected only with a written rationale. BoundaryLab appends the decision to a durable ledger together with the reviewer, timestamp and SHA-256 of the exact candidate snapshot. A later decision adds another record instead of rewriting history. Approval is governance evidence; active execution still requires a reviewed target adapter.

## Container profile

From the repository root, set a 16-character-or-longer secret and run `docker compose up --build`. The image compiles the React client in a Node build stage, installs the Python service in a slim runtime stage and runs as an unprivileged user. Compose publishes only `127.0.0.1:8080`; fixture ports remain internal to the process. The root filesystem is read-only, `/tmp` is a restricted tmpfs and `/data` is the only durable volume.

## Remediation modes

Every completed run supports deterministic root-cause triage. To enable the optional model path, set `OPENAI_API_KEY`; optionally set `BOUNDARYLAB_AI_MODEL`. The model receives only failed-case summaries, uses a strict JSON schema, has no tools, cannot start runs and cannot affect verdicts. If the provider is unavailable or its response fails validation, the API fails closed and deterministic triage still works.

## CI gate

Start a trusted local adapter, then run:

```powershell
& '.\.venv\Scripts\python.exe' -m boundarylab.cli gate `
  --target http://127.0.0.1:9013 `
  --alias ci-fixed `
  --fail-on violation,inconclusive,execution_error
```

Exit code `1` blocks the build when a selected condition is present. Remote origins are rejected because the local runner does not yet implement DNS pinning and isolated egress. `.github/workflows/boundarylab-ci.yml` exercises the fixed build with real localhost sockets.

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
