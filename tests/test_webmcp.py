import json
from pathlib import Path

from api.webmcp import COMMON_TOOLS, THEME, manifest, tool
from fastapi.testclient import TestClient
from api.main import app


def test_manifest_has_ten_product_and_two_common_tools():
    payload = manifest()
    names = [item["name"] for item in payload["tools"]]
    assert payload["schema"] == "securedme.webmcp.v1"
    assert len(payload["tools"]) == 12
    assert len([name for name in names if name.startswith("fnp_")]) == 10
    assert set(COMMON_TOOLS).issubset(names)
    assert len(names) == len(set(names))
    assert all(entry["inputSchema"]["additionalProperties"] is False for entry in payload["tools"])
    assert all(entry["outputSchema"]["type"] == "object" for entry in payload["tools"])
    assert all(entry["handler"]["kind"] for entry in payload["tools"])


def test_static_exports_match_runtime_and_evidence_gate_shape():
    root = Path(__file__).parents[1]
    assert json.loads((root / "webmcp" / "manifest.json").read_text(encoding="utf-8")) == manifest()
    fixtures = json.loads((root / "webmcp" / "fixtures.json").read_text(encoding="utf-8"))
    assert set(fixtures) == {"tools", "journeys"}
    assert set(fixtures["tools"]) == {item["name"] for item in manifest()["tools"]}
    assert len(fixtures["journeys"]) == 6


def test_runtime_run_is_staged_and_non_clinical():
    assert tool("fnp_stage_runtime_run")["mode"] == "STAGE"
    assert "non-clinical" in manifest()["boundaries"]["authority"]


def test_theme_uses_product_specific_stitch_handoff():
    assert "stitch_fnp_qnn_research_simulator_design_system" in THEME["source"]


def test_discovery_is_public_and_invocation_fails_closed():
    client = TestClient(app)
    assert len(client.get("/webmcp/manifest").json()["tools"]) == 12
    rejected = client.post("/webmcp/invoke", json={"name": "fnp_inspect_health", "arguments": {}})
    assert rejected.status_code == 503
    assert rejected.json()["detail"]["error_code"] == "GATEWAY_SESSION_REQUIRED"
