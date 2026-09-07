"""SecuredMe WebMCP v1 descriptors for the FNP-QNN research simulator."""

from __future__ import annotations

from typing import Any

SCHEMA = "securedme.webmcp.v1"
PRODUCT_SLUG = "fnp-qnn"
COMMON_TOOLS = ("securedme_companion_context", "securedme_qbit_plan_handoff")
THEME = {
    "slug": PRODUCT_SLUG,
    "source": "securedme-site/assets/landing/secureme.ca-product/education/FNP-QNN-MVP/desing/stitch_fnp_qnn_research_simulator_design_system/stitch_fnp_qnn_research_simulator_design_system/desing.md",
    "sourceStatus": "verified-product-stitch",
    "assets": {"dark": "landing dark.png", "light": "landing light.png", "logo": "FNP-QNN logo.png"},
    "tokens": {"background": "#061026", "surface": "#101b35", "primary": "#23b8ff", "secondary": "#6f42ff", "accent": "#d8a548", "text": "#f7fbff", "muted": "#8fa0bd", "focus": "#23d5ff"},
    "typography": {"display": "system-ui, sans-serif", "body": "system-ui, sans-serif", "code": "monospace"},
    "fallback": "High-contrast system fonts, visible focus, and text-first simulator states.",
}


def _object(properties: dict[str, Any] | None = None, required: list[str] | None = None) -> dict[str, Any]:
    return {"type": "object", "properties": properties or {}, "required": required or [], "additionalProperties": False}


def _tool(name: str, mode: str, description: str, schema: dict[str, Any], handler: str) -> dict[str, Any]:
    parts = handler.split(" ", 1)
    mapped = {"kind": "http", "method": parts[0], "path": parts[1]} if len(parts) == 2 and parts[0] in {"GET", "POST", "PUT", "DELETE"} else {"kind": "local", "operation": handler.replace(" ", "_")}
    return {"name": name, "title": name.replace("_", " ").title(), "description": description, "mode": mode, "availability": "available", "inputSchema": schema, "outputSchema": {"type": "object", "required": ["status", "tool", "data", "secret_values_exposed"], "properties": {"status": {"const": "success"}, "tool": {"const": name}, "data": {}, "secret_values_exposed": {"const": False}}, "additionalProperties": False}, "handler": mapped}


OBSERVATION = {"type": "object", "properties": {"modality": {"type": "string", "maxLength": 32}, "value": {}, "timestamp": {"type": "number"}, "starting_time": {"type": "number"}, "ending_time": {"type": "number"}, "end_time": {"type": "number"}, "label": {"type": "string", "maxLength": 200}, "source": {"type": "string", "maxLength": 200}, "weight": {"type": "number"}, "payload_ref": {"type": "string", "maxLength": 200}}, "additionalProperties": False}
RUNTIME = {"memories": {"type": "array", "maxItems": 128, "items": OBSERVATION}, "run_qnn": {"type": "boolean"}}
TOOLS = (
    _tool("fnp_inspect_health", "READ", "Inspect the sanitized local non-clinical simulator health.", _object(), "GET /health"),
    _tool("fnp_inspect_cerebrum_status", "READ", "Inspect the deterministic demo observation bundle.", _object(), "GET /cerebrum/status"),
    _tool("fnp_encode_observations", "STAGE", "Encode bounded observation feature vectors.", _object({"observations": {"type": "array", "maxItems": 128, "items": OBSERVATION}}), "POST /cerebrum/encode"),
    _tool("fnp_inspect_runtime_status", "READ", "Inspect the local Cerebrum runtime and candidate backend status.", _object(), "GET /cerebrum/runtime/status"),
    _tool("fnp_stage_runtime_ingest", "STAGE", "Stage bounded runtime events and crossmodal pairs.", _object(RUNTIME), "POST /cerebrum/runtime/ingest"),
    _tool("fnp_stage_runtime_pairs", "STAGE", "Stage the runtime crossmodal pair projection.", _object(RUNTIME), "POST /cerebrum/runtime/pairs"),
    _tool("fnp_stage_runtime_run", "STAGE", "Run a local deterministic research simulation candidate; never a clinical inference.", _object(RUNTIME), "POST /cerebrum/runtime/run"),
    _tool("fnp_inspect_latest_runtime_state", "READ", "Inspect the latest sanitized local runtime state receipt.", _object(), "GET /cerebrum/runtime/state/latest"),
    _tool("fnp_list_qnn_candidates", "READ", "List available and unavailable QNN candidate lanes honestly.", _object(), "GET /qnn/candidates"),
    _tool("fnp_preview_neurobit_gates", "STAGE", "Preview deterministic NeuroBit gate behavior as educational simulation.", _object({"truth": {"type": "number", "minimum": 0, "maximum": 1}, "indeterminacy": {"type": "number", "minimum": 0, "maximum": 1}, "falsity": {"type": "number", "minimum": 0, "maximum": 1}, "n_qubits": {"type": "integer", "minimum": 1, "maximum": 12}}), "POST /fnp-qnn/neurobit/gates/run"),
    _tool("securedme_companion_context", "READ", "Read a sanitized Hero Book projection while AlgoQuest retains authority.", _object(), "Gateway session projection"),
    _tool("securedme_qbit_plan_handoff", "STAGE", "Prepare a Qbit return proposal without changing progression.", _object({"mission_ref": {"type": "string", "minLength": 1, "maxLength": 120}, "artifact_refs": {"type": "array", "maxItems": 20, "items": {"type": "string", "maxLength": 160}}}, ["mission_ref"]), "local proposal only"),
)


def manifest() -> dict[str, Any]:
    return {"schema": SCHEMA, "manifestVersion": "1.0.0", "product": {"slug": PRODUCT_SLUG, "name": "FNP-QNN MVP", "status": "public-pre-alpha", "canonicalStateOwner": "algoquest", "applicationStateOwner": "fnp-qnn", "pagePatterns": ["https://fnpqnn.securedme.ca/", "http://localhost:8000/dashboard"], "theme": THEME}, "boundaries": {"authority": "Local non-clinical educational research simulation only.", "secrets": "Provider secrets, private CeLeBrUm corpus and raw learner records are forbidden.", "externalWrites": "No shell, E2B, provisioning or browser automation is exposed; simulations remain staged local evidence.", "heroProgression": "AlgoQuest alone owns Hero Book progression and evidence admission."}, "tools": list(TOOLS)}


def tool(name: str) -> dict[str, Any] | None:
    return next((item for item in TOOLS if item["name"] == name), None)
