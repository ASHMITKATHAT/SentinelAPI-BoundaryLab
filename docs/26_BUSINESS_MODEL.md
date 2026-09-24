# Business model: sell a maintained permission promise

All prices and economics here are **experiments in INR, excluding taxes**, not quotations, revenue, validated demand or investment advice. No outreach, interview, pilot or sale has been performed.

## Customer and purchase trigger

Beachhead: B2B SaaS with multi-tenant records, collaboration and report/export features; approximately 5–30 engineers; a staging API and owner of permission policy. Start with document/reporting/operations products rather than heavily regulated production deployments that require a much larger trust program.

Trigger: a permission incident, enterprise customer asking about tenant isolation, a major sharing/role change, or repeated manual regression work. User is a backend engineer; buyer is a CTO/engineering lead. A security consultant can become a channel partner if the runner makes their repeat assessments easier.

## Offer and pricing experiments

| Offer | Proposed price | Included boundary | Why it may sell |
|---|---:|---|---|
| Bounded design-partner pilot | ₹15,000 once for two weeks | One staging API, up to three agreed workflows, policy workshop, local setup and one review | Buyer pays for a concrete evaluated workflow, not a vague platform promise |
| Team subscription | ₹8,000/month | One application, up to ten maintained workflow definitions, local runner, reports, business-hours support budget | Recurring regression use across releases |
| Growth experiment | ₹25,000/month | Up to three applications, collaboration/history after built, defined onboarding/support | Test only after multi-user controls and demand exist |
| Private deployment | Scoped quotation | Required review, deployment and support commitments | Avoid promising enterprise service levels before capability exists |

Do not charge by number of vulnerabilities found: that rewards noisy results. A workflow/application unit is more aligned with maintained value; execution quotas should primarily control resource abuse. The precise packaging needs customer interviews and commercial testing.

## First 10 customers

1. Identify 30 relevant SaaS teams or consultants through the team's existing network and public technical communities. Prepare a specific demo and one-page offer.
2. Conduct 10 discovery interviews. Ask about a recent change and existing tests before showing features.
3. Invite 3 teams with real staging fixtures into a bounded pilot. Require explicit testing authorization and a named policy owner.
4. Measure setup effort, recurring usage, useful regressions, false/inconclusive results and engineer review time.
5. Ask for paid continuation with actual terms. A compliment, waitlist entry or free trial is not paid demand.

This is a proposed go-to-market plan. It does not authorize this agent to send messages or scan customer APIs.

## Unit economics example

For a hypothetical ₹8,000/month account:

| Monthly cost assumption | Low-touch | High-touch |
|---|---:|---:|
| Hosting/storage/support tooling allocation | ₹500 | ₹1,000 |
| Optional model usage budget | ₹100 | ₹300 |
| Support labor at assumed ₹1,000/hour | ₹1,000 (1 h) | ₹4,000 (4 h) |
| Total direct cost | ₹1,600 | ₹5,300 |
| Contribution before sales, R&D, admin and taxes | ₹6,400 (80%) | ₹2,700 (33.75%) |

The labor assumption drives the model. Customer-run compute does not make support free. Ten retained accounts at ₹8,000 imply ₹80,000 MRR arithmetically, not a forecast. With illustrative fixed monthly costs of ₹100,000, contribution break-even is 16 low-touch accounts or 38 high-touch accounts, ignoring acquisition, churn, taxes and timing. These are sensitivities to validate.

Pilot delivery at 8 labor hours plus ₹1,000 incidental direct cost would cost ₹9,000 under the same labor assumption and leave ₹6,000 contribution. At 20 hours it loses ₹6,000. Track onboarding hours from the first pilot; narrow scope or reprice if the support burden is structurally high.

## Value and ROI without inflated claims

Ask a customer to measure current monthly permission-test and triage hours. Compare with the proposed workflow using the same releases. For illustration only, saving 6 hours at the customer's own ₹2,000/hour internal cost gives ₹12,000 gross time value, before integration/maintenance cost. Do not count hypothetical avoided breaches as guaranteed ROI.

## Defensibility and expansion

Policy/adapter expertise, reliable evidence history and trusted integration can accumulate. Cross-customer data reuse requires permission and careful sanitization; do not assume a free proprietary dataset. Expand from export revocation to role changes or cached reports only after the same customer needs them.

Potential open-core route: publish the runner/schema/benchmark, sell collaboration and maintained workflow support. This makes trust and adoption easier but can reduce software-only differentiation. Decide licence and support economics after pilots; do not assert that all open-source dependencies permit any packaging.

## Kill or pivot criteria

After 10 qualified interviews: fewer than 3 serious pilot offers, no identifiable budget owner, no recurring use case, or existing scripts accepted as sufficient by most teams. During pilots: setup routinely exceeds a day, policy upkeep is abandoned, or users cannot interpret evidence. A useful fallback business could be a specialist testing service or a contribution to an existing tool rather than another SaaS platform.
