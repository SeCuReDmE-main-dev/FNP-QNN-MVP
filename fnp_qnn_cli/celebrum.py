"""CeLeBrUm/Cerebrum CLI adapters for AI logic testing."""

from __future__ import annotations

from typing import Any

from .auth import validate_token
from .registry import HIERARCHY_BOUNDARY, RESEARCH_BOUNDARY, runtime_run

SECRET_MARKERS = ("token", "secret", "key", "password", "authorization", "bearer")


def sanitize_payload(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized = {}
        for key, item in value.items():
            key_text = str(key)
            if any(marker in key_text.lower() for marker in SECRET_MARKERS):
                sanitized[key_text] = "[redacted]"
            else:
                sanitized[key_text] = sanitize_payload(item)
        return sanitized
    if isinstance(value, list):
        return [sanitize_payload(item) for item in value]
    return value


def cerebrum_runtime_function(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return runtime_run(payload or {"epochs": 2})


def celebrum_clip_function(
    payload: dict[str, Any] | None = None,
    *,
    token: str | None = None,
    require_auth: bool = False,
) -> dict[str, Any]:
    if require_auth:
        auth_result = validate_token(token)
        if not auth_result["success"]:
            return {
                "success": False,
                "type": "celebrum-ai-cli",
                "error": auth_result["reason"],
                "research_boundary": RESEARCH_BOUNDARY,
            }

    safe_payload = sanitize_payload(payload or {})
    return {
        "success": True,
        "type": "celebrum-ai-cli",
        "function_name": "celebrum_clip_function",
        "python_callable": "fnp_qnn_cli.celebrum:celebrum_clip_function",
        "research_boundary": RESEARCH_BOUNDARY,
        "hierarchy_boundary": HIERARCHY_BOUNDARY,
        "auth": "required" if require_auth else "optional",
        "sanitized_payload": safe_payload,
        "ai_logic_contract": {
            "input": "dict payload with optional memories/events/observations and statefield",
            "output": "sanitized local diagnostic contract; no raw secrets",
            "allowed_execution": "local simulator functions only; no arbitrary shell",
        },
    }
