# BoundaryLab UI benchmark and redesign record

Research date: 24 September 2026  
Scope: authenticated developer, observability, API and security consoles with dense operational data.

This is a pattern study, not a visual clone exercise. BoundaryLab keeps its own evidence-first information model, red/grey/navy/white palette and local safety constraints. The review asked one question of every product: **how does the interface help an operator move from signal to a defensible action without losing context?**

## Twenty-product benchmark

| Product | Strong interaction pattern observed | Risk or drawback to avoid | BoundaryLab decision |
|---|---|---|---|
| [Linear](https://linear.app/changelog/page/3) | Calm hierarchy, dim navigation, consistent headers and compact controls | Beautiful density can hide unfamiliar workflows | Dim sidebar plus a single, quiet current-stage header |
| [Vercel Observability](https://vercel.com/products/observability) | Mission-control summary followed by route-level drill-down | KPI cards without a release decision become decoration | Four operational facts only; every metric points to evidence |
| [Sentry issue details](https://docs.sentry.io/product/issues/issue-details/) | Issue header, status action, trend and event detail in one hierarchy | Large event payloads can dominate the page | Run question first, sanitized payload only in a drawer |
| [Datadog App and API Protection](https://docs.datadoghq.com/security/application_security/attack_summary/) | Exposure and attack summary that pivots into traces | Broad security dashboards can drown a narrow decision | Keep the unit of work a permission promise, not a generic score |
| [Grafana](https://grafana.com/docs/grafana/latest/visualizations/dashboards/use-dashboards/) | Reusable panels, breadcrumbs, filters and drill-down links | Excessive customization makes shared views inconsistent | Fixed mentor-ready layout with contextual drill-down |
| [GitHub security overview](https://docs.github.com/en/code-security/how-tos/view-and-interpret-data/analyze-organization-data/viewing-security-insights) | Detection/remediation/prevention views and globally applied filters | Aggregate numbers can omit permission or coverage context | Always show build, policy, denominator and incomplete state |
| [GitLab security dashboards](https://docs.gitlab.com/user/application_security/security_dashboard/) | Advanced search, vulnerability trends and exportable charts | Enterprise navigation can become deep and fragmented | Five top-level tasks with flat, verb-led labels |
| [Cloudflare custom dashboards](https://developers.cloudflare.com/analytics/custom-dashboards/) | Global filters change every chart; rare events remain inspectable | Charts can imply certainty when data is sampled | Label HAR as a sample and never infer “zombie API” from absence |
| [Postman](https://learning.postman.com/docs/getting-started/basics/navigating-postman) | Header + workspace + workbench model with searchable resources | Too many nested panels shrink the actual work surface | Persistent product shell and one task-focused canvas |
| [Auth0 Security Center](https://auth0.com/docs/secure/security-center) | Security pulse with immediate paths to event inspection | Red-heavy threat screens create constant visual alarm | Red is reserved for action, active scope and confirmed violations |
| [Clerk Dashboard](https://clerk.com/docs/guides/dashboard/overview) | Workspace, application and environment context stays visible | Multiple context pickers can consume the header | Compact breadcrumb with fixed local policy context |
| [Supabase](https://supabase.com/docs/guides/deployment/branching/dashboard) | Branch/environment context in the top bar and task tools in the sidebar | Product-wide tools can compete with the selected resource | Current workflow and trusted local scope remain persistent |
| [Render Dashboard](https://render.com/docs/render-dashboard) | Workspace search, breadcrumbs, service list and resource detail | A generic resource list does not explain release risk | Run list shows outcome; detail opens the actual policy question |
| [Aikido main feed](https://help.aikido.dev/getting-started/core-functionalities/main-feed) | Focus view, grouped findings, filters and an actionable details sidebar | Auto-triage can obscure why a finding left the queue | Candidate approval is append-only and requires rationale |
| [Semgrep AppSec Platform](https://semgrep.dev/docs/for-developers/resolve-findings-through-app) | Status-first triage and bulk focus on actionable findings | “Priority” can become an opaque model judgment | Deterministic verdict stays primary; AI output is a labelled draft |
| [Wiz](https://www.wiz.io/platform) | Relationship context and attack paths reduce isolated-alert noise | Graphs become spectacle if they do not change an action | Use a temporal permission path with measured evidence nodes |
| [Orca Security](https://orca.security/resources/press-releases/attack-path-analysis-and-business-impact-score/) | Attack-path prioritization connects weaknesses to impact | Business scores can hide the exact evidence | Show expected, observed and sanitized request before remediation |
| [Tailscale admin console](https://tailscale.com/kb/1017/install/) | Restrained admin UI around devices, users and permissions | Simple tables can become ambiguous without state explanations | Compact rows retain explicit lifecycle/status labels |
| [New Relic dashboards](https://docs.newrelic.com/docs/query-your-data/explore-query-data/dashboards/manage-your-dashboard/) | Filter bar, focused charts, pages and presentation mode | Arbitrary panel layout weakens a rehearsed demo | Stable composition designed for a two-minute mentor walkthrough |
| [SonarQube Cloud](https://docs.sonarsource.com/sonarqube-cloud/managing-your-projects/retrieving-projects) | Quality gate, health snapshot and click-through issue breakdown | Rating badges can oversimplify false-positive review | Separate deterministic failures, inconclusive checks and human review |

## Patterns selected for BoundaryLab

1. **Persistent orientation.** The shell exposes product, current task, local control-plane health and locked policy once. The former duplicate workflow rail was removed.
2. **Progressive disclosure.** A run starts with the release question and four facts. Raw OpenAPI/HAR editors are collapsed until requested, and request/response excerpts stay in a focused evidence drawer.
3. **Decision-shaped density.** Tables use sticky headers, compact rows and status-first scanning. Red is limited to confirmed violations and the primary action.
4. **Evidence before remediation.** Deterministic case results remain above AI or deterministic repair guidance.
5. **Safe import clarity.** OpenAPI and HAR inputs explain what is required, what is optional, what is discarded and which hard limits apply.
6. **Human-governed inference.** Candidate rules expose confidence and required setup. Approval or rejection needs rationale and creates an append-only record.
7. **Demo continuity.** The navigation order matches the story: Discover → Define → Verify → Compare → Handoff.
8. **Failure recovery.** A partial workspace load no longer impersonates an expired session. The operator sees the concrete control-API error and can retry without losing state.

## Visual system

- Canvas: cool grey `#f7f8fa`; cards: white.
- Navigation and code surfaces: navy `#071426` through `#274463`.
- Primary action and confirmed security failure: red `#b4232b`; softer red surfaces for attention.
- Neutral borders and supporting text: grey scale; success is a restrained dark green with a text label.
- Radius: 8–16 px; shadows remain shallow except for modal/drawer layers.
- Body controls remain at least 42 px; focus rings, text labels and status dots avoid color-only meaning.

## Verification targets

- Desktop widths: 1440 × 900 and 1280 × 800.
- Compact browser: 720 × 858.
- Mobile widths: 390 × 844 and 360 × 800.
- No horizontal page overflow; only code, tables, timelines and horizontal run lists may scroll.
- All five views must render with persisted demo data.
- Invalid discovery input must preserve the form and show an actionable inline error.
- Evidence drawer must expose an accessible dialog name and remain keyboard reachable.
- Browser console must have no uncaught errors during the full mentor flow.
