# Mentor review pack

## What to bring

Before implementation: this pack, [interactive design](../design/boundarylab-prototype.html), [PRD](06_PRODUCT_PRD.md), [competitor matrix](04_MARKET_AND_EXISTING_SOLUTIONS.md), [two-day scope](17_IMPLEMENTATION_PHASES.md) and [business model](26_BUSINESS_MODEL.md). Label them specifications/prototypes.

After implementation: real app on laptop, three actual run reports, build/commit identifier, policy and fixture hashes, measured request/duration counts, acceptance results, one failed-context example and a labelled recorded fallback. Do not fill missing measured fields with planned numbers.

## First 10-minute mentor session

| Minute | Topic | Concrete output wanted |
|---|---|---|
| 0–2 | Permission timeline and customer | Confirm whether the pain is intelligible and relevant |
| 2–5 | Show live evidence or clearly labelled design | Challenge the business policy, positive controls and test scope |
| 5–7 | Compare close alternatives | Identify whether our workflow advantage is meaningful enough |
| 7–9 | Two-day scope and business | Identify one feature to cut and one buyer assumption to test |
| 9–10 | Record decisions | Named action, owner and acceptance condition |

## Questions worth asking

1. Does your rubric reward a narrow falsifiable workflow or wider vulnerability-class coverage more strongly?
2. Is the active-collaborator control enough to demonstrate a correct repair, or is another business invariant essential?
3. Would a SaaS engineering lead own this purchase, or is a consultant/AppSec team the better first buyer?
4. Which closest existing tool should we benchmark for this exact scenario?
5. What evidence would make the local MVP suitable for an authorized staging pilot?

## Decision log template

`Date/time | mentor role | observation | fact or opinion | decision | owner | due time | evidence needed`.

Keep feedback tied to the problem. “Add blockchain/agents/a mobile app” is not automatically a requirement. Ask what user decision or judged criterion it improves, then trade it against a named P0 task. Policy/safety corrections outrank visual flourishes.

## Submission contents

Application source and lockfiles; clear run instructions; real screenshot/video; actual evaluation report; scope/limitations; architecture; business hypothesis; source links; team contributions. The documentation ZIP contains the design/specification stage only. Add implementation artifacts later with their true completion status.
