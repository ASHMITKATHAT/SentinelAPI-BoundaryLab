from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Verdict(StrEnum):
    PASS = "pass"
    VIOLATION = "violation"
    INCONCLUSIVE = "inconclusive"
    SKIPPED = "skipped"


class FindingKind(StrEnum):
    SECURITY_VIOLATION = "security_violation"
    FUNCTIONAL_REGRESSION = "functional_regression"


class RunAssessment(StrEnum):
    BLOCKED = "blocked"
    INCOMPLETE = "incomplete"
    PASS_IN_SCOPE = "pass_in_scope"


@dataclass(frozen=True, slots=True)
class CaseResult:
    case_id: str
    name: str
    verdict: Verdict
    expected: str
    observed: str
    finding_kind: FindingKind | None = None
    evidence_ids: tuple[str, ...] = ()
    reason_code: str = ""
    required: bool = True


@dataclass(frozen=True, slots=True)
class Evidence:
    evidence_id: str
    operation_id: str
    identity: str
    method: str
    path: str
    status_code: int | None
    marker_match: bool | None
    start_offset_ms: int
    duration_ms: int
    request_headers: dict[str, str]
    response_excerpt: Any
    sha256: str


@dataclass(slots=True)
class ScanReport:
    target_alias: str
    build_id: str | None
    policy_version: str
    cases: list[CaseResult] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    request_count: int = 0
    cleanup_status: str = "not_started"
    execution_error: str | None = None

    @property
    def has_incomplete_cases(self) -> bool:
        return (
            self.execution_error is not None
            or self.cleanup_status == "failed"
            or any(case.required and case.verdict in {Verdict.INCONCLUSIVE, Verdict.SKIPPED} for case in self.cases)
        )

    @property
    def assessment(self) -> RunAssessment:
        if any(case.required and case.verdict == Verdict.VIOLATION for case in self.cases):
            return RunAssessment.BLOCKED
        if self.has_incomplete_cases:
            return RunAssessment.INCOMPLETE
        return RunAssessment.PASS_IN_SCOPE

    @property
    def counts(self) -> dict[str, int]:
        return {verdict.value: sum(case.verdict == verdict for case in self.cases) for verdict in Verdict}
