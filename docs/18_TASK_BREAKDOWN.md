# Implementation backlog and estimates

Estimates are focused person-hours for two developers, excluding dependency downloads. Dependencies identify work that cannot safely be parallelized. A task is done only with the stated evidence.

| ID | Owner | Hours | Depends | Done evidence |
|---|---|---:|---|---|
| T01 | Both | 2 | — | Contracts and policy reviewed; local toolchain starts |
| T02 | A | 3 | T01 | Independent fixture API, namespace factory and three disclosed build variants |
| T03 | B | 2 | T01 | DB migrations, operator session and typed control API skeleton |
| T04 | A | 3 | T02 | All target HTTP through scoped transport; budgets and redaction verified |
| T05 | B | 2 | T03 | Import support summary, policy validation/approval and run creation |
| T06 | A | 4 | T04 | BOLA, field and lifecycle assertions produce real evidence; positive controls gate conclusions |
| T07 | B | 3 | T05 | Persisted worker queue/events and terminal states integrated with runner |
| T08 | B | 3 | T06,T07 | Run table, timeline and evidence drawer bound to actual API |
| T09 | A | 2 | T06,T07 | Owner-only/correct behavior comparison and failure semantics |
| T10 | B | 2 | T08,T09 | HTML/JSON report and compatible-run comparison |
| T11 | A | 3 | T04,T07,T09 | Adversarial scope, crash, secret and cleanup cases |
| T12 | B | 2 | T10 | Fresh startup, keyboard/mobile and restart/report checks |
| T13 | Both | 3 | T11,T12 | Live rehearsal, recorded actual fallback, measured results and pitch |
| T14 | Both | 2 | T13 | Fix only discovered critical integration defects |
| Total | | 36 | | Remaining planned capacity ~4 hours |

The worker queue has a shared interface agreed in T01 so T06 and T07 can progress independently. Pair for the first complete run; avoid finishing all backend and frontend separately before integrating.

## Work tickets ready to copy

**Fixture:** expose the operation IDs in the bundled target contract. Keep scanner and fixture assertion code independent. Use generated subject/object IDs under a namespace and report build ID. Demonstrate that switching the actual fixture implementation changes HTTP behavior.

**Runner:** accept immutable run input and callbacks for evidence/state persistence. No direct UI assumptions. Return case results even on partial failure. Every request has identity/operation metadata; cleanup cannot bypass budgets.

**Comparison:** reject incompatible hashes server-side. Include both security and functional outcomes. An owner-only run has failed active-access controls and incomplete dependent cases; it cannot be represented as “all leaks fixed” without that qualification.

**Reports:** provide an executive explanation and technical evidence. Escape all imported strings. Include report-generation version and hashes; credentials are placeholders. Link to local evidence by opaque IDs or embed already-sanitized data.

**Evaluation:** run the committed case manifest against actual implementations; export observed values alongside expected values. Expected fixtures are a benchmark, never the data source for product findings.

## Definition of done

Application behavior implemented, relevant tests passing, no unhandled errors in the main flow, user-visible failure state, contract matches implementation, and demo uses current build. Screenshots, mock JSON and documentation alone do not close implementation tickets.
