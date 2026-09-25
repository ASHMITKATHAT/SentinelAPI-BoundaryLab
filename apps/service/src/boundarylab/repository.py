from __future__ import annotations

import hashlib
import json
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Iterator


TERMINAL_STATES = {"completed", "failed", "interrupted", "cancelled"}


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class Repository:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        try:
            yield connection
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self.connection() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY,
                    csrf_token TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY,
                    target_alias TEXT NOT NULL,
                    target_origin TEXT NOT NULL,
                    state TEXT NOT NULL CHECK(state IN ('queued','running','completed','failed','interrupted','cancelled')),
                    assessment TEXT,
                    has_incomplete_cases INTEGER NOT NULL DEFAULT 0,
                    build_id TEXT,
                    counts_json TEXT,
                    request_count INTEGER NOT NULL DEFAULT 0,
                    cleanup_status TEXT NOT NULL DEFAULT 'not_started',
                    execution_error TEXT,
                    report_json TEXT,
                    cancellation_requested INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_runs_created_at ON runs(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_runs_state_created_at ON runs(state, created_at);
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
                    type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_events_run_id_id ON events(run_id, id);
                CREATE TABLE IF NOT EXISTS artifacts (
                    id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
                    format TEXT NOT NULL CHECK(format IN ('report_html','results_json')),
                    content BLOB NOT NULL,
                    sha256 TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS discovery_analyses (
                    id TEXT PRIMARY KEY,
                    label TEXT NOT NULL,
                    spec_sha256 TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_discovery_created_at ON discovery_analyses(created_at DESC);
                CREATE TABLE IF NOT EXISTS candidate_reviews (
                    id TEXT PRIMARY KEY,
                    analysis_id TEXT NOT NULL REFERENCES discovery_analyses(id) ON DELETE CASCADE,
                    candidate_id TEXT NOT NULL,
                    decision TEXT NOT NULL CHECK(decision IN ('approved','rejected')),
                    rationale TEXT NOT NULL,
                    reviewer TEXT NOT NULL,
                    candidate_sha256 TEXT NOT NULL,
                    candidate_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_candidate_reviews_analysis_created
                    ON candidate_reviews(analysis_id, created_at, id);
                CREATE TABLE IF NOT EXISTS explanations (
                    id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
                    mode TEXT NOT NULL,
                    model TEXT,
                    result_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(run_id, mode, model)
                );
                """
            )
            connection.execute(
                "INSERT OR IGNORE INTO schema_migrations(version, applied_at) VALUES(1, ?)",
                (utc_now(),),
            )
            connection.execute(
                "INSERT OR IGNORE INTO schema_migrations(version, applied_at) VALUES(2, ?)",
                (utc_now(),),
            )
            connection.execute(
                "INSERT OR IGNORE INTO schema_migrations(version, applied_at) VALUES(3, ?)",
                (utc_now(),),
            )
            now = utc_now()
            connection.execute(
                """UPDATE runs SET state='interrupted', has_incomplete_cases=1,
                   execution_error='worker stopped before completion', updated_at=?, completed_at=?
                   WHERE state='running'""",
                (now, now),
            )

    def create_session(self, lifetime_hours: int = 8) -> tuple[str, str]:
        token = secrets.token_urlsafe(32)
        csrf = secrets.token_urlsafe(24)
        now = datetime.now(UTC)
        with self.connection() as connection:
            connection.execute("DELETE FROM sessions WHERE expires_at <= ?", (now.isoformat(),))
            connection.execute(
                "INSERT INTO sessions(token_hash, csrf_token, expires_at, created_at) VALUES(?,?,?,?)",
                (token_hash(token), csrf, (now + timedelta(hours=lifetime_hours)).isoformat(), now.isoformat()),
            )
        return token, csrf

    def get_session(self, token: str | None) -> dict[str, str] | None:
        if not token:
            return None
        with self.connection() as connection:
            row = connection.execute(
                "SELECT csrf_token, expires_at FROM sessions WHERE token_hash=? AND expires_at > ?",
                (token_hash(token), utc_now()),
            ).fetchone()
        return dict(row) if row else None

    def delete_session(self, token: str | None) -> None:
        if not token:
            return
        with self.connection() as connection:
            connection.execute("DELETE FROM sessions WHERE token_hash=?", (token_hash(token),))

    def create_run(self, target_alias: str, target_origin: str) -> dict[str, Any]:
        run_id = f"run_{secrets.token_hex(8)}"
        now = utc_now()
        with self.connection() as connection:
            connection.execute(
                """INSERT INTO runs(id,target_alias,target_origin,state,created_at,updated_at)
                   VALUES(?,?,?,'queued',?,?)""",
                (run_id, target_alias, target_origin, now, now),
            )
            connection.execute(
                "INSERT INTO events(run_id,type,message,created_at) VALUES(?,?,?,?)",
                (run_id, "queued", f"Run queued for trusted target {target_alias}", now),
            )
        return self.get_run(run_id)

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self.connection() as connection:
            row = connection.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
        return self._run_row(row) if row else None

    def list_runs(self, limit: int = 20) -> list[dict[str, Any]]:
        with self.connection() as connection:
            rows = connection.execute("SELECT * FROM runs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [self._run_row(row) for row in rows]

    def claim_next_run(self) -> dict[str, Any] | None:
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT id FROM runs WHERE state='queued' AND cancellation_requested=0 ORDER BY created_at LIMIT 1"
            ).fetchone()
            if not row:
                connection.execute("COMMIT")
                return None
            now = utc_now()
            connection.execute(
                "UPDATE runs SET state='running', started_at=?, updated_at=? WHERE id=? AND state='queued'",
                (now, now, row["id"]),
            )
            connection.execute(
                "INSERT INTO events(run_id,type,message,created_at) VALUES(?,?,?,?)",
                (row["id"], "running", "Worker claimed run", now),
            )
            connection.execute("COMMIT")
        return self.get_run(row["id"])

    def complete_run(self, run_id: str, report: dict[str, Any]) -> None:
        now = utc_now()
        with self.connection() as connection:
            connection.execute(
                """UPDATE runs SET state='completed', assessment=?, has_incomplete_cases=?, build_id=?,
                   counts_json=?, request_count=?, cleanup_status=?, execution_error=?, report_json=?,
                   updated_at=?, completed_at=? WHERE id=?""",
                (
                    report["assessment"], int(report["has_incomplete_cases"]), report.get("build_id"),
                    json.dumps(report["counts"], separators=(",", ":")), report["request_count"],
                    report["cleanup_status"], report.get("execution_error"),
                    json.dumps(report, separators=(",", ":")), now, now, run_id,
                ),
            )
            connection.execute(
                "INSERT INTO events(run_id,type,message,created_at) VALUES(?,?,?,?)",
                (run_id, "completed", f"Run completed with assessment {report['assessment']}", now),
            )

    def fail_run(self, run_id: str, state: str, message: str) -> None:
        if state not in {"failed", "interrupted", "cancelled"}:
            raise ValueError("invalid terminal failure state")
        now = utc_now()
        with self.connection() as connection:
            connection.execute(
                """UPDATE runs SET state=?, has_incomplete_cases=1, execution_error=?, updated_at=?, completed_at=?
                   WHERE id=? AND state NOT IN ('completed','failed','interrupted','cancelled')""",
                (state, message, now, now, run_id),
            )
            connection.execute(
                "INSERT INTO events(run_id,type,message,created_at) VALUES(?,?,?,?)",
                (run_id, state, message, now),
            )

    def request_cancel(self, run_id: str) -> dict[str, Any] | None:
        with self.connection() as connection:
            row = connection.execute("SELECT state FROM runs WHERE id=?", (run_id,)).fetchone()
            if not row:
                return None
            if row["state"] == "queued":
                self.fail_run(run_id, "cancelled", "Cancelled before worker execution")
            elif row["state"] == "running":
                connection.execute(
                    "UPDATE runs SET cancellation_requested=1, updated_at=? WHERE id=?",
                    (utc_now(), run_id),
                )
        return self.get_run(run_id)

    def get_report(self, run_id: str) -> dict[str, Any] | None:
        run = self.get_run(run_id)
        return run.get("report") if run else None

    def events(self, run_id: str, after: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT id,run_id,type,message,created_at FROM events WHERE run_id=? AND id>? ORDER BY id LIMIT ?",
                (run_id, after, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def append_event(self, run_id: str, event_type: str, message: str) -> None:
        with self.connection() as connection:
            connection.execute(
                "INSERT INTO events(run_id,type,message,created_at) VALUES(?,?,?,?)",
                (run_id, event_type, message, utc_now()),
            )

    def create_artifact(self, run_id: str, format_name: str, content: bytes) -> dict[str, Any]:
        artifact_id = f"artifact_{secrets.token_hex(8)}"
        digest = hashlib.sha256(content).hexdigest()
        created_at = utc_now()
        with self.connection() as connection:
            connection.execute(
                "INSERT INTO artifacts(id,run_id,format,content,sha256,created_at) VALUES(?,?,?,?,?,?)",
                (artifact_id, run_id, format_name, content, digest, created_at),
            )
        return {"id": artifact_id, "run_id": run_id, "format": format_name, "sha256": digest, "created_at": created_at}

    def get_artifact(self, artifact_id: str) -> dict[str, Any] | None:
        with self.connection() as connection:
            row = connection.execute("SELECT * FROM artifacts WHERE id=?", (artifact_id,)).fetchone()
        return dict(row) if row else None

    def create_discovery_analysis(self, label: str, result: dict[str, Any]) -> dict[str, Any]:
        analysis_id = f"analysis_{secrets.token_hex(8)}"
        created_at = utc_now()
        with self.connection() as connection:
            connection.execute(
                "INSERT INTO discovery_analyses(id,label,spec_sha256,result_json,created_at) VALUES(?,?,?,?,?)",
                (
                    analysis_id,
                    label,
                    result["spec"]["sha256"],
                    json.dumps(result, separators=(",", ":")),
                    created_at,
                ),
            )
        return {"id": analysis_id, "label": label, "created_at": created_at, **result}

    def list_discovery_analyses(self, limit: int = 20) -> list[dict[str, Any]]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT id,label,spec_sha256,result_json,created_at FROM discovery_analyses ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                "id": row["id"],
                "label": row["label"],
                "created_at": row["created_at"],
                **json.loads(row["result_json"]),
            }
            for row in rows
        ]

    def get_discovery_analysis(self, analysis_id: str) -> dict[str, Any] | None:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT id,label,result_json,created_at FROM discovery_analyses WHERE id=?",
                (analysis_id,),
            ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "label": row["label"],
            "created_at": row["created_at"],
            **json.loads(row["result_json"]),
        }

    def create_candidate_review(
        self,
        analysis_id: str,
        candidate: dict[str, Any],
        decision: str,
        rationale: str,
        reviewer: str = "local-operator",
    ) -> dict[str, Any]:
        review_id = f"review_{secrets.token_hex(8)}"
        created_at = utc_now()
        candidate_json = json.dumps(candidate, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        candidate_sha256 = hashlib.sha256(candidate_json.encode("utf-8")).hexdigest()
        with self.connection() as connection:
            connection.execute(
                """INSERT INTO candidate_reviews(
                       id,analysis_id,candidate_id,decision,rationale,reviewer,
                       candidate_sha256,candidate_json,created_at
                   ) VALUES(?,?,?,?,?,?,?,?,?)""",
                (
                    review_id,
                    analysis_id,
                    str(candidate["id"]),
                    decision,
                    rationale,
                    reviewer,
                    candidate_sha256,
                    candidate_json,
                    created_at,
                ),
            )
        return {
            "id": review_id,
            "analysis_id": analysis_id,
            "candidate_id": str(candidate["id"]),
            "decision": decision,
            "rationale": rationale,
            "reviewer": reviewer,
            "candidate_sha256": candidate_sha256,
            "created_at": created_at,
            "candidate": candidate,
        }

    def list_candidate_reviews(self, analysis_id: str) -> list[dict[str, Any]]:
        with self.connection() as connection:
            rows = connection.execute(
                """SELECT id,analysis_id,candidate_id,decision,rationale,reviewer,
                          candidate_sha256,candidate_json,created_at
                   FROM candidate_reviews WHERE analysis_id=? ORDER BY rowid""",
                (analysis_id,),
            ).fetchall()
        return [
            {
                **{key: row[key] for key in (
                    "id", "analysis_id", "candidate_id", "decision", "rationale",
                    "reviewer", "candidate_sha256", "created_at",
                )},
                "candidate": json.loads(row["candidate_json"]),
            }
            for row in rows
        ]

    def save_explanation(self, run_id: str, result: dict[str, Any]) -> dict[str, Any]:
        explanation_id = f"explanation_{secrets.token_hex(8)}"
        created_at = utc_now()
        mode = str(result["mode"])
        model = result.get("model")
        model_key = model or ""
        with self.connection() as connection:
            connection.execute(
                """INSERT INTO explanations(id,run_id,mode,model,result_json,created_at) VALUES(?,?,?,?,?,?)
                   ON CONFLICT(run_id,mode,model) DO UPDATE SET
                     id=excluded.id,result_json=excluded.result_json,created_at=excluded.created_at""",
                (explanation_id, run_id, mode, model_key, json.dumps(result, separators=(",", ":")), created_at),
            )
        return {"id": explanation_id, "run_id": run_id, "created_at": created_at, **result}

    @staticmethod
    def _run_row(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        result["has_incomplete_cases"] = bool(result["has_incomplete_cases"])
        result["cancellation_requested"] = bool(result["cancellation_requested"])
        result["counts"] = json.loads(result.pop("counts_json")) if result.get("counts_json") else {
            "pass": 0, "violation": 0, "inconclusive": 0, "skipped": 0
        }
        result["report"] = json.loads(result.pop("report_json")) if result.get("report_json") else None
        return result
