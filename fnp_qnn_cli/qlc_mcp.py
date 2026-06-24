"""Metadata-only QLC MCP helpers for the FNP-QNN simulator surface."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence


WORKFLOW_SCHEMA = "ffed.qlc.protection_workflow_bundle.v1"
GATEWAY_SUBMISSION_SCHEMA = "ffed.qlc.gateway_submission.v1"
LOOP_RECEIPT_SCHEMA = "ffed.qlc.gateway_celebrum_loop_receipt.v1"

FORBIDDEN_QCL_MCP_FIELDS = {
    "api_key",
    "authorization",
    "browsing_history",
    "credential",
    "full_activity_dump",
    "image_bytes",
    "ocr_text",
    "password",
    "private_key",
    "raw_activity",
    "raw_browsing_history",
    "raw_image",
    "raw_ocr",
    "raw_payload",
    "raw_secret",
    "screenshot",
    "screenshots",
    "secret",
    "token",
    "video_bytes",
}


def qlc_workflow_build_plan(
    *,
    input_path: str,
    source_id: str,
    output_path: str,
    media_type: str = "image",
) -> dict[str, Any]:
    if not input_path.strip() or not source_id.strip() or not output_path.strip():
        raise ValueError("input_path, source_id, and output_path are required")
    return {
        "success": True,
        "tool": "qlc.workflow.build",
        "schema": WORKFLOW_SCHEMA,
        "command": [
            "ffed-qlc",
            "protect-workflow",
            "--input",
            input_path,
            "--source-id",
            source_id,
            "--output",
            output_path,
            "--media-type",
            media_type,
        ],
        "raw_payload_embedded": False,
        "claim_boundary": "mcp_build_plan_only_not_raw_media_processing",
    }


def qlc_status_inspect(bundle: Mapping[str, Any]) -> dict[str, Any]:
    submission = _extract_submission(bundle)
    mesh_payload = _mapping(submission.get("mesh_payload"))
    plugin_context = _mapping(mesh_payload.get("plugin_context"))
    swop = _mapping(plugin_context.get("sensitivity_weighted_obfuscation_policy"))
    raw_flags = {
        "bundle_raw_media_embedded": bool(bundle.get("raw_media_embedded", False)),
        "bundle_raw_payload_embedded": bool(bundle.get("raw_payload_embedded", False)),
        "submission_raw_payload_embedded": bool(submission.get("raw_payload_embedded", False)),
        "mesh_raw_payload_exposed": bool(mesh_payload.get("raw_payload_exposed", False)),
    }
    return {
        "success": not any(raw_flags.values()),
        "tool": "qlc.status.inspect",
        "bundle_schema": str(bundle.get("schema") or submission.get("schema") or "")[:120],
        "workflow_fingerprint": str(submission.get("workflow_fingerprint") or bundle.get("workflow_fingerprint") or "")[:64],
        "mesh_payload_fingerprint": str(submission.get("mesh_payload_fingerprint") or _fingerprint(mesh_payload))[:64],
        "route_action": str(submission.get("route_action") or "unknown")[:80],
        "media_type": str(bundle.get("media_type") or swop.get("media_type") or "unknown")[:40],
        "swop_level": str(swop.get("sensitivity_level") or "unknown")[:40],
        "target_endpoint": str(submission.get("target_endpoint") or "POST /cerebrum/runtime/run")[:120],
        "redaction_verdict": "metadata_only_pass" if not any(raw_flags.values()) else "review_required",
        "raw_flags": raw_flags,
        "raw_payload_embedded": False,
    }


def qlc_gateway_submit_plan(
    bundle: Mapping[str, Any],
    *,
    simulator_url: str = "http://localhost:8000",
    dry_run: bool = True,
) -> dict[str, Any]:
    status = qlc_status_inspect(bundle)
    return {
        "success": True,
        "tool": "qlc.gateway.submit",
        "dry_run": dry_run,
        "command": [
            "fnpqnn",
            "gateway",
            "qlc-submit",
            "--bundle",
            "<qlc_bundle.json>",
            "--simulator-url",
            simulator_url,
            *(["--dry-run"] if dry_run else []),
        ],
        "status": status,
        "raw_payload_embedded": False,
    }


def qlc_loop_receipt(bundle: Mapping[str, Any], simulator_result: Mapping[str, Any]) -> dict[str, Any]:
    _reject_forbidden_fields(simulator_result)
    submission = _extract_submission(bundle)
    status = str(simulator_result.get("status") or "unknown")[:80]
    route_action = str(submission.get("route_action") or "submit_to_cerebrum")
    if status not in {"ok", "accepted", "success", "not_run"}:
        route_action = "human_review"
    return {
        "success": True,
        "tool": "qlc.loop.receipt",
        "schema": LOOP_RECEIPT_SCHEMA,
        "workflow_fingerprint": str(submission.get("workflow_fingerprint") or "")[:64],
        "simulator_status": status,
        "route_action": route_action,
        "fingerprints": {
            "gateway_submission": _fingerprint(submission),
            "simulator_result": _fingerprint(_compact_simulator_result(simulator_result)),
        },
        "raw_payload_embedded": False,
    }


def _extract_submission(bundle: Mapping[str, Any]) -> Mapping[str, Any]:
    _reject_forbidden_fields(bundle)
    if bundle.get("schema") == WORKFLOW_SCHEMA:
        submission = _mapping(bundle.get("gateway_submission"))
    elif bundle.get("schema") == GATEWAY_SUBMISSION_SCHEMA:
        submission = bundle
    else:
        raise ValueError("QLC MCP tools require a protection workflow bundle or gateway submission")
    if submission.get("schema") != GATEWAY_SUBMISSION_SCHEMA:
        raise ValueError("QLC gateway submission schema is missing")
    if not isinstance(submission.get("mesh_payload"), Mapping):
        raise ValueError("QLC gateway submission requires mesh_payload")
    return submission


def _compact_simulator_result(simulator_result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": str(simulator_result.get("status") or "unknown")[:80],
        "runtime_fingerprint": _fingerprint(simulator_result.get("runtime") or {}),
        "persistence_fingerprint": _fingerprint(simulator_result.get("persistence") or {}),
    }


def _reject_forbidden_fields(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in FORBIDDEN_QCL_MCP_FIELDS and normalized != "secret_manager_ref":
                raise ValueError(f"raw QLC MCP field is not allowed: {key}")
            _reject_forbidden_fields(nested)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for item in value:
            _reject_forbidden_fields(item)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _fingerprint(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
