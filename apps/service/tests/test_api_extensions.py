from __future__ import annotations

import httpx
import pytest

from boundarylab.app import Settings, create_app


def openapi_document() -> dict:
    return {
        "openapi": "3.1.0",
        "info": {"title": "External Orders", "version": "1"},
        "security": [{"bearer": []}],
        "paths": {
            "/orders/{order_id}": {
                "get": {
                    "operationId": "getOrder",
                    "parameters": [{"name": "order_id", "in": "path"}],
                    "responses": {"200": {}},
                }
            }
        },
    }


def completed_report() -> dict:
    return {
        "target_alias": "demo-vulnerable",
        "build_id": "invoice-vulnerable",
        "policy_version": "invoice-policy-v1",
        "assessment": "blocked",
        "has_incomplete_cases": False,
        "counts": {"pass": 0, "violation": 1, "inconclusive": 0, "skipped": 0},
        "request_count": 1,
        "cleanup_status": "complete",
        "execution_error": None,
        "cases": [{
            "case_id": "C02", "name": "Bob denied", "verdict": "violation",
            "expected": "403", "observed": "200 disclosed marker", "finding_kind": "security_violation",
            "evidence_ids": ["e1"], "reason_code": "PROTECTED_CONTENT_EXPOSED", "required": True,
        }],
        "evidence": [],
    }


def release_report(alias: str, verdicts: list[str]) -> dict:
    cases = []
    for index, verdict in enumerate(verdicts, start=1):
        cases.append({
            "case_id": f"C{index:02}",
            "name": f"Boundary promise {index}",
            "verdict": verdict,
            "expected": "declared behavior",
            "observed": verdict,
            "finding_kind": "security_violation" if verdict == "violation" else None,
            "evidence_ids": [],
            "reason_code": "TEST_VIOLATION" if verdict == "violation" else "",
            "required": True,
        })
    counts = {name: verdicts.count(name) for name in ("pass", "violation", "inconclusive", "skipped")}
    return {
        "target_alias": alias,
        "build_id": alias,
        "policy_version": "release-gate-v1",
        "assessment": "pass_in_scope" if counts["violation"] == counts["inconclusive"] == counts["skipped"] == 0 else "blocked",
        "has_incomplete_cases": bool(counts["inconclusive"] or counts["skipped"]),
        "counts": counts,
        "request_count": len(verdicts),
        "cleanup_status": "complete",
        "execution_error": None,
        "cases": cases,
        "evidence": [],
    }


async def login(client: httpx.AsyncClient) -> str:
    response = await client.post(
        "/api/v1/session",
        headers={"Origin": "http://testserver"},
        json={"bootstrap_secret": "correct-horse-battery-staple"},
    )
    assert response.status_code == 201
    return response.json()["csrf_token"]


@pytest.mark.asyncio
async def test_discovery_and_remediation_endpoints_are_authenticated_persisted_and_honest(tmp_path):
    settings = Settings(
        database_path=tmp_path / "boundarylab.db",
        bootstrap_secret="correct-horse-battery-staple",
        targets={},
        allowed_origins=("http://testserver",),
        web_dist=tmp_path / "missing",
    )
    app = create_app(settings)
    run = app.state.repository.create_run("demo-vulnerable", "http://127.0.0.1:9011")
    app.state.repository.complete_run(run["id"], completed_report())

    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
            csrf = await login(client)
            headers = {"Origin": "http://testserver", "X-CSRF-Token": csrf, "X-Request-ID": "acceptance-42"}

            capabilities = await client.get("/api/v1/capabilities")
            assert capabilities.json()["remediation"]["ai_configured"] is False
            assert capabilities.headers["x-request-id"]
            assert capabilities.headers["cache-control"] == "no-store"

            analysis = await client.post(
                "/api/v1/discovery/analyses",
                headers=headers,
                json={"label": "External API", "document": openapi_document(), "har": None},
            )
            assert analysis.status_code == 201, analysis.text
            assert analysis.headers["x-request-id"] == "acceptance-42"
            assert analysis.json()["summary"]["ownership_candidates"] == 1

            stored = await client.get("/api/v1/discovery/analyses")
            assert stored.json()[0]["id"] == analysis.json()["id"]

            candidate_id = analysis.json()["invariant_candidates"][0]["id"]
            review = await client.post(
                f"/api/v1/discovery/analyses/{analysis.json()['id']}/reviews",
                headers=headers,
                json={
                    "candidate_id": candidate_id,
                    "decision": "approved",
                    "rationale": "Order ownership must be checked before response serialization.",
                },
            )
            assert review.status_code == 201, review.text
            assert review.json()["decision"] == "approved"
            assert review.json()["reviewer"] == "local-operator"
            assert len(review.json()["candidate_sha256"]) == 64
            ledger = await client.get(
                f"/api/v1/discovery/analyses/{analysis.json()['id']}/reviews"
            )
            assert [item["id"] for item in ledger.json()] == [review.json()["id"]]

            unknown_candidate = await client.post(
                f"/api/v1/discovery/analyses/{analysis.json()['id']}/reviews",
                headers=headers,
                json={
                    "candidate_id": "ownership-does-not-exist",
                    "decision": "approved",
                    "rationale": "This candidate was not part of the saved analysis.",
                },
            )
            assert unknown_candidate.status_code == 422

            blank_rationale = await client.post(
                f"/api/v1/discovery/analyses/{analysis.json()['id']}/reviews",
                headers=headers,
                json={"candidate_id": candidate_id, "decision": "rejected", "rationale": "        "},
            )
            assert blank_rationale.status_code == 422

            triage = await client.post(
                f"/api/v1/runs/{run['id']}/explanations",
                headers=headers,
                json={"mode": "deterministic"},
            )
            assert triage.status_code == 201, triage.text
            assert triage.json()["root_causes"][0]["category"] == "object_authorization"

            unavailable_ai = await client.post(
                f"/api/v1/runs/{run['id']}/explanations",
                headers=headers,
                json={"mode": "ai"},
            )
            assert unavailable_ai.status_code == 409
            assert "not configured" in unavailable_ai.json()["error"]["message"]


@pytest.mark.asyncio
async def test_discovery_body_limit_rejects_before_parsing(tmp_path):
    app = create_app(Settings(
        database_path=tmp_path / "boundarylab.db",
        bootstrap_secret="correct-horse-battery-staple",
        targets={},
        allowed_origins=("http://testserver",),
        web_dist=tmp_path / "missing",
    ))
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
            csrf = await login(client)
            response = await client.post(
                "/api/v1/discovery/analyses",
                headers={"Origin": "http://testserver", "X-CSRF-Token": csrf, "Content-Type": "application/json"},
                content=b" " * 2_000_001,
            )
    assert response.status_code == 413


@pytest.mark.asyncio
async def test_discovery_rejects_excessive_json_nesting_without_server_error(tmp_path):
    app = create_app(Settings(
        database_path=tmp_path / "boundarylab.db",
        bootstrap_secret="correct-horse-battery-staple",
        targets={},
        allowed_origins=("http://testserver",),
        web_dist=tmp_path / "missing",
    ))
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
            csrf = await login(client)
            nested = b'{"label":"x","document":' + (b'{"x":' * 1_100) + b'0' + (b'}' * 1_100) + b'}'
            response = await client.post(
                "/api/v1/discovery/analyses",
                headers={"Origin": "http://testserver", "X-CSRF-Token": csrf, "Content-Type": "application/json"},
                content=nested,
            )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_release_gate_explains_fixes_preserved_behavior_and_regressions(tmp_path):
    app = create_app(Settings(
        database_path=tmp_path / "boundarylab.db",
        bootstrap_secret="correct-horse-battery-staple",
        targets={},
        allowed_origins=("http://testserver",),
        web_dist=tmp_path / "missing",
    ))
    baseline = app.state.repository.create_run("baseline", "http://127.0.0.1:9011")
    app.state.repository.complete_run(baseline["id"], release_report("baseline", ["violation", "pass"]))
    fixed = app.state.repository.create_run("fixed", "http://127.0.0.1:9012")
    app.state.repository.complete_run(fixed["id"], release_report("fixed", ["pass", "pass"]))
    regressed = app.state.repository.create_run("regressed", "http://127.0.0.1:9013")
    app.state.repository.complete_run(regressed["id"], release_report("regressed", ["pass", "violation"]))

    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
            csrf = await login(client)
            headers = {"Origin": "http://testserver", "X-CSRF-Token": csrf}
            ready = await client.post(
                "/api/v1/comparisons",
                headers=headers,
                json={"run_ids": [baseline["id"], fixed["id"]]},
            )
            blocked = await client.post(
                "/api/v1/comparisons",
                headers=headers,
                json={"run_ids": [fixed["id"], regressed["id"]]},
            )

    assert ready.status_code == 200, ready.text
    assert ready.json()["gate"]["decision"] == "ready"
    assert ready.json()["gate"]["fixed"] == 1
    assert ready.json()["gate"]["preserved"] == 1
    assert [item["classification"] for item in ready.json()["gate"]["changes"]] == ["fixed", "preserved"]
    assert blocked.json()["gate"]["decision"] == "blocked"
    assert blocked.json()["gate"]["regressed"] == 1
