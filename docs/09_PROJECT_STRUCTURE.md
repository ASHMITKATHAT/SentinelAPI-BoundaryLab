# Project structure and ownership

## Files delivered now

This workspace currently contains documentation, machine-readable contracts/examples, validation tooling and a standalone design prototype. The directories in the next section are the **proposed application layout**, not a claim that the app exists.

```text
README.md
docs/                    # product, research, build, business and mentor pack
contracts/               # OpenAPI 3.1 and JSON Schema
examples/                # policy, fixture semantics and evaluation manifest
design/                  # interactive synthetic prototype and design tokens
tools/validate_pack.py   # checks this handoff, not the future scanner
```

## Proposed implementation layout

```text
apps/
  web/
    src/
      app/               # routes, API client, operator session
      features/
        setup/           # import, target selection, credential references
        policy/          # policy review and approval
        runs/            # timeline, controls, coverage
        findings/        # evidence drawer and severity
        comparisons/     # policy-compatible fix comparisons
      components/        # table, status, code view, modal, empty state
      styles/            # tokens and responsive layout
    package.json
    package-lock.json
  service/
    boundarylab/
      api/               # FastAPI routes and response models
      domain/            # states, entities, comparison and assessment rules
      db/                # repositories, SQLite config, migrations
      engine/
        compiler.py      # supported policy -> typed plan
        runner.py        # step scheduling, controls, deadlines
        assertions.py   # deterministic oracles
        transport.py    # sole target network boundary
        redaction.py    # sanitize before persistence
        artifacts.py    # JSON and escaped HTML reports
        scenarios/      # invoice-v1 template; no imported user code
      worker/            # queue lease, heartbeat, recovery, cancellation
      adapters/
        fixtures.py     # isolated namespace setup/cleanup
        secrets.py      # configured runtime references
        explanation.py # optional AI, disabled by default
      cli.py
    pyproject.toml
    uv.lock
fixtures/
  invoice_api/
    app.py               # same API, three declared implementation variants
    policies.py          # seeded bugs / owner-only / correct policies
    factory.py           # lab-only namespaced setup and cleanup
tests/
  unit/                  # policy and assessment invariants
  integration/           # transport, worker, DB, actual fixture behavior
  adversarial/           # redirects, secret leaks, broken preconditions
  e2e/                   # one complete UI workflow
deploy/
  compose.yaml
  Dockerfile
  targets.example.json
  supervisor.py
scripts/
  smoke.ps1
  smoke.sh
  seed_benchmark.py
.github/workflows/ci.yml
```

Feature UI modules may depend on shared components and generated API types, not worker internals. Domain rules do not depend on React or HTTP handlers. Scenario modules use the scoped transport interface only. The fixture API never imports scanner assertions: independent implementations reduce circular testing.

Two developers: Developer A owns engine, target fixture and safety; Developer B owns API persistence, UI, artifacts and demo. Share the contracts first. Solo: use the same separation but plain forms and polling; do not build a reusable component framework before the vertical slice works.

Generated lockfiles and migration files must be committed when implementation starts. The documentation pack intentionally contains no fake install or run command for an application that is not present.
