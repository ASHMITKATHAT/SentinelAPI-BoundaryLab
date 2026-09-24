from __future__ import annotations

import json

import httpx
import pytest

from boundarylab.remediation import OpenAITriageClient, deterministic_triage


def failed_report() -> dict:
    return {
        "target_alias": "demo-vulnerable",
        "build_id": "invoice-vulnerable",
        "policy_version": "invoice-policy-v1",
        "assessment": "blocked",
        "counts": {"pass": 10, "violation": 2, "inconclusive": 0, "skipped": 0},
        "cases": [
            {
                "case_id": "C02", "name": "Bob denied", "verdict": "violation",
                "expected": "403 without marker", "observed": "200 disclosed marker",
                "reason_code": "PROTECTED_CONTENT_EXPOSED", "finding_kind": "security_violation",
            },
            {
                "case_id": "C06", "name": "Owner field hidden", "verdict": "violation",
                "expected": "field absent", "observed": "field returned",
                "reason_code": "OWNER_FIELD_EXPOSED", "finding_kind": "security_violation",
            },
        ],
        "evidence": [{"request_headers": {"authorization": "[REDACTED]"}, "response_excerpt": "sensitive"}],
    }


def test_deterministic_triage_is_specific_and_scope_honest():
    result = deterministic_triage(failed_report())
    assert result["mode"] == "deterministic"
    assert result["risk"] == "high"
    assert {item["category"] for item in result["root_causes"]} == {
        "object_authorization", "property_authorization"
    }
    assert "line-level diff" in result["limitations"][0]
    assert "active_share" in result["patch_outline"]


@pytest.mark.asyncio
async def test_openai_triage_uses_structured_output_and_minimized_context():
    captured: dict = {}
    narrative = {
        "summary": "Two authorization defects.",
        "risk": "high",
        "root_causes": [{
            "case_id": "C02", "category": "object_authorization", "explanation": "Owner scope missing.",
            "recommended_guard": "Bind lookup to tenant and relation.",
        }],
        "remediation_steps": ["Add scoped lookup."],
        "regression_checks": ["Retest owner and collaborator."],
        "patch_outline": "repository.find(id, tenant_id=user.tenant_id)",
        "limitations": ["No source tree supplied."],
    }

    async def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content))
        return httpx.Response(200, json={
            "output": [{"type": "message", "content": [{"type": "output_text", "text": json.dumps(narrative)}]}]
        })

    result = await OpenAITriageClient(
        "test-key-never-real", "test-model", transport=httpx.MockTransport(handler)
    ).generate(failed_report())
    assert result["mode"] == "openai_structured"
    assert captured["store"] is False
    assert captured["max_output_tokens"] == 1200
    assert captured["text"]["format"]["type"] == "json_schema"
    prompt = json.dumps(captured["input"])
    assert "request_headers" not in prompt
    assert "sensitive" not in prompt
    assert "PROTECTED_CONTENT_EXPOSED" in prompt


@pytest.mark.asyncio
async def test_openai_triage_rejects_missing_output_text():
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"output": []})

    with pytest.raises(RuntimeError, match="structured output"):
        await OpenAITriageClient("test-key-never-real", "test-model", transport=httpx.MockTransport(handler)).generate(failed_report())
