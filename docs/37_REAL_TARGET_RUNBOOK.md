# Real staging target runbook

BoundaryLab starts with **no active target**. A real probe is enabled only through a reviewed local registry supplied at process start. The browser cannot add URLs, tokens, resource IDs or expected marker values.

This mode is intentionally read-only. It sends one fixed `GET` request per configured identity to one fixed path template. The target must be a service the operator is authorized to test and must be reachable on numeric loopback, either as a local staging service or through an approved local forward/proxy.

## What the probe proves

For one stable staging resource:

- every `allow` identity must receive a 2xx response containing the configured proof marker;
- every `deny` identity must receive an approved deny status without the proof marker;
- configured forbidden JSON pointers must be absent for that identity;
- missing proof, unusual responses and transport failures become `inconclusive`, never a pass.

It does not crawl, mutate, brute-force IDs, follow redirects or certify the API beyond this declared boundary.

## 1. Prepare safe staging data

Create a non-production resource with a unique, non-PII proof value in a stable JSON field. Prepare dedicated short-lived tokens for at least one allowed and one denied identity. Use least privilege and an expiry suitable for the test window.

The proof marker should identify the exact resource without containing customer data. BoundaryLab compares it in memory and persists only `<MATCHED_PROTECTED_MARKER>`.

## 2. Create the reviewed registry

Copy the files under `examples/real-target` into a private working directory. Replace the example OpenAPI document with the actual reviewed contract and edit the registry so these values match exactly:

- `origin`: numeric loopback HTTP(S) origin, with no path;
- `operation_id`: the OpenAPI `GET` operation ID;
- `path_template`: the exact OpenAPI path containing one `{resource_id}` placeholder;
- environment variable names for resource ID, proof marker, build ID and bearer tokens;
- allowed deny statuses and identity-specific forbidden response pointers.

The registry contains references only. Do not put tokens, marker values or resource IDs in JSON.

## 3. Set runtime values

PowerShell example using the names from the template:

```powershell
$env:BOUNDARYLAB_ORDER_ID = 'staging-order-2026-09-25'
$env:BOUNDARYLAB_ORDER_MARKER = 'random-non-pii-proof-value'
$env:BOUNDARYLAB_ORDER_BUILD = 'orders-api-staging-2026.09.25'
$env:BOUNDARYLAB_OWNER_TOKEN = '<short-lived-owner-token>'
$env:BOUNDARYLAB_OUTSIDER_TOKEN = '<short-lived-outsider-token>'
$env:BOUNDARYLAB_BOOTSTRAP_SECRET = '<16-plus-character-local-secret>'
```

Environment values are read by the worker at execution time. Bearer headers are redacted before evidence persistence. Resource IDs are URL-encoded and the evidence path retains only the reviewed template.

## 4. Start the workbench

```powershell
& '.\.venv\Scripts\python.exe' -m boundarylab.devserver `
  --bootstrap-secret $env:BOUNDARYLAB_BOOTSTRAP_SECRET `
  --target-config '.\private-targets\registry.json' `
  --data-dir '.\var\staging-probe'
```

Open `http://127.0.0.1:8080`. The target card must show **Authorized staging**, `ready`, the correct fixed origin and the expected identity count. Review the Policy screen before starting the run.

If an environment reference is absent, the target is shown as not ready and the control API rejects the run.

## 5. Interpret the result

- `pass_in_scope`: every declared identity produced the expected proof for this resource/build;
- `blocked`: a denied identity received the marker/forbidden field, or a legitimate identity was denied;
- `incomplete`: the response did not establish the declared contract or execution stopped.

Exported HTML and JSON reports retain the target alias, operator-supplied build ID, policy hash, case denominator, redacted evidence and incomplete context. They do not retain token values, the resource ID or the proof marker.

## Explicit lab mode

The three-build invoice benchmark remains available only when explicitly requested:

```powershell
& '.\.venv\Scripts\python.exe' -m boundarylab.devserver --with-lab-fixtures
```

The UI labels these targets **Disclosed lab**. Lab results are useful for the mentor demonstration and regression tests; they are never presented as customer findings.

## Current boundary

Real mode covers reviewed read authorization and property exposure for a stable staging resource. Automated grant/revoke/background-job mutation on an external product still requires a product-specific adapter with setup and cleanup semantics. Public multi-tenant execution additionally requires isolated runners, managed secrets, DNS/IP pinning, SSO/RBAC, Postgres, observability and an independent security review.
