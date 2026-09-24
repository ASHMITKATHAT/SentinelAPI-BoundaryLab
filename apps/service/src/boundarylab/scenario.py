from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from .domain import CaseResult, FindingKind, ScanReport, Verdict
from .transport import ResponseRecord, ScopedTransport


@dataclass(frozen=True, slots=True)
class ScenarioPolicy:
    version: str = "invoice-policy-v1"
    grace_ms: int = 2_000
    probe_margin_ms: int = 200
    max_export_polls: int = 10
    export_poll_interval_ms: int = 250


class InvoiceScenario:
    def __init__(self, transport: ScopedTransport, *, target_alias: str, policy: ScenarioPolicy | None = None):
        self.transport = transport
        self.target_alias = target_alias
        self.policy = policy or ScenarioPolicy()
        self.report = ScanReport(target_alias=target_alias, build_id=None, policy_version=self.policy.version)
        self.tokens: dict[str, str] = {}
        self.objects: dict[str, str] = {}
        self.markers: dict[str, str] = {}
        self.namespace: str | None = None

    async def run(self) -> ScanReport:
        try:
            await self._execute()
        except Exception as exc:
            self.report.execution_error = f"{type(exc).__name__}: {exc}"
            existing = {case.case_id for case in self.report.cases}
            for number in range(1, 13):
                case_id = f"C{number:02}"
                if case_id not in existing:
                    self._case(case_id, f"Required case {case_id}", Verdict.INCONCLUSIVE,
                               "required behavior evaluated", f"runner stopped: {type(exc).__name__}",
                               reason_code="RUNNER_STOPPED")
        finally:
            await self._cleanup()
            self.report.evidence = list(self.transport.evidence)
            self.report.request_count = self.transport.request_count
        return self.report

    async def _execute(self) -> None:
        health = await self._request("health", "anonymous", None)
        if health.status_code != 200 or not isinstance(health.json_body, dict) or not health.json_body.get("build_id"):
            raise RuntimeError("target build preflight failed")
        self.report.build_id = str(health.json_body["build_id"])

        fixture = await self._request("labCreate", "lab-admin", "lab-factory-token", json_body={})
        if fixture.status_code != 200 or not isinstance(fixture.json_body, dict):
            raise RuntimeError("fixture creation failed")
        self.namespace = fixture.json_body.get("namespace")
        self.tokens = fixture.json_body.get("identity_tokens", {})
        self.objects = fixture.json_body.get("objects", {})
        self.markers = fixture.json_body.get("markers", {})
        if not self.namespace or set(self.tokens) != {"alice", "bob", "mallory"}:
            raise RuntimeError("fixture identity bindings invalid")

        for identity, expected_tenant in (("alice", "A"), ("bob", "A"), ("mallory", "B")):
            response = await self._request("getMe", identity, self.tokens[identity])
            body = response.json_body if isinstance(response.json_body, dict) else {}
            if response.status_code != 200 or body.get("subject_id") != identity or body.get("tenant_id") != expected_tenant:
                raise RuntimeError(f"identity preflight failed: {identity}")

        private_id = self.objects["private_invoice"]
        shared_id = self.objects["shared_invoice"]
        private_marker = self.markers["private_invoice"]
        shared_marker = self.markers["shared_invoice"]

        c01 = await self._request("getInvoicePreview", "alice", self.tokens["alice"], path={"invoice_id": private_id})
        self._allow_case("C01", "Alice reads private preview", c01, private_marker, security=False)

        c02 = await self._request("getInvoicePreview", "bob", self.tokens["bob"], path={"invoice_id": private_id})
        self._deny_case("C02", "Bob is denied private preview", c02, private_marker)

        c03 = await self._request("getInvoicePreview", "mallory", self.tokens["mallory"], path={"invoice_id": private_id})
        self._deny_case("C03", "Mallory is denied private preview", c03, private_marker)

        c04 = await self._request("getInvoicePreview", "anonymous", None, path={"invoice_id": private_id})
        self._anonymous_case(c04, private_marker)

        grant = await self._request("grantShare", "alice", self.tokens["alice"], path={"invoice_id": shared_id}, json_body={"subject_id": "bob"})
        grant_ok = grant.status_code == 201

        if grant_ok:
            c05 = await self._request("getInvoice", "bob", self.tokens["bob"], path={"invoice_id": shared_id})
            c05_result = self._allow_case("C05", "Bob reads active shared detail", c05, shared_marker, security=False)
        else:
            c05_result = self._case("C05", "Bob reads active shared detail", Verdict.INCONCLUSIVE,
                                    "200 with shared marker", f"grant returned {grant.status_code}", reason_code="GRANT_FAILED")

        if c05_result.verdict == Verdict.PASS:
            leaked_field = isinstance(c05.json_body, dict) and "internal_bank_ref" in c05.json_body
            if leaked_field:
                self._case("C06", "Owner-only property is hidden from Bob", Verdict.VIOLATION,
                           "internal_bank_ref absent", "internal_bank_ref returned",
                           FindingKind.SECURITY_VIOLATION, (c05.evidence_id,), "OWNER_FIELD_EXPOSED")
            else:
                self._case("C06", "Owner-only property is hidden from Bob", Verdict.PASS,
                           "internal_bank_ref absent", "field absent", evidence_ids=(c05.evidence_id,))
        else:
            self._case("C06", "Owner-only property is hidden from Bob", Verdict.INCONCLUSIVE,
                       "evaluate field on allowed object response", "active-access prerequisite failed",
                       evidence_ids=c05_result.evidence_ids, reason_code="DEPENDENCY_FAILED")

        c07 = await self._request("getInvoice", "alice", self.tokens["alice"], path={"invoice_id": shared_id})
        owner_field = isinstance(c07.json_body, dict) and isinstance(c07.json_body.get("internal_bank_ref"), str)
        if c07.status_code == 200 and self._marker(c07, shared_marker) and owner_field:
            self._case("C07", "Alice retains owner-only property", Verdict.PASS,
                       "owner response contains marker and internal_bank_ref", "both values returned", evidence_ids=(c07.evidence_id,))
        else:
            self._case("C07", "Alice retains owner-only property", Verdict.VIOLATION,
                       "owner response contains marker and internal_bank_ref", f"status {c07.status_code}; required values missing",
                       FindingKind.FUNCTIONAL_REGRESSION, (c07.evidence_id,), "OWNER_FIELD_UNAVAILABLE")

        c08 = await self._request("queueExport", "bob", self.tokens["bob"], path={"invoice_id": shared_id})
        export_id = c08.json_body.get("id") if isinstance(c08.json_body, dict) else None
        if c08.status_code == 202 and isinstance(export_id, str):
            c08_result = self._case("C08", "Bob queues export while shared", Verdict.PASS,
                                    "202 with export ID", "export queued", evidence_ids=(c08.evidence_id,))
        elif c08.status_code in {403, 404}:
            c08_result = self._case("C08", "Bob queues export while shared", Verdict.VIOLATION,
                                    "202 with export ID", f"denied with {c08.status_code}",
                                    FindingKind.FUNCTIONAL_REGRESSION, (c08.evidence_id,), "ACTIVE_EXPORT_DENIED")
        else:
            c08_result = self._case("C08", "Bob queues export while shared", Verdict.INCONCLUSIVE,
                                    "202 with export ID", f"unexpected status {c08.status_code}",
                                    evidence_ids=(c08.evidence_id,), reason_code="UNEXPECTED_RESPONSE")

        c09_result: CaseResult
        if c08_result.verdict == Verdict.PASS and export_id:
            ready = await self._wait_ready(export_id, "bob")
            if ready:
                c09 = await self._request("getExportContent", "bob", self.tokens["bob"], path={"export_id": export_id})
                c09_result = self._allow_case("C09", "Bob retrieves ready export before revoke", c09, shared_marker, security=False)
            else:
                c09_result = self._case("C09", "Bob retrieves ready export before revoke", Verdict.INCONCLUSIVE,
                                        "ready export and 200 marker", "export did not become ready", reason_code="EXPORT_TIMEOUT")
        else:
            c09_result = self._case("C09", "Bob retrieves ready export before revoke", Verdict.INCONCLUSIVE,
                                    "ready export and 200 marker", "queue prerequisite failed",
                                    evidence_ids=c08_result.evidence_ids, reason_code="DEPENDENCY_FAILED")

        if c09_result.verdict == Verdict.PASS and export_id:
            revoke = await self._request("revokeShare", "alice", self.tokens["alice"],
                                         path={"invoice_id": shared_id, "subject_id": "bob"})
            if revoke.status_code == 204:
                await asyncio.sleep((self.policy.grace_ms + self.policy.probe_margin_ms) / 1000)
                auth = await self._request("getMe", "bob", self.tokens["bob"])
                if auth.status_code == 200:
                    c10 = await self._request("getExportContent", "bob", self.tokens["bob"], path={"export_id": export_id})
                    self._deny_case("C10", "Bob is denied export after revocation deadline", c10, shared_marker)
                else:
                    self._case("C10", "Bob is denied export after revocation deadline", Verdict.INCONCLUSIVE,
                               "valid identity then denial without marker", f"identity recheck returned {auth.status_code}",
                               evidence_ids=(auth.evidence_id,), reason_code="AUTH_CONTEXT_INVALID")
            else:
                self._case("C10", "Bob is denied export after revocation deadline", Verdict.INCONCLUSIVE,
                           "successful revoke then denial", f"revoke returned {revoke.status_code}",
                           evidence_ids=(revoke.evidence_id,), reason_code="REVOKE_FAILED")
        else:
            self._case("C10", "Bob is denied export after revocation deadline", Verdict.INCONCLUSIVE,
                       "successful pre-revoke retrieval then post-revoke denial", "pre-revoke prerequisite failed",
                       evidence_ids=c09_result.evidence_ids, reason_code="DEPENDENCY_FAILED")

        independent_grant = await self._request("grantShare", "alice", self.tokens["alice"], path={"invoice_id": shared_id}, json_body={"subject_id": "bob"})
        independent_revoke = await self._request("revokeShare", "alice", self.tokens["alice"], path={"invoice_id": shared_id, "subject_id": "bob"}) if independent_grant.status_code == 201 else None
        if independent_revoke and independent_revoke.status_code == 204:
            c11 = await self._request("getInvoice", "bob", self.tokens["bob"], path={"invoice_id": shared_id})
            self._deny_case("C11", "Bob is denied detail after revoke", c11, shared_marker)
        else:
            evidence = tuple(item.evidence_id for item in (independent_grant, independent_revoke) if item)
            self._case("C11", "Bob is denied detail after revoke", Verdict.INCONCLUSIVE,
                       "independent grant/revoke then denial", "independent setup failed", evidence_ids=evidence,
                       reason_code="REVOKE_SETUP_FAILED")

        owner_queue = await self._request("queueExport", "alice", self.tokens["alice"], path={"invoice_id": shared_id})
        owner_export_id = owner_queue.json_body.get("id") if isinstance(owner_queue.json_body, dict) else None
        if owner_queue.status_code == 202 and isinstance(owner_export_id, str) and await self._wait_ready(owner_export_id, "alice"):
            c12 = await self._request("getExportContent", "alice", self.tokens["alice"], path={"export_id": owner_export_id})
            self._allow_case("C12", "Alice retrieves independent owner export", c12, shared_marker, security=False)
        else:
            self._case("C12", "Alice retrieves independent owner export", Verdict.VIOLATION,
                       "owner queues and retrieves export", f"owner queue status {owner_queue.status_code} or export not ready",
                       FindingKind.FUNCTIONAL_REGRESSION, (owner_queue.evidence_id,), "OWNER_EXPORT_UNAVAILABLE")

        final_health = await self._request("health", "anonymous", None)
        final_build = final_health.json_body.get("build_id") if isinstance(final_health.json_body, dict) else None
        if final_build != self.report.build_id:
            raise RuntimeError("target build changed during run")

    async def _wait_ready(self, export_id: str, identity: str) -> bool:
        for _ in range(self.policy.max_export_polls):
            response = await self._request("getExport", identity, self.tokens[identity], path={"export_id": export_id})
            if response.status_code == 200 and isinstance(response.json_body, dict) and response.json_body.get("state") == "ready":
                return True
            if response.status_code not in {200, 409}:
                return False
            await asyncio.sleep(self.policy.export_poll_interval_ms / 1000)
        return False

    async def _cleanup(self) -> None:
        if not self.namespace:
            self.report.cleanup_status = "not_started"
            return
        self.report.cleanup_status = "pending"
        try:
            response = await self._request("labCleanup", "lab-admin", "lab-factory-token",
                                           path={"namespace": self.namespace}, cleanup=True)
            self.report.cleanup_status = "complete" if response.status_code == 204 else "failed"
        except Exception:
            self.report.cleanup_status = "failed"

    async def _request(self, operation_id: str, identity: str, token: str | None, **kwargs) -> ResponseRecord:
        return await self.transport.request(operation_id, identity=identity, token=token, **kwargs)

    @staticmethod
    def _marker(response: ResponseRecord, expected_marker: str) -> bool:
        return isinstance(response.json_body, dict) and response.json_body.get("content_marker") == expected_marker

    def _allow_case(self, case_id: str, name: str, response: ResponseRecord, marker: str, *, security: bool) -> CaseResult:
        if response.status_code == 200 and self._marker(response, marker):
            return self._case(case_id, name, Verdict.PASS, "200 with expected protected marker", "allowed response matched",
                              evidence_ids=(response.evidence_id,))
        if response.status_code in {403, 404}:
            return self._case(case_id, name, Verdict.VIOLATION, "200 with expected protected marker",
                              f"legitimate access denied with {response.status_code}", FindingKind.FUNCTIONAL_REGRESSION,
                              (response.evidence_id,), "LEGITIMATE_ACCESS_DENIED")
        return self._case(case_id, name, Verdict.INCONCLUSIVE, "200 with expected protected marker",
                          f"unexpected status/body: {response.status_code}", evidence_ids=(response.evidence_id,),
                          reason_code="UNEXPECTED_RESPONSE")

    def _deny_case(self, case_id: str, name: str, response: ResponseRecord, marker: str) -> CaseResult:
        leaked = self._marker(response, marker)
        if leaked:
            return self._case(case_id, name, Verdict.VIOLATION, "403/404 without protected marker",
                              f"status {response.status_code} disclosed protected marker", FindingKind.SECURITY_VIOLATION,
                              (response.evidence_id,), "PROTECTED_CONTENT_EXPOSED")
        if response.status_code in {403, 404}:
            return self._case(case_id, name, Verdict.PASS, "403/404 without protected marker",
                              f"denied with {response.status_code}; marker absent", evidence_ids=(response.evidence_id,))
        return self._case(case_id, name, Verdict.INCONCLUSIVE, "403/404 without protected marker",
                          f"unexpected status {response.status_code}; marker absent", evidence_ids=(response.evidence_id,),
                          reason_code="UNEXPECTED_RESPONSE")

    def _anonymous_case(self, response: ResponseRecord, marker: str) -> None:
        if self._marker(response, marker):
            self._case("C04", "Anonymous is denied private preview", Verdict.VIOLATION,
                       "401/403/404 without marker", f"status {response.status_code} disclosed marker",
                       FindingKind.SECURITY_VIOLATION, (response.evidence_id,), "ANONYMOUS_CONTENT_EXPOSED")
        elif response.status_code in {401, 403, 404}:
            self._case("C04", "Anonymous is denied private preview", Verdict.PASS,
                       "401/403/404 without marker", f"denied with {response.status_code}", evidence_ids=(response.evidence_id,))
        else:
            self._case("C04", "Anonymous is denied private preview", Verdict.INCONCLUSIVE,
                       "401/403/404 without marker", f"unexpected status {response.status_code}",
                       evidence_ids=(response.evidence_id,), reason_code="UNEXPECTED_RESPONSE")

    def _case(self, case_id: str, name: str, verdict: Verdict, expected: str, observed: str,
              finding_kind: FindingKind | None = None, evidence_ids: tuple[str, ...] = (), reason_code: str = "") -> CaseResult:
        result = CaseResult(case_id, name, verdict, expected, observed, finding_kind, evidence_ids, reason_code)
        self.report.cases.append(result)
        return result
