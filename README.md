# SentinelAPI BoundaryLab — AmiHacks build pack

**PS3 is locked by the team. Prepared 24 September 2026 for 1–2 developers and a two-day build.**

**Status: researched specifications, contracts, fixtures and an interactive design prototype. The scanner application has not been implemented or tested.** Proposed performance numbers and prices are targets or hypotheses, not achieved results. The prototype uses synthetic evidence.

BoundaryLab asks: **after access is revoked, can a user still retrieve a previously queued export—and does the fix preserve legitimate access?** It combines ordinary object/field authorization checks with one complete permission-lifecycle test. The product name is provisional; trademark availability has not been checked.

## Start here

1. Read the [master brief](docs/29_PROJECT_MASTER_BRIEF.md) and [winning strategy](docs/05_WINNING_STRATEGY.md).
2. Build against the [PRD](docs/06_PRODUCT_PRD.md), [TRD](docs/07_TECHNICAL_TRD.md), [architecture](docs/08_SYSTEM_ARCHITECTURE.md) and [contracts](docs/13_API_CONTRACTS.md).
3. Open [the interactive UI prototype](design/boundarylab-prototype.html) in a browser; read the [UI/UX specification](docs/10_UI_UX_DESIGN.md).
4. Follow the [two-day plan](docs/17_IMPLEMENTATION_PHASES.md) and [task breakdown](docs/18_TASK_BREAKDOWN.md).
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

`docs/HACKATHON_SELECTION.md` and `docs/AMIHACKS_MARKET_AND_BUSINESS_ANALYSIS.md` preserve earlier research. Their earlier PS1 selection is superseded. This pack's team size, PS3 selection and scope are authoritative.

## What “working” means at submission

A fresh local setup starts the actual application, imports the bundled OpenAPI JSON, checks identity/fixture preconditions, runs real HTTP requests against the seeded targets, persists redacted evidence, compares actual runs and exports a report. Restarting the application must preserve reports. Changing a target response must change the result. No button may silently substitute the design prototype's example evidence.

Two developers target this complete local MVP. A solo developer targets the same narrow security workflow with simpler forms and fewer report formats. Hosted SaaS, automatic patching, arbitrary-target pentesting, billing and broad protocol support are later work. See the explicit production gates before calling the product production ready.
