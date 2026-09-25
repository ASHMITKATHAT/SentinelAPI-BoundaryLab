# SentinelAPI BoundaryLab — working AmiHacks system

**PS3 is locked by the team. Built for 1–2 developers and a two-day competition sprint.**

**Status: the complete local vertical slice and a safe real-staging read adapter are implemented and tested.** The default process starts with no active target. Operators can load a reviewed, environment-backed staging registry, while the three synthetic builds remain an explicit mentor-lab mode. The system produces redacted evidence, compares compatible runs and exports mentor-ready HTML or JSON artifacts. Market sizes, performance targets and prices remain hypotheses until externally validated.

BoundaryLab asks: **after access is revoked, can a user still retrieve a previously queued export—and does the fix preserve legitimate access?** It combines ordinary object/field authorization checks with one complete permission-lifecycle test. The product name is provisional; trademark availability has not been checked.

## Run the mentor demo

Prerequisites: Python 3.12+ and Node.js 20.19+ (or 22.12+).

```powershell
python -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install -e '.\apps\service[dev]'
Push-Location apps/web
npm ci
npm run build
Pop-Location
& '.\tools\start-local.ps1' -LabFixtures
```

Open `http://127.0.0.1:8080` and enter the bootstrap secret printed by the server. The **Start** workspace presents the mentor story and links every working capability into a five-stage walkthrough: Discover, Define, Verify, Compare and Handoff. Follow it in order, run the disclosed lab matrix in Verify, then show the live evidence and scoped release decision. Runtime state survives a browser refresh and service restart in `var/boundarylab.db`.

`start-local.ps1` launches the workbench as a hidden background process, waits for `/api/healthz`, prints the one-time login secret and records the process/log paths under `var`. This avoids leaving a stale browser shell that later reports a vague network failure.

The expected disclosed demo matrix is:

| Build | Pass | Violations | Inconclusive | Assessment |
|---|---:|---:|---:|---|
| Vulnerable | 8 | 4 | 0 | Blocked |
| Owner-only repair | 7 | 2 | 3 | Blocked |
| Correct repair | 12 | 0 | 0 | Pass in scope |

The owner-only build matters: it closes access too aggressively and breaks legitimate collaborator behavior. BoundaryLab therefore demonstrates both security and product-preservation checks.

## What is implemented

- A declared 12-case invoice sharing policy, including post-revocation export retrieval.
- Real localhost HTTP traffic to three separately bound target services; verdicts do not read fixture variant names.
- A trusted target registry, redirect blocking, one in-flight request, rate/request/response limits and cleanup reserve.
- Opaque hashed sessions, strict cookies, CSRF and Origin checks, Trusted Host enforcement and security headers.
- A durable SQLite WAL queue, restart recovery, cancellation, run events, reports and artifact hashes.
- Evidence redaction and response-field allowlisting before persistence.
- A responsive React interface using navy blue, red shades, grey and white, with accessible labels and reduced-motion handling.
- Passive OpenAPI 3.x and HAR analysis that finds resource-ID operations, proposes dual-identity policy candidates and reports traffic routes missing from the contract.
- A real GitHub repository importer for OpenAPI JSON. Public repositories work without browser credentials; private access uses an optional server-side `BOUNDARYLAB_GITHUB_TOKEN` that is never returned to or stored by the web client.
- An append-only policy decision ledger that records approve/reject rationale, reviewer, timestamp and an immutable hash of the exact candidate snapshot.
- Persisted deterministic remediation with an optional, explicitly invoked Structured Outputs model path. AI never controls execution or changes a verdict.
- A loopback-only CI gate with configurable failure conditions and a GitHub Actions workflow that runs the fixed build through real sockets.
- A fail-closed real-target mode for a reviewed OpenAPI-bound `GET`, multiple environment-backed identities, marker proof and identity-specific forbidden fields.
- A deterministic release gate that compares an ordered baseline and candidate, then explains fixed controls, preserved product behavior, regressions and missing evidence.
- Connection-aware UI errors, session-expiry recovery, request timeouts, explicit login/run progress and a persistent local launcher with a health check.
- A mentor-first product overview and persistent stage guide that make discovery, policy, runtime proof, remediation, release comparison, reports, CI and real-target safeguards visible without relying on a separate explanation.
- A database-backed execution trace that shows the real worker accepting a run, verifying target scope, executing cases, sealing sanitized evidence and producing the verdict.

## Run the hardened local container

The default container starts the control plane with no active target. It runs as a non-root user; the Compose profile drops Linux capabilities, uses a read-only root filesystem and persists SQLite state in a named volume. This fail-closed default prevents a packaged deployment from silently presenting fixture results as real scans.

```powershell
$env:BOUNDARYLAB_BOOTSTRAP_SECRET = 'replace-with-a-16-plus-character-secret'
docker compose up --build
```

Open `http://127.0.0.1:8080`. Configure an active staging adapter using the [real-target runbook](docs/37_REAL_TARGET_RUNBOOK.md), or use the explicit local lab command above for the mentor matrix. The container profile improves repeatability for a local pilot; it does not turn the application into a public multi-tenant service.

See [implementation status](docs/32_IMPLEMENTATION_STATUS.md) for verified behavior and the remaining hosted-production gates.

## Start with the product pack

1. Read the [master brief](docs/29_PROJECT_MASTER_BRIEF.md) and [winning strategy](docs/05_WINNING_STRATEGY.md).
2. Build against the [PRD](docs/06_PRODUCT_PRD.md), [TRD](docs/07_TECHNICAL_TRD.md), [architecture](docs/08_SYSTEM_ARCHITECTURE.md) and [contracts](docs/13_API_CONTRACTS.md).
3. Review the [UI/UX specification](docs/10_UI_UX_DESIGN.md); the older [interactive prototype](design/boundarylab-prototype.html) remains a clearly labelled synthetic design reference.
4. Review the [two-day plan](docs/17_IMPLEMENTATION_PHASES.md), [task breakdown](docs/18_TASK_BREAKDOWN.md) and [implemented system](docs/32_IMPLEMENTATION_STATUS.md).
5. Rehearse the [live demo](docs/20_DEMO_PLAN.md), [pitch](docs/21_PITCH_STRATEGY.md), [judge questions](docs/22_JUDGE_QA.md) and [mentor pack](docs/27_MENTOR_REVIEW_PACK.md).

## Product decision

The memorable demonstration has three disclosed target implementations: vulnerable, an overly restrictive owner-only fix, and a correct fix. The same reviewed policy and test suite must identify the leak, reject the broken fix and accept the correct fix **only within the tested scope**. Build IDs identify which target actually answered.

We do not claim that multi-user tests, evidence, CI, authorization matrices or temporal revocation are new inventions. Current competitors overlap substantially. Our differentiation hypothesis is a compact, usable workflow for maintaining a business permission promise through asynchronous work and proving that a repair preserves it.

## Contents

| Area | Files |
|---|---|
| Research and product positioning | [01 research](docs/01_PROBLEM_RESEARCH.md), [02 track comparison](docs/02_PROBLEM_STATEMENT_COMPARISON.md), [03 saturation](docs/03_COMPETITOR_SATURATION_ANALYSIS.md), [04 competitors](docs/04_MARKET_AND_EXISTING_SOLUTIONS.md), [25 sources](docs/25_RESEARCH_SOURCES.md) |
| Product and implementation | [06 PRD](docs/06_PRODUCT_PRD.md), [07 TRD](docs/07_TECHNICAL_TRD.md), [09 structure](docs/09_PROJECT_STRUCTURE.md), [11 flows](docs/11_USER_FLOWS.md), [12 model](docs/12_DATA_MODEL.md), [14 AI](docs/14_AI_ML_DESIGN.md) |
| Reliability | [15 security](docs/15_SECURITY_PRIVACY.md), [16 failure handling](docs/16_FAILURE_AND_FALLBACK_STRATEGY.md), [19 testing](docs/19_TESTING_STRATEGY.md), [23 risks](docs/23_RISK_REGISTER.md), [28 readiness](docs/28_PRODUCTION_READINESS.md) |
| Business | [26 business model](docs/26_BUSINESS_MODEL.md), [24 roadmap](docs/24_FUTURE_ROADMAP.md), [00 executive summary](docs/00_EXECUTIVE_SUMMARY.md) |
| Machine-readable handoff | [control API](contracts/control-api.openapi.json), [demo API](contracts/demo-api.openapi.json), [policy schema](contracts/policy.schema.json), [example policy](examples/invoice-policy.json), [fixture manifest](examples/fixture-manifest.json), [evaluation cases](examples/evaluation-cases.json), [design tokens](design/tokens.json) |
| Implementation accountability | [30 requirement traceability](docs/30_REQUIREMENTS_TRACEABILITY.md), [artifact checks](docs/31_ARTIFACT_VALIDATION.md) |
| Working system status | [32 implementation status](docs/32_IMPLEMENTATION_STATUS.md), [real-target runbook](docs/37_REAL_TARGET_RUNBOOK.md), [0.3.2 release evidence](docs/39_RELEASE_EVIDENCE_0.3.2.md), [service runbook](apps/service/README.md) |

`docs/HACKATHON_SELECTION.md` and `docs/AMIHACKS_MARKET_AND_BUSINESS_ANALYSIS.md` preserve earlier research. Their earlier PS1 selection is superseded. This pack's team size, PS3 selection and scope are authoritative.

## Verification

```powershell
Set-Location apps/service
& '..\..\.venv\Scripts\python.exe' -m pytest -q -p no:cacheprovider
Set-Location ../web
npm run build
Set-Location ../..
& '.\.venv\Scripts\python.exe' tools/validate_pack.py
```

The application starts fail-closed with no active target. In explicit lab mode it runs real HTTP requests against disclosed seeded targets; with a reviewed registry it runs fixed read-only probes against an authorized loopback staging adapter. Both modes persist redacted evidence, compare actual runs and export reports. Changing a target response changes the verdict. The working UI never substitutes the prototype's example evidence.

The CLI gate is intentionally limited to loopback targets. A reviewed deployment adapter is required before remote active testing:

```powershell
& '.\.venv\Scripts\python.exe' -m boundarylab.cli gate `
  --target http://127.0.0.1:9013 `
  --fail-on violation,inconclusive,execution_error
```

Optional AI remediation uses the Responses API only when `OPENAI_API_KEY` is present. Set `BOUNDARYLAB_AI_MODEL` to choose an approved model. Failed-case summaries are sent only after the operator clicks the AI action; deterministic triage remains available offline.

The Discover page can import an OpenAPI 3.x JSON file from GitHub using `owner/repository`, a branch/ref and a repository-relative path. Public repositories need no token. For a private repository, set `BOUNDARYLAB_GITHUB_TOKEN` in the server environment before startup. The integration calls only `api.github.com`, blocks redirects, caps responses and imported documents, and never accepts a token from the browser. Importing a contract is passive discovery; active staging execution still requires a reviewed target registry as documented in the [real-target runbook](docs/37_REAL_TARGET_RUNBOOK.md).

## Production boundary

This is a production-minded **local, single-operator workbench**, suitable for a controlled mentor demonstration. An internet-facing or multi-tenant deployment still requires TLS/SSO, Postgres, isolated runner processes, DNS/IP pinning for remote targets, secrets management, backups, observability, load tests and an independent security review. The UI calls successful results “Pass in scope”; it does not make a broad security certification claim.

## Team & Contributors

- **Ashmit Kathat** ([@ASHMITKATHAT](https://github.com/ASHMITKATHAT))
- **Abhinav Pandey** ([@abhinavpandey98645-bot](https://github.com/abhinavpandey98645-bot))

