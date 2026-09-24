# Project master brief — the source of truth

## Locked decisions

- Problem: **PS3 SentinelAPI**, selected by the team, superseding earlier PS1 recommendations.
- Team/time: **1–2 developers, two days**; assume about 20 focused hours per person.
- Product: **SentinelAPI BoundaryLab**, provisional name.
- Buyer hypothesis: SaaS CTO/engineering lead maintaining sharing and export permissions.
- Core promise: test a declared access policy through revocation and asynchronous export retrieval; verify that a repair preserves legitimate access.
- MVP: local single-operator workbench, one REST/JSON adapter, OpenAPI 3.1 JSON, three disclosed fixture implementations.
- Stack: React/TypeScript UI, Python/FastAPI service, SQLite, one worker, bounded HTTP transport.
- AI: optional drafting/explanation, no authority to decide policy, verdicts or network scope.
- Current completion: documentation/contracts/design only; application implementation remains outstanding.

## Canonical demo rules

Alice owns two synthetic invoices in tenant A. Bob belongs to tenant A but owns neither. Mallory belongs to tenant B. An anonymous identity has no credential. Private preview requires ownership. Shared detail/export requires owner or active collaborator. `/internal_bank_ref` is owner-only. A fresh export-content request started more than 2,000 ms after successful revocation acknowledgement must deny the revoked collaborator without exposing its marker; the scanner adds 200 ms timing margin. Owner access remains allowed.

There are three independent seeded defects in the vulnerable fixture: preview BOLA, restricted detail field exposure and stale authorization for a previously queued export. The owner-only implementation removes those exposures but wrongly denies active collaborators. The correct implementation preserves the full policy. Prepared variants are explicitly disclosed.

## Canonical operational limits

200 requests maximum per run (180 main + 20 cleanup reserve), 2 RPS, one in flight, 5-second total request deadline, 120-second overall deadline including 10 seconds cleanup reserve, 64 KiB decoded response body cap, 1 MiB imported spec cap. Queue length 10; one active run globally. Poll export at most 10 times within 20 seconds and the overall budget. Actual measured duration/request counts are not yet available.

## Canonical states

Run: `queued`, `preflight`, `running`, `finalizing`, `completed`, `failed`, `interrupted`, `cancelled`.

Case: `pass`, `violation`, `inconclusive`, `skipped`.

Assessment: `blocked` if any required case violates; otherwise `incomplete` if required coverage or execution is incomplete; otherwise `pass_in_scope`. Keep an incomplete flag even when blocked takes precedence. Findings distinguish `security_violation` and `functional_regression`.

Expected benchmark: 12 core cases per variant; vulnerable 8 pass/4 violation; owner-only 7 pass/2 violation/3 inconclusive; fixed 12 pass. These are expected fixtures, not executed scanner results. Add 18 failure/safety cases during implementation.

## Read in implementation order

[PRD](06_PRODUCT_PRD.md) → [flows](11_USER_FLOWS.md) → [TRD](07_TECHNICAL_TRD.md) → [API](13_API_CONTRACTS.md) → [data model](12_DATA_MODEL.md) → [security](15_SECURITY_PRIVACY.md) → [tests](19_TESTING_STRATEGY.md) → [schedule](17_IMPLEMENTATION_PHASES.md).

Business/presentation: [research](01_PROBLEM_RESEARCH.md) → [competitors](04_MARKET_AND_EXISTING_SOLUTIONS.md) → [business](26_BUSINESS_MODEL.md) → [demo](20_DEMO_PLAN.md) → [judge Q&A](22_JUDGE_QA.md).

## Decisions deliberately deferred

Hosted tenancy, remote arbitrary-target support, payment provider, model/provider, production identity system and broader protocols. Choose these when customer or implementation evidence demands them. This keeps the first product understandable and achievable while preserving a credible business direction.
