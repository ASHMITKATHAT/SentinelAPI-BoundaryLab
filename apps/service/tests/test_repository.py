from __future__ import annotations

from boundarylab.repository import Repository


def test_run_survives_restart_and_active_work_becomes_interrupted(tmp_path):
    database = tmp_path / "boundarylab.db"
    first = Repository(database)
    created = first.create_run("demo-fixed", "http://127.0.0.1:9013")
    claimed = first.claim_next_run()
    assert claimed["id"] == created["id"]
    assert claimed["state"] == "running"

    restarted = Repository(database)
    recovered = restarted.get_run(created["id"])
    assert recovered["state"] == "interrupted"
    assert recovered["has_incomplete_cases"] is True
    assert "stopped before completion" in recovered["execution_error"]


def test_session_is_stored_as_hash_and_can_be_revoked(tmp_path):
    repository = Repository(tmp_path / "boundarylab.db")
    token, csrf = repository.create_session()
    assert repository.get_session(token)["csrf_token"] == csrf

    with repository.connection() as connection:
        row = connection.execute("SELECT token_hash FROM sessions").fetchone()
        assert row["token_hash"] != token

    repository.delete_session(token)
    assert repository.get_session(token) is None


def test_queued_cancellation_is_terminal_and_evented(tmp_path):
    repository = Repository(tmp_path / "boundarylab.db")
    run = repository.create_run("demo-fixed", "http://127.0.0.1:9013")
    cancelled = repository.request_cancel(run["id"])
    assert cancelled["state"] == "cancelled"
    assert cancelled["has_incomplete_cases"] is True
    assert repository.claim_next_run() is None
    assert [event["type"] for event in repository.events(run["id"])] == ["queued", "cancelled"]


def test_discovery_and_explanation_records_survive_repository_restart(tmp_path):
    database = tmp_path / "boundarylab.db"
    repository = Repository(database)
    analysis = repository.create_discovery_analysis("orders", {
        "spec": {"sha256": "a" * 64}, "summary": {"documented_operations": 1}
    })
    run = repository.create_run("demo-fixed", "http://127.0.0.1:9013")
    explanation = repository.save_explanation(run["id"], {
        "mode": "deterministic", "model": None, "summary": "reviewed"
    })

    restarted = Repository(database)
    assert restarted.list_discovery_analyses()[0]["id"] == analysis["id"]
    with restarted.connection() as connection:
        row = connection.execute("SELECT result_json FROM explanations WHERE id=?", (explanation["id"],)).fetchone()
    assert "reviewed" in row["result_json"]


def test_candidate_review_is_append_only_and_preserves_candidate_snapshot(tmp_path):
    database = tmp_path / "boundarylab.db"
    repository = Repository(database)
    candidate = {
        "id": "ownership-123",
        "operation_id": "getOrder",
        "method": "GET",
        "path": "/orders/{order_id}",
    }
    analysis = repository.create_discovery_analysis("orders", {
        "spec": {"sha256": "a" * 64},
        "summary": {"documented_operations": 1},
        "invariant_candidates": [candidate],
    })
    first = repository.create_candidate_review(
        analysis["id"], candidate, "approved", "Owner scoping is required for this resource."
    )
    second = repository.create_candidate_review(
        analysis["id"], candidate, "rejected", "Replaced after confirming this endpoint is public."
    )

    restarted = Repository(database)
    reviews = restarted.list_candidate_reviews(analysis["id"])
    assert [review["id"] for review in reviews] == [first["id"], second["id"]]
    assert reviews[0]["candidate"] == candidate
    assert reviews[0]["candidate_sha256"] == reviews[1]["candidate_sha256"]
    assert len(reviews[0]["candidate_sha256"]) == 64
