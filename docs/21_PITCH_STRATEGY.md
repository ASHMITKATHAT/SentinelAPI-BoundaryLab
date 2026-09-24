# Pitch and mentor narrative

## 45-second Hinglish opening

“API ka permission check ek moment par sahi ho sakta hai, lekin background export us permission ko purana samajh ke data deta reh sakta hai. Alice ne Bob ka access hata diya. Invoice page band ho gaya, par Bob ka pehle se queued export ab bhi download ho raha hai. BoundaryLab permission ka poora timeline test karta hai. Aur jab developer fix karta hai, hum check karte hain ki leak band hua aur genuine collaborators ka access bhi chalta raha. Aaj hum ye teen actual API implementations par dikhayenge—vulnerable, wrong fix aur correct fix.”

Use “actual” only once the application genuinely executes the tests. Before that, describe the plan as proposed.

## Eight-slide content ready for a deck

| Slide | Headline | Visual/content | Speaker point |
|---|---|---|---|
| 1 | Removing access must remove the ways to retrieve data | Alice → Bob → export → revoked access | One familiar problem |
| 2 | Permission is a lifecycle | Grant/queue/ready/revoke/retrieve timeline | A request-only view can miss a workflow |
| 3 | The policy is explicit | Owner/collaborator/foreign matrix + grace | We do not guess business intent |
| 4 | Live: vulnerable → owner-only → correct | Actual comparison and evidence | A secure repair must preserve intended use |
| 5 | Evidence has boundaries | Case counts, hashes, unknown states | Missing evidence cannot become a green badge |
| 6 | Strong market, focused entry | 4 close alternatives and our narrow workflow | Multiuser/AI/proof are already crowded |
| 7 | One buyer and a paid pilot | SaaS CTO, local runner, onboarding + subscription hypothesis | Recurring value is maintained regression confidence |
| 8 | What is built and what comes next | Actual completed gates, missing work, 30-day validation | Ask for staging design partners and policy feedback |

Slides are an outline, not a delivered PPTX. Populate measured results only after implementation. All charts must label hypothetical economics versus actual performance.

## Differentiation answer

“Existing products already do multi-user testing and evidence. Our focus is making one business permission promise executable across asynchronous work, then testing the repair against legitimate use too. We are validating whether this focused workflow is easier for a small SaaS team to maintain.”

## Business close

“We want three staging design partners with sharing/export workflows. We propose a paid, bounded setup plus recurring regression suite. Our immediate metric is not number of findings; it is whether a team keeps using and maintaining the policy after onboarding.”

## Evidence hierarchy

Lead with live behavior, then actual repeatability data, then external category evidence, then future hypotheses. Never present a hypothetical ROI estimate next to a measured result without labels. The source-backed competitor research is stronger than an exaggerated total addressable market slide.
