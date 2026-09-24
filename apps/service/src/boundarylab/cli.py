from __future__ import annotations

import argparse
import asyncio
import json

import httpx

from .fixture import Variant, create_fixture_app
from .scenario import InvoiceScenario, ScenarioPolicy
from .transport import ScopedTransport, TransportLimits


async def run_variant(variant: Variant, *, benchmark_speed: bool) -> dict:
    app = create_fixture_app(variant, export_delay_ms=1 if benchmark_speed else 10)
    limits = TransportLimits(requests_per_second=10_000 if benchmark_speed else 2)
    policy = ScenarioPolicy(
        grace_ms=5 if benchmark_speed else 2_000,
        probe_margin_ms=1 if benchmark_speed else 200,
        export_poll_interval_ms=1 if benchmark_speed else 250,
    )
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://fixture") as client:
        report = await InvoiceScenario(
            ScopedTransport(client, base_url="http://fixture", limits=limits),
            target_alias=f"demo-{variant.value}",
            policy=policy,
        ).run()
    return {
        "target": report.target_alias,
        "build_id": report.build_id,
        "assessment": report.assessment.value,
        "has_incomplete_cases": report.has_incomplete_cases,
        "counts": report.counts,
        "request_count": report.request_count,
        "cleanup_status": report.cleanup_status,
        "execution_error": report.execution_error,
        "cases": [
            {
                "id": case.case_id,
                "verdict": case.verdict.value,
                "kind": case.finding_kind.value if case.finding_kind else None,
                "reason": case.reason_code,
            }
            for case in report.cases
        ],
    }


async def matrix(benchmark_speed: bool) -> list[dict]:
    return [await run_variant(variant, benchmark_speed=benchmark_speed) for variant in Variant]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run BoundaryLab's local synthetic fixture matrix")
    parser.add_argument("command", choices=["matrix"])
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Use reduced timing only for development verification; does not validate the 2-second policy timing",
    )
    args = parser.parse_args()
    results = asyncio.run(matrix(args.fast))
    print(json.dumps({"status": "executed_local_asgi_fixture_matrix", "results": results}, indent=2))
    expected = {
        "demo-vulnerable": {"pass": 8, "violation": 4, "inconclusive": 0, "skipped": 0},
        "demo-owner-only": {"pass": 7, "violation": 2, "inconclusive": 3, "skipped": 0},
        "demo-fixed": {"pass": 12, "violation": 0, "inconclusive": 0, "skipped": 0},
    }
    return 0 if all(item["counts"] == expected[item["target"]] and item["cleanup_status"] == "complete" for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
