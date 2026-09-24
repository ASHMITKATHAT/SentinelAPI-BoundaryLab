from __future__ import annotations

import hashlib
import json
from typing import Any


SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "proxy-authorization", "x-api-key"}


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    return {
        key: "<REDACTED>" if key.lower() in SENSITIVE_HEADERS else value
        for key, value in headers.items()
    }


def allowlisted_body(body: Any, pointers: tuple[str, ...]) -> Any:
    if not isinstance(body, dict):
        return {"body_type": type(body).__name__}
    result: dict[str, Any] = {}
    for pointer in pointers:
        if not pointer.startswith("/") or "/" in pointer[1:]:
            continue
        key = pointer[1:].replace("~1", "/").replace("~0", "~")
        if key in body:
            value = body[key]
            result[key] = value if isinstance(value, (str, int, float, bool, type(None))) else "<COMPLEX_VALUE>"
    return result


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()

