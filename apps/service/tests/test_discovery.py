from __future__ import annotations

import json

import pytest

from boundarylab.discovery import DiscoveryError, analyze_api_surface


def sample_spec() -> dict:
    return {
        "openapi": "3.1.0",
        "info": {"title": "Orders", "version": "1.2.0"},
        "security": [{"bearerAuth": []}],
        "paths": {
            "/v1/orders/{order_id}": {
                "get": {
                    "operationId": "getOrder",
                    "parameters": [{"in": "path", "name": "order_id", "required": True}],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string"},
                                            "owner_id": {"type": "string"},
                                            "secret_token": {"type": "string"},
                                        },
                                    }
                                }
                            }
                        }
                    },
                }
            },
            "/v1/orders": {"post": {"operationId": "createOrder", "responses": {"201": {}}}},
        },
    }


def sample_har() -> dict:
    return {
        "log": {
            "entries": [
                {
                    "request": {
                        "method": "GET",
                        "url": "https://api.example/v1/orders/123?expand=owner",
                        "headers": [{"name": "Authorization", "value": "Bearer must-never-persist"}],
                        "postData": {"text": "private body"},
                    }
                },
                {"request": {"method": "GET", "url": "https://api.example/v1/internal/debug-user/99881"}},
                {"request": {"method": "GET", "url": "https://api.example/v1/users/alice@example.com"}},
            ]
        }
    }


def test_infers_dual_identity_candidate_and_shadow_route_without_har_secrets():
    result = analyze_api_surface(sample_spec(), sample_har())
    assert result["summary"] == {
        "documented_paths": 2,
        "documented_operations": 2,
        "ownership_candidates": 1,
        "authenticated_operations": 2,
        "shadow_operations": 2,
        "har_entries": 3,
    }
    candidate = result["invariant_candidates"][0]
    assert candidate["operation_id"] == "getOrder"
    assert candidate["resource_parameter"] == "order_id"
    assert candidate["confidence"] == "high"
    assert result["traffic_diff"]["shadow_operations"][0] == {
        "method": "GET", "path": "/v1/internal/debug-user/{id}", "sample_count": 1, "risk": "high"
    }
    encoded = json.dumps(result)
    assert "must-never-persist" not in encoded
    assert "private body" not in encoded
    assert "alice@example.com" not in encoded
    assert result["safety"]["active_requests_sent"] is False


def test_refuses_duplicate_operation_ids():
    document = sample_spec()
    document["paths"]["/v1/orders"]["post"]["operationId"] = "getOrder"
    with pytest.raises(DiscoveryError, match="duplicate operationId"):
        analyze_api_surface(document)


def test_requires_openapi_three_and_bounded_har():
    with pytest.raises(DiscoveryError, match="OpenAPI 3"):
        analyze_api_surface({"swagger": "2.0", "paths": {"/x": {}}})
    har = {"log": {"entries": [{}] * 5_001}}
    with pytest.raises(DiscoveryError, match="HAR entry limit"):
        analyze_api_surface(sample_spec(), har)


def test_external_references_are_rejected_without_network_fetch():
    document = sample_spec()
    document["components"] = {"schemas": {"Order": {"$ref": "https://example.com/order.json"}}}
    with pytest.raises(DiscoveryError, match="external OpenAPI references"):
        analyze_api_surface(document)
