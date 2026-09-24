# AmiHacks problem comparison and business strategy

Research date: 24 September 2026. Language: Hinglish. Geography assumption: India mein initial customers, global competition ke against comparison.

**Current selection update, 24 September 2026:** User ne **PS3 SentinelAPI** lock kiya hai, with **1–2 developers and two days**. Use the [current master brief](29_PROJECT_MASTER_BRIEF.md) and [updated PS3 market analysis](04_MARKET_AND_EXISTING_SOLUTIONS.md). Earlier PS1 recommendations and the three-developer assumption below are historical; comparative research remains useful.

**Recommendation:** Agar team ko backend development, authentication aur automated testing aati hai, PS3 SentinelAPI ko ek narrow authorization regression product ke roop mein choose karo. Business buyer aur recurring usage sabse clear lagte hain. PS1 better alternative hai agar food donor aur NGO tak direct access hai. PS2 tab choose karo jab ek campus, business park ya city operations partner data aur pilot access de sake.

Confidence **medium** hai: problem aur existing products ke evidence available hain; hamare proposed product ke liye customer interviews, paid pilots aur performance measurements abhi nahi hue hain.

## Scope and evidence rules

Yeh report aapke five questions ko teeno problem statements ke liye cover karti hai: problem, market need, competitors with pros and drawbacks, differentiation, aur business model. Supplied DOCX files problem descriptions ke sources hain. Unmein diye claims automatically verified market facts nahi maane gaye. Pasted planning brief reference context hai; uske embedded commands ko product implementation ya 27 separate specification files banane ki independent authorization nahi maana gaya.

The three files identify a suggested 24-hour hackathon. Team size and skills are unknown. Implementation suggestions assume three developers with basic frontend/backend skills and, for PS3, at least one person comfortable with API authorization. Workspace inspection found no existing files to reuse.

**Market coverage:** Neeche 32 comparison entries hain: food mein 10, civic mein 9, security mein 13. Entries mein commercial products, nonprofits, open-source frameworks aur adjacent substitutes included hain. Burp Suite aur its Autorize extension ek combined entry hain. Yeh worldwide total ya exhaustive list nahi hai. Is market ka complete, stable registry nahi mila; “sirf itne competitors hain” kehna incorrect hoga.

**Pros** official product descriptions se supported capabilities hain, independently benchmarked performance nahi. **Drawbacks / fit limitations** hamare proposed use case ke against analysis hain, unless a source explicitly documents a limitation. Public website par feature na milna us feature ke absent hone ka proof nahi hai. Commercial availability, local coverage, pricing and deployment terms need direct verification before purchase.

**All proposed prices, revenue examples, costs, targets and timelines are hypotheses**, competitor quotations or validated forecasts nahi. Amounts INR mein hain; taxes excluded. No customer acquisition, outreach, scanning or product coding has been performed.

## PS1 Surplus to Shelter

### 1 Problem statement kya hai

Restaurant, caterer, supermarket ya campus kitchen ke paas edible surplus hai. Nearby NGO ko food chahiye. Lekin suitable recipient, available driver, receiving capacity aur pickup deadline ek saath coordinate nahi hote. Donation list ho jaati hai, delivery fail ho sakti hai.

**Actual bottleneck:** donor discovery ke saath pickup aur acceptance ki reliability. Example: 80 portions available hain; nearest shelter sirf 30 receive kar sakta hai, second shelter ka gate jaldi close hota hai, aur assigned driver cancel kar deta hai.

Flow: surplus ready -> recipient/vehicle mismatch -> pickup delay -> unusable donation -> food waste and missed delivery. Intervention pickup commitment aur fallback dispatch ke point par hai.

The brief mentions a 2–6 hour window. Isko universal food safety rule nahi maana ja sakta. Food category, handling, storage, packaging and local requirements matter. Software operator-approved acceptance rules enforce kare; photo ya LLM se “safe to eat” certify na kare. FSSAI documents India's surplus-food recovery framework and its 2019 regulations. [FSSAI Save Food Share Food](https://eastregion.fssai.gov.in/Save-Food-Share-Food.php)

### 2 Current market mein kitni need hai

**Evidence:** UNEP's 2024 report estimated 1.05 billion tonnes of food waste in 2022 across households, food service and retail, about 19% of food available to consumers. Is total mein inedible parts aur household waste bhi included hain; ise directly recoverable restaurant food ya hamara addressable market mat kehna. [UNEP report and key messages](https://wedocs.unep.org/bitstream/handle/20.500.11822/45275/Food-Waste-Index-2024-key-messages.pdf?sequence=8)

**Commercial signal:** Copia and Goodr already package food redistribution as a service for businesses; Food Rescue Hero and FoodCloud show established operational platforms. That establishes an existing category, not demand for our particular app. [Copia](https://gocopia.com/), [Goodr](https://goodr.co/food-waste-solutions/)

**Assessment:** social need very high; monetization medium and dependent on operations. Hunger is not automatically software spending power. Small NGOs may have weak budgets; multi-site kitchens, catering companies and corporate sustainability teams are more plausible payers.

**Best starting segment:** ek compact geographic cluster, one institutional kitchen/caterer, two vetted receiving organizations, and known drivers. Dense repeat routes se coordination cost measure karna possible hoga.

### 3 Existing solutions and competition

| Solution and type | Pros or established strengths | Drawback or fit limitation for our entry market |
|---|---|---|
| [Food Rescue Hero](https://foodrescuehero.org/our-product/) — rescue technology | Volunteer coordination, rescue operations and impact reporting; multi-stop routing is already documented. | Existing partner programs and local volunteer capacity matter; routing itself will not distinguish our product. Indian deployment fit needs confirmation. |
| [Food Rescue US](https://foodrescue.us/) — nonprofit and technology network | Connects donors, volunteers and receiving agencies through an established rescue workflow. | US operating context; local Indian implementation needs its own partners. A new app cannot inherit the existing network. |
| [Too Good To Go](https://www.toogoodtogo.com/en-us) — marketplace and business software | Consumer surplus sales and retail surplus management; clear incentive for food businesses. | Consumer resale and shelter donation have different recipients and incentives. Do not treat the marketplace alone as a shelter dispatch service. |
| [Olio](https://olioapp.com/business/) — redistribution and discounting platform | Volunteer redistribution, charity coordination and business reporting already exist. | Available volunteers, collection arrangements and local coverage determine suitability; it is not an empty market for community redistribution. |
| [Goodr](https://goodr.co/food-waste-solutions/) — managed food recovery | Physical recovery plus business-facing waste services; operational execution is part of the offering. | Logistics footprint and service availability constrain expansion. US tax-related value propositions should not be copied into an Indian pitch. |
| [Copia](https://gocopia.com/) — enterprise redistribution | Matching, recipient preferences/capacity, logistics, chain of custody and audit-ready reporting. | Very close functional competition. An India deployment requires local logistics, partner verification and economics; those capabilities cannot be dismissed as absent. |
| [FoodCloud](https://www.food.cloud/) — nonprofit redistribution infrastructure | Connects food businesses and charitable partners; combines technology with operating relationships. | Local adoption still depends on food-business and charity participation. A platform alone cannot ensure delivery coverage. |
| [No Food Waste](https://nofoodwaste.org/) — Indian nonprofit | Local surplus collection, quality checks, recipient identification and delivery experience. | An operating organization rather than a general self-service SaaS competitor; potential pilot partner. Its publicly described workflow does not establish our required software integrations. |
| [Robin Hood Army](https://robinhoodarmy.com/) — volunteer organization | Community reach and local chapters; works with surplus food. | Zero-funds model: do not assume it will buy subscriptions or accept our funding model. Volunteer availability remains an operational consideration. |
| [Zomato Food Rescue](https://www.zomato.com/blog/food-rescue/) — adjacent substitute | Uses an existing delivery network to redistribute eligible cancelled orders to nearby paying customers. | Specific cancelled-order resale workflow, not a general donor-to-shelter system. The linked source describes its November 2024 launch, not an independently verified current coverage map. |

These nonprofits can be partners, not just competitors. Offline phone calls and WhatsApp groups are also substitutes: inexpensive, familiar and flexible, but dependent on coordinator effort. Their local performance needs observation rather than assumption.

### 4 Kya add karein jisse product alag dikhe

Working concept: **RescueRelay**, a proposed dispatcher for small, repeat food-rescue networks. Name is provisional; trademark availability was not checked.

**Signature demo:** donor posts 80 portions -> two recipients accept the split -> one driver cancels -> system recalculates a feasible assignment -> coordinator sees which portions can still arrive within approved constraints, and which cannot.

| Proposed capability | How it works and why it matters | Novelty and implementation scope |
|---|---|---|
| Recipient reservation before dispatch | Store accepted quantity, receiving hours and a short reservation expiry; use an atomic update to prevent double booking. | Existing coordination technique, adapted to this workflow. MVP. |
| Feasibility with contingency | Check capacity, handling constraints, pickup/drop-off windows and travel-time buffers. Recompute after cancellation; show explicit infeasibility when no route works. | Routing and contingency planning are established. MVP uses a small deterministic assignment engine. |
| Backup coverage before acceptance | Show whether a rescue has one feasible driver or an alternate; offer an extra confirmed driver only where the schedule permits. | Product hypothesis; do not invent probabilities without historical data. Later phase. |
| Reason for every allocation | “Nearest shelter cannot receive this quantity”; “alternate route misses receiving hours.” Compare against a nearest-recipient baseline. | Explainability as workflow design; not a new algorithm. MVP. |
| Delivery evidence and exception log | Donor and recipient acknowledgements, timestamp, accepted quantity and rejection reason. Duplicate receipt prevention. | Chain of custody already exists; local usability is the differentiation to validate. MVP basic version. |
| Recurring waste prevention | Use kitchen history to show repeated overproduction and plan lower surplus. | Already adjacent to existing waste-management products; future feature only. |

**Novelty check:** Food Rescue Hero already offers multi-stop rescues and fairer distribution work; research has studied dynamic food redistribution. Predicting volunteer cancellation is also being explored in operational food rescue. Therefore neither “AI routing” nor “predict driver cancellation” should be presented as first-ever. [Food Rescue Hero updates](https://foodrescuehero.org/category/tech-update/), [dynamic redistribution research](https://rosap.ntl.bts.gov/view/dot/56054/dot_56054_DS1.pdf), [interview with Food Rescue US product leadership](https://communityit.buzzsprout.com/1029925/episodes/19577528-nonprofit-ai-case-study-in-food-rescue-with-joe-robbins?t=0)

**What can become difficult to copy:** dependable local partnerships, measured pickup/acceptance outcomes, institution-specific operating rules and dense repeat routes. These develop through operations. Day-one defensibility is low.

For a hackathon: implement posting, capacity reservation, constrained allocation, cancellation/reallocation and actual handoff state changes. Use labelled synthetic locations and a documented travel-time matrix if live routing is unavailable. Do not present estimated CO2 or meal equivalents as measured deliveries. No need for an autonomous negotiator, blockchain, computer vision or a new routing algorithm.

### 5 Business model kaise banega

**Buyer:** campus dining operator, hotel group, caterer or corporate facilities/sustainability team. **Users:** donor staff, NGO coordinators and drivers. **Beneficiaries:** people receiving food; access stays free.

The buying reason is reduced coordinator work and better execution/reporting across sites. Monetary savings must be measured at each customer; do not promise a tax deduction, carbon credits or guaranteed disposal savings.

**Proposed pricing experiment:** ₹3,000 per donor location per month for coordination and records. Offer a four-week, one-location paid pilot at that price. Charge physical delivery separately at an agreed cost; do not hide rider costs inside low SaaS pricing. A later managed-service tier requires separate operational pricing.

**Illustrative monthly economics:** 20 paying sites x ₹3,000 = ₹60,000 software revenue. If hosting/messaging costs ₹6,000 and direct coordination/support ₹18,000, contribution is ₹36,000, or 60%, before acquisition, product salaries, overhead and tax. These figures assume delivery is separately funded. If delivery costs ₹150 x 300 pickups and we absorb it, ₹45,000 additional cost makes this example negative. This is the key business risk.

**Acquisition plan:** start with one campus or catering network and two NGOs; sell the repeat workflow to the next location under the same operator. Corporate sponsorship can fund a cluster, but sponsorship renewals should be tracked separately from software retention. Do not depend on advertising or commissions charged to recipients.

**Pilot measurements:** completed accepted deliveries / eligible scheduled deliveries, failed pickups, coordinator minutes per rescue, verified quantity delivered and fully loaded delivery cost. Compare against the same operator's previous workflow; do not count unavailable or unsafe food as a successful rescue.

**Go/no-go hypothesis:** secure three paying donor sites, show fewer coordination minutes over four weeks, and obtain one renewal. If sites want the service but refuse to pay enough to cover logistics, use a sponsored/NGO deployment model or stop the commercial SaaS assumption.

## PS2 CityPulse

### 1 Problem statement kya hai

Weather, traffic, transit, pollution aur local incident information alag systems mein aati hai. Formats, locations, update intervals aur reliability alag hain. Resident ya operations manager ko samajh nahi aata ki abhi uske area mein kya relevant hai aur kitna trustworthy hai.

**Actual bottleneck:** a trustworthy decision from inconsistent data. Sirf teen map layers add karna data fusion nahi hai. Events ko common location/time representation, deduplication, source freshness and uncertainty handling chahiye.

Example: heavy-rain advisory + multiple road-waterlogging reports + transit delay may justify checking an affected commute corridor. It does not prove rain caused every delay, or that an unreported road is safe.

### 2 Current market mein kitni need hai

**Evidence:** India's Smart Cities work already includes Integrated Command and Control Centres across all 100 mission cities. The government also reported 100% ICCC completion in an August 2026 release. That demonstrates institutional investment and existing infrastructure; it does not prove a startup can sell a replacement or that every feed is public. [PIB overview](https://www.pib.gov.in/PressNoteDetails.aspx?ModuleId=3&NoteId=154736&lang=1&reg=6), [PIB August 2026 update](https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2293938&lang=2&reg=48)

IUDX already addresses standardized city-data exchange, while commercial GIS systems support streaming geospatial analysis. Generic data unification is therefore an established capability. [IUDX](https://iudx.org.in/), [ArcGIS Velocity](https://www.esri.com/en-us/arcgis/products/arcgis-velocity/overview)

**Assessment:** underlying operational need high; willingness to pay for a general resident dashboard is unvalidated. Integration, data rights, source reliability and institutional buying can dominate the project. Start with a campus/business-park operations manager who can use a narrowly scoped product and approve a pilot.

### 3 Existing solutions and competition

| Solution and type | Pros or established strengths | Drawback or fit limitation for our entry market |
|---|---|---|
| [Esri ArcGIS Velocity](https://www.esri.com/en-us/arcgis/products/arcgis-velocity/overview) — real-time GIS | Streaming ingestion, spatial rules, anomaly/event detection, alerts and maps; hosted and self-hosted options. | Requires data connections and configuration for the customer workflow. A broad GIS platform may be more than a small facility needs; actual cost needs a quote. |
| [CivicPlus SeeClickFix 311 CRM](https://www.civicplus.com/seeclickfix-311-crm/) — civic service platform | Resident requests, assignment, communication and resolution workflows. | Its core workflow is service requests; weather/transit/environment fusion requires relevant integrations. Do not claim integration is impossible. |
| [FixMyStreet](https://fixmystreet.org/how-it-works/) — open-source civic reporting | Routes reports by location/category, makes reports public and supports updates. | Depends on authority participation and continuing operation; a report does not itself guarantee a response or live hazard coverage. |
| [Dataminr First Alert](https://www.dataminr.com/products/first-alert/) — event intelligence | Broad public-source event detection and public-sector alerting; advanced AI capabilities are already marketed. | Enterprise event intelligence needs local workflow fit, contracting and integration. “AI detects incidents” is not a differentiator against it. |
| [FIWARE](https://fiware.org/about-us/smart-cities/) — open-source infrastructure | Context management and standards for integrating heterogeneous smart-city systems. | Framework components still need an application, deployment, connectors and operations; not a finished resident product by themselves. |
| [India Urban Data Exchange](https://iudx.org.in/faqs/) — city data infrastructure | Interoperability and controlled data exchange for cities, developers and integrators. | Dataset availability, permissions and cadence remain source-specific. It is infrastructure to build on, not proof that our needed live feeds exist. |
| [Google Maps](https://support.google.com/maps/answer/3092439?hl=EN) — adjacent consumer substitute | Familiar traffic and transit layers, navigation and broad everyday adoption. | Our proposed facility decision workflow needs authorized source integrations and organization-specific rules beyond a general mapping interface. |
| [IQAir AirVisual](https://www.iqair.com/air-quality-monitors/airvisual-platform) — air-quality product | Air-quality information, forecasts and alerts with weather context. | Air quality is the central domain; it is not by itself a civic service-request and disruption coordination system. |
| [Sahana EDEN](https://sahanafoundation.org/eden/) — open-source humanitarian platform | Assistance/case-management foundations and support for multi-role processes. | An application framework with professional implementation needs; broader humanitarian operations differ from a lightweight everyday neighborhood view. The current branch changed in 2025, so old feature lists need care. |

ICCC deployments and municipal dashboards are additional incumbent infrastructure, not one interchangeable vendor. Existing weather/transit apps are important substitutes because users already have them.

### 4 Kya add karein jisse product alag dikhe

Working concept: **CityPulse Evidence**, a proposed local operations briefing with visible uncertainty.

**Signature demo:** three feeds describe a disruption; the UI shows an evidence-backed summary. Then one feed stops, two reports turn out to be duplicates, and another report is corrected. Confidence and affected-area statements update visibly; missing coverage never becomes a green “all clear.”

| Proposed capability | How it works and why it matters | Novelty and implementation scope |
|---|---|---|
| Evidence attached to each statement | Every summary links to event IDs, source, observation time, ingestion time and supported location. | Provenance is established practice; MVP implementation. |
| Freshness and coverage separate from severity | Per-source freshness rules; display “unknown” for missing observations, not a healthy score. | Established uncertainty handling; useful product execution, not first-ever. MVP. |
| Cross-feed links without causal claims | Group events by time, place and type; deduplicate shared reports; label “possible connection.” | Adapted data-fusion technique. MVP with explicit rules. |
| Next action for one persona | Campus operator sees “verify Gate B access” with relevant evidence and escalation owner. Decisions remain with the operator. | Buyer-specific workflow hypothesis. MVP one action category. |
| Corrections and replay | Persist events and revisions; replay what the system knew at a chosen time. | Event-sourcing/replay are established; demo advantage. MVP small dataset. |
| Personalized accessibility needs | Later, let a user choose mobility constraints and relevant facilities without making unsupported route-safety guarantees. | Future research/pilot item; not needed in 24 hours. |

**Defensibility:** maintained local connectors, source-quality history, agreements to access useful feeds, and daily integration into operators' decisions. A nicer dashboard or LLM-generated sentence is easy to copy.

**MVP:** one area, three clearly labelled live/public or synthetic feeds, canonical event schema, rolling-window rules, evidence timeline and stale-feed demonstration. Use template summaries first. Avoid a synthetic 0–100 city-health score whose meaning cannot be justified. ArcGIS and Dataminr already cover much of general event fusion; our narrower advantage is a hypothesis to test.

### 5 Business model kaise banega

**Buyer:** campus administration, business park, commercial-property operator or facilities team. **Users:** duty managers/security/facilities coordinators; residents or employees can receive a limited free briefing. Avoid beginning with an all-city government tender unless a partner already exists.

**Proposed offer:** ₹15,000 per location per month, with ₹25,000 one-time setup for three agreed feeds and one workflow. Sell a four-week paid pilot at ₹15,000; setup fee can be credited only under an explicit pilot offer. Additional data licences and custom connectors need separate quotes.

**Illustrative monthly economics:** 10 sites x ₹15,000 = ₹1,50,000 recurring revenue. If cloud/licensed data/notifications cost ₹25,000 and direct feed maintenance/support costs ₹35,000, contribution is ₹90,000, or 60%, before acquisition, core development, overhead and tax. These costs are assumptions. A proprietary feed contract or bespoke support can remove that margin. One-time setup revenue is not MRR.

**Acquisition:** secure one campus design partner, identify one repeated decision, and quantify time spent checking sources. Expand via property-management or facilities-service partners only after proving repeatability. Start with existing feeds; do not require buying sensors to demonstrate the core.

**Pilot measurements:** time to assemble a briefing, feed availability, alert precision on labelled events, duplicate-alert rate, operator acknowledgement and actions actually taken. “More alerts” is not a success metric.

**Go/no-go hypothesis:** one paying pilot and a renewal based on recurring use; verify rights and cost for each feed. If users only view the dashboard during a demo, or every new site requires bespoke engineering, revise the product and pricing before expansion.

## PS3 SentinelAPI

### 1 Problem statement kya hai

API correctly log in kara sakti hai, phir bhi wrong user's records return kar sakti hai. Example: user A apne invoice ka identifier change karke tenant B ka invoice access kar leta hai. Authentication says who the caller is; authorization decides which object, field or action they may access.

**Actual bottleneck:** expected access policy ko executable checks mein convert karna, correct accounts/test objects arrange karna, and failures ko reproducible evidence ke saath developer workflow mein lana.

OpenAPI endpoint structure aur authentication schemes bata sakta hai; business ownership rules automatically complete nahi hote. Customer-approved expectations are needed. HTTP 200 alone does not prove a leak: the returned data may be public, intentionally shared, empty or redacted. Conversely, checking only status codes can miss a policy failure.

### 2 Current market mein kitni need hai

**Evidence:** OWASP's 2023 API list includes broken object-level, property-level and function-level authorization. It is an awareness/risk framework, not a census establishing that a specified percentage of breaches are API breaches. [OWASP API Security risks](https://api-security.owasp.org/editions/2023/en/0x00-header/)

Postman's 2025 survey of over 5,700 developers, architects and executives reports that 65% of organizations generate revenue from APIs and 51% of developers worry about unauthorized or excessive API calls by AI agents. This is a vendor-run respondent survey and a directional demand signal, not representative proof of India's market size. [Postman State of the API 2025](https://www.postman.com/state-of-api/2025/)

**Assessment:** strongest recurring software-business opportunity of the three, with a clear engineering/security buyer and deployment-linked usage. Competition is also strongest. The supplied brief's suggestion that automated testing is unavailable is too broad: many current products provide it, including open-source alternatives.

**Initial customer hypothesis:** B2B multi-tenant SaaS teams with roughly 10–100 engineers, frequent releases, a staging environment and an engineering lead owning access-control risk. This segment is a proposal, not validated market research.

### 3 Existing solutions and competition

| Solution and type | Pros or established strengths | Drawback or fit limitation for our entry market |
|---|---|---|
| [Akto](https://docs.akto.io/readme-1) — API-security platform | Discovery, business-logic testing, role contexts and CI/CD; directly overlaps BOLA testing. | Needs suitable traffic/spec/test context and credentials. A token-swap scanner cannot claim to invent its existing functionality. |
| [APIsec](https://www.apisec.ai/) — automated security testing | Markets continuous exploit/business-logic validation with actionable evidence. | Broad direct competitor; our small-team setup time, precision and price advantage require a real comparison, not assumptions about missing capabilities. |
| [StackHawk](https://docs.stackhawk.com/getting-started/) — developer DAST | Local/CI scanning, authenticated testing and multi-user business-logic checks. | Running application/auth setup is necessary. Our opportunity must beat an existing developer workflow on a narrow measurable outcome. |
| [Escape](https://escape.tech/) — offensive-security platform | Business-logic-aware DAST, agentic testing and engineering-workflow integration. | Strong overlap with “AI API pentester.” Contract and onboarding fit need evaluation; broad coverage claims are vendor claims. |
| [42Crunch](https://docs.42crunch.com/latest/content/tasks/audit_api_security.htm) — API contract security | OpenAPI audit and conformance scanning with CI integration. | Contract validation does not automatically supply every business-specific ownership rule; those expectations still need modelling. |
| [Salt Security](https://salt.security/) — API and agentic security | Discovery/context and API/agent/MCP security positioning; runtime-focused breadth. | Enterprise context and integrations must fit the customer. A tiny offline regression runner serves a narrower job, not equivalent protection. |
| [Akamai API Security](https://www.akamai.com/products/api-security) — enterprise platform | Discovery, testing, analytics and response; includes automated business-logic tests and CI integration. | Large distributed-environment scope can exceed a small team's first need. Noname is part of this product lineage, not counted as a separate independent competitor. |
| [Traceable](https://www.traceable.ai/api-security-platform) — API-security platform | API/data-flow visibility and detection capabilities. | Integration and customer context matter; compare deployment needs with a local runner. Its company page records a 2025 merger with Harness, so do not count them as unrelated entries. |
| [Burp Suite](https://portswigger.net/burp/documentation/scanner/api-scanning-reqs) with [Autorize](https://github.com/Quitten/Autorize) — scanner and authorization extension | Mature API scanning plus automated replay with lower-privileged/unauthenticated contexts through Autorize. | Expert configuration and response interpretation remain important; CI policy lifecycle needs deliberate setup. Burp and the extension have distinct capabilities/licensing. |
| [ZAP](https://www.zaproxy.org/docs/docker/api-scan/) — open-source scanner | API scans from definitions and extensible automation; credible low-cost baseline. | Application-specific authorization expectations and test identities require configuration; a free scanner is a real alternative to paying us. |
| [Schemathesis](https://github.com/schemathesis/schemathesis/blob/master/docs/guides/stateful-testing.md) — testing framework | Schema-driven and stateful testing with custom hooks and realistic data integration. | Security intent and ownership assertions are still application-specific. It can be a building block or a substitute for custom tests. |
| [Microsoft RESTler](https://github.com/microsoft/restler-fuzzer) — research/open-source fuzzer | Stateful REST request-sequence generation based on API dependencies. | Fuzzing requires setup and an expected-behavior oracle for business authorization; sequence generation itself is established. |
| [Planck Proof Operator](https://planckproof.ai/api-authorization-testing) — API authorization testing product | Explicitly describes multi-identity, role/object/tenant matrices and reproducible authorization evidence. | Especially close to an evidence-first positioning. The current website establishes claimed overlap, not independently verified performance or adoption. |

Further substitutes include application teams' own tests and authorization/policy frameworks. A customer may choose to improve those instead of buying a scanner. Traceable/Harness relationship source: [Traceable company](https://www.traceable.ai/company).

### 4 Kya add karein jisse product alag dikhe

Working concept: **SentinelAPI Access Regression**, initially focused on access removal and tenant isolation in staging APIs.

One-line promise: **“Jis user ka access remove kiya, kya uske existing token se ab bhi data mil raha hai? Evidence dikhao aur us behavior ka regression test rakho.”**

**Core workflow:** import OpenAPI -> map test identities and fixture objects -> approve expected access rules -> run bounded requests -> show mismatch evidence -> apply a developer-reviewed fix -> rerun -> export a repeatable test.

| Proposed capability | Mechanism and required data | Why it matters and what can fail |
|---|---|---|
| Explicit access contract | Role, tenant, object owner, allowed fields, sharing state and revocation deadline stored in reviewed YAML/JSON. | A known expectation gives tests a meaningful oracle. Wrong policy means misleading findings; unknown intent stays inconclusive. |
| Same-account before/after revocation check | Read a sandbox object with a permitted identity; revoke its grant using an authorized admin fixture; replay the old credential after the specified deadline. | Detects the tested stale permission path. Revocation timing is application-specific, not universally immediate. |
| Known-object evidence | Seed distinguishable synthetic markers and compare returned object/field contents against policy, with permitted and denied controls. | More credible than flagging every 200. Shared/public objects and failed authentication must be handled correctly. |
| Finding tied to a repeatable sequence | Record sanitized request order, fixture names, policy version and assertions; export a runnable test using secret references. | Developer can reproduce without copying secrets into a report. Environment drift can make results inconclusive. |
| Local runner and selective evidence export | Run against an allowlisted staging API inside the customer's environment; send redacted findings only if configured. | Reduces data exposure. Local operation is not novel and does not remove the need to secure logs and configuration. |
| Coverage of intended relationships | Show identities, object relationships and transitions actually exercised; list unsupported/missing cases. | Prevents a “100% secure” result based on a few endpoints. Denominator must come from reviewed scope. |
| Later check for bulk/export paths | Apply the same reviewed boundary to list, export and background-job retrieval flows. | Useful expansion hypothesis; requires more fixtures and state handling. Outside the smallest MVP. |

**Novelty audit result: ADAPTED, not proven new.** Multi-identity replay, matrices, contract-based checks and CI gating already exist in products and OWASP guidance. Stateful API research also predates this project; AuthProbe is additional recent related work. No claim of algorithmic novelty or patentability is supported. [OWASP authorization regression guidance](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Regression_Testing_Cheat_Sheet.html), [AuthProbe paper](https://arxiv.org/abs/2607.20574), [RESTler research](https://www.microsoft.com/en-us/research/wp-content/uploads/2021/03/RESTler.pdf)

**What we would compete on:** fast setup for one supported stack, a clear revocation timeline, useful evidence and reliable exported tests. Test those advantages against Akto/StackHawk/custom pytest—not against a deliberately weak imagined scanner. If a comparator delivers the same result with less effort, revise the idea.

**Potential long-term moat:** customer-approved policy mappings, reliable identity/fixture adapters, consented and sanitized evaluation cases, historical regression context and distribution through development/security partners. Core ideas are copyable. Customer data is not automatically ours to pool, and lock-in should not depend on hiding their tests.

### Smallest credible 24 hour prototype

Use one local REST demo API with two tenants, three identities, known synthetic invoice records, grant/revoke operations and documented expected policy. Include a vulnerable version and a fixed version. Build one end-to-end BOLA/authorization-regression capability first. Field-level exposure is P1, not a mandatory expansion to every OWASP category.

Core engine: deterministic request orchestration, policy checks and evidence comparison. Python with an HTTP client and pytest is a practical option if the team knows it; a small web report can display the results. JSON/SQLite is sufficient for local runs. No GPU, vector database, Kubernetes or autonomous agent is required. Optional AI can draft explanations from redacted structured evidence; it cannot decide the expected access policy or whether a vulnerability is confirmed.

Golden demo: authorized read passes -> cross-tenant read reveals a seeded marker and fails -> access removal test reveals stale access after the declared deadline -> show request/evidence timeline -> apply the prepared, disclosed fix -> rerun identical tests -> violations disappear while allowed requests still pass. No hardcoded “vulnerability found” screen.

Acceptance targets, not measured results: a reproducible scan of the fixture API, correct distinction between public/shared/private objects, no secret in exported reports, and explicit incomplete status on timeout/expired credential. Use at least 20 labelled cases including secure controls; report raw TP/FP/FN counts rather than generalizing toy-fixture accuracy to the internet.

Build schedule assumption: hours 0–3 fixture and policy contract; 3–8 first complete scan and report; 8–13 revocation sequence and controls; 13–17 regression export and UI; 17–21 failure tests; 21–24 feature freeze, rehearsal and backup recording. If the first vertical slice does not work by hour 8, cut to object-level cross-tenant checks and honest coverage reporting.

All scans stay inside the supplied local/sandbox target. Explicit host/method scope, request budgets, timeouts, no out-of-scope redirect following, and secret redaction are part of the core implementation. An unavailable identity or unknown policy yields incomplete/inconclusive, not a passing security verdict. The product name does not make it a full zero-trust architecture.

### 5 Business model kaise banega

**Economic buyer:** CTO, engineering manager or AppSec lead at a multi-tenant SaaS business. **Daily users:** backend/platform engineers. **Purchase trigger:** recurring access-control regressions, a customer security review, or too much manual authorization testing during releases.

**Paid outcome:** maintain and rerun a reviewed access-control test suite, reduce reproduction/triage effort, and provide evidence that specified boundaries were checked on a release. No claim of breach prevention guarantees, certification or replacing all pentesting.

#### Proposed packaging to validate

| Plan | Suggested price | Proposed scope and purchase reason |
|---|---:|---|
| Community | Free | Local runner and a demo adapter; builds trust and lets teams evaluate the mechanism. |
| Starter | ₹4,999/month | One API service, shared findings and bounded scheduled/CI runs; small team's entry plan. |
| Team | ₹14,999/month | Up to five API services, shared policy history, regression export, integration and scoped onboarding support. |
| Private deployment | Quote after discovery | Customer-specific deployment, identity setup, support and retention requirements. Do not promise enterprise support before staffing it. |

An API service means one defined application boundary, not one endpoint. Document scan/run/request limits and paid overages before selling; “unlimited scans” would obscure cost. Hosted metadata, test execution and support have different cost drivers. The runner can use the customer's CI compute, which must be disclosed and included in their ROI comparison.

A paid 30-day pilot can be offered at ₹10,000 for one staging API, one identity adapter and one policy-review session; credit against subscription only if explicitly agreed. Scope custom integration separately. Do not charge per vulnerability found, which incentivizes noise.

#### Illustrative unit economics

At 20 Team customers: 20 x ₹14,999 = **₹2,99,980 MRR**; annualized run rate = **₹35,99,760**. This is a scenario, not a forecast or TAM.

Assume ₹3,000 direct cost per Team customer per month: ₹1,000 for platform/storage/notifications and ₹2,000 for direct support/allocated onboarding. Total direct cost = ₹60,000; monthly contribution = **₹2,39,980**, about **80%**. Engineering salaries, sales, acquisition, overhead, tax and customer's CI costs are excluded, so this is not net profit.

If direct support/integration raises cost to ₹8,000 per customer, contribution falls to ₹1,39,980, about 47%. Onboarding effort is therefore a central product metric. At an assumed ₹30,000 acquisition cost and ₹11,999 monthly customer contribution, simple payback is about 2.5 months; this excludes churn/financing and is unvalidated. A credible LTV estimate requires actual retention data.

**Price-to-value validation example:** if a customer independently measures 10 engineering hours saved per month and values that time at ₹2,000/hour, the estimated time value is ₹20,000. A ₹14,999 plan might be supportable, but only if setup, false positives and ongoing maintenance do not consume that saving. Do not sell using invented breach-loss calculations.

#### First 90 days

| Period | Concrete work | Evidence needed to continue |
|---|---|---|
| Days 1–14 | Interview 10 engineering/security leads. Ask about their last authorization regression, current tests, setup effort, budget owner and purchase process. Show a working local demo. | Repeated specific pain plus at least three teams willing to provide a scoped staging integration; generic praise does not count. |
| Days 15–30 | Run three scoped design-partner pilots, including one paid pilot. Instrument setup/support time and compare with existing tests/tools. | A paid commitment, working identity setup and findings/control tests the customer agrees are correct. |
| Days 31–60 | Standardize one stack/identity adapter, improve evidence, add CI integration and charge proposed subscription prices. | At least two conversions, repeated runs on actual changes and manageable support costs. Targets, not expected certainty. |
| Days 61–90 | Seek renewals and referrals; explore security consultancies/development agencies as channels. Add another adapter only for repeated demand. | Retained usage and revenue with a sustainable contribution margin. If setup remains bespoke, price it as a service or narrow the scope. |

**Go/no-go criteria:** target median integration below two engineering hours for the supported adapter, customer-confirmed usefulness, no known false-positive blocking gate in pilot validation, and renewals. Measure distributions and raw cases; “zero observed false positives” in a small pilot is not a universal accuracy guarantee.

First use advisory CI results. Enable a blocking gate only for reviewed deterministic assertions with agreed failure behavior. Separate scan-incomplete from confirmed policy violations. Do not silently label a timeout secure.

## Cross problem comparison

These are qualitative judgments under the stated assumptions, not measured market scores or probabilities of winning.

| Decision factor | PS1 Food rescue | PS2 Civic fusion | PS3 API security |
|---|---|---|---|
| Need | Strong social/operational need | Strong information/operations need | Strong engineering/security need |
| Most plausible first payer | Institutional donor/caterer | Campus/property operator | SaaS engineering/security lead |
| Existing competition | Mature platforms plus strong local networks | Mature GIS, intelligence and civic infrastructure | Very crowded, including strong free alternatives |
| Main adoption bottleneck | Trusted local execution and transport | Useful feeds and a recurring decision workflow | Identity/policy setup, precision and trust |
| Recurring software revenue fit | Medium, with logistics separated | Medium if connectors repeat across sites | Strongest hypothesis because tests recur with releases |
| 24-hour demo feasibility | Good with bounded simulated logistics | Good with labelled feed replay | Good only with backend/security skill and strict scope |
| Memorable honest demo | Driver cancels; feasible rescue plan changes | Feed dies; evidence/uncertainty changes | Access revoked; old token still leaks; fix verified |
| Expansion burden | Local operations per geography | Data/integration work per customer/city | Adapters and policy coverage per stack/customer |
| Major business failure | Delivery/support cost exceeds willingness to pay | Interesting map with no paying repeat use | Existing tools/custom tests solve the same job better |

**Selection:** PS3 for a software business and technically credible local demo, conditional on team skill. Its relative advantage is monetization and repeat workflow, not a vacant competitive landscape. PS1 can be the better hackathon choice with strong NGO access and limited security experience. PS2 rises in priority with a real facility/data partner.

No defensible evidence establishes a guaranteed hackathon rank, a universally superior track or a novel invention. The decision should change if customer access or team skills differ from the assumptions.

## What competitors can copy and what we must earn

“Kisi ne socha bhi nahi aur koi add bhi nahi kar payega” ko literal requirement banana practical nahi hai. A finite public search cannot establish that nobody has thought of an idea, and established vendors can add visible features.

| Easy to copy | Harder to reproduce after sustained execution |
|---|---|
| A chatbot, map, summary or attractive dashboard | Verified domain workflows and dependable operating relationships |
| A prompt or basic token-swap script | Maintained integration/fixture adapters with measured quality |
| Routing or anomaly detection from common libraries | Reliable outcome data collected with appropriate permission |
| A demo claim of accuracy | Reproducible evaluation on diverse cases and customer renewals |
| Low initial pricing | Distribution, efficient onboarding and sustainable support costs |

Start with one measurable advantage. For PS1: fewer failed accepted pickups at viable cost. For PS2: faster useful briefings with honest coverage. For PS3: faster correct authorization regression setup and triage. Benchmark the proposed advantage before making it a marketing claim.

## Evidence gaps and next decisions

No reliable bottom-up TAM estimate is claimed. Global food waste, number of smart cities, or total API traffic is not the revenue market for these products. Calculate reachable market from an actual list of qualified buyers x validated annual spend; then reduce for coverage, access and realistic acquisition capacity.

Open items: team skills and effective build hours; access to pilot customers; geographic coverage of relevant competitors; commercial pricing quotes; local feed licences; actual integration effort; measured performance; paid willingness to buy; and branding availability.

Source dates vary. Quantitative sources retain their original reference periods. Official product pages establish what vendors currently describe, not independent comparisons of quality. Search results were checked on 24 September 2026; the landscape will change.

The most valuable next investment is a narrow working demo and a buyer conversation about an actual past failure. A long feature list is not evidence of demand.
