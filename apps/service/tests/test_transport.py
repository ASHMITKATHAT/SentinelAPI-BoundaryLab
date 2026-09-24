from __future__ import annotations

import httpx
import pytest

from boundarylab.fixture import Variant, create_fixture_app
from boundarylab.transport import BudgetExceeded, ScopeViolation, ScopedTransport, TransportLimits


async def test_unknown_operation_is_rejected_before_request():
    app = create_fixture_app(Variant.FIXED)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://fixture") as client:
        transport = ScopedTransport(client, base_url="http://fixture", limits=TransportLimits(requests_per_second=10_000))
        with pytest.raises(ScopeViolation):
            await transport.request("arbitraryUrl", identity="anonymous", token=None)
        assert transport.request_count == 0


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


def test_origin_requires_exact_http_origin():
    app = create_fixture_app(Variant.FIXED)
    client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://fixture")
    with pytest.raises(ValueError):
        ScopedTransport(client, base_url="http://fixture/hidden/path")
