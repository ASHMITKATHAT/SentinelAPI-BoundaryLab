# 32 questions judges and mentors may ask

1. **What is the exact problem?** A declared access change may not propagate to all retrieval paths, especially queued exports. We test that promise and its legitimate-use controls.
2. **Why PS3?** It gives us a controlled, falsifiable demonstration and a plausible recurring engineering workflow. The team explicitly selected it.
3. **Is this just another scanner?** Much of the baseline is established. Our narrow workflow is policy → permission timeline → evidence → repair validation, not a claim of a new vulnerability class.
4. **Who already does this?** StackHawk, Akto, APIsec, Escape and Planck Proof overlap; Hadrian and custom tests are credible substitutes. Exact lifecycle ergonomics need a hands-on benchmark.
5. **Why not a few pytest tests?** For one simple API, custom tests may be enough. We must earn value through reusable policy, maintained fixtures and reviewable evidence. If customers prefer their scripts, the business thesis fails.
6. **Where is AI?** Optional drafting/explanation. Verdicts are deterministic because business intent and security evidence should not depend on a model guess.
7. **How do you know Bob should be denied?** A reviewed policy names his relation, action, object and revocation semantics. Unknown intent is not a confirmed flaw.
8. **Is every 200 a vulnerability?** No. We need valid identity, a known protected marker, policy denial and successful controls. Unexpected bodies are inconclusive.
9. **Can a 403 still leak?** Yes, if its body includes the protected marker. Both status and content are evaluated.
10. **What if the token expired?** A failed identity preflight or probe-adjacent auth check makes the authorization conclusion incomplete; it does not prove the repair worked.
11. **Why a two-second grace period?** It is the fixture's explicit policy, not a general security standard. Real customers must choose and justify their own contract.
12. **What about in-flight requests?** We evaluate requests started after acknowledgement plus grace and margin. We do not retroactively judge a request begun before that boundary.
13. **What about eventual consistency?** Its allowed delay belongs in the reviewed policy. If we cannot establish the timing/control context, we report uncertainty.
14. **Are signed URLs always wrong after sharing is revoked?** No. Expiry-based capability access can be intentional. P0 tests a bearer-auth JSON endpoint, not S3 semantics.
15. **Why test a wrong fix?** Owner-only checks can close access too broadly. Failed positive controls expose the functional regression.
16. **Does the wrong-fix run prove revocation is fixed?** No. If Bob cannot queue/retrieve while authorized, the temporal case is inconclusive. The release is already blocked by broken legitimate behavior.
17. **Are the bugs seeded?** Yes, three disclosed implementations. This evaluates known cases; it is not an independent real-world discovery claim.
18. **Can you hard-code the result?** The implementation must derive evidence from requests. We can change IDs, delays or a response and show changed outcomes; target variant names cannot control verdicts.
19. **How broad is coverage?** One REST/JSON workflow, declared operations and identities. Reports list unsupported/untested operations and classes.
20. **How do you avoid harming targets?** Explicit scope, lab fixtures, bounded methods, 2 RPS, one request in flight, total budgets and namespace-only cleanup.
21. **Could OpenAPI cause SSRF?** Not through automatic server/ref fetching; aliases and a scoped transport govern network access. Scope-escape tests are a release gate.
22. **Where are credentials?** In the local runtime secret registry. Evidence contains references and redacted placeholders, not credential values.
23. **What if the worker dies?** Persist incomplete/interrupted state, do not replay an ambiguous mutation, and rerun with a new namespace.
24. **Are evidence hashes tamper-proof?** No. They detect byte changes relative to a manifest. They are not a trusted signature or notarization.
25. **Can it run offline?** The intended core can run locally after dependencies/images are preloaded. AI is optional. Demonstrate this before claiming it.
26. **Why SQLite?** One local operator and one worker keep deployment small. Multi-tenant hosting requires a different operational/security design.
27. **Is it production ready?** Not from this specification. The event target is a working local MVP. Pilot and hosted release gates are separately listed.
28. **Who pays?** Hypothesis: SaaS CTO/engineering lead repeatedly maintaining sharing/export permissions. Interviews and paid pilots must validate this.
29. **How much?** Proposed experiments: ₹15,000 bounded onboarding pilot and ₹8,000/month for one small maintained suite; these are unvalidated prices.
30. **What is the moat?** None proven today. Potential advantage is policy/adapter knowledge, onboarding speed and trusted evidence history with customer adoption.
31. **What would make you stop?** No paid demand, little recurring pain, high integration burden, or existing tools delivering the same job cheaply with less effort.
32. **What is next after the hackathon?** Independent staging pilot, transport/security review, second workflow adapter and measured repeat use before broadening scope.
