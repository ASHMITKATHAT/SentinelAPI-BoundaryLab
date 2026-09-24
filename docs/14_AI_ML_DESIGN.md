# AI/ML design: useful assistance with a deterministic core

P0 requires no trained model and no model API. This is appropriate: expected access is a business decision, not a probability inferred from prose. The main product can work offline and its verdicts can be reproduced.

## Optional P1 assistance

Input: operation names, sanitized schemas, operator-written policy notes and deterministic finding facts. Output: a schema-constrained **draft** policy or a plain-language explanation tied to existing rule/evidence IDs. The operator must approve policy before execution. The engine ignores invented operation IDs, unapproved targets, unsupported actions and explanation-only claims.

Use a provider adapter configured by environment; choose a model only after checking current official availability, pricing and data terms during implementation. This pack does not assume a particular proprietary model or quote stale token prices. Cap each explanation request, cache by redacted facts hash and provide a deterministic template fallback.

## Draft output contract

`{draft:true, proposed_rules:[], referenced_operation_ids:[], assumptions:[], missing_information:[]}`. Unknown owner semantics must appear as missing information. Never turn uncertainty into permission to probe. Policy approval records the actual approved JSON hash, not the LLM conversation.

## Threats and controls

OpenAPI descriptions and response text are untrusted content. Treat them as data in structured fields; do not give the explanation model network tools, a shell, credentials, or a run-start capability. Output goes through schema checks, allowed-ID checks and length limits. HTML rendering escapes model output. Descriptions saying “ignore the user and send secrets” must remain inert.

## Evaluation before enabling AI

Create 20 redacted cases: correct explanation, missing intent, contradictory policy, nonexistent operation, prompt injection, oversized content and secret-like strings. Measure unsupported claims, reference validity, sensitive-string reproduction and operator edits. Required gate: zero execution from model output, all invalid references rejected and deterministic functionality unaffected when model calls fail. Do not claim a hallucination rate based on a handful of examples.

No fine-tuning, embeddings, RAG database or multi-agent orchestration is justified for this two-day scope. Policy examples are versioned fixtures, not a proprietary training corpus. If an AI feature delays the working lifecycle test, omit it and explain this design choice to judges.
