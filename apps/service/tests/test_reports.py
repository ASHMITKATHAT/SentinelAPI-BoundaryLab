from __future__ import annotations

import json

from boundarylab.reports import html_report, json_report


def sample_report() -> dict:
    return {
        "target_alias": "<script>alert(1)</script>",
        "build_id": "invoice-fixed",
        "policy_version": "invoice-policy-v1",
        "assessment": "pass_in_scope",
        "has_incomplete_cases": False,
        "counts": {"pass": 1, "violation": 0, "inconclusive": 0, "skipped": 0},
        "request_count": 2,
        "cleanup_status": "complete",
        "execution_error": None,
        "cases": [{
            "case_id": "C01",
            "name": "Owner <b>reads</b>",
            "verdict": "pass",
            "expected": "200",
            "observed": "<img src=x onerror=alert(1)>",
        }],
        "evidence": [],
    }


def test_html_report_escapes_target_derived_content():
    output = html_report(sample_report()).decode("utf-8")
    assert "<script>alert(1)</script>" not in output
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in output
    assert "<img src=x onerror=alert(1)>" not in output
    assert "&lt;img src=x onerror=alert(1)&gt;" in output


def test_json_report_is_valid_utf8_with_trailing_newline():
    output = json_report(sample_report())
    assert output.endswith(b"\n")
    assert json.loads(output)["assessment"] == "pass_in_scope"
