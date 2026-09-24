# AmiHacks selection for competing against 250 teams

> **SUPERSEDED — historical recommendation.** The team has now explicitly chosen **PS3 SentinelAPI** with **1–2 developers and two days**. Use the [current master brief](29_PROJECT_MASTER_BRIEF.md). The PS1 recommendation below is retained only as decision history.

Decision date: 24 September 2026.

**Select PS1 Surplus to Shelter.** Build a food-rescue coordinator that identifies the smallest permitted operational changes needed to make an otherwise infeasible rescue possible, asks the responsible people to commit, and recomputes the plan from confirmed commitments.

This supersedes the earlier hackathon selection. The earlier report favored PS3 for recurring software revenue. The user's clarified priority is differentiation and a convincing live demonstration against teams with similar AI coding capabilities. Under a general hackathon rubric, PS1 offers the strongest combination of a quickly understood problem, visible human stakes, constrained optimization, and an interactive test of the result. No actual judging weights or intelligence about the other teams is available.

## Core insight

A dispatcher can have enough food and willing recipients yet lack one specific commitment at one specific time. Another driver may add no value if the receiving site closes before the food can arrive. Knowing whom to ask, exactly what to ask for, and whether it changes feasibility is a useful operational decision.

The user-facing question is: **What is the smallest practical change that lets us deliver the remaining food?**

Possible changes are drawn from explicit, bounded offers: a recipient can provide receiving staff for up to 20 extra minutes; an eligible driver can take an additional trip; a verified recipient can accept an additional quantity within actual capacity. The system cannot invent willingness or availability. Food acceptance, handling and safety constraints are never relaxed by the optimizer.

A proposal becomes an available planning resource only after the relevant person confirms it. A feasible plan becomes a completed rescue only after the delivery is acknowledged. These are distinct states.

## Why choose this over the other tracks

| Track | Attractive conventional solution | Reason for this selection |
|---|---|---|
| PS1 food rescue | Matching, routing, notifications, impact reports | A specific operational decision can be explained and challenged in seconds. The additional commitment and resulting outcome are visible to generalist judges. |
| PS2 civic data | Multi-feed map, anomalies, AI summaries | Strong visualization potential, but incident meaning and downstream benefits are difficult to validate using limited or synthetic live data. The demonstration can depend heavily on an authored story. |
| PS3 API security | Authorization tests, attack agents, evidence and CI | Excellent software business candidate. Strong existing tools and readily reproducible testing patterns raise the differentiation bar. A security-focused judging panel might weight it differently. |

These are strategic assessments, not measured win probabilities. The proposed PS1 mechanism remains implementable by another strong team; advantage must come from problem understanding, correct implementation, evaluation and real workflow validation.

## A consistent illustrative demonstration

This scenario is synthetic. Its fixed-route assignments were exhaustively checked in a small analytical script; no production routing system or real rescue was tested.

There are three donation batches, A, B and C, each with 60 labelled portions. Two drivers are available. A and B have simultaneous scheduled pickups at 18:00, with deliveries at 18:18 and 18:20. C becomes available at 18:36 and its specified route delivers at 18:42. Drivers finishing A or B can reposition to C in ten minutes. C's recipient stops receiving at 18:30. All other quantity, eligibility and fixture handling constraints are satisfied; the synthetic delivery deadline for C is 18:55. That deadline is scenario input, not food-safety advice.

| Change to the scenario | Maximum planned portions under these fixed routes | Explanation |
|---|---:|---|
| Existing two drivers and receiving hours | 120 | A and B fit; C arrives after its recipient closes. |
| Add a third driver only | 120 | C is not ready earlier; the receiving-time bottleneck remains. |
| Recipient confirms 12 extra receiving minutes | 180 | One driver can do A, then C; the other does B. |
| One original driver becomes unavailable | 60 | One driver cannot serve the simultaneous A and B trips; C still cannot be received. |
| One driver unavailable, recipient confirms extension | 120 | The remaining driver serves one early batch and C. |
| Replacement driver plus recipient extension confirmed | 180 | Both bottlenecks are resolved. |
| C gains five minutes of travel delay, extension stays at 12 minutes | 120 | The previous proposal is no longer sufficient. |
| C gains five minutes of delay, recipient agrees to 17 extra minutes | 180 | The new receiving window accommodates the changed arrival. |

The counterintuitive moment is that recruiting another driver has zero marginal benefit in the original scenario, while a recipient's time commitment changes feasibility. The main screen shows the reason and the exact request, rather than asking the audience to infer it from moving map markers.

Twelve minutes is the nominal minimum in this deliberately precise example. A production proposal must show buffers and uncertainty; a scenario with a five-minute travel buffer requires 17 minutes. Never imply the calculation guarantees a delivery.

## What the actual engine must do

1. Normalize offers, donation quantities, food eligibility, time windows, locations, recipient capacities and driver availability. Distinguish unknown values from zero capacity.
2. Find the best feasible allocation with the currently confirmed resources, including capacity reservation and pickup-before-delivery constraints.
3. Evaluate approved candidate interventions and small combinations. Compute the additional accepted portions relative to the same solver with no added intervention. Test combinations because two changes can be jointly necessary.
4. Present useful alternatives and their real burden: money, people, extra receiving time and travel. “Smallest” requires an explicit rule, such as meeting a target with the least monetary cost and then the fewest people affected. Do not silently add incompatible units into an arbitrary score.
5. Ask the named role for a specific commitment with an expiry. Keep pending offers out of the confirmed plan.
6. After acceptance, recheck current state and reserve capacity atomically. A stale confirmation cannot double-book a recipient or driver.
7. Track pickup, receipt and exceptions separately from planned results. Replan when facts change; report infeasibility honestly when no permitted intervention works.

For a bounded MVP, a small integer/constraint optimization model plus enumeration of a short list of allowed interventions is sufficient. Claim minimum only within the modeled scope and solved search space. A timeout must display the best found result and its limitations. Existing optimization libraries are appropriate; the project's engineering lies in the operational model, intervention search, commitment workflow and independently checked feasibility.

AI can parse messages such as “I can receive food until 6:45, maximum 40 portions” into proposed structured constraints, subject to confirmation. It can explain already computed evidence. It must not guess physical capacity, food safety, recipient consent or route feasibility.

## Three features that carry the project

- **Bottleneck explanation:** show why a donation cannot currently complete and what resources are actually limiting it.
- **Specific commitment request:** compute an actionable request and quantify its marginal effect under stated assumptions.
- **Live challenge and verification:** let the judge change a driver, time or capacity and watch the result recompute, including a possible honest “no feasible plan.”

Keep donation intake, status tracking and a small supporting map because the problem statement needs the operational workflow. The primary view is the decision and its evidence. Do not spend the core build time on a chatbot, carbon leaderboard, speculative food-quality classifier or unsupported forecasting.

## How to make the demonstration credible

Build a batch of scenarios before tuning presentation: transport bottleneck, receiving-time bottleneck, insufficient capacity, two coupled bottlenecks, no permitted rescue, rejected request and stale confirmation. Keep some scenarios held out from UI tuning. Include cases where an extra driver is the correct answer and where no intervention is needed.

Compare three layers: a documented simple baseline, the same resource-aware solver with current resources, and that solver with explicitly disclosed new commitments. Extra capacity has a cost; it cannot be hidden inside an apparent algorithmic improvement.

Have an independent checker validate every proposed schedule's capacities, order and deadlines. For small instances, compare with enumeration. Measure planned feasible quantity, verified delivery quantity when real trials exist, extra staff/driver minutes, notification count, decision latency and rejection recovery. Report simulation and field observations separately.

Stage sequence: establish the blocked rescue, let the judge propose or select a bounded change, compute the result, let a teammate acting as the recipient accept or decline the specific request, then recompute. Role-play is labelled. A later real pilot can validate operational value; a theatrical demo cannot substitute for that evidence.

Before the event, the team should conduct a few consented workflow walkthroughs with a kitchen, recipient and coordinator. Record anonymized examples of failed pickups and constraints. No outreach has been performed in this task. The validation target is whether this decision actually consumes time or causes failures, and whether the proposed requests are acceptable to staff.

## Novelty and related work

Generic donor-to-recipient matching already appears in hackathon submissions such as [FoodBridge](https://devpost.com/software/foodbridge-oydvkl). Established rescue operations explicitly address closed or non-accepting recipient agencies; see the [Leftovers Foundation FAQ](https://rescuefood.ca/contact/).

The underlying mathematical direction is also established. [AAAI research from 2020](https://ojs.aaai.org/index.php/AAAI/article/view/7051) studies volunteer uncertainty and intervention/notification optimization. [Counterfactual explanations for linear optimization](https://dare.uva.nl/id/2896af4f-1160-4160-9125-fd13e1b79857) includes a World Food Programme case study. The proposed project is an adaptation into an interactive food-rescue commitment workflow, not a claim to invent counterfactual optimization.

For comparison, [Hadrian](https://github.com/praetorian-inc/hadrian) documents existing role-based API authorization testing and verification, strengthening the case that a basic PS3 scanner would need a substantially different advantage.

The practical distinction to validate is the complete path from a blocked plan to a minimal permitted request, a real confirmation and a revalidated delivery plan. This research does not establish that no existing product can implement that path.

## Business continuation

First buyer: a multi-site caterer or institutional kitchen operator working with an existing NGO network. Sell coordination software, operating visibility and useful records; the receiving organizations and beneficiaries need not pay. Charge separately for physical logistics and staffed support.

A subscription or sponsored cluster is a plausible hypothesis, but only a paid pilot can establish willingness to pay. Measure failed accepted pickups, coordinator time and full operating cost. The previously proposed ₹3,000 per donor site per month remains an experiment, not a validated price. No per-portion success fee should incentivize inflated counts or unnecessary food production.

The pitch: **We identify the specific commitment that can make a blocked food rescue feasible, then coordinate and verify it.**
