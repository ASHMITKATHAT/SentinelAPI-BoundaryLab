from __future__ import annotations

import argparse
import asyncio
import ipaddress
import json
import socket
from urllib.parse import urlsplit

import httpx

from .fixture import Variant, create_fixture_app
from .scenario import InvoiceScenario, ScenarioPolicy
from .serialization import report_to_dict
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


def validate_local_target(origin: str) -> str:
    parsed = urlsplit(origin)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("target must be an HTTP(S) origin without credentials")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ValueError("target must be an origin without path, query or fragment")
    try:
        addresses = {
            ipaddress.ip_address(item[4][0].split("%", 1)[0])
            for item in socket.getaddrinfo(parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80))
        }
    except (OSError, ValueError) as exc:
        raise ValueError("target hostname could not be resolved safely") from exc
    if not addresses or any(not address.is_loopback for address in addresses):
        raise ValueError("CI gate accepts loopback targets only; remote execution requires a reviewed runner adapter")
    return origin.rstrip("/")


async def gate(origin: str, alias: str) -> dict:
    trusted_origin = validate_local_target(origin)
    limits = httpx.Limits(max_connections=1, max_keepalive_connections=1)
    async with httpx.AsyncClient(
        timeout=None,
        follow_redirects=False,
        trust_env=False,
        limits=limits,
        headers={"User-Agent": "BoundaryLab/0.3 CI-gate"},
    ) as client:
        report = await InvoiceScenario(
            ScopedTransport(client, base_url=trusted_origin, limits=TransportLimits()),
            target_alias=alias,
        ).run()
    return report_to_dict(report)


def gate_exit_code(report: dict, fail_on: set[str]) -> int:
    counts = report.get("counts", {})
    blocked = "violation" in fail_on and int(counts.get("violation", 0)) > 0
    incomplete = "inconclusive" in fail_on and (
        int(counts.get("inconclusive", 0)) > 0 or bool(report.get("has_incomplete_cases"))
    )
    execution = "execution_error" in fail_on and bool(report.get("execution_error"))
    return 1 if blocked or incomplete or execution else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run BoundaryLab authorization regression checks")
    commands = parser.add_subparsers(dest="command", required=True)
    matrix_parser = commands.add_parser("matrix", help="run the three in-process disclosed fixture builds")
    matrix_parser.add_argument(
        "--fast",
        action="store_true",
        help="Use reduced timing only for development verification; does not validate the 2-second policy timing",
    )
    gate_parser = commands.add_parser("gate", help="run the policy suite against a trusted loopback target")
    gate_parser.add_argument("--target", required=True, help="loopback HTTP(S) origin")
    gate_parser.add_argument("--alias", default="ci-target")
    gate_parser.add_argument(
        "--fail-on",
        default="violation,inconclusive,execution_error",
        help="comma-separated: violation,inconclusive,execution_error",
    )
    args = parser.parse_args()
    if args.command == "matrix":
        results = asyncio.run(matrix(args.fast))
        print(json.dumps({"status": "executed_local_asgi_fixture_matrix", "results": results}, indent=2))
        expected = {
            "demo-vulnerable": {"pass": 8, "violation": 4, "inconclusive": 0, "skipped": 0},
            "demo-owner-only": {"pass": 7, "violation": 2, "inconclusive": 3, "skipped": 0},
            "demo-fixed": {"pass": 12, "violation": 0, "inconclusive": 0, "skipped": 0},
        }
        return 0 if all(item["counts"] == expected[item["target"]] and item["cleanup_status"] == "complete" for item in results) else 1

    allowed = {"violation", "inconclusive", "execution_error"}
    fail_on = {item.strip() for item in args.fail_on.split(",") if item.strip()}
    unknown = fail_on - allowed
    if unknown:
        parser.error(f"unknown --fail-on values: {', '.join(sorted(unknown))}")
    try:
        report = asyncio.run(gate(args.target, args.alias))
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps({"status": "executed_live_ci_gate", "report": report}, indent=2))
    return gate_exit_code(report, fail_on)


if __name__ == "__main__":
    raise SystemExit(main())
