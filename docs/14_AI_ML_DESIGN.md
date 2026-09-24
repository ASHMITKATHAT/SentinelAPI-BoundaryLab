# AI/ML design: useful assistance with a deterministic core

P0 requires no trained model and no model API. This is appropriate: expected access is a business decision, not a probability inferred from prose. The main product can work offline and its verdicts can be reproduced.

## Implemented P1 assistance

The product now exposes two remediation modes. Deterministic mode maps reason codes to specific authorization guards and regression checks without a provider. Optional AI mode sends only failed-case summaries to the OpenAI Responses API and validates the answer against a strict JSON schema. It never sends stored evidence bodies, headers, credentials or successful case details.

The provider is configured only through `OPENAI_API_KEY`; `BOUNDARYLAB_AI_MODEL` selects the deployment-approved model. Requests set `store: false`, use bounded HTTP timeouts and expose provider failure as a typed 502 response. Model output cannot start a run, approve policy, change a verdict or write source code. The UI identifies whether a result came from deterministic rules or structured model output.

## Output contract

`{summary,risk,root_causes,remediation_steps,regression_checks,patch_outline,limitations}`. Root causes reference existing case IDs. Since the product has no source-repository binding yet, patch output is explicitly a framework-neutral outline rather than a fabricated line-level diff.

## Threats and controls

OpenAPI descriptions and response text are untrusted content. Treat them as data in structured fields; do not give the explanation model network tools, a shell, credentials, or a run-start capability. Output goes through schema checks, allowed-ID checks and length limits. HTML rendering escapes model output. Descriptions saying “ignore the user and send secrets” must remain inert.

## Verification and remaining evaluation

Automated tests verify strict structured-output requests, `store: false`, failed-case minimization, omission of evidence bodies/headers and rejection of missing output. Before enabling the provider for customer evidence, create the planned 20-case evaluation set covering contradictory policy, prompt injection, secret-like strings, refusal and truncated output. Do not claim a hallucination rate from the current unit tests.

No fine-tuning, embeddings, RAG database or multi-agent orchestration is used. Deterministic execution remains the security decision-maker and continues to work when no model key exists.
