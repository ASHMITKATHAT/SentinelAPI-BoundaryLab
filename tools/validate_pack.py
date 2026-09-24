"""Validate static BoundaryLab handoff artifacts. This does not test a scanner."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def load(relative: str):
    path = ROOT / relative
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{relative}: invalid JSON: {exc}")
        return {}


def resolve_local_ref(document: dict, reference: str):
    if not reference.startswith("#/"):
        errors.append(f"unsupported non-local JSON reference: {reference}")
        return
    value = document
    try:
        for part in reference[2:].split("/"):
            value = value[part.replace("~1", "/").replace("~0", "~")]
    except (KeyError, TypeError):
        errors.append(f"unresolved JSON reference: {reference}")


control = load("contracts/control-api.openapi.json")
demo = load("contracts/demo-api.openapi.json")
schema = load("contracts/policy.schema.json")
policy = load("examples/invoice-policy.json")
evaluation = load("examples/evaluation-cases.json")
load("examples/fixture-manifest.json")
load("design/tokens.json")

for name, document in [("control", control), ("demo", demo)]:
    if document.get("openapi") != "3.1.0":
        errors.append(f"{name}: expected OpenAPI 3.1.0")
    operation_ids: list[str] = []
    for path_item in document.get("paths", {}).values():
        for operation in path_item.values():
            if isinstance(operation, dict) and "operationId" in operation:
                operation_ids.append(operation["operationId"])
    duplicates = [key for key, count in Counter(operation_ids).items() if count > 1]
    if duplicates:
        errors.append(f"{name}: duplicate operation IDs: {duplicates}")
    for match in re.finditer(r'"\$ref"\s*:\s*"([^"]+)"', json.dumps(document)):
        resolve_local_ref(document, match.group(1))

required_cases = [f"C{index:02}" for index in range(1, 13)]
if policy.get("required_cases") != required_cases:
    errors.append("policy: required_cases must be C01 through C12")
if schema.get("properties", {}).get("required_cases", {}).get("const") != required_cases:
    errors.append("policy schema: required case constant differs")

core = evaluation.get("core_cases", [])
failure = evaluation.get("failure_cases", [])
if len(core) != 12:
    errors.append(f"evaluation: expected 12 core cases, found {len(core)}")
if len(failure) != 18:
    errors.append(f"evaluation: expected 18 failure cases, found {len(failure)}")
for variant in ["vulnerable", "owner-only", "fixed"]:
    actual = Counter(case.get("expected", {}).get(variant) for case in core)
    expected = evaluation.get("expected_core_counts", {}).get(variant, {})
    for verdict in ["pass", "violation", "inconclusive"]:
        if actual[verdict] != expected.get(verdict):
            errors.append(f"evaluation: {variant} {verdict} count {actual[verdict]} != {expected.get(verdict)}")

link_pattern = re.compile(r"\[[^\]]*\]\((?!https?://|mailto:|#)([^)]+)\)")
markdown_files = [
    path for path in ROOT.rglob("*.md")
    if not ({".git", ".venv", "node_modules"} & set(path.relative_to(ROOT).parts))
]
for markdown in markdown_files:
    text = markdown.read_text(encoding="utf-8")
    for raw in link_pattern.findall(text):
        target = raw.strip().strip("<>").split("#", 1)[0]
        if target and not (markdown.parent / target).resolve().exists():
            errors.append(f"broken Markdown link: {markdown.relative_to(ROOT)} -> {raw}")

prototype = (ROOT / "design/boundarylab-prototype.html").read_text(encoding="utf-8")
label = "DESIGN PROTOTYPE · SYNTHETIC EVIDENCE · NO SCANNER CONNECTED"
if label not in prototype:
    errors.append("prototype: mandatory synthetic-design label missing")

review_path = control.get("paths", {}).get("/discovery/analyses/{analysis_id}/reviews", {})
if not {"get", "post"}.issubset(review_path):
    errors.append("control contract: candidate review ledger routes are missing")

dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
exposed_ports = re.findall(r"(?mi)^EXPOSE\s+(.+)$", dockerfile)
if exposed_ports != ["8080"]:
    errors.append(f"container: expected only EXPOSE 8080, found {exposed_ports}")
for required in ["USER boundarylab", "HEALTHCHECK", '"--host", "0.0.0.0"']:
    if required not in dockerfile:
        errors.append(f"container: missing Dockerfile control: {required}")
for required in [
    '"127.0.0.1:8080:8080"',
    "BOUNDARYLAB_BOOTSTRAP_SECRET:",
    "read_only: true",
    "no-new-privileges:true",
    "cap_drop:",
    "- ALL",
    "boundarylab-data:/data",
]:
    if required not in compose:
        errors.append(f"container: missing Compose control: {required}")
if re.search(r"(?m)^\s*-\s*['\"]?(?:9011|9012|9013):", compose):
    errors.append("container: synthetic fixture port must not be published")

if errors:
    print("PACK VALIDATION FAILED")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("PACK VALIDATION PASSED")
print("JSON artifacts: 7")
print("OpenAPI documents: 2")
print("Evaluation cases: 30 (12 core + 18 failure)")
print(f"Markdown files: {len(markdown_files)}")
print("Container profile: policy controls present (image build not performed)")
