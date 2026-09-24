# Two-day implementation plan

Assumption: **1–2 developers**, 48 elapsed hours, approximately **20 focused hours per person**, with sleep, meals and contingency. The two-person plan is about 40 person-hours, not 96 continuous coding hours. If tooling or experience differs, gates take priority over extra features.

## Two-developer route

| Elapsed window | Developer A: engine/fixture | Developer B: service/UI | Gate |
|---|---|---|---|
| H0–H2 | Lock policy, three target variants, operation IDs | Lock contracts, wire API types and minimal screens | Same scenario and payload names |
| H2–H8 | Fixture factory, auth, preview and export variants; minimal runner | SQLite models, import/approval/run endpoints, raw evidence page | One real policy violation through UI |
| H8–H12 | Positive controls, timing, redaction and budgets | Run states, case table, timeline and persistence | Full vulnerable lifecycle, no fake evidence |
| H12–H24 | Rest; one reserved joint checkpoint | Rest; fix only blocking integration issues | Stable reproducible baseline |
| H24–H30 | Wrong/correct fix cases, scope and failure tests | Comparison, HTML/JSON export and cleanup visibility | Three actual runs with honest outcomes |
| H30–H36 | Crash, token, deadline, secret and transport checks | Responsive/keyboard pass, fresh-install smoke, report copy | Required acceptance evidence captured |
| H36–H42 | Contingency and optional CLI if P0 green | Deck/report rehearsal and local recording | Feature freeze; no new architecture |
| H42–H48 | Rest, final smoke and delivery buffer | Rest, final smoke and pitch | Fresh run on event laptop |

Allocate focused work within these elapsed windows rather than working continuously. [Task estimates](18_TASK_BREAKDOWN.md) total 36 person-hours with about 4 person-hours of contingency for two developers.

## Solo route: 20 focused hours

Use a single-page React interface, one project, seeded trusted target aliases, JSON policy editor plus human-readable preview, polling instead of streaming, and HTML/JSON only. Preserve all P0 behavior, but build the smallest expression of each requirement.

| Work | Focused hours |
|---|---:|
| Bootstrap + target fixture with variants | 3.0 |
| Deterministic scenario, controls and transport limits | 5.0 |
| SQLite state, minimal control API and policy approval | 3.0 |
| Single-page run/evidence/compare interface | 3.0 |
| Report/export and restart persistence | 1.5 |
| Failure/security smoke and evaluation recording | 2.5 |
| Pitch/rehearsal and buffer | 2.0 |
| Total | 20.0 |

These are aggressive estimates, not a guarantee. If solo H8 does not have one end-to-end real run, keep the primitive UI and cut all P1 and visual refinement. If core safety/identity checks do not pass, remain local-lab-only. Do not remove the safety checks to meet an external-target promise.

## Cut order and stop conditions

Cut AI, quota check, CI wrapper, markdown report, rich policy editing and advanced animations in that order. Do not cut policy approval, positive controls, scope enforcement, evidence redaction, wrong-fix detection or honest incomplete states.

If H30 lacks a reliable temporal scenario, spend the remainder repairing it and present a reduced local prototype honestly. If a requirement is unfinished, mark it in the submission and readiness matrix. The docs describe the intended product; they do not make incomplete functionality exist.
