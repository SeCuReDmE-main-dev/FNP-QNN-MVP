"""Support reports for provider-aware CLI onboarding."""

from __future__ import annotations

from typing import Any

from .agent_profiles import agent_profile, wake_prompt
from .mcp_bridge import provider_connection_status
from .simulator_control import simulator_control_tasks

PROVIDERS = ("openai", "google")


def provider_support_report(provider: str) -> dict[str, Any]:
    profile = agent_profile(provider)
    connection = provider_connection_status(provider)
    issues: list[str] = []
    next_steps: list[str] = []

    if not connection["tool_available"]:
        issues.append(f"{connection['tool']} CLI is not available on PATH")
        if connection["tool"] == "codex":
            next_steps.append("Install or expose Codex CLI, then rerun `fnp-qnn external-ai status`.")
        elif connection["tool"] == "antigravity":
            next_steps.append("Install or expose Antigravity CLI, then rerun provider status.")

    if not connection["connected"]:
        issues.append("provider is not connected")
        next_steps.append(f"Run `fnp-qnn auth web-login {connection['provider']} --open`.")
        next_steps.append(f"Then run `fnp-qnn auth login-provider {connection['provider']} --token <token>`.")


    if connection["provider"] == "google" and not connection["runtime_connected"]:
        next_steps.append("For OAuth style auth, run `fnp-qnn auth web-login google --run-gcloud`.")

    if connection["provider"] == "openai" and not connection["runtime_connected"]:
        next_steps.append("For Codex web auth, run `fnp-qnn external-ai connect codex --device-auth`.")

    if not issues:
        next_steps.append(f"Run `fnp-qnn onboarding apply {connection['provider']} --approve-fingerprint`.")
        next_steps.append(f"Preview the wake prompt with `fnp-qnn agent wake-prompt {connection['provider']}`.")

    return {
        "success": True,
        "provider": connection["provider"],
        "system": profile["system"],
        "tool": connection["tool"],
        "connected": connection["connected"],
        "tool_available": connection["tool_available"],
        "issues": issues,
        "next_steps": next_steps,
        "support_summary": "ready" if not issues else "needs-action",
        "native_assets_policy": profile["native_assets"],
        "wake_prompt_preview": wake_prompt(connection["provider"]).splitlines()[:12],
        "control_tasks": [item["name"] for item in simulator_control_tasks()],
        "raw_token_stored": False,
    }


def all_provider_support_reports() -> dict[str, Any]:
    reports = [provider_support_report(provider) for provider in PROVIDERS]
    return {
        "success": True,
        "reports": reports,
        "ready_providers": [item["provider"] for item in reports if item["support_summary"] == "ready"],
        "needs_action": [item["provider"] for item in reports if item["support_summary"] != "ready"],
    }
