# Winning strategy: make the repair prove both sides

## The one sentence

“Hum sirf unauthorized access pakadte nahi; hum test karte hain ki access remove hone ke baad purane exports bhi band hue, aur fix se genuine collaborators ka kaam nahi toota.”

## The product's promise

For one reviewed policy and a declared set of API operations, provide evidence of whether access behaved as expected through a permission change. Show leaks, legitimate-use regressions and incomplete tests separately. Every result names its scope and target build.

## The three-act demonstration

1. **Vulnerable:** Bob legitimately queues an export. Alice revokes sharing. After the declared deadline, Bob still receives the synthetic invoice canary. Separately Mallory can fetch a private cross-tenant invoice and Bob sees an owner-only field.
2. **Owner-only patch:** those leaks disappear, but Bob is blocked while he is still an active collaborator. This is a functional regression. The lifecycle scenario becomes incomplete if it cannot establish its legitimate precondition; it must not be called a successful revocation test.
3. **Correct patch:** Bob can use active sharing, loses retrieval access after revocation, and Alice retains owner access. Object and field checks also meet the same policy.

Prepared implementations are disclosed test fixtures. Switching them is **not** AI fixing production code. Runs must make fresh HTTP requests and derive results from responses. Never select findings from a hard-coded target-mode table.

## Features worth the two-day budget

| Feature | Reason it matters | Proof on stage |
|---|---|---|
| Policy before scanning | Avoids guessing what “allowed” means | Mentor sees and can change one rule |
| Permission timeline | Makes async authorization understandable | Grant, queue, ready, revoke, probe with elapsed times |
| Positive controls | Rejects the easy but broken fix | Active collaborator access fails on owner-only patch |
| Evidence drawer | Makes claims inspectable | Actual redacted request, response marker, rule and build |
| Comparable reruns | Supports a release decision | Same policy/suite hashes, different build IDs |
| Unknown/incomplete state | Prevents “zero findings = secure” | Expired token or failed export visibly stops the claim |
| Regression export | Makes the demo useful after judging | Policy, report, machine results and replay instructions |

## Avoid the attractive distractions

No generic chatbot homepage, 3D attack globe, fabricated “security score”, automated production patching, arbitrary internet crawling, 20 empty integrations, blockchain evidence claims or simulated “live” dashboard. A clean timeline showing one real flaw is stronger than a broad unverified feature list.

## What a mentor should be able to challenge

Ask for an identity change, a denied request, a different grace period or a broken token. The application should explain how the result follows or why the run cannot conclude. Changing the policy creates a new immutable version and blocks misleading comparisons to old-policy runs.

The competitive advantage is the quality of that interaction. The same idea can be implemented by others; our claim must be supported by actual implementation and evaluation, not exclusivity language.
