# UI/UX specification

Open [the interactive prototype](../design/boundarylab-prototype.html). It is a design artifact with synthetic data and no scanner connection. Its label must remain visible in screenshots. The product implementation must replace its state with control-API responses.

## Visual direction

A calm engineering review desk: cool grey canvas, white evidence surfaces, navy navigation and a disciplined red action/failure accent. Use a system sans font for text and monospace only for paths, IDs and request payloads. The primary unit is a permission promise with evidence, not a generic security score card. The implemented benchmark and redesign rationale are recorded in [35_UI_BENCHMARK_AND_REDESIGN.md](35_UI_BENCHMARK_AND_REDESIGN.md).

Design tokens are in [tokens.json](../design/tokens.json). Use a 4 px spacing base, 8/12/16/24/32 px rhythm, 12 px panel radius, 1 px borders and a 1,360 px maximum content width. Body text ≥14 px, controls ≥44 px high, line-height ≥1.45. Severity uses an icon/text label as well as color. Do not encode meaning only in red/green.

## Navigation and screens

| Route | User decision | Required content |
|---|---|---|
| `/setup` | What is authorized and testable? | OpenAPI file, support summary, trusted target alias, runtime identity refs, network/request scope |
| `/policies/:id` | What should access mean? | Human-readable rules, owner/collaborator/foreign matrix, grace period, restricted fields, immutable version, approve action |
| `/runs/:id` | What actually happened? | Run/build identifiers, required-case counts, timeline, controls, coverage, cancel, explicit incomplete state |
| `/findings/:id` | Is this a real violation? | Expected vs observed, redacted request/response, canary check, preconditions, affected rule, reproduction |
| `/compare` | Did the change fix it without breaking use? | Same-policy compatibility check, three outcome columns, legitimate-use regressions, unresolved/incomplete cases |
| `/reports/:id` | What can I share? | Executive paragraph, technical appendix, covered/omitted operations, export controls |

Keep setup to one page and policy review to one page. Do not create a project/org billing onboarding flow for the local MVP.

## Primary screen composition

Header: project, environment alias, build and run status. Main question: “Can Bob still retrieve this invoice after sharing ends?” Below it, the expected rule and observed outcome. A horizontal or stacked timeline shows grant → queue → ready → revoke → probe; each node names the identity, operation, relative time and evidence link.

Right panel shows prerequisites: correct identities, active-sharing control, owner access, fixture freshness and policy approval. At narrow widths it follows the timeline in DOM order. Below, a compact case table exposes pass/violation/inconclusive/skipped separately and links to evidence. Do not hide failed positive controls behind aggregate counts.

## Microcopy

- Confirmed: “Bob received the invoice marker 2,243 ms after revocation acknowledgement. Policy requires denial after 2,000 ms.” This is example copy; real UI uses measured times.
- Incomplete: “Bob's credential expired. We could not evaluate revocation. Restore the test identity and start a new run.”
- Scoped pass: “All required cases passed for this policy and build. Other endpoints and attack classes were not assessed.”
- Comparison rejected: “These runs use different policies. Select runs with matching policy and suite versions.”
- Empty evidence: “No target request was sent for this step.”

## Interaction and accessibility

Use actual buttons/links with visible keyboard focus. Tables need column headers; drawers need an accessible name, Escape close and restored trigger focus. Announce async state changes politely; do not announce every log line. Preserve form input on validation errors and focus the error summary. Respect reduced motion. At 360 px, stack panels; request/code blocks scroll horizontally without widening the entire page. Show copy confirmation, and never copy a real credential with a request snippet.

Loading, empty, malformed spec, token mismatch, target unavailable, permission denied, cancellation, cleanup failure and noncomparable runs are designed states. AI prose has an “AI draft” label and cannot replace deterministic evidence. Every export warns only about concrete contents, not generic alarmist disclaimers.
