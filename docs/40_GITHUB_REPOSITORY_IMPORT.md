# GitHub repository import

BoundaryLab can load a real OpenAPI 3.x JSON contract from a GitHub repository on the **Discover** page. This replaces copy/paste as the primary onboarding path while keeping active API execution fail-closed.

## Operator flow

1. Start BoundaryLab and sign in locally.
2. Open **Discover**.
3. Enter the repository as `owner/name` or `https://github.com/owner/name`.
4. Enter a branch, tag or commit ref. Leave it blank to use the repository default branch.
5. Enter a repository-relative `.json` path such as `contracts/openapi.json`.
6. Select **Connect & import**. The UI shows a running state and then the repository, resolved ref, path, operation count and Git blob SHA.
7. Optionally add a HAR sample, then select **Map API boundary**.

## Private repositories

Set a GitHub token only in the service environment:

```powershell
$env:BOUNDARYLAB_GITHUB_TOKEN = '<fine-grained token with read access to the selected repository>'
& '.\tools\start-local.ps1' -LabFixtures
```

The web UI never asks for, receives or persists the token. Use the narrowest repository scope and rotate the token through the organization’s normal secret-management process.

## Safety boundary

- The server connects only to `https://api.github.com`; a browser-supplied host is never used.
- Redirect following is disabled.
- Repository, ref and path inputs are validated and dot-segment paths are rejected.
- GitHub responses and decoded contracts are size limited.
- Only OpenAPI 3.x JSON is accepted in this release.
- Imports use bounded timeouts and a single outbound connection.
- GitHub errors are sanitized before they reach the browser.

Repository import supplies source data for passive analysis. It does not authorize BoundaryLab to call the repository’s deployed API. Active verification still requires an operator-reviewed target registry, environment-backed identities and the execution limits in the [real-target runbook](37_REAL_TARGET_RUNBOOK.md).
