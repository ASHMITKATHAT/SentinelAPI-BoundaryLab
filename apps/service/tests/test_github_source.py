from __future__ import annotations

import base64
import json

import httpx
import pytest

from boundarylab.app import Settings, create_app
from boundarylab.github_source import GitHubSourceError, GitHubSourceClient, normalize_source


OPENAPI = {
    "openapi": "3.1.0",
    "info": {"title": "Orders API", "version": "1"},
    "paths": {
        "/orders/{order_id}": {
            "get": {"operationId": "getOrder", "responses": {"200": {}}},
            "patch": {"operationId": "updateOrder", "responses": {"200": {}}},
        }
    },
}


def github_transport() -> httpx.MockTransport:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["user-agent"].startswith("SentinelAPI-BoundaryLab")
        if request.url.path == "/repos/acme/orders":
            return httpx.Response(200, json={
                "html_url": "https://github.com/acme/orders",
                "default_branch": "trunk",
                "private": False,
            })
        if request.url.path == "/repos/acme/orders/contents/contracts/openapi.json":
            assert request.url.params["ref"] == "trunk"
            return httpx.Response(200, json={
                "type": "file",
                "encoding": "base64",
                "sha": "abc123",
                "content": "\n".join(
                    base64.b64encode(json.dumps(OPENAPI).encode()).decode()[index:index + 60]
                    for index in range(0, len(base64.b64encode(json.dumps(OPENAPI).encode()).decode()), 60)
                ),
            })
        return httpx.Response(404, json={"message": "Not Found"})

    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_github_source_imports_openapi_from_fixed_api_host():
    result = await GitHubSourceClient(transport=github_transport()).import_openapi(
        "https://github.com/acme/orders.git",
        "",
        "contracts/openapi.json",
    )
    assert result["repository"] == "acme/orders"
    assert result["ref"] == "trunk"
    assert result["file_sha"] == "abc123"
    assert result["operation_count"] == 2
    assert result["document"] == OPENAPI


@pytest.mark.parametrize("repository", ["https://evil.example/acme/orders", "http://github.com/acme/orders", "acme/orders/extra", "../orders", "acme/.."])
def test_github_source_rejects_non_repository_inputs(repository: str):
    with pytest.raises(GitHubSourceError):
        normalize_source(repository, "main", "openapi.json")


@pytest.mark.parametrize("path", ["../openapi.json", "contracts/../../secret.json", "openapi.yaml", "/"])
def test_github_source_rejects_unsafe_or_unsupported_paths(path: str):
    with pytest.raises(GitHubSourceError):
        normalize_source("acme/orders", "main", path)


@pytest.mark.asyncio
async def test_authenticated_github_import_endpoint_uses_server_side_integration(tmp_path):
    app = create_app(Settings(
        database_path=tmp_path / "boundarylab.db",
        bootstrap_secret="correct-horse-battery-staple",
        targets={},
        allowed_origins=("http://testserver",),
        web_dist=tmp_path / "missing",
        github_transport=github_transport(),
    ))
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
            login = await client.post(
                "/api/v1/session",
                headers={"Origin": "http://testserver"},
                json={"bootstrap_secret": "correct-horse-battery-staple"},
            )
            response = await client.post(
                "/api/v1/integrations/github/import",
                headers={"Origin": "http://testserver", "X-CSRF-Token": login.json()["csrf_token"]},
                json={"repository": "acme/orders", "ref": "", "path": "contracts/openapi.json"},
            )
    assert response.status_code == 200, response.text
    assert response.json()["operation_count"] == 2
    assert response.json()["document"]["info"]["title"] == "Orders API"
