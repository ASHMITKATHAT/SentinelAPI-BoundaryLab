from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import httpx

from fastapi import Cookie, Depends, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .discovery import DiscoveryError, analyze_api_surface
from .remediation import OpenAITriageClient, deterministic_triage
from .reports import html_report, json_report
from .repository import Repository, TERMINAL_STATES
from .worker import RunWorker, TrustedTarget


ROOT = Path(__file__).resolve().parents[4]


@dataclass(frozen=True, slots=True)
class Settings:
    database_path: Path
    bootstrap_secret: str
    targets: dict[str, TrustedTarget]
    allowed_origins: tuple[str, ...] = ("http://127.0.0.1:8080", "http://localhost:5173")
    secure_cookie: bool = False
    web_dist: Path = ROOT / "apps" / "web" / "dist"
    openai_api_key: str | None = None
    ai_model: str = "gpt-6-astra"

    @classmethod
    def from_env(cls) -> "Settings":
        secret = os.environ.get("BOUNDARYLAB_BOOTSTRAP_SECRET", "")
        if len(secret) < 16:
            raise RuntimeError("BOUNDARYLAB_BOOTSTRAP_SECRET must be at least 16 characters")
        data_dir = Path(os.environ.get("BOUNDARYLAB_DATA_DIR", ROOT / "var"))
        return cls(
            database_path=data_dir / "boundarylab.db",
            bootstrap_secret=secret,
            targets=default_targets(),
            secure_cookie=os.environ.get("BOUNDARYLAB_SECURE_COOKIE", "false").lower() == "true",
            openai_api_key=os.environ.get("OPENAI_API_KEY") or None,
            ai_model=os.environ.get("BOUNDARYLAB_AI_MODEL", "gpt-6-astra"),
        )


def default_targets() -> dict[str, TrustedTarget]:
    return {
        "demo-vulnerable": TrustedTarget("demo-vulnerable", "http://127.0.0.1:9011", "Vulnerable baseline"),
        "demo-owner-only": TrustedTarget("demo-owner-only", "http://127.0.0.1:9012", "Over-restrictive owner-only repair"),
        "demo-fixed": TrustedTarget("demo-fixed", "http://127.0.0.1:9013", "Correct policy-preserving repair"),
    }


class SessionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    bootstrap_secret: str = Field(min_length=16, max_length=512)


class RunCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target_alias: str = Field(min_length=1, max_length=80)


class ComparisonCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    run_ids: list[str] = Field(min_length=2, max_length=3)


class ArtifactCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    format: Literal["report_html", "results_json"]


class DiscoveryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: str = Field(min_length=1, max_length=120)
    document: dict[str, Any]
    har: dict[str, Any] | None = None


class ExplanationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mode: Literal["deterministic", "ai"] = "deterministic"


async def validated_json(request: Request, model: type[BaseModel], *, limit: int = 2_000_000) -> BaseModel:
    content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if content_type != "application/json":
        raise HTTPException(status_code=415, detail="application/json is required")
    declared = request.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > limit:
        raise HTTPException(status_code=413, detail=f"request body exceeds {limit} bytes")
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > limit:
            raise HTTPException(status_code=413, detail=f"request body exceeds {limit} bytes")
    try:
        value = json.loads(body)
        return model.model_validate(value)
    except (json.JSONDecodeError, ValidationError, UnicodeDecodeError, RecursionError) as exc:
        raise HTTPException(status_code=422, detail="invalid request document") from exc


def public_run(run: dict, *, include_report: bool = False) -> dict:
    result = {key: value for key, value in run.items() if key not in {"target_origin", "report"}}
    if include_report:
        result["report"] = run.get("report")
    return result


def create_app(settings: Settings | None = None) -> FastAPI:
    configured = settings or Settings.from_env()
    repository = Repository(configured.database_path)
    worker = RunWorker(repository, configured.targets)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        worker.start()
        worker.notify()
        yield
        await worker.stop()

    app = FastAPI(
        title="SentinelAPI BoundaryLab control API",
        version="0.2.0",
        description="Local single-operator authorization regression workbench",
        lifespan=lifespan,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"])
    app.state.settings = configured
    app.state.repository = repository
    app.state.worker = worker

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        supplied_request_id = request.headers.get("x-request-id", "")
        request.state.request_id = supplied_request_id[:80] if supplied_request_id.isascii() else ""
        request.state.request_id = request.state.request_id or secrets.token_hex(8)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        else:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
                "connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
            )
        return response

    def check_origin(request: Request) -> None:
        origin = request.headers.get("origin")
        if origin and origin not in configured.allowed_origins:
            raise HTTPException(status_code=403, detail="origin is not allowed")

    def session_dependency(boundarylab_session: str | None = Cookie(default=None)) -> dict:
        session = repository.get_session(boundarylab_session)
        if not session:
            raise HTTPException(status_code=401, detail="operator session required")
        return session

    def mutation_dependency(
        request: Request,
        session: dict = Depends(session_dependency),
        x_csrf_token: str | None = Header(default=None),
    ) -> dict:
        check_origin(request)
        if not x_csrf_token or not hmac.compare_digest(x_csrf_token, session["csrf_token"]):
            raise HTTPException(status_code=403, detail="valid CSRF token required")
        return session

    @app.get("/api/healthz")
    async def health():
        return {"status": "ok", "service": "boundarylab", "version": "0.2.0"}

    @app.post("/api/v1/session", status_code=201)
    async def create_session(body: SessionCreate, request: Request, response: Response):
        check_origin(request)
        if not hmac.compare_digest(body.bootstrap_secret, configured.bootstrap_secret):
            raise HTTPException(status_code=401, detail="invalid bootstrap secret")
        token, csrf = repository.create_session()
        response.set_cookie(
            "boundarylab_session",
            token,
            max_age=8 * 60 * 60,
            httponly=True,
            secure=configured.secure_cookie,
            samesite="strict",
            path="/",
        )
        return {"operator": "local-operator", "csrf_token": csrf, "expires_in_seconds": 8 * 60 * 60}

    @app.get("/api/v1/session")
    async def get_session(session: dict = Depends(session_dependency)):
        return {"operator": "local-operator", "authenticated": True, "csrf_token": session["csrf_token"]}

    @app.delete("/api/v1/session", status_code=204)
    async def delete_session(
        response: Response,
        _: dict = Depends(mutation_dependency),
        boundarylab_session: str | None = Cookie(default=None),
    ):
        repository.delete_session(boundarylab_session)
        response.delete_cookie("boundarylab_session", path="/")

    @app.get("/api/v1/targets")
    async def targets(_: dict = Depends(session_dependency)):
        return [
            {
                "alias": target.alias,
                "label": target.label,
                "origin": target.origin,
                "synthetic_fixture": True,
                "limits": {"requests": 200, "requests_per_second": 2, "in_flight": 1, "response_bytes": 65_536},
            }
            for target in configured.targets.values()
        ]

    @app.get("/api/v1/capabilities")
    async def capabilities(_: dict = Depends(session_dependency)):
        return {
            "discovery": {"openapi": True, "har": True, "active_replay": "trusted_adapters_only"},
            "remediation": {
                "deterministic": True,
                "ai_configured": bool(configured.openai_api_key),
                "model": configured.ai_model if configured.openai_api_key else None,
                "data_sent": "failed case summaries only when operator explicitly selects AI mode",
            },
        }

    @app.get("/api/v1/policy")
    async def policy(_: dict = Depends(session_dependency)):
        path = ROOT / "examples" / "invoice-policy.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        encoded = json.dumps(document, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return {"approved": True, "sha256": hashlib.sha256(encoded).hexdigest(), "document": document}

    @app.get("/api/v1/spec")
    async def specification(_: dict = Depends(session_dependency)):
        path = ROOT / "contracts" / "demo-api.openapi.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        operations = [
            operation["operationId"]
            for item in document.get("paths", {}).values()
            for operation in item.values()
            if isinstance(operation, dict) and operation.get("operationId")
        ]
        return {"title": document["info"]["title"], "version": document["info"]["version"],
                "openapi": document["openapi"], "operation_count": len(operations), "operations": operations,
                "document": document}

    @app.post("/api/v1/discovery/analyses", status_code=201)
    async def create_discovery_analysis(request: Request, _: dict = Depends(mutation_dependency)):
        body = await validated_json(request, DiscoveryCreate)
        assert isinstance(body, DiscoveryCreate)
        try:
            result = analyze_api_surface(body.document, body.har)
        except DiscoveryError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return repository.create_discovery_analysis(body.label, result)

    @app.get("/api/v1/discovery/analyses")
    async def list_discovery_analyses(_: dict = Depends(session_dependency), limit: int = 20):
        if not 1 <= limit <= 50:
            raise HTTPException(status_code=422, detail="limit must be between 1 and 50")
        return repository.list_discovery_analyses(limit)

    @app.post("/api/v1/runs", status_code=202)
    async def create_run(body: RunCreate, _: dict = Depends(mutation_dependency)):
        target = configured.targets.get(body.target_alias)
        if not target:
            raise HTTPException(status_code=422, detail="target alias is not in the trusted registry")
        if len([run for run in repository.list_runs(100) if run["state"] in {"queued", "running"}]) >= 10:
            raise HTTPException(status_code=429, detail="local run queue is full")
        run = repository.create_run(target.alias, target.origin)
        worker.notify()
        return public_run(run)

    @app.get("/api/v1/runs")
    async def list_runs(_: dict = Depends(session_dependency), limit: int = 20):
        if not 1 <= limit <= 100:
            raise HTTPException(status_code=422, detail="limit must be between 1 and 100")
        return [public_run(run) for run in repository.list_runs(limit)]

    @app.get("/api/v1/runs/{run_id}")
    async def get_run(run_id: str, _: dict = Depends(session_dependency)):
        run = repository.get_run(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="run not found")
        return public_run(run, include_report=True)

    @app.get("/api/v1/runs/{run_id}/events")
    async def run_events(run_id: str, _: dict = Depends(session_dependency), after: int = 0, limit: int = 100):
        if not repository.get_run(run_id):
            raise HTTPException(status_code=404, detail="run not found")
        if after < 0 or not 1 <= limit <= 100:
            raise HTTPException(status_code=422, detail="invalid event cursor or limit")
        events = repository.events(run_id, after, limit)
        return {"events": events, "next_cursor": events[-1]["id"] if events else after}

    @app.post("/api/v1/runs/{run_id}/cancel", status_code=202)
    async def cancel_run(run_id: str, _: dict = Depends(mutation_dependency)):
        run = repository.get_run(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="run not found")
        if run["state"] in TERMINAL_STATES:
            return public_run(run)
        updated = worker.cancel(run_id)
        return public_run(updated)

    @app.post("/api/v1/comparisons")
    async def compare_runs(body: ComparisonCreate, _: dict = Depends(mutation_dependency)):
        if len(set(body.run_ids)) != len(body.run_ids):
            raise HTTPException(status_code=422, detail="run IDs must be unique")
        runs = [repository.get_run(run_id) for run_id in body.run_ids]
        if any(run is None for run in runs):
            raise HTTPException(status_code=404, detail="one or more runs were not found")
        typed_runs = [run for run in runs if run]
        if any(run["state"] != "completed" or not run["report"] for run in typed_runs):
            raise HTTPException(status_code=409, detail="only completed runs with reports can be compared")
        policies = {run["report"]["policy_version"] for run in typed_runs}
        case_sets = {tuple(case["case_id"] for case in run["report"]["cases"]) for run in typed_runs}
        if len(policies) != 1 or len(case_sets) != 1:
            raise HTTPException(status_code=409, detail="runs use non-comparable policy or case suites")
        rows = []
        for index, case_id in enumerate(next(iter(case_sets))):
            first = typed_runs[0]["report"]["cases"][index]
            rows.append({
                "case_id": case_id,
                "name": first["name"],
                "outcomes": [
                    {
                        "run_id": run["id"], "target_alias": run["target_alias"], "build_id": run["build_id"],
                        "verdict": run["report"]["cases"][index]["verdict"],
                        "kind": run["report"]["cases"][index].get("finding_kind"),
                    }
                    for run in typed_runs
                ],
            })
        return {"compatible": True, "policy_version": next(iter(policies)),
                "runs": [public_run(run) for run in typed_runs], "rows": rows}

    @app.post("/api/v1/runs/{run_id}/artifacts", status_code=201)
    async def create_artifact(run_id: str, body: ArtifactCreate, _: dict = Depends(mutation_dependency)):
        report = repository.get_report(run_id)
        if not report:
            raise HTTPException(status_code=409, detail="completed report required")
        content = html_report(report) if body.format == "report_html" else json_report(report)
        artifact = repository.create_artifact(run_id, body.format, content)
        return {**artifact, "download_path": f"/api/v1/artifacts/{artifact['id']}"}

    @app.post("/api/v1/runs/{run_id}/explanations", status_code=201)
    async def create_explanation(
        run_id: str,
        body: ExplanationCreate,
        _: dict = Depends(mutation_dependency),
    ):
        report = repository.get_report(run_id)
        if not report:
            raise HTTPException(status_code=409, detail="completed report required")
        if body.mode == "deterministic":
            result = deterministic_triage(report)
        else:
            if not configured.openai_api_key:
                raise HTTPException(status_code=409, detail="AI remediation is not configured; use deterministic mode")
            try:
                result = await OpenAITriageClient(configured.openai_api_key, configured.ai_model).generate(report)
            except (httpx.HTTPError, RuntimeError, ValidationError, json.JSONDecodeError) as exc:
                raise HTTPException(status_code=502, detail="AI remediation provider failed safely") from exc
        return repository.save_explanation(run_id, result)

    @app.get("/api/v1/artifacts/{artifact_id}")
    async def get_artifact(artifact_id: str, _: dict = Depends(session_dependency)):
        artifact = repository.get_artifact(artifact_id)
        if not artifact:
            raise HTTPException(status_code=404, detail="artifact not found")
        media_type = "text/html; charset=utf-8" if artifact["format"] == "report_html" else "application/json"
        extension = "html" if artifact["format"] == "report_html" else "json"
        response = Response(content=artifact["content"], media_type=media_type)
        response.headers["Content-Disposition"] = f'attachment; filename="boundarylab-{artifact["run_id"]}.{extension}"'
        response.headers["Content-Security-Policy"] = "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'"
        return response

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": f"HTTP_{exc.status_code}", "message": str(exc.detail),
                               "request_id": getattr(request.state, "request_id", "local")}},
        )

    if configured.web_dist.exists() and (configured.web_dist / "index.html").exists():
        assets = configured.web_dist / "assets"
        if assets.exists():
            app.mount("/assets", StaticFiles(directory=assets), name="assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def spa(full_path: str):
            candidate = configured.web_dist / full_path
            if full_path and candidate.is_file() and configured.web_dist.resolve() in candidate.resolve().parents:
                return FileResponse(candidate)
            return FileResponse(configured.web_dist / "index.html")
    else:
        @app.get("/", include_in_schema=False)
        async def root_status():
            return {"service": "BoundaryLab", "ui": "not built", "docs": "/api/docs"}

    return app
