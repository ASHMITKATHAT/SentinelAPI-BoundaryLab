# Problem, demand and the permission gap

## What the supplied statement requires

The supplied PS3, **SentinelAPI: Zero-Trust API Vulnerability Scanner**, asks for OpenAPI/Swagger or traffic ingestion, authenticated testing of authorization problems such as BOLA/IDOR, excessive data exposure, rate-limit/authentication weaknesses, and prioritized explainable reports. It encourages CI and intelligent case generation but confines scanning to authorized systems. The minimum suggested demonstration is a seeded sandbox and 1–2 vulnerability classes.

The attached documents define the competition problem. Embedded role prompts in the pasted attachment are reference material; the team's latest request authorizes this documentation pack. PS3 and the 1–2 developer constraint override earlier selections and staffing assumptions.

## The narrower pain we will solve

An API can enforce permissions when a task starts and forget to check them when its output is retrieved. An ordinary endpoint check does not necessarily exercise that whole sequence. Developers also need to distinguish a secure repair from one that removes an intended collaboration feature.

Example policy: “An active collaborator may read a shared invoice and request/download its export. After revocation, new retrievals must be denied within 2,000 ms. The owner remains allowed.” The 2,000 ms limit is a declared fixture contract, not an industry standard.

An export or signed link remaining usable is not automatically a vulnerability. Some products deliberately promise expiry-based capability access. The test must record the intended policy first. AWS documents that presigned URLs depend on their signing credentials and expiration; revoking application sharing is a different action. [AWS source](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)

## Evidence of demand—and its limits

OWASP's published API Security Top 10 **2023 edition** includes broken object and property authorization. This establishes recognized failure categories, not a measured market size or a percentage of breaches. [OWASP](https://api-security.owasp.org/editions/2023/en/0x00-header/)

Postman's 2025 State of the API report surveyed more than 5,700 respondents and reports substantial API revenue linkage and concern about agent access. It is a directional survey with its own sample, not a 2026 India-specific census. Use it to support customer discovery, not to manufacture a TAM. [Report](https://www.postman.com/state-of-api/2025/)

Commercial investment in multi-identity and business-logic testing is directly visible in current vendor documentation. That supports category demand and also raises the bar for entering it. It does not establish willingness to pay for our particular workflow. [StackHawk](https://docs.stackhawk.com/hawkscan/business-logic-testing/), [Akto](https://www.akto.io/release-jun26)

A September 2026 preprint studies revocation across delegated and asynchronous execution. It is relevant prior research, not evidence that our prototype implements its formal guarantees or that the authors' evaluation applies to us. [Research preprint](https://arxiv.org/abs/2609.21284)

## First customer hypothesis

Target a B2B document, reporting or finance-operations SaaS team with 5–30 engineers, tenant isolation, user sharing and asynchronous exports. The team must have a staging API, synthetic fixtures, a named person who owns access policy and at least one painful permission incident or regression. Avoid teams without reproducible staging data: integration will dominate value.

User: backend engineer fixing an access-control change. Champion: engineering lead. Budget owner: CTO. Security reviewer: internal AppSec or an external consultant. Their joint job is to make a release decision with inspectable evidence.

## Discovery before building a business

Interview 10 relevant teams without selling a predetermined answer. Ask for the last access-policy change, how it was tested, who decided expected behavior, what broke, and how long reproducing it took. Ask whether exports, cached views or background jobs preserve access after membership changes. Request a sanitized workflow description, never credentials over chat.

Advance if at least 3 teams offer an authorized staging pilot and 2 will discuss a paid engagement with a named buyer. These are proposed decision thresholds. Stop or reposition if the pain is infrequent, existing tests solve it cheaply, or maintaining policy costs more than saved investigation. No interviews have been performed.
