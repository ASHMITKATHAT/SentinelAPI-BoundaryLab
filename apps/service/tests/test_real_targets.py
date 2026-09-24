from __future__ import annotations

import json

import httpx
import pytest

from boundarylab.app import Settings, create_app
from boundarylab.real_scenario import AccessProbeScenario
from boundarylab.serialization import report_to_dict
from boundarylab.targets import AccessProbeAdapter, ProbeIdentity, RealTargetConfigError, load_real_targets
from boundarylab.transport import ScopedTransport, TransportLimits


def openapi_document() -> dict:
    return {
        "openapi": "3.1.0",
        "info": {"title": "Staging orders", "version": "1.0"},
        "paths": {
            "/v1/orders/{resource_id}": {
                "get": {
                    "operationId": "getOrder",
                    "responses": {"200": {"description": "Order"}, "404": {"description": "Hidden"}},
                }
            }
        },
    }


def target_config(*, origin: str = "http://127.0.0.1:9443", operation_id: str = "getOrder") -> dict:
    return {
        "version": "1.0",
        "targets": [{
            "alias": "staging-orders",
            "label": "Orders staging",
            "origin": origin,
            "openapi_path": "orders.openapi.json",
            "probe": {
                "operation_id": operation_id,
                "method": "GET",
                "path_template": "/v1/orders/{resource_id}",
                "resource_id_env": "BOUNDARYLAB_ORDER_ID",
                "marker_pointer": "/proof",
                "marker_env": "BOUNDARYLAB_ORDER_MARKER",
                "build_id_env": "BOUNDARYLAB_ORDER_BUILD",
                "deny_statuses": [403, 404],
                "identities": [
                    {"name": "owner", "expectation": "allow", "token_env": "BOUNDARYLAB_OWNER_TOKEN"},
                    {"name": "outsider", "expectation": "deny", "token_env": "BOUNDARYLAB_OUTSIDER_TOKEN"},
                ],
            },
        }],
    }


def write_registry(tmp_path, config: dict | None = None):
    (tmp_path / "orders.openapi.json").write_text(json.dumps(openapi_document()), encoding="utf-8")
    path = tmp_path / "targets.json"
    path.write_text(json.dumps(config or target_config()), encoding="utf-8")
    return path


def test_real_target_registry_binds_probe_to_openapi_and_environment(tmp_path):
    target = load_real_targets(write_registry(tmp_path))["staging-orders"]

    assert target.synthetic_fixture is False
    assert target.adapter is not None
    assert target.adapter.operation.method == "GET"
    assert target.missing_environment({}) == (
        "BOUNDARYLAB_ORDER_ID",
        "BOUNDARYLAB_ORDER_MARKER",
        "BOUNDARYLAB_ORDER_BUILD",
        "BOUNDARYLAB_OWNER_TOKEN",
        "BOUNDARYLAB_OUTSIDER_TOKEN",
    )
    assert target.missing_environment({name: "configured" for name in target.adapter.required_environment}) == ()


@pytest.mark.parametrize(
    ("config", "message"),
    [
        (target_config(origin="https://staging.example.com"), "numeric loopback"),
        (target_config(operation_id="deleteOrder"), "must declare GET"),
    ],
)
def test_real_target_registry_rejects_scope_escape_or_contract_mismatch(tmp_path, config, message):
    with pytest.raises(RealTargetConfigError, match=message):
        load_real_targets(write_registry(tmp_path, config))


@pytest.mark.asyncio
async def test_control_api_exposes_real_target_context_and_blocks_missing_environment(tmp_path, monkeypatch):
    targets = load_real_targets(write_registry(tmp_path))
    target = targets["staging-orders"]
    for name in target.adapter.required_environment if target.adapter else ():
        monkeypatch.delenv(name, raising=False)
    app = create_app(Settings(
        database_path=tmp_path / "boundarylab.db",
        bootstrap_secret="correct-horse-battery-staple",
        targets=targets,
        allowed_origins=("http://testserver",),
        web_dist=tmp_path / "missing-web",
    ))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        login = await client.post(
            "/api/v1/session",
            headers={"Origin": "http://testserver"},
            json={"bootstrap_secret": "correct-horse-battery-staple"},
        )
        csrf = login.json()["csrf_token"]
        listed = await client.get("/api/v1/targets")
        policy = await client.get("/api/v1/policy?target_alias=staging-orders")
        specification = await client.get("/api/v1/spec?target_alias=staging-orders")
        blocked = await client.post(
            "/api/v1/runs",
            headers={"Origin": "http://testserver", "X-CSRF-Token": csrf},
            json={"target_alias": "staging-orders"},
        )

    assert listed.json()[0]["mode"] == "real_read_probe"
    assert listed.json()[0]["ready"] is False
    assert set(listed.json()[0]["missing_environment"]) == set(target.adapter.required_environment)
    assert policy.json()["document"]["operation_id"] == "getOrder"
    assert specification.json()["configured"] is True
    assert specification.json()["title"] == "Staging orders"
    assert blocked.status_code == 422
    assert "missing environment references" in blocked.json()["error"]["message"]


@pytest.mark.asyncio
async def test_real_probe_uses_encoded_path_and_persists_only_redacted_proof():
    marker = "customer-secret-proof"
    owner_token = "owner-token-that-must-not-persist"
    outsider_token = "outsider-token-that-must-not-persist"
    paths: list[bytes] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        paths.append(request.url.raw_path)
        if request.headers.get("Authorization") == f"Bearer {owner_token}":
            return httpx.Response(200, json={"proof": marker, "name": "Order"})
        return httpx.Response(404, json={"code": "NOT_FOUND"})

    adapter = AccessProbeAdapter(
        operation_id="getOrder",
        path_template="/v1/orders/{resource_id}",
        resource_id_env="ORDER_ID",
        marker_pointer="/proof",
        marker_env="ORDER_MARKER",
        build_id_env="ORDER_BUILD",
        deny_statuses=(403, 404),
        identities=(
            ProbeIdentity("owner", "allow", "OWNER_TOKEN", ()),
            ProbeIdentity("outsider", "deny", "OUTSIDER_TOKEN", ()),
        ),
    )
    environment = {
        "ORDER_ID": "order/42 with space",
        "ORDER_MARKER": marker,
        "ORDER_BUILD": "orders-2026.09.25",
        "OWNER_TOKEN": owner_token,
        "OUTSIDER_TOKEN": outsider_token,
    }
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        transport = ScopedTransport(
            client,
            base_url="http://127.0.0.1:9443",
            limits=TransportLimits(max_requests=2, cleanup_reserve=0, requests_per_second=10_000),
            operations={adapter.operation_id: adapter.operation},
        )
        report = await AccessProbeScenario(
            transport,
            target_alias="staging-orders",
            adapter=adapter,
            environment=environment,
        ).run()

    serialized = json.dumps(report_to_dict(report))
    assert report.counts == {"pass": 2, "violation": 0, "inconclusive": 0, "skipped": 0}
    assert report.assessment == "pass_in_scope"
    assert paths == [b"/v1/orders/order%2F42%20with%20space", b"/v1/orders/order%2F42%20with%20space"]
    assert report.evidence[0].response_excerpt["proof"] == "<MATCHED_PROTECTED_MARKER>"
    assert report.evidence[0].request_headers["Authorization"] == "<REDACTED>"
    assert marker not in serialized
    assert owner_token not in serialized
    assert outsider_token not in serialized
    assert environment["ORDER_ID"] not in serialized


@pytest.mark.asyncio
async def test_denied_identity_restricted_field_is_a_violation_and_value_is_redacted():
    secret_field = "internal-value-that-must-not-persist"

    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"code": "DENIED", "internal_note": secret_field})

    adapter = AccessProbeAdapter(
        operation_id="getOrder",
        path_template="/v1/orders/{resource_id}",
        resource_id_env="ORDER_ID",
        marker_pointer="/proof",
        marker_env="ORDER_MARKER",
        build_id_env="ORDER_BUILD",
        deny_statuses=(403, 404),
        identities=(ProbeIdentity("outsider", "deny", "OUTSIDER_TOKEN", ("/internal_note",)),),
    )
    environment = {
        "ORDER_ID": "order-42",
        "ORDER_MARKER": "expected-proof",
        "ORDER_BUILD": "orders-build",
        "OUTSIDER_TOKEN": "outsider-token",
    }
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        transport = ScopedTransport(
            client,
            base_url="http://127.0.0.1:9443",
            limits=TransportLimits(max_requests=1, cleanup_reserve=0, requests_per_second=10_000),
            operations={adapter.operation_id: adapter.operation},
        )
        report = await AccessProbeScenario(
            transport,
            target_alias="staging-orders",
            adapter=adapter,
            environment=environment,
        ).run()

    serialized = json.dumps(report_to_dict(report))
    assert report.cases[0].verdict == "violation"
    assert report.cases[0].reason_code == "RESTRICTED_FIELD_EXPOSED"
    assert report.evidence[0].response_excerpt["internal_note"] == "<RESTRICTED_FIELD_PRESENT>"
    assert secret_field not in serialized


@pytest.mark.asyncio
async def test_real_probe_does_not_persist_transport_exception_details():
    marker = "marker-that-must-not-persist"
    resource_id = "resource-that-must-not-persist"

    async def handler(_request: httpx.Request) -> httpx.Response:
        raise RuntimeError(f"upstream failure for {resource_id} with {marker}")

    adapter = AccessProbeAdapter(
        operation_id="getOrder",
        path_template="/v1/orders/{resource_id}",
        resource_id_env="ORDER_ID",
        marker_pointer="/proof",
        marker_env="ORDER_MARKER",
        build_id_env="ORDER_BUILD",
        deny_statuses=(403, 404),
        identities=(
            ProbeIdentity("owner", "allow", "OWNER_TOKEN", ()),
            ProbeIdentity("outsider", "deny", "OUTSIDER_TOKEN", ()),
        ),
    )
    environment = {
        "ORDER_ID": resource_id,
        "ORDER_MARKER": marker,
        "ORDER_BUILD": "orders-build",
        "OWNER_TOKEN": "owner-token",
        "OUTSIDER_TOKEN": "outsider-token",
    }
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        transport = ScopedTransport(
            client,
            base_url="http://127.0.0.1:9443",
            limits=TransportLimits(max_requests=2, cleanup_reserve=0, requests_per_second=10_000),
            operations={adapter.operation_id: adapter.operation},
        )
        report = await AccessProbeScenario(
            transport,
            target_alias="staging-orders",
            adapter=adapter,
            environment=environment,
        ).run()

    serialized = json.dumps(report_to_dict(report))
    assert report.execution_error == "RuntimeError: real probe stopped; inspect local service logs"
    assert report.counts["inconclusive"] == 2
    assert marker not in serialized
    assert resource_id not in serialized
