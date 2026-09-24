# Risk register

Likelihood/impact are planning judgments. Owners A/B refer to the two-person plan; one developer owns both in the solo route.

| Risk | Likelihood / impact | Owner | Mitigation and trigger |
|---|---|---|---|
| Scope exceeds two days | High / high | Both | Freeze one workflow; H8 vertical slice; cut P1 first |
| Wrong business oracle | High / high | A | Reviewed explicit policy; uncertainty state; reject inference from schema alone |
| False “fixed” due to broken auth | Medium / critical | A | Identity checks, positive controls and dependent-case gating |
| Unsafe network scope | Medium / critical | A | Alias-only transport, pinning, no redirects/remote refs; local-only until verified |
| Credential/evidence leak | Medium / critical | Both | Sanitize before persistence, sentinel tests, private artifact routes |
| Time-based flaky result | Medium / high | A | Monotonic time, post-ack boundary, margin and bounded readiness; repeated runs |
| Fixture and scanner share the same mistake | Medium / high | A | Independent implementations, code review and held-out variation |
| Fake-looking demo | High / high | B | Real requests/build IDs, visible policy edits, disclosed seeded targets |
| Competitor already solves workflow well | High / medium | Both | Specific claims only; hands-on comparison after event; narrow or contribute instead |
| Customer onboarding too costly | High / high | Both | Track fixture/policy setup hours; paid bounded scope; stop criteria |
| Worker crash causes duplicate writes | Medium / high | A | Persist step start, no automatic mutation replay, new namespaces |
| Cleanup loses unrelated data | Low / critical | A | Lab token, namespace ownership, no reset-all operation |
| Report implies wider coverage | Medium / high | B | Tested-scope label, explicit denominator and omitted checks |
| Event setup fails | Medium / high | B | Preload images, fresh-start rehearsal, labelled actual-run fallback |
| Solo workload becomes unsustainable | High / high | Both | 20 focused-hour plan, rest, simple forms and no P1 |
| Production claim outruns controls | Medium / high | Both | Readiness gates and explicit release labels |

Open assumptions requiring validation: exact judging rubric, team's Python/React/Docker experience, laptop resources, available presentation duration, customer access and willingness to pay. These do not block preparing the pack; they should guide implementation cuts and mentor discussion.
