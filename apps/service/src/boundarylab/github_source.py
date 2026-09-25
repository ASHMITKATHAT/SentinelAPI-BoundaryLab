from __future__ import annotations

import base64
import binascii
import json
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import httpx


MAX_OPENAPI_BYTES = 2_000_000
MAX_GITHUB_RESPONSE_BYTES = 3_000_000
REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}/[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$")


class GitHubSourceError(ValueError):
    """A safe, operator-facing GitHub source error."""


@dataclass(frozen=True, slots=True)
class GitHubSource:
    repository: str
    ref: str
    path: str


def normalize_source(repository: str, ref: str, path: str) -> GitHubSource:
    normalized_repository = repository.strip()
    for prefix in ("https://github.com/",):
        if normalized_repository.lower().startswith(prefix):
            normalized_repository = normalized_repository[len(prefix):]
            break
    normalized_repository = normalized_repository.removesuffix(".git").strip("/")
    if not REPOSITORY_PATTERN.fullmatch(normalized_repository):
        raise GitHubSourceError("Use a GitHub repository in owner/name or https://github.com/owner/name format.")

    normalized_ref = ref.strip()
    if len(normalized_ref) > 200 or any(ord(character) < 32 for character in normalized_ref):
        raise GitHubSourceError("Git ref is invalid or exceeds 200 characters.")

    normalized_path = path.strip().replace("\\", "/").lstrip("/")
    parts = normalized_path.split("/")
    if (
        not normalized_path
        or len(normalized_path) > 500
        or any(part in {"", ".", ".."} for part in parts)
        or not normalized_path.lower().endswith(".json")
    ):
        raise GitHubSourceError("OpenAPI path must be a repository-relative JSON file without dot segments.")
    return GitHubSource(normalized_repository, normalized_ref, normalized_path)


async def _limited_json(response: httpx.Response) -> dict[str, Any]:
    body = bytearray()
    async for chunk in response.aiter_bytes():
        body.extend(chunk)
        if len(body) > MAX_GITHUB_RESPONSE_BYTES:
            raise GitHubSourceError("GitHub response exceeds the safe import limit.")
    try:
        value = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError, RecursionError) as exc:
        raise GitHubSourceError("GitHub returned an invalid response.") from exc
    if not isinstance(value, dict):
        raise GitHubSourceError("GitHub returned an unexpected response shape.")
    return value


class GitHubSourceClient:
    def __init__(self, token: str | None = None, *, transport: httpx.AsyncBaseTransport | None = None):
        self.token = token
        self.transport = transport

    async def import_openapi(self, repository: str, ref: str, path: str) -> dict[str, Any]:
        source = normalize_source(repository, ref, path)
        owner, name = source.repository.split("/", 1)
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "SentinelAPI-BoundaryLab/0.4",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        timeout = httpx.Timeout(12, connect=5)
        limits = httpx.Limits(max_connections=1, max_keepalive_connections=1)
        try:
            async with httpx.AsyncClient(
                base_url="https://api.github.com",
                headers=headers,
                timeout=timeout,
                limits=limits,
                follow_redirects=False,
                transport=self.transport,
            ) as client:
                async with client.stream("GET", f"/repos/{quote(owner, safe='')}/{quote(name, safe='')}") as repository_response:
                    self._raise_for_status(repository_response, "repository")
                    repository_data = await _limited_json(repository_response)
                resolved_ref = source.ref or str(repository_data.get("default_branch") or "main")

                async with client.stream(
                    "GET",
                    f"/repos/{quote(owner, safe='')}/{quote(name, safe='')}/contents/{quote(source.path, safe='/')}",
                    params={"ref": resolved_ref},
                ) as content_response:
                    self._raise_for_status(content_response, "OpenAPI file")
                    content_data = await _limited_json(content_response)
        except GitHubSourceError:
            raise
        except (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError) as exc:
            raise GitHubSourceError("GitHub could not be reached. Check connectivity and try again.") from exc

        if content_data.get("type") != "file" or content_data.get("encoding") != "base64":
            raise GitHubSourceError("The selected GitHub path is not an importable JSON file.")
        encoded = content_data.get("content")
        if not isinstance(encoded, str):
            raise GitHubSourceError("GitHub did not return file content.")
        try:
            compact_encoded = "".join(encoded.split())
            raw = base64.b64decode(compact_encoded, validate=True)
        except (ValueError, binascii.Error) as exc:
            raise GitHubSourceError("GitHub returned invalid file encoding.") from exc
        if len(raw) > MAX_OPENAPI_BYTES:
            raise GitHubSourceError("OpenAPI file exceeds the 2 MB import limit.")
        try:
            document = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError, RecursionError) as exc:
            raise GitHubSourceError("The selected file is not valid OpenAPI JSON.") from exc
        if not isinstance(document, dict) or not str(document.get("openapi", "")).startswith("3."):
            raise GitHubSourceError("The selected file must contain an OpenAPI 3.x document.")
        operation_count = sum(
            1
            for path_item in document.get("paths", {}).values()
            if isinstance(path_item, dict)
            for method, operation in path_item.items()
            if method.lower() in {"get", "put", "post", "delete", "patch", "head", "options", "trace"}
            and isinstance(operation, dict)
        ) if isinstance(document.get("paths"), dict) else 0
        return {
            "repository": source.repository,
            "repository_url": str(repository_data.get("html_url") or f"https://github.com/{source.repository}"),
            "private": bool(repository_data.get("private")),
            "default_branch": str(repository_data.get("default_branch") or ""),
            "ref": resolved_ref,
            "path": source.path,
            "file_sha": str(content_data.get("sha") or ""),
            "operation_count": operation_count,
            "document": document,
        }

    def _raise_for_status(self, response: httpx.Response, resource: str) -> None:
        if response.status_code < 400:
            return
        if response.status_code == 404:
            message = f"GitHub {resource} was not found. Check the repository, ref and path."
        elif response.status_code in {401, 403}:
            message = "GitHub denied the import or the API rate limit was reached. Configure BOUNDARYLAB_GITHUB_TOKEN for private repositories or higher limits."
        elif response.status_code == 429:
            message = "GitHub rate limit reached. Wait or configure BOUNDARYLAB_GITHUB_TOKEN."
        else:
            message = f"GitHub {resource} request failed with HTTP {response.status_code}."
        raise GitHubSourceError(message)
