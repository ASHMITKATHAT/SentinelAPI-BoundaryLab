from __future__ import annotations

import dataclasses
from typing import Any

from .domain import ScanReport


def report_to_dict(report: ScanReport) -> dict[str, Any]:
    return {
        "target_alias": report.target_alias,
        "build_id": report.build_id,
        "policy_version": report.policy_version,
        "assessment": report.assessment.value,
        "has_incomplete_cases": report.has_incomplete_cases,
        "counts": report.counts,
        "request_count": report.request_count,
        "cleanup_status": report.cleanup_status,
        "execution_error": report.execution_error,
        "cases": [dataclasses.asdict(case) for case in report.cases],
        "evidence": [dataclasses.asdict(item) for item in report.evidence],
    }
