# User flows and permission semantics

## First run

Operator signs in locally → selects a configured target alias → imports OpenAPI JSON → sees supported/unsupported operations → binds three credential references → reviews the policy → approves its immutable hash → starts a run → sees preflight results → inspects cases/evidence → exports report.

No request is sent merely by importing a spec. Approval of a target scope and approval of business policy are separate persisted decisions. A changed spec, scope or policy requires a new reviewed version; earlier approval cannot silently carry over.

## Canonical fixture identities and objects

| Symbol | Meaning |
|---|---|
| `alice` | Owner in tenant A |
| `bob` | Ordinary user in tenant A, legitimate collaborator only on explicitly shared objects |
| `mallory` | Ordinary user in tenant B |
| `anonymous` | No credential |
| `private_invoice` | Alice's private invoice; no sharing |
| `shared_invoice` | Alice's second invoice; Bob may be granted/revoked |
| `internal_bank_ref` | Synthetic owner-only property; not a real bank identifier |
| `content_marker` | Unique per-run synthetic value proving which invoice was returned |

Two separate HTTP surfaces make the fixture realistic and the bugs independent. `getInvoicePreview` returns a compact preview and contains the seeded object-authorization bug. `getInvoice` enforces object permission in all variants but the vulnerable implementation leaks the owner-only property to a valid collaborator. Export retrieval has a separate stale-authorization bug. This separation prevents one always-open detail endpoint from obscuring the export lifecycle issue.

## The lifecycle, exactly

1. Create a run-specific namespace and synthetic records through the internal lab adapter. Verify Alice/Bob/Mallory subject and tenant bindings.
2. Alice grants Bob read/export access to `shared_invoice`. Bob reads the detail and queues an export. Export creation is a legitimate action, not an attack.
3. Poll `getExport` at the global request rate until ready, at most 10 polls within 20 seconds and the overall run deadline. Confirm Bob can retrieve the correct marker while sharing is active.
4. Alice revokes Bob with `revokeShare`. Its 204 acknowledgement establishes local monotonic time `t0`. The policy applies to requests initiated after `t0 + 2,000 ms`; the scanner waits a further 200 ms margin.
5. Confirm Bob is still authenticated via `getMe`, then start a fresh `getExportContent` request. Do not count a request begun before the boundary as a post-revocation probe.
6. Accept denial only when the response is 403/404 **and no protected marker is disclosed**. A 200 without a protected marker is a contract anomaly/inconclusive, not proof of a leak or a pass. A 401 means invalid auth context, not proof of object authorization.
7. Confirm Bob's detail access is denied using an independent grant/revoke setup. Confirm Alice's retrieval using a separate Alice-created export, so this owner control still runs when Bob's queue operation fails on the owner-only implementation.
8. Recheck target build and clean only this namespace. Show incomplete cleanup independently.

Expected success response for content is JSON containing the synthetic marker; P0 does not parse PDFs or follow signed URLs. Polling, setup, preflights and cleanup all use the same bounded transport accounting.

## Compare a repair

Run vulnerable build → run owner-only build → run correct build → verify comparison fingerprints match → display case-by-case differences. The owner-only patch is rejected because active collaborator controls fail. Its dependent temporal cases are inconclusive, not evidence that the patch passed revocation. Correct build must pass every required case.

Policy edits create a new version. Comparing the old and new policy directly is a policy-change review, which is out of P0 scope; the fix-comparison endpoint rejects it.

## Exception flow

Invalid identity/fixture: stop dependent tests with a specific recovery instruction. Timeout: retain completed evidence and mark required unfinished cases inconclusive. Cancel: stop scheduling, attempt permitted cleanup, preserve report. User may retry only by creating a fresh run; do not resume ambiguous mutations mid-scenario.
