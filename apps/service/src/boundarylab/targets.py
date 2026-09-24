from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .transport import Operation


ENV_NAME = re.compile(r"^[A-Z][A-Z0-9_]{2,127}$")
ALIAS = re.compile(r"^[a-z][a-z0-9-]{1,62}$")


class RealTargetConfigError(ValueError):
    pass


def _pointer(value: str) -> str:
    if not value.startswith("/") or ".." in value or len(value) > 200 or any(ord(char) < 32 for char in value):
        raise ValueError("JSON pointers must start with / and stay below 200 characters")
    return value


class IdentityConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=40, pattern=r"^[a-z][a-z0-9_-]*$")
    expectation: Literal["allow", "deny"]
    token_env: str | None = None
    forbidden_pointers: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("token_env")
    @classmethod
    def validate_token_env(cls, value: str | None) -> str | None:
        if value is not None and not ENV_NAME.fullmatch(value):
            raise ValueError("token_env must be an uppercase environment variable name")
        return value

    @field_validator("forbidden_pointers")
    @classmethod
    def validate_forbidden_pointers(cls, values: list[str]) -> list[str]:
        return list(dict.fromkeys(_pointer(value) for value in values))

    @model_validator(mode="after")
    def anonymous_has_no_secret(self) -> "IdentityConfig":
        if self.name == "anonymous" and self.token_env is not None:
            raise ValueError("anonymous identity cannot reference a token")
        if self.name != "anonymous" and self.token_env is None:
            raise ValueError("authenticated identities require token_env")
        return self


class ProbeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z][A-Za-z0-9_.-]*$")
    method: Literal["GET"] = "GET"
    path_template: str = Field(min_length=2, max_length=300)
    resource_id_env: str
    marker_pointer: str
    marker_env: str
    build_id_env: str
    deny_statuses: list[int] = Field(default_factory=lambda: [401, 403, 404], min_length=1, max_length=5)
    identities: list[IdentityConfig] = Field(min_length=2, max_length=6)

    @field_validator("resource_id_env", "marker_env", "build_id_env")
    @classmethod
    def validate_env_name(cls, value: str) -> str:
        if not ENV_NAME.fullmatch(value):
            raise ValueError("secret/value references must be uppercase environment variable names")
        return value

    @field_validator("marker_pointer")
    @classmethod
    def validate_marker_pointer(cls, value: str) -> str:
        return _pointer(value)

    @field_validator("path_template")
    @classmethod
    def validate_path(cls, value: str) -> str:
        parsed = urlsplit(value)
        if (
            not value.startswith("/")
            or parsed.scheme
            or parsed.netloc
            or parsed.query
            or parsed.fragment
            or ".." in value
            or "//" in value
            or any(ord(char) < 32 for char in value)
        ):
            raise ValueError("path_template must be a safe absolute path")
        remainder = value.replace("{resource_id}", "")
        if value.count("{resource_id}") != 1 or "{" in remainder or "}" in remainder:
            raise ValueError("path_template must contain exactly one {resource_id} placeholder")
        return value

    @field_validator("deny_statuses")
    @classmethod
    def validate_deny_statuses(cls, values: list[int]) -> list[int]:
        if any(value not in {401, 403, 404} for value in values):
            raise ValueError("deny_statuses may contain only 401, 403 and 404")
        return sorted(set(values))

    @model_validator(mode="after")
    def validate_identities(self) -> "ProbeConfig":
        names = [identity.name for identity in self.identities]
        if len(set(names)) != len(names):
            raise ValueError("identity names must be unique")
        if not any(identity.expectation == "allow" for identity in self.identities):
            raise ValueError("at least one allowed identity is required")
        if not any(identity.expectation == "deny" for identity in self.identities):
            raise ValueError("at least one denied identity is required")
        return self


class TargetConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alias: str
    label: str = Field(min_length=1, max_length=100)
    origin: str
    openapi_path: str = Field(min_length=1, max_length=500)
    probe: ProbeConfig

    @field_validator("alias")
    @classmethod
    def validate_alias(cls, value: str) -> str:
        if not ALIAS.fullmatch(value):
            raise ValueError("alias must use lowercase letters, digits and hyphens")
        return value

    @field_validator("origin")
    @classmethod
    def validate_origin(cls, value: str) -> str:
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.path not in {"", "/"}:
            raise ValueError("origin must be an HTTP(S) origin without a path")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("origin cannot contain credentials, query or fragment")
        if parsed.hostname.lower() not in {"127.0.0.1", "::1"}:
            raise ValueError("real probes require a numeric loopback target; use an authorized local or SSH-forwarded staging port")
        return value.rstrip("/")


class TargetRegistryConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: Literal["1.0"]
    targets: list[TargetConfig] = Field(min_length=1, max_length=10)

    @model_validator(mode="after")
    def unique_aliases(self) -> "TargetRegistryConfig":
        aliases = [target.alias for target in self.targets]
        if len(set(aliases)) != len(aliases):
            raise ValueError("target aliases must be unique")
        return self


@dataclass(frozen=True, slots=True)
class ProbeIdentity:
    name: str
    expectation: Literal["allow", "deny"]
    token_env: str | None
    forbidden_pointers: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AccessProbeAdapter:
    operation_id: str
    path_template: str
    resource_id_env: str
    marker_pointer: str
    marker_env: str
    build_id_env: str
    deny_statuses: tuple[int, ...]
    identities: tuple[ProbeIdentity, ...]

    @property
    def operation(self) -> Operation:
        pointers = tuple(dict.fromkeys((self.marker_pointer, "/code", "/message", *(
            pointer for identity in self.identities for pointer in identity.forbidden_pointers
        ))))
        return Operation("GET", self.path_template, pointers)

    @property
    def required_environment(self) -> tuple[str, ...]:
        names = [self.resource_id_env, self.marker_env, self.build_id_env]
        names.extend(identity.token_env for identity in self.identities if identity.token_env)
        return tuple(dict.fromkeys(name for name in names if name))


@dataclass(frozen=True, slots=True)
class TrustedTarget:
    alias: str
    origin: str
    label: str
    synthetic_fixture: bool = False
    adapter: AccessProbeAdapter | None = None
    openapi_path: Path | None = None

    def missing_environment(self, environment: dict[str, str] | os._Environ[str] | None = None) -> tuple[str, ...]:
        source = environment if environment is not None else os.environ
        if not self.adapter:
            return ()
        return tuple(name for name in self.adapter.required_environment if not source.get(name))


def load_real_targets(path: Path) -> dict[str, TrustedTarget]:
    try:
        if not path.is_file() or path.stat().st_size > 1_000_000:
            raise RealTargetConfigError("target registry is missing or exceeds 1 MB")
        raw = path.read_text(encoding="utf-8")
        parsed = TargetRegistryConfig.model_validate_json(raw)
    except (OSError, ValueError) as exc:
        raise RealTargetConfigError(f"invalid real-target registry: {exc}") from exc

    targets: dict[str, TrustedTarget] = {}
    for item in parsed.targets:
        config_root = path.parent.resolve()
        spec_path = (config_root / item.openapi_path).resolve()
        if not spec_path.is_relative_to(config_root):
            raise RealTargetConfigError(f"OpenAPI file for {item.alias} must stay inside the target-config directory")
        try:
            if not spec_path.is_file() or spec_path.stat().st_size > 2_000_000:
                raise RealTargetConfigError(f"OpenAPI file for {item.alias} is missing or exceeds 2 MB")
            document = json.loads(spec_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RealTargetConfigError(f"OpenAPI file for {item.alias} is not valid JSON") from exc
        if not isinstance(document, dict) or not str(document.get("openapi", "")).startswith("3."):
            raise RealTargetConfigError(f"OpenAPI file for {item.alias} must be OpenAPI 3.x JSON")
        operation = document.get("paths", {}).get(item.probe.path_template, {}).get("get")
        if not isinstance(operation, dict) or operation.get("operationId") != item.probe.operation_id:
            raise RealTargetConfigError(
                f"OpenAPI file for {item.alias} must declare GET {item.probe.path_template} "
                f"with operationId {item.probe.operation_id}"
            )

        adapter = AccessProbeAdapter(
            operation_id=item.probe.operation_id,
            path_template=item.probe.path_template,
            resource_id_env=item.probe.resource_id_env,
            marker_pointer=item.probe.marker_pointer,
            marker_env=item.probe.marker_env,
            build_id_env=item.probe.build_id_env,
            deny_statuses=tuple(item.probe.deny_statuses),
            identities=tuple(
                ProbeIdentity(
                    name=identity.name,
                    expectation=identity.expectation,
                    token_env=identity.token_env,
                    forbidden_pointers=tuple(identity.forbidden_pointers),
                )
                for identity in item.probe.identities
            ),
        )
        targets[item.alias] = TrustedTarget(
            alias=item.alias,
            origin=item.origin,
            label=item.label,
            adapter=adapter,
            openapi_path=spec_path,
        )
    return targets
