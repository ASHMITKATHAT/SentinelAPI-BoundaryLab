# Live demonstration plan

Length: 5 minutes, plus questions. Use only the team's local authorized fixture. This is a script for the implemented product; the supplied HTML prototype cannot substitute for a live scan.

| Time | Screen/action | Spoken point | Visible proof |
|---|---|---|---|
| 0:00–0:30 | Show invoice sharing and policy | “Alice removed Bob. Can he still download an export he queued earlier?” | Identities, one invoice, explicit 2-second revocation policy |
| 0:30–1:00 | Show imported spec and scope | “We test the declared operations with real identities and synthetic data.” | Supported operations, target alias, limits, approved policy |
| 1:00–2:00 | Start vulnerable run | “Watch the permission timeline.” | Actual grant/queue/ready/revoke/probe requests; Bob gets marker after deadline |
| 2:00–2:35 | Open evidence | “This is the expected rule, returned marker and measured time.” | Redacted request/response, valid identity, build and rule IDs |
| 2:35–3:25 | Compare owner-only implementation | “Blocking all collaborators hides the leak but breaks the product.” | Failed active-sharing controls and incomplete temporal case |
| 3:25–4:10 | Compare correct implementation | “This fix meets both allowed and denied behavior in our tested scope.” | Same policy/suite, legitimate access preserved, post-revoke denial |
| 4:10–4:35 | Export report | “The result becomes a repeatable release check.” | Actual JSON/HTML with coverage and reproduction manifest |
| 4:35–5:00 | Business and boundary | “Our first buyer owns SaaS sharing/export regressions. We are validating a paid local-runner pilot.” | One buyer, one workflow, no unsupported market claims |

If three live runs do not fit five minutes, run the vulnerable case live and show clearly dated actual prior runs for comparison, with build/hash compatibility. Say which runs were recorded. Keep one correct-build rerun available for questions.

## Pre-demo checklist

- Preload dependencies/images and verify the local app works with internet disconnected.
- Use the current committed build; show its identifier. Ensure synthetic fixture namespace isolation and clean target state.
- Run all three variants and export actual reports. Confirm labels and counts match observed data, not this plan's expectations.
- Verify keyboard navigation, browser zoom and laptop screen readability. Keep terminal/API output available for technical inspection.
- Record one real successful demo as a labelled fallback; preserve one failure/incomplete example as well.
- Confirm no secrets are visible in terminal history, UI, requests, screenshots or report exports.

## Mentor intervention

Offer an inspectable change: alter grace period in a **new policy version**, expire Bob's test token, or switch to owner-only target. Explain why policy changes invalidate direct fix comparison. Do not permit arbitrary external target entry on stage.

## What not to say

Do not say “100% secure”, “zero false positives”, “world's first”, “production ready”, “AI fixed the API”, “all OWASP vulnerabilities covered” or “nobody can copy this.” State what was actually executed, what was seeded and what remains untested.
