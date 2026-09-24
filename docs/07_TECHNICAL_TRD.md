# Technical requirements and implementation decisions

## Stack and deployment

Use React + TypeScript + Vite for the interface and Python 3.12 + FastAPI + Pydantic 2 for the service. Use the installed patched Python release and pin resolved dependencies during implementation. Node 24 is the selected LTS line per the [official schedule](https://nodejs.org/en/about/previous-releases); do not invent exact dependency versions in this pack.

FastAPI serves the built frontend and `/api/v1` from one origin. One dedicated Python worker executes scans; one API process handles control requests. SQLite on a local volume stores metadata and queue state; sanitized evidence is in a private directory. Use SQLAlchemy 2 and a simple migration chain. No Redis, vector database or Kubernetes is needed.

Package API and worker in one app container under a small supervisor that forwards shutdown and fails health if either exits. Do not use request-process background tasks as a durable job queue. Docker Compose starts app plus three isolated instances of the fixture image. Only app port 8080 binds to `127.0.0.1`; target containers are internal. A native development path can run the same processes with fixed loopback target ports.

SQLite uses WAL, foreign keys, short transactions and a bounded busy timeout. There is one scan worker and one active run globally. WAL still allows only one writer at a time, so evidence/network I/O must occur outside transactions. Do not deploy this database on shared network storage. [SQLite WAL](https://www.sqlite.org/wal.html)

## Deterministic execution

1. Load immutable approved policy, normalized specification, target authorization and engine/suite identifiers.
2. Claim the queued run atomically; persist start/build fingerprint. Get a new fixture namespace from the approved lab adapter.
3. Resolve runtime secret references and confirm each identity through `getMe`. A token for the wrong subject invalidates the context.
4. Execute the fixed typed scenario graph. Its operations must be present in the spec and approved manifest. No `eval`, imported Python or shell fragments from policy.
5. For every request enforce scope, deadline, budget and body limit; sanitize evidence immediately. Evaluate deterministic assertions against allowed canary fields and response status.
6. On a denied prerequisite, record the relevant case result and mark dependent cases inconclusive. Continue independent cases only when safe.
7. Run namespaced cleanup, persist report/artifact metadata and terminal run state. Cleanup failure is recorded even if the tests completed.

The engine reads responses to determine outcomes. `target variant` is displayed provenance, never an input to verdict logic.

## HTTP transport boundary

All requests go through one `ScopedTransport`; tests never call HTTPX directly. The transport takes a target alias and operation ID, never an arbitrary URL. Resolve approved DNS names, verify each resulting address against configured CIDRs/exact addresses and pin the connection to the checked address while preserving Host/SNI. Reject redirects, userinfo, fragments, mixed schemes, path traversal and unconfigured ports. Set `trust_env=False`, `follow_redirects=False`, TLS verification on for HTTPS. Imported OpenAPI `servers` never authorizes a target.

The loopback/private-address exception is explicit for known lab aliases. The default denies control-plane endpoints, metadata addresses and every undeclared host. Network egress restrictions are a second boundary. Do not expose custom remote-target support until DNS pinning and scope-escape tests pass; local fixed-address demo mode remains the honest P0 fallback.

Limits: 200 total requests/run, of which at most 180 are scenario/setup/poll requests and 20 reserved for permitted cleanup; 2 RPS, one in flight; 5-second per-request total deadline implemented around connect/read/write operations; 120-second total run including a reserved final 10 seconds for cleanup; 64 KiB decoded response cap. HTTPX phase timeouts alone are not a total response deadline. [HTTPX timeouts](https://www.python-httpx.org/advanced/timeouts/), [API defaults](https://www.python-httpx.org/api/)

## Durability and cancellation

Worker heartbeat every 2 seconds; lease expires after 10 seconds. Persist step start before any mutation and completion after evidence commit. If the process crashes between them, mark the run interrupted/incomplete on recovery. Do not automatically replay ambiguous mutations. A rerun gets a new namespace; old cleanup is tracked separately. This intentionally makes no exactly-once claim.

On cancel, stop scheduling new test requests, cancel active I/O within the request deadline and use only the reserved cleanup allowance. Emit a terminal result after cleanup attempt. If cleanup is impossible, retain namespace and a safe cleanup instruction without silently deleting unrelated records.

## Comparison and output

Comparison key is `(policy_hash, spec_hash, suite_hash, fixture_semantics_hash, engine_version)`; origin/build IDs may differ and are shown. A mismatch returns `409 NON_COMPARABLE_RUNS`. Target health/build IDs are checked before and after: a change makes the affected run incomplete. Runtime IDs and timestamps differ legitimately and are normalized only for presentation, not discarded from evidence.

Each report includes case denominators, omitted operations, failed controls, policy version, timing basis, request counts and fixture disclosure. Content hashes detect accidental changes; they do not prove third-party authenticity. AI never changes this output.
