# Saturation and defensible differentiation

Research cutoff: 24 September 2026. See the [vendor matrix](04_MARKET_AND_EXISTING_SOLUTIONS.md) and [source register](25_RESEARCH_SOURCES.md).

| Feature claim | Saturation assessment | Decision |
|---|---|---|
| Upload OpenAPI and generate tests | Common across commercial and open-source tools | Required entry feature, no novelty claim |
| Multiple roles/tenants for BOLA | Explicitly documented by competitors | Baseline |
| Reproducible evidence and severity | Widely marketed | Baseline, implement carefully |
| AI explanation or attack generation | Strong competitive activity | Optional utility; not the pitch |
| CI failure/retest | Established workflow | Useful handoff, not a moat |
| Positive and negative authorization matrix | Known practice and product overlap | Necessary to reject overly restrictive repairs |
| Revocation and asynchronous execution | Existing research and related tools | Prior art; narrow product-workflow hypothesis |
| Small-team permission timeline plus repair comparison | Specific packaging and usability hypothesis | Validate with users; no verified exclusivity |

StackHawk's multi-profile business logic testing and Planck Proof's authorization matrix plus retesting directly invalidate a broad claim that existing scanners only use one identity or merely flag a 200 response. Avoid repeating competitor marketing claims about all other tools as facts. [StackHawk documentation](https://docs.stackhawk.com/hawkscan/business-logic-testing/), [Planck Proof](https://planckproof.ai/api-authorization-testing)

Authorization regression matrices are also documented by OWASP. Our contribution is an implementation and workflow choice, not invention of the matrix. [OWASP cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Regression_Testing_Cheat_Sheet.html)

## What could become hard to copy

1. A library of customer-reviewed lifecycle policies, adapter patterns and difficult negative controls, contributed with permission and without customer data.
2. Fast onboarding from real application semantics into a maintained test suite, with recorded reasons for each rule.
3. Evidence history linking policy, build and outcomes so developers trust a release decision.
4. A benchmark with disclosed seeded faults, legitimate-use controls and failure injection that prevents superficial improvements from passing.

All four require sustained work. Today there is no proprietary dataset, validated distribution advantage or proven moat. Another team could copy this demo. We should win on a coherent system, measured behavior, candid scope and a sharp customer problem.

## Competitive falsification experiment

After the event, give a permitted fixture and its policy to 2–3 relevant tools. Compare setup time, expressiveness for revocation, detection of the seeded leak, treatment of owner-only regression, reproducibility and operator effort. Publish configuration and versions. Until then, do not claim higher accuracy, faster scans or unique coverage.
