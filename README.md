# SentinelAPI BoundaryLab — working AmiHacks system

**PS3 is locked by the team. Built for 1–2 developers and a two-day competition sprint.**

**Status: the complete local vertical slice is implemented and tested.** It runs a React workbench, a FastAPI control plane, a durable SQLite queue and three independent HTTP fixture builds. It produces redacted evidence, compares repairs and exports mentor-ready HTML or JSON artifacts. Market sizes, performance targets and prices in the strategy documents remain hypotheses until externally validated.

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
& '.\.venv\Scripts\python.exe' -m boundarylab.devserver
```

Open `http://127.0.0.1:8080` and enter the bootstrap secret printed by the server. Click **Queue three-build proof**, then show the live evidence, policy, repair comparison and report handoff screens. Runtime state survives a browser refresh and service restart in `var/boundarylab.db`.

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
- Persisted deterministic remediation with an optional, explicitly invoked Structured Outputs model path. AI never controls execution or changes a verdict.
- A loopback-only CI gate with configurable failure conditions and a GitHub Actions workflow that runs the fixed build through real sockets.

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
| Working system status | [32 implementation status](docs/32_IMPLEMENTATION_STATUS.md), [service runbook](apps/service/README.md) |

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

The application imports the bundled contract, runs real HTTP requests against seeded targets, persists redacted evidence, compares actual runs and exports reports. Changing a target response changes the verdict. The working UI never substitutes the prototype's example evidence.

The CLI gate is intentionally limited to loopback targets. A reviewed deployment adapter is required before remote active testing:

```powershell
& '.\.venv\Scripts\python.exe' -m boundarylab.cli gate `
  --target http://127.0.0.1:9013 `
  --fail-on violation,inconclusive,execution_error
```

Optional AI remediation uses the Responses API only when `OPENAI_API_KEY` is present. Set `BOUNDARYLAB_AI_MODEL` to choose an approved model. Failed-case summaries are sent only after the operator clicks the AI action; deterministic triage remains available offline.

## Production boundary

This is a production-minded **local, single-operator workbench**, suitable for a controlled mentor demonstration. An internet-facing or multi-tenant deployment still requires TLS/SSO, Postgres, isolated runner processes, DNS/IP pinning for remote targets, secrets management, backups, observability, load tests and an independent security review. The UI calls successful results “Pass in scope”; it does not make a broad security certification claim.
