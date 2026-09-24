# Documentation-pack validation

This page records validation of the **specification pack**, not the future scanner application.

## Checks to run before each documentation release

- Parse every JSON file in `contracts/`, `examples/` and `design/tokens.json`.
- Confirm both OpenAPI documents declare `3.1.0`, unique operation IDs and locally resolvable component references.
- Confirm the example policy satisfies the supported policy schema and includes all 12 required case IDs.
- Confirm the evaluation manifest has 12 core and 18 failure cases, and that declared aggregate counts match the cases.
- Resolve every relative Markdown link in this repository; ignore web URLs and fragment-only links.
- Confirm every internal file linked from the root README exists.
- Confirm the prototype retains the visible `DESIGN PROTOTYPE · SYNTHETIC EVIDENCE · NO SCANNER CONNECTED` label.
- Search specification outputs for credential-like values. Examples may contain symbolic references such as `lab/alice`, never real tokens.

## Interpretation

A successful pack validation means the documents and machine-readable examples are internally consistent enough for implementation handoff. It does not mean the API server runs, that security controls work, or that benchmark cases were executed.

Once implementation begins, record application tests and live run IDs separately. Never replace this distinction with a single generic “all tests passed” line.
