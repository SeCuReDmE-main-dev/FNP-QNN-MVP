from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence


QLC_RUNTIME_CONTEXT_SCHEMA = "ffed.qlc.runtime_normalized_context.v1"
QLC_WIRING_CONTRACT_VERSION = "qlc-wiring-contract.v2"

FORBIDDEN_QCL_RUNTIME_FIELDS = {
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


def normalize_qlc_runtime_payload(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    """Attach a compact QLC runtime summary to a Cerebrum payload."""

    runtime_payload = dict(payload or {})
    reject_forbidden_qlc_fields(runtime_payload)
    plugin_context = _mapping(runtime_payload.get("plugin_context"))
    cpai_context = _mapping(runtime_payload.get("cpai_context"))
    swop = _mapping(plugin_context.get("sensitivity_weighted_obfuscation_policy"))
    detected = bool(swop or str(plugin_context.get("orchestrator") or "").lower() == "celebrum")
    summary = {
        "schema": QLC_RUNTIME_CONTEXT_SCHEMA,
        "contract_version": str(runtime_payload.get("contract_version") or plugin_context.get("contract_version") or QLC_WIRING_CONTRACT_VERSION)[:80]
        if detected
        else "unknown",
        "detected": detected,
        "orchestrator": str(plugin_context.get("orchestrator") or "CeLeBrUm")[:80] if detected else "unknown",
        "runtime_memory_surface": str(plugin_context.get("runtime_memory_surface") or "Cerebrum")[:80] if detected else "unknown",
        "media_type": str(swop.get("media_type") or "unknown")[:40],
        "swop_level": str(swop.get("sensitivity_level") or "unknown")[:40],
        "recommended_chunk_mode": str(swop.get("recommended_chunk_mode") or "unknown")[:80],
        "mesh_enabled": bool(cpai_context.get("mesh_enabled", False)),
        "mesh_payload_fingerprint": _fingerprint(_compact_runtime_payload(runtime_payload)),
        "lvfm_metadata": {
            "bridge": "qlc-gateway-to-cerebrum-runtime" if detected else "standard-runtime",
            "metadata_only": True,
            "raw_payload_embedded": False,
        },
        "raw_payload_embedded": False,
    }
    if detected:
        normalized_plugin_context = dict(plugin_context)
        normalized_plugin_context["qlc_runtime_normalized_context"] = summary
        runtime_payload["plugin_context"] = normalized_plugin_context
    runtime_payload["qlc_runtime_normalized_context"] = summary
    return runtime_payload


def qlc_runtime_summary(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    normalized = normalize_qlc_runtime_payload(payload)
    return dict(_mapping(normalized.get("qlc_runtime_normalized_context")))


def reject_forbidden_qlc_fields(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in FORBIDDEN_QCL_RUNTIME_FIELDS and normalized != "secret_manager_ref":
                raise ValueError(f"raw QLC runtime field is not allowed: {key}")
            reject_forbidden_qlc_fields(nested)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for item in value:
            reject_forbidden_qlc_fields(item)


def _compact_runtime_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "memories_count": len(payload.get("memories") or []),
        "events_count": len(payload.get("events") or []),
        "observations_count": len(payload.get("observations") or []),
        "plugin_context": _mapping(payload.get("plugin_context")),
        "cpai_context": _mapping(payload.get("cpai_context")),
    }


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _fingerprint(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
