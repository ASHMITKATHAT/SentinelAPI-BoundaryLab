from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

import httpx

from .domain import Evidence
from .redaction import allowlisted_body, canonical_sha256, redact_headers


class ScopeViolation(RuntimeError):
    pass


class BudgetExceeded(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class Operation:
    method: str
    path_template: str
    response_pointers: tuple[str, ...] = ("/code", "/content_marker", "/id", "/state", "/subject_id", "/tenant_id", "/build_id")


OPERATIONS: dict[str, Operation] = {
    "health": Operation("GET", "/healthz", ("/build_id", "/fixture_semantics_version")),
    "getMe": Operation("GET", "/v1/me"),
    "getInvoice": Operation("GET", "/v1/invoices/{invoice_id}", ("/id", "/content_marker", "/internal_bank_ref", "/code")),
    "getInvoicePreview": Operation("GET", "/v1/invoices/{invoice_id}/preview"),
    "grantShare": Operation("POST", "/v1/invoices/{invoice_id}/shares"),
    "revokeShare": Operation("DELETE", "/v1/invoices/{invoice_id}/shares/{subject_id}"),
    "queueExport": Operation("POST", "/v1/invoices/{invoice_id}/exports", ("/id", "/invoice_id", "/state", "/code")),
    "getExport": Operation("GET", "/v1/exports/{export_id}", ("/id", "/invoice_id", "/state", "/code")),
    "getExportContent": Operation("GET", "/v1/exports/{export_id}/content"),
    "labCreate": Operation("POST", "/__lab/fixtures"),
    "labCleanup": Operation("DELETE", "/__lab/fixtures/{namespace}"),
}


@dataclass(frozen=True, slots=True)
class TransportLimits:
    max_requests: int = 200
    cleanup_reserve: int = 20
    requests_per_second: float = 2.0
    request_deadline_seconds: float = 5.0
    response_body_bytes: int = 65_536


@dataclass(frozen=True, slots=True)
class ResponseRecord:
    status_code: int
    json_body: Any
    evidence_id: str
    start_offset_ms: int
    duration_ms: int


class ScopedTransport:
    """The only scanner component allowed to make target requests.

    Network/DNS pinning is intentionally not claimed here yet. The current gate is a
    fixed-origin, fixed-operation client suitable for the local ASGI fixture.
    """

    def __init__(self, client: httpx.AsyncClient, *, base_url: str, limits: TransportLimits | None = None):
        parsed = urlsplit(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.path not in {"", "/"}:
            raise ValueError("base_url must be an HTTP(S) origin without a path")
        self.client = client
        self.base_url = base_url.rstrip("/")
        self.limits = limits or TransportLimits()
        self.request_count = 0
        self.evidence: list[Evidence] = []
        self._started = time.monotonic()
        self._last_started = 0.0
        self._lock = asyncio.Lock()

    async def request(
        self,
        operation_id: str,
        *,
        identity: str,
        token: str | None,
        path: dict[str, str] | None = None,
        json_body: dict[str, Any] | None = None,
        cleanup: bool = False,
    ) -> ResponseRecord:
        if operation_id not in OPERATIONS:
            raise ScopeViolation(f"operation is not approved: {operation_id}")
        operation = OPERATIONS[operation_id]
        path_values = path or {}
        try:
            rendered_path = operation.path_template.format_map(path_values)
        except KeyError as exc:
            raise ScopeViolation(f"missing approved path parameter: {exc.args[0]}") from exc
        if ".." in rendered_path or not rendered_path.startswith("/") or "//" in rendered_path:
            raise ScopeViolation("rendered path is outside the approved form")

        main_limit = self.limits.max_requests - self.limits.cleanup_reserve
        if self.request_count >= (self.limits.max_requests if cleanup else main_limit):
            raise BudgetExceeded("target request budget exhausted")

        async with self._lock:
            now = time.monotonic()
            interval = 1 / self.limits.requests_per_second if self.limits.requests_per_second > 0 else 0
            wait = self._last_started + interval - now
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_started = time.monotonic()
            self.request_count += 1
            number = self.request_count

            headers = {"Accept": "application/json"}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            started = time.monotonic()
            try:
                async with asyncio.timeout(self.limits.request_deadline_seconds):
                    response = await self.client.request(
                        operation.method,
                        self.base_url + rendered_path,
                        headers=headers,
                        json=json_body,
                        follow_redirects=False,
                    )
                    raw = await response.aread()
            except TimeoutError:
                raise
            duration_ms = int((time.monotonic() - started) * 1000)
            if 300 <= response.status_code < 400:
                raise ScopeViolation("redirect response rejected")
            if len(raw) > self.limits.response_body_bytes:
                raise BudgetExceeded("decoded response body limit exceeded")
            try:
                body = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                body = {"body_type": response.headers.get("content-type", "unknown")}

            excerpt = allowlisted_body(body, operation.response_pointers)
            marker_match = isinstance(body, dict) and isinstance(body.get("content_marker"), str)
            evidence_data = {
                "operation_id": operation_id,
                "identity": identity,
                "method": operation.method,
                "path": operation.path_template,
                "status_code": response.status_code,
                "marker_match": marker_match,
                "response_excerpt": excerpt,
            }
            evidence_id = f"ev-{number:04}"
            self.evidence.append(Evidence(
                evidence_id=evidence_id,
                operation_id=operation_id,
                identity=identity,
                method=operation.method,
                path=operation.path_template,
                status_code=response.status_code,
                marker_match=marker_match,
                start_offset_ms=int((started - self._started) * 1000),
                duration_ms=duration_ms,
                request_headers=redact_headers(headers),
                response_excerpt=excerpt,
                sha256=canonical_sha256(evidence_data),
            ))
            return ResponseRecord(response.status_code, body, evidence_id, self.evidence[-1].start_offset_ms, duration_ms)
