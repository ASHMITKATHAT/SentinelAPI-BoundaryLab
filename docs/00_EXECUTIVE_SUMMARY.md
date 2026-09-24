# Executive summary

Status: design specification, 24 September 2026. Audience: team, mentors and judges.

**Build SentinelAPI BoundaryLab: a local authorization regression workbench for SaaS APIs.** The wedge is the interval between “permission was removed” and “all relevant ways of retrieving the data actually stopped.”

In the demonstration, Alice shares an invoice with Bob. Bob queues an export. Alice removes Bob's access. The invoice endpoint correctly refuses him, but a poorly implemented export endpoint still serves the invoice. A second implementation closes the leak by refusing every collaborator, including legitimate ones. BoundaryLab should distinguish both failures from a correct repair using the same policy, identities and scenario.

This addresses PS3's core obligations: ingest a specification, use multiple authenticated identities, detect object and field authorization problems, rank findings, show reproducible evidence and explain the result. A scoped authentication check is included. Rate-limit behavior is an optional bounded contract test, never an uncontrolled load test or a claim about all abuse protection.

The business buyer hypothesis is a CTO or engineering lead at a small B2B SaaS company with multi-tenant data, sharing and exports. Initial distribution should be a local runner plus paid onboarding to a small recurring workflow suite. The paid value is maintenance of important permission contracts and usable release evidence, not the number of AI messages generated.

The market is crowded. StackHawk, Akto, APIsec, Escape, Planck Proof and open-source tools have overlapping capabilities; see [current comparisons](04_MARKET_AND_EXISTING_SOLUTIONS.md). There is no defensible “nobody else can do this” claim. A useful policy library, repeatable onboarding and customer-validated tests could become an advantage over time. Neither a prompt nor the dashboard is a moat.

For two days and 1–2 developers, use React/TypeScript, FastAPI, SQLite and a deterministic Python worker. Support one reviewed REST/JSON fixture adapter and OpenAPI 3.1 JSON. AI is optional and excluded from verdicts. Keep secrets and evidence local. The deployment is a single-operator local workbench, not a public multi-tenant service.

Success at the hackathon means a live, inspectable request trace; known vulnerable/incorrectly fixed/correctly fixed cases; honest incomplete results on failures; and a clear answer to who would pay. Winning probability cannot be calculated without the rubric and competing projects. No performance, customer or revenue result has been measured yet.
