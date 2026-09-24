# Roadmap with evidence gates

## Event: prove one loop

Local runner, one adapter, declared policy, two primary vulnerability classes, temporal export test, repair comparison and real evidence. Finish the [P0 acceptance gates](06_PRODUCT_PRD.md) before expansion.

## Weeks 1–2: validate portability and usefulness

Interview 10 relevant teams. Adapt to a second independent authorized staging API; measure fixture/policy setup time and evidence usefulness. Review transport/redaction externally. Add CLI/CI only if not finished at the event. Gate: at least one engineer other than the author can onboard and interpret the result without live assistance.

## Weeks 3–6: paid design-partner pilot

Offer a bounded pilot for one application and up to three permission workflows. Introduce policy version review, retained baselines and clearer fixture adapters. Add team collaboration only if customers request it. Gate: two paid pilots, maintained policy changes and repeat use across real releases. Pricing is tested, not assumed.

## Months 2–3: expand the same job

Prioritize one adjacent path supported by customer evidence: export links with explicit expiry semantics, role downgrade, workspace removal, cached report access or service-account revocation. Model each separately; do not label all retained access a bug. Optional crAPI integration can test portability for specific supported cases, not claim comprehensive coverage. [OWASP crAPI](https://owasp.org/projects/crapi)

## Hosted product only after isolation gates

Customer-owned runners remain viable. If shared hosting is justified, design tenant isolation, identity federation, scoped job authorization, secret storage, retention/deletion, audit access and incident operations. Replace the local queue/storage as needed. Gate: independent review plus tested recovery and isolation, not an attractive pricing page.

## Longer research bets

Delegated agents, MCP tools and callbacks introduce additional authority paths. Study existing work and define observable manifests before adding them. A September 2026 revocation preprint is prior research, not a ready-made guarantee for our scanner. [Preprint](https://arxiv.org/abs/2609.21284)

Potential community strategy: open the policy schema, fixture benchmark and basic runner while charging for maintained workflow packs, collaboration and private deployment support. Choose licence and business boundaries deliberately before publishing. No code or data has been published by this documentation task.
