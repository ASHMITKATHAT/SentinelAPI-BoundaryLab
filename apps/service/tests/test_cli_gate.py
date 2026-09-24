from __future__ import annotations

import pytest

from boundarylab.cli import gate_exit_code, validate_local_target


def test_gate_exit_semantics_are_configurable():
    report = {
        "counts": {"violation": 1, "inconclusive": 0},
        "has_incomplete_cases": False,
        "execution_error": None,
    }
    assert gate_exit_code(report, {"violation"}) == 1
    assert gate_exit_code(report, {"inconclusive"}) == 0


def test_ci_gate_rejects_non_loopback_and_url_paths():
    assert validate_local_target("http://127.0.0.1:9013") == "http://127.0.0.1:9013"
    with pytest.raises(ValueError, match="loopback"):
        validate_local_target("http://192.0.2.10:8080")
    with pytest.raises(ValueError, match="without path"):
        validate_local_target("http://127.0.0.1:9013/admin")
