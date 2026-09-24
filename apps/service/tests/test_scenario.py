from __future__ import annotations

import httpx
import pytest

from boundarylab.domain import RunAssessment, Verdict
from boundarylab.fixture import Variant, create_fixture_app
from boundarylab.scenario import InvoiceScenario, ScenarioPolicy
from boundarylab.transport import ScopedTransport, TransportLimits


EXPECTED = {
    Variant.VULNERABLE: {"pass": 8, "violation": 4, "inconclusive": 0, "assessment": RunAssessment.BLOCKED},
    Variant.OWNER_ONLY: {"pass": 7, "violation": 2, "inconclusive": 3, "assessment": RunAssessment.BLOCKED},
    Variant.FIXED: {"pass": 12, "violation": 0, "inconclusive": 0, "assessment": RunAssessment.PASS_IN_SCOPE},
}


@pytest.mark.parametrize("variant", list(Variant))
async def test_canonical_scenario_distinguishes_vulnerability_regression_and_fix(variant: Variant):
    app = create_fixture_app(variant, export_delay_ms=1)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://fixture") as client:
        transport = ScopedTransport(client, base_url="http://fixture", limits=TransportLimits(requests_per_second=10_000))
        report = await InvoiceScenario(
            transport,
            target_alias=f"demo-{variant.value}",
            policy=ScenarioPolicy(grace_ms=5, probe_margin_ms=1, export_poll_interval_ms=1),
        ).run()

    expected = EXPECTED[variant]
    assert len(report.cases) == 12
    assert report.counts[Verdict.PASS] == expected["pass"]
    assert report.counts[Verdict.VIOLATION] == expected["violation"]
    assert report.counts[Verdict.INCONCLUSIVE] == expected["inconclusive"]
    assert report.assessment == expected["assessment"]
    assert report.cleanup_status == "complete"
    assert report.build_id == f"invoice-{variant.value}"
    assert all(item.request_headers.get("Authorization") == "<REDACTED>" for item in report.evidence if "Authorization" in item.request_headers)


async def test_owner_only_failure_does_not_become_revocation_pass():
    app = create_fixture_app(Variant.OWNER_ONLY, export_delay_ms=1)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://fixture") as client:
        report = await InvoiceScenario(
            ScopedTransport(client, base_url="http://fixture", limits=TransportLimits(requests_per_second=10_000)),
            target_alias="demo-owner-only",
            policy=ScenarioPolicy(grace_ms=1, probe_margin_ms=1, export_poll_interval_ms=1),
        ).run()
    by_id = {case.case_id: case for case in report.cases}
    assert by_id["C08"].verdict == Verdict.VIOLATION
    assert by_id["C09"].verdict == Verdict.INCONCLUSIVE
    assert by_id["C10"].verdict == Verdict.INCONCLUSIVE

