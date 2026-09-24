from __future__ import annotations

import httpx
import pytest

from boundarylab.fixture import Variant, create_fixture_app
from boundarylab.transport import BudgetExceeded, ScopeViolation, ScopedTransport, TransportLimits


@pytest.mark.asyncio
async def test_unknown_operation_is_rejected_before_request():
    app = create_fixture_app(Variant.FIXED)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://fixture") as client:
        transport = ScopedTransport(client, base_url="http://fixture", limits=TransportLimits(requests_per_second=10_000))
        with pytest.raises(ScopeViolation):
            await transport.request("arbitraryUrl", identity="anonymous", token=None)
        assert transport.request_count == 0


@pytest.mark.asyncio
async def test_main_budget_preserves_cleanup_reserve():
    app = create_fixture_app(Variant.FIXED)
    limits = TransportLimits(max_requests=3, cleanup_reserve=1, requests_per_second=10_000)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://fixture") as client:
        transport = ScopedTransport(client, base_url="http://fixture", limits=limits)
        await transport.request("health", identity="anonymous", token=None)
        await transport.request("health", identity="anonymous", token=None)
        with pytest.raises(BudgetExceeded):
            await transport.request("health", identity="anonymous", token=None)
        cleanup = await transport.request("labCleanup", identity="lab-admin", token="lab-factory-token",
                                          path={"namespace": "missing"}, cleanup=True)
        assert cleanup.status_code == 204
        assert transport.request_count == 3


@pytest.mark.asyncio
async def test_origin_requires_exact_http_origin():
    app = create_fixture_app(Variant.FIXED)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://fixture") as client:
        with pytest.raises(ValueError):
            ScopedTransport(client, base_url="http://fixture/hidden/path")


@pytest.mark.asyncio
async def test_response_body_limit_stops_oversized_evidence():
    async def oversized(_request: httpx.Request):
        return httpx.Response(200, json={"content_marker": "x" * 200})

    async with httpx.AsyncClient(transport=httpx.MockTransport(oversized), base_url="http://fixture") as client:
        transport = ScopedTransport(
            client,
            base_url="http://fixture",
            limits=TransportLimits(requests_per_second=10_000, response_body_bytes=80),
        )
        with pytest.raises(BudgetExceeded):
            await transport.request("health", identity="anonymous", token=None)
        assert transport.evidence == []


@pytest.mark.asyncio
async def test_redirect_is_not_followed_or_recorded_as_success():
    requested: list[str] = []

    async def redirect(request: httpx.Request):
        requested.append(str(request.url))
        return httpx.Response(302, headers={"Location": "http://metadata.invalid/latest"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(redirect), base_url="http://fixture") as client:
        transport = ScopedTransport(client, base_url="http://fixture", limits=TransportLimits(requests_per_second=10_000))
        with pytest.raises(ScopeViolation, match="redirect"):
            await transport.request("health", identity="anonymous", token=None)
        assert requested == ["http://fixture/healthz"]
