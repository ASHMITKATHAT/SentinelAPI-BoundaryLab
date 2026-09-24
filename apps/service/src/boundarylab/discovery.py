from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from typing import Any
from urllib.parse import urlsplit


HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}
RESOURCE_PARAMETER = re.compile(r"(^id$|_id$|Id$|uuid$|key$)", re.IGNORECASE)
UUID_SEGMENT = re.compile(r"^[0-9a-f]{8}-[0-9a-f-]{27,}$", re.IGNORECASE)
OPAQUE_SEGMENT = re.compile(r"^(?:[A-Z]{2,8}-)?[0-9a-f]{6,}$", re.IGNORECASE)
EMAIL_SEGMENT = re.compile(r"^[^/@\s]+@[^/@\s]+\.[^/@\s]+$")
SENSITIVE_FIELD_HINTS = {
    "account", "address", "amount", "balance", "bank", "card", "content", "email",
    "invoice", "owner", "payment", "phone", "secret", "ssn", "tenant", "token",
}
MAX_PATHS = 500
MAX_OPERATIONS = 2_000
MAX_HAR_ENTRIES = 5_000


class DiscoveryError(ValueError):
    pass


def _canonical_hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _resolve_schema(document: dict[str, Any], schema: Any, depth: int = 0) -> dict[str, Any]:
    if not isinstance(schema, dict) or depth > 5:
        return {}
    reference = schema.get("$ref")
    if isinstance(reference, str) and reference.startswith("#/"):
        value: Any = document
        try:
            for part in reference[2:].split("/"):
                value = value[part.replace("~1", "/").replace("~0", "~")]
        except (KeyError, TypeError):
            return {}
        return _resolve_schema(document, value, depth + 1)
    return schema


def _response_fields(document: dict[str, Any], operation: dict[str, Any]) -> list[str]:
    fields: set[str] = set()
    for response in operation.get("responses", {}).values():
        if not isinstance(response, dict):
            continue
        for media in response.get("content", {}).values():
            schema = _resolve_schema(document, media.get("schema", {}) if isinstance(media, dict) else {})
            if schema.get("type") == "array":
                schema = _resolve_schema(document, schema.get("items", {}))
            properties = schema.get("properties", {})
            if isinstance(properties, dict):
                fields.update(str(name) for name in properties)
    return sorted(fields)[:100]


def _path_regex(template: str) -> re.Pattern[str]:
    escaped = re.escape(template)
    pattern = re.sub(r"\\\{[^/{}]+\\\}", r"[^/]+", escaped)
    return re.compile(f"^{pattern}/?$")


def _generalize_observed_path(path: str) -> str:
    parts = []
    for segment in path.split("/"):
        if (
            segment.isdigit()
            or UUID_SEGMENT.match(segment)
            or OPAQUE_SEGMENT.match(segment)
            or EMAIL_SEGMENT.match(segment)
            or len(segment) > 40
        ):
            parts.append("{id}")
        else:
            parts.append(segment[:120])
    normalized = "/".join(parts)
    return normalized if normalized.startswith("/") else f"/{normalized}"


def _har_operations(har: dict[str, Any] | None) -> tuple[list[tuple[str, str]], int]:
    if har is None:
        return [], 0
    entries = har.get("log", {}).get("entries")
    if not isinstance(entries, list):
        raise DiscoveryError("HAR must contain log.entries")
    if len(entries) > MAX_HAR_ENTRIES:
        raise DiscoveryError(f"HAR entry limit is {MAX_HAR_ENTRIES}")
    observed: list[tuple[str, str]] = []
    for entry in entries:
        request = entry.get("request", {}) if isinstance(entry, dict) else {}
        method = str(request.get("method", "")).upper()
        url = request.get("url")
        if method.lower() not in HTTP_METHODS or not isinstance(url, str):
            continue
        try:
            path = urlsplit(url).path
        except ValueError:
            continue
        if path.startswith("/") and len(path) <= 2_048:
            observed.append((method, path))
    return observed, len(entries)


def analyze_api_surface(document: dict[str, Any], har: dict[str, Any] | None = None) -> dict[str, Any]:
    if not isinstance(document, dict) or not str(document.get("openapi", "")).startswith("3."):
        raise DiscoveryError("an OpenAPI 3.x document is required")
    paths = document.get("paths")
    if not isinstance(paths, dict) or not paths:
        raise DiscoveryError("OpenAPI paths must be a non-empty object")
    if len(paths) > MAX_PATHS:
        raise DiscoveryError(f"OpenAPI path limit is {MAX_PATHS}")
    for value in _walk_values(document):
        if isinstance(value, dict) and isinstance(value.get("$ref"), str) and not value["$ref"].startswith("#/"):
            raise DiscoveryError("external OpenAPI references are not fetched; bundle the document first")

    root_security = document.get("security")
    operations: list[dict[str, Any]] = []
    matchers: list[tuple[str, str, re.Pattern[str]]] = []
    invariant_candidates: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for path, item in sorted(paths.items()):
        if not isinstance(path, str) or not path.startswith("/") or not isinstance(item, dict):
            continue
        common_parameters = item.get("parameters", []) if isinstance(item.get("parameters", []), list) else []
        for method, operation in item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            if len(operations) >= MAX_OPERATIONS:
                raise DiscoveryError(f"OpenAPI operation limit is {MAX_OPERATIONS}")
            operation_id = str(operation.get("operationId") or f"{method.lower()}:{path}")[:200]
            if operation_id in seen_ids:
                raise DiscoveryError(f"duplicate operationId: {operation_id}")
            seen_ids.add(operation_id)
            parameters = [*common_parameters, *(operation.get("parameters", []) or [])]
            path_parameters = sorted({
                str(parameter.get("name"))
                for parameter in parameters
                if isinstance(parameter, dict) and parameter.get("in") == "path" and parameter.get("name")
            })
            resource_parameters = [name for name in path_parameters if RESOURCE_PARAMETER.search(name)]
            security = operation.get("security", root_security)
            auth_required = bool(security)
            fields = _response_fields(document, operation)
            sensitive_fields = sorted({
                field for field in fields
                if any(hint in field.lower() for hint in SENSITIVE_FIELD_HINTS)
            })
            record = {
                "operation_id": operation_id,
                "method": method.upper(),
                "path": path,
                "auth_required": auth_required,
                "path_parameters": path_parameters,
                "resource_parameters": resource_parameters,
                "response_fields": fields,
                "sensitive_fields": sensitive_fields,
            }
            operations.append(record)
            matchers.append((record["method"], path, _path_regex(path)))

            if resource_parameters and method.lower() in {"get", "put", "patch", "delete"}:
                confidence = "high" if auth_required else "medium"
                digest = hashlib.sha256(f"{method}:{path}".encode()).hexdigest()[:10]
                invariant_candidates.append({
                    "id": f"ownership-{digest}",
                    "kind": "resource_ownership",
                    "operation_id": operation_id,
                    "method": method.upper(),
                    "path": path,
                    "resource_parameter": resource_parameters[0],
                    "confidence": confidence,
                    "proposed_rule": (
                        f"A second authenticated actor must not access another actor's "
                        f"{resource_parameters[0]} unless an explicit sharing relation permits it."
                    ),
                    "required_setup": "Capture an owner-created resource ID, then replay the operation as another valid actor.",
                    "review_required": True,
                })

    observed, har_entry_count = _har_operations(har)
    documented_hits: Counter[tuple[str, str]] = Counter()
    shadows: Counter[tuple[str, str]] = Counter()
    for method, path in observed:
        matched = next(((m, template) for m, template, pattern in matchers if m == method and pattern.match(path)), None)
        if matched:
            documented_hits[matched] += 1
        else:
            shadows[(method, _generalize_observed_path(path))] += 1

    documented_keys = {(operation["method"], operation["path"]) for operation in operations}
    unobserved = sorted(documented_keys - set(documented_hits)) if har is not None else []
    shadow_operations = [
        {
            "method": method,
            "path": path,
            "sample_count": count,
            "risk": "high" if any(word in path.lower() for word in ("admin", "debug", "internal", "export")) else "review",
        }
        for (method, path), count in sorted(shadows.items())
    ]

    return {
        "analysis_version": "boundarylab-discovery-v1",
        "spec": {
            "title": str(document.get("info", {}).get("title", "Untitled API"))[:200],
            "version": str(document.get("info", {}).get("version", "unknown"))[:80],
            "openapi": str(document.get("openapi")),
            "sha256": _canonical_hash(document),
        },
        "summary": {
            "documented_paths": len(paths),
            "documented_operations": len(operations),
            "ownership_candidates": len(invariant_candidates),
            "authenticated_operations": sum(bool(item["auth_required"]) for item in operations),
            "shadow_operations": len(shadow_operations),
            "har_entries": har_entry_count,
        },
        "operations": operations,
        "invariant_candidates": invariant_candidates,
        "traffic_diff": {
            "provided": har is not None,
            "documented_operations_observed": len(documented_hits),
            "shadow_operations": shadow_operations,
            "unobserved_documented_operations": [
                {"method": method, "path": path} for method, path in unobserved
            ],
        },
        "safety": {
            "active_requests_sent": False,
            "credentials_persisted": False,
            "har_headers_persisted": False,
            "requires_human_policy_approval": True,
        },
        "limitations": [
            "Candidate invariants are deterministic review suggestions, not approved authorization policy.",
            "An unobserved documented operation is not a zombie API; the supplied traffic sample may be incomplete.",
            "Active replay requires a trusted adapter that defines identities, setup, cleanup, markers and allowed operations.",
        ],
    }


def _walk_values(value: Any):
    stack = [value]
    while stack:
        current = stack.pop()
        yield current
        if isinstance(current, dict):
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
