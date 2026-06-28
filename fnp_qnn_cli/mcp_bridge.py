"""Provider-aware MCP bridge for external AI simulator control."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .auth import status as auth_status
from .external_ai import _run_capture, command_path, control_simulator
from .simulator_control import simulator_control_tasks

PROVIDER_TOOL_MAP = {
    "openai": "codex",
    "chatgpt": "codex",
    "chat-gpt": "codex",
    "google": "antigravity",
    "gemini": "antigravity",
    "google-ai": "antigravity",
}

PROVIDER_ALIASES = {
    "openai": {"openai", "chatgpt", "chat-gpt", "chatgpt-openai-token"},
    "google": {"google", "gemini", "google-ai", "google-ai-gemini-token"},
}


def normalize_provider(provider: str) -> str:
    normalized = provider.strip().lower()
    if normalized in PROVIDER_ALIASES["openai"]:
        return "openai"
    if normalized in PROVIDER_ALIASES["google"]:
        return "google"
    raise ValueError(f"unsupported provider: {provider}")


def tool_for_provider(provider: str) -> str:
    normalized = normalize_provider(provider)
    if normalized == "openai":
        return "codex"
    if normalized == "google":
        return "antigravity"
    raise ValueError(f"unsupported provider: {provider}")


def _google_adc_exists() -> bool:
    candidates = []
    appdata = os.environ.get("APPDATA")
    if appdata:
        candidates.append(Path(appdata) / "gcloud" / "application_default_credentials.json")
    candidates.append(Path.home() / ".config" / "gcloud" / "application_default_credentials.json")
    return any(path.exists() for path in candidates)


def provider_connection_status(provider: str) -> dict[str, Any]:
    normalized = normalize_provider(provider)
    selected_tool = tool_for_provider(normalized)
    auth = auth_status()
    auth_provider = str(auth.get("provider") or "").strip().lower()
    provider_aliases = PROVIDER_ALIASES[normalized]
    local_fingerprint = bool(auth.get("authenticated") and auth_provider in provider_aliases)
    ignore_runtime_auth = os.environ.get("FNP_QNN_MCP_IGNORE_RUNTIME_AUTH") == "1"
    runtime_signal: dict[str, Any] | None = None
    runtime_connected = False
    if not ignore_runtime_auth and normalized == "openai" and command_path("codex"):
        runtime_signal = _run_capture(("codex", "login", "status"), timeout=20)
        runtime_connected = bool(runtime_signal.get("returncode") == 0)
    if not ignore_runtime_auth and normalized == "google":
        runtime_connected = _google_adc_exists()
        runtime_signal = {"google_adc_exists": runtime_connected}
    return {
        "success": True,
        "provider": normalized,
        "tool": selected_tool,
        "tool_available": bool(command_path(selected_tool)),
        "connected": bool(local_fingerprint or runtime_connected),
        "local_fingerprint": local_fingerprint,
        "runtime_connected": runtime_connected,
        "runtime_auth_ignored": ignore_runtime_auth,
        "auth_provider": auth.get("provider"),
        "auth_storage": auth.get("storage"),
        "runtime_signal": runtime_signal,
        "raw_token_stored": False,
    }


def mcp_control_simulator(
    provider: str,
    task: str,
    execute: bool = False,
    timeout: int = 300,
    prompt: str | None = None,
) -> dict[str, Any]:
    connection = provider_connection_status(provider)
    if not connection["connected"]:
        return {
            "success": False,
            "provider": connection["provider"],
            "tool": connection["tool"],
            "task": task,
            "error": "provider is not connected; run provider web login and store a provider fingerprint first",
            "next_step": f"fnp-qnn auth web-login {connection['provider']} --open",
            "connection": connection,
        }
    payload = control_simulator(
        task,
        tool=connection["tool"],
        execute=execute,
        timeout=timeout,
        extra_prompt=prompt,
    )
    payload["provider"] = connection["provider"]
    payload["connection"] = connection
    return payload


def mcp_manifest() -> dict[str, Any]:
    return {
        "success": True,
        "name": "fnp-qnn-ai-control-mcp",
        "tools": [
            {
                "name": "fnp_qnn_provider_status",
                "description": "Check whether OpenAI/ChatGPT or Google/Gemini is connected for school-mode simulator control.",
            },
            {
                "name": "fnp_qnn_control_simulator",
                "description": "Control an allowlisted FNP-QNN simulator task through Codex or Antigravity.",
            },
            {
                "name": "fnp_qnn_control_tasks",
                "description": "List allowlisted simulator control tasks.",
            },
            {
                "name": "fnp_qnn_onboarding_questions",
                "description": "List the directed onboarding questions used to shape simulator context.",
            },
            {
                "name": "fnp_qnn_onboard_user",
                "description": "Apply provider-approved onboarding answers into AGENTS.md, SOUL.md, USER.md, MEMORY.md, and config/user_wiring.json.",
            },
            {
                "name": "fnp_qnn_agent_profile",
                "description": "Return the native-system profile for Codex or Antigravity/Gemini.",
            },
            {
                "name": "fnp_qnn_wake_prompt",
                "description": "Return the provider-specific wake prompt that explains FNP-QNN and the active interface.",
            },
            {
                "name": "qlc.workflow.build",
                "description": "Return a metadata-only command plan for building a QLC protection workflow bundle.",
            },
            {
                "name": "qlc.gateway.submit",
                "description": "Validate a QLC gateway submission and return the simulator submit plan.",
            },
            {
                "name": "qlc.loop.receipt",
                "description": "Build a compact QLC gateway-to-CeLeBrUm loop receipt from a simulator result.",
            },
            {
                "name": "qlc.status.inspect",
                "description": "Inspect a QLC workflow bundle or gateway submission without exposing raw payloads.",
            },
        ],
        "control_tasks": simulator_control_tasks(),
    }
