from __future__ import annotations

import os

from .domain import CaseResult, FindingKind, ScanReport, Verdict
from .targets import AccessProbeAdapter
from .transport import ResponseRecord, ScopedTransport, json_pointer_value


class AccessProbeScenario:
    """Read-only authorization probe for an explicitly registered real target."""

    def __init__(
        self,
        transport: ScopedTransport,
        *,
        target_alias: str,
        adapter: AccessProbeAdapter,
        environment: dict[str, str] | os._Environ[str] | None = None,
    ):
        self.transport = transport
        self.target_alias = target_alias
        self.adapter = adapter
        self.environment = environment if environment is not None else os.environ
        self.report = ScanReport(target_alias=target_alias, build_id=None, policy_version="read-boundary-v1")

    async def run(self) -> ScanReport:
        try:
            missing = [name for name in self.adapter.required_environment if not self.environment.get(name)]
            if missing:
                raise RuntimeError(f"missing target environment references: {', '.join(missing)}")
            self.report.build_id = self._bounded_value(self.adapter.build_id_env, 120)
            resource_id = self._bounded_value(self.adapter.resource_id_env, 300)
            marker = self._bounded_value(self.adapter.marker_env, 2_048)
            for index, identity in enumerate(self.adapter.identities, start=1):
                token = self._bounded_value(identity.token_env, 16_384) if identity.token_env else None
                response = await self.transport.request(
                    self.adapter.operation_id,
                    identity=identity.name,
                    token=token,
                    path={"resource_id": resource_id},
                    marker_pointer=self.adapter.marker_pointer,
                    marker_value=marker,
                    redact_pointers=identity.forbidden_pointers,
                )
                self._evaluate(index, identity.name, identity.expectation, identity.forbidden_pointers, response, marker)
        except Exception as exc:
            self.report.execution_error = f"{type(exc).__name__}: real probe stopped; inspect local service logs"
            completed = {case.case_id for case in self.report.cases}
            for index, identity in enumerate(self.adapter.identities, start=1):
                case_id = f"R{index:02}"
                if case_id not in completed:
                    self.report.cases.append(CaseResult(
                        case_id=case_id,
                        name=f"{identity.name} access boundary",
                        verdict=Verdict.INCONCLUSIVE,
                        expected=identity.expectation,
                        observed=f"probe stopped: {type(exc).__name__}",
                        reason_code="RUNNER_STOPPED",
                    ))
        finally:
            self.report.cleanup_status = "not_required"
            self.report.evidence = list(self.transport.evidence)
            self.report.request_count = self.transport.request_count
        return self.report

    def _bounded_value(self, name: str, maximum: int) -> str:
        value = self.environment.get(name, "")
        if not value or len(value) > maximum or any(ord(char) < 32 for char in value):
            raise RuntimeError(f"environment reference {name} is empty, oversized or contains control characters")
        return value

    def _evaluate(
        self,
        index: int,
        name: str,
        expectation: str,
        forbidden_pointers: tuple[str, ...],
        response: ResponseRecord,
        marker: str,
    ) -> None:
        case_id = f"R{index:02}"
        marker_matches = json_pointer_value(response.json_body, self.adapter.marker_pointer) == marker
        exposed_fields = [pointer for pointer in forbidden_pointers if json_pointer_value(response.json_body, pointer) is not None]
        evidence_ids = (response.evidence_id,)
        if expectation == "allow":
            if exposed_fields:
                verdict = Verdict.VIOLATION
                observed = f"restricted field exposed: {', '.join(exposed_fields)}"
                finding = FindingKind.SECURITY_VIOLATION
                reason = "RESTRICTED_FIELD_EXPOSED"
            elif 200 <= response.status_code < 300 and marker_matches:
                verdict = Verdict.PASS
                observed = "allowed response matched the configured resource marker"
                finding = None
                reason = ""
            elif response.status_code in self.adapter.deny_statuses:
                verdict = Verdict.VIOLATION
                observed = f"legitimate identity denied with {response.status_code}"
                finding = FindingKind.FUNCTIONAL_REGRESSION
                reason = "LEGITIMATE_ACCESS_DENIED"
            else:
                verdict = Verdict.INCONCLUSIVE
                observed = f"status {response.status_code}; configured marker was not verified"
                finding = None
                reason = "MARKER_NOT_VERIFIED"
            expected = "2xx response with the configured marker and no restricted fields"
        else:
            if marker_matches or exposed_fields:
                verdict = Verdict.VIOLATION
                details = ["configured protected marker" if marker_matches else ""]
                details.extend(exposed_fields)
                observed = f"status {response.status_code} disclosed {', '.join(item for item in details if item)}"
                finding = FindingKind.SECURITY_VIOLATION
                reason = "PROTECTED_RESOURCE_EXPOSED" if marker_matches else "RESTRICTED_FIELD_EXPOSED"
            elif response.status_code in self.adapter.deny_statuses:
                verdict = Verdict.PASS
                observed = f"denied with {response.status_code}; protected marker absent"
                finding = None
                reason = ""
            else:
                verdict = Verdict.INCONCLUSIVE
                observed = f"unexpected status {response.status_code}; marker absent"
                finding = None
                reason = "UNEXPECTED_RESPONSE"
            expected = f"one of {list(self.adapter.deny_statuses)} without the configured marker"

        self.report.cases.append(CaseResult(
            case_id=case_id,
            name=f"{name} is {'allowed' if expectation == 'allow' else 'denied'} by the resource boundary",
            verdict=verdict,
            expected=expected,
            observed=observed,
            finding_kind=finding,
            evidence_ids=evidence_ids,
            reason_code=reason,
        ))
