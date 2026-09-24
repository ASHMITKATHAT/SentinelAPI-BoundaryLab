from __future__ import annotations

import httpx
import pytest

from boundarylab.app import Settings, create_app, default_targets


@pytest.mark.asyncio
async def test_session_csrf_and_trusted_target_boundary(tmp_path):
    settings = Settings(
        database_path=tmp_path / "boundarylab.db",
        bootstrap_secret="correct-horse-battery-staple",
        targets=default_targets(),
        allowed_origins=("http://testserver",),
    )
    app = create_app(settings)
    transport = httpx.ASGITransport(app=app)
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            denied = await client.get("/api/v1/targets")
            assert denied.status_code == 401
            assert denied.json()["error"]["code"] == "HTTP_401"

            bad_login = await client.post(
                "/api/v1/session",
                headers={"Origin": "http://testserver"},
                json={"bootstrap_secret": "wrong-secret-value"},
            )
            assert bad_login.status_code == 401

            login = await client.post(
                "/api/v1/session",
                headers={"Origin": "http://testserver"},
                json={"bootstrap_secret": settings.bootstrap_secret},
            )
            assert login.status_code == 201
            csrf = login.json()["csrf_token"]
            assert client.cookies.get("boundarylab_session")

            targets = await client.get("/api/v1/targets")
            assert targets.status_code == 200
            assert [target["alias"] for target in targets.json()] == [
                "demo-vulnerable", "demo-owner-only", "demo-fixed"
            ]

            missing_csrf = await client.post("/api/v1/runs", json={"target_alias": "demo-fixed"})
            assert missing_csrf.status_code == 403, missing_csrf.text

            arbitrary = await client.post(
                "/api/v1/runs",
                headers={"Origin": "http://testserver", "X-CSRF-Token": csrf},
                json={"target_alias": "https://example.com"},
            )
            assert arbitrary.status_code == 422


@pytest.mark.asyncio
async def test_origin_rejected_before_session_creation(tmp_path):
    app = create_app(Settings(
        database_path=tmp_path / "boundarylab.db",
        bootstrap_secret="correct-horse-battery-staple",
        targets={},
        allowed_origins=("http://testserver",),
    ))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/session",
            headers={"Origin": "https://evil.example"},
            json={"bootstrap_secret": "correct-horse-battery-staple"},
        )
    assert response.status_code == 403
    assert "boundarylab_session" not in response.cookies
