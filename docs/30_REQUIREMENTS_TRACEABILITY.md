# Requirements traceability

All implementation status is **planned** until actual evidence is attached. This table prevents the signature idea from replacing the original problem statement.

| Original requirement / extension | Product requirement | Implementation owner/surface | Acceptance evidence |
|---|---|---|---|
| OpenAPI or captured traffic input | R01 | Spec importer/control API | Valid 3.1 JSON imported, unsupported versions explicit; traffic capture excluded |
| Multiple authenticated sessions | R02 | Secrets adapter/preflight | Alice/Bob/Mallory identities verified; wrong token inconclusive |
| BOLA/IDOR | R04 | Preview scenario/assertions | C01–C04 against three variants |
| Excessive data exposure | R05 | Field oracle | C06–C07; explicit field policy |
| Authentication weakness | R02,R04 | Anonymous case and identity checks | C04 and failure-context tests; no broad auth audit claim |
| Rate-limit weakness | R13 P1 | Optional quota-contract check | Bounded configured quota test if implemented; otherwise unsupported |
| Prioritized actionable findings | R07,R09 | Findings/report | Category, impact reason, evidence and reproduction |
| Engineer/nontechnical output | R09 | HTML/JSON artifacts | Executive explanation plus technical appendix |
| Authorized/sandboxed use | R10 | Scope registry/transport/fixtures | Redirect, DNS, namespace and budget tests |
| CI continuous testing optional | R12 P1 | CLI | Same engine, documented 0/1/2 exit codes if implemented |
| LLM generation optional | R14 P1 | Explanation adapter | No effect on core verdict, injection tests if implemented |
| Temporal permission extension | R06 | Lifecycle runner | C08–C12 with acknowledged revocation timing |
| Correct repair without lost functionality | R08 | Comparator/positive controls | Owner-only rejected; fixed passes tested scope |
| Working durable product | R11 | Worker/DB/recovery | Restart preserves reports; crashed mutation not replayed |

## Implementation evidence template

`Requirement | commit/build | test/run IDs | observed result | remaining limitation | reviewer/date`.

Do not replace the evidence column with screenshots of the synthetic prototype. If a priority-1 feature is omitted, say so in the UI/report/pitch. For the user’s two-day request, a reliable complete P0 workflow takes precedence over unfinished breadth.
