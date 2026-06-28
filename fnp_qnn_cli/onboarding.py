"""User onboarding that shapes simulator context without requiring AI logic."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .agent_profiles import agent_profile, wake_prompt
from .mcp_bridge import mcp_control_simulator, provider_connection_status
from .operator import PROJECT_ROOT

QUESTION_SET = [
    {
        "id": "primary_goal",
        "question": "What should this simulator help you do first?",
        "default": "Run local non-clinical FNP-QNN research simulations safely.",
    },
    {
        "id": "audience",
        "question": "Who is the simulator for?",
        "default": "Maintainer/operator using a local research simulator.",
    },
    {
        "id": "preferred_workflow",
        "question": "How should the simulator workflow feel?",
        "default": "Clear CLI/TUI first, deterministic local commands, optional AI handoff only after approval.",
    },
    {
        "id": "data_boundary",
        "question": "What data boundary must the simulator enforce?",
        "default": "No clinical, diagnostic, therapeutic, emergency, or production-public claims.",
    },
    {
        "id": "agent_role",
        "question": "What should the selected AI agent do after onboarding?",
        "default": "Review generated context and propose or implement narrow wiring changes only with explicit approval.",
    },
    {
        "id": "ui_preference",
        "question": "What CLI/TUI style should be prioritized?",
        "default": "OpenClaw-like clarity with Codex/Gemini-like command affordances.",
    },
    {
        "id": "success_signal",
        "question": "How should success be measured?",
        "default": "Tests pass, alpha readiness passes, and simulator commands remain usable without AI providers.",
    },
]

MANAGED_START = "<!-- FNP-QNN-ONBOARDING-START -->"
MANAGED_END = "<!-- FNP-QNN-ONBOARDING-END -->"


def onboarding_questions() -> dict[str, Any]:
    return {"success": True, "questions": QUESTION_SET}


def _load_answers(path: str | None, overrides: dict[str, Any] | None = None) -> dict[str, str]:
    payload: dict[str, Any] = {}
    if path:
        with Path(path).open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, dict):
            raise ValueError("answers file must contain a JSON object")
    if overrides:
        payload.update({key: value for key, value in overrides.items() if value is not None})
    answers = {}
    for item in QUESTION_SET:
        value = payload.get(item["id"], item["default"])
        answers[item["id"]] = str(value).strip() or item["default"]
    return answers


def _managed_block(provider: str, answers: dict[str, str]) -> str:
    profile = agent_profile(provider)
    lines = [
        MANAGED_START,
        "## FNP-QNN User Onboarding Context",
        "",
        f"Updated: {datetime.now(timezone.utc).isoformat()}",
        f"Approved provider: {provider}",
        f"Selected system: {profile['system']}",
        f"Native interface: {profile['interface']}",
        "",
        "Rules from onboarding:",
    ]
    for item in QUESTION_SET:
        lines.append(f"- {item['id']}: {answers[item['id']]}")
    lines.extend(
        [
            "",
            "Agent boundary:",
            "- Simulator base functions must run without Codex or Antigravity/Gemini.",
            "- External AI providers may only operate as optional wiring/onboarding adapters after approval.",
            "- Native plugins/skills remain in the user's original tool; FNP-QNN only passes context and MCP calls.",
            f"- Wake prompt path: config/agent_wake_prompt_{provider}.md",
            "- Preserve I -> I_system^S -> D_f -> dF -> i_fractal.",
            MANAGED_END,
            "",
        ]
    )
    return "\n".join(lines)


def _upsert_managed_block(path: Path, block: str, heading: str | None = None) -> None:
    if path.exists():
        text = path.read_text(encoding="utf-8")
    else:
        text = f"# {heading or path.stem}\n\n"
    if MANAGED_START in text and MANAGED_END in text:
        before = text.split(MANAGED_START, 1)[0].rstrip()
        after = text.split(MANAGED_END, 1)[1].lstrip()
        text = f"{before}\n\n{block}\n{after}"
    else:
        text = f"{text.rstrip()}\n\n{block}"
    path.write_text(text, encoding="utf-8")


def apply_onboarding(
    provider: str,
    answers_path: str | None = None,
    approve_fingerprint: bool = False,
    overrides: dict[str, Any] | None = None,
    delegate: bool = False,
    execute_delegate: bool = False,
    project_root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    connection = provider_connection_status(provider)
    if not approve_fingerprint:
        return {
            "success": False,
            "error": "fingerprint approval is required",
            "next_step": "rerun with --approve-fingerprint after confirming the provider identity",
            "connection": connection,
        }
    if not connection["connected"]:
        return {
            "success": False,
            "error": "provider is not connected",
            "next_step": f"fnp-qnn auth web-login {connection['provider']} --open",
            "connection": connection,
        }
    answers = _load_answers(answers_path, overrides)
    config_dir = project_root / "config"
    config_dir.mkdir(exist_ok=True)
    payload = {
        "version": 1,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "provider": connection["provider"],
        "tool": connection["tool"],
        "answers": answers,
        "base_simulator_ai_dependency": False,
        "optional_ai_adapter": True,
    }
    wiring_path = config_dir / "user_wiring.json"
    prompt_path = config_dir / f"agent_wake_prompt_{connection['provider']}.md"
    wiring_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    prompt_path.write_text(wake_prompt(connection["provider"], answers), encoding="utf-8")

    block = _managed_block(connection["provider"], answers)
    _upsert_managed_block(project_root / "AGENTS.md", block)
    _upsert_managed_block(project_root / "SOUL.md", block, heading="SOUL.md")
    _upsert_managed_block(project_root / "USER.md", block, heading="USER.md")
    _upsert_managed_block(project_root / "MEMORY.md", block, heading="MEMORY.md")

    delegate_payload = None
    if delegate:
        prompt = (
            "Review config/user_wiring.json and the managed onboarding blocks in AGENTS.md, SOUL.md, USER.md, "
            "MEMORY.md, and the provider wake prompt under config/. Keep simulator base functions AI-independent. "
            "Use native skills/plugins from your original system when available. Propose or implement only narrow "
            "wiring changes that match the user's onboarding answers."
        )
        delegate_payload = mcp_control_simulator(
            connection["provider"],
            "validate",
            execute=execute_delegate,
            prompt=prompt,
        )
    return {
        "success": True,
        "provider": connection["provider"],
        "tool": connection["tool"],
        "connection": connection,
        "wiring_path": str(wiring_path),
        "wake_prompt_path": str(prompt_path),
        "wake_prompt": wake_prompt(connection["provider"], answers),
        "updated_files": [
            str(project_root / "AGENTS.md"),
            str(project_root / "SOUL.md"),
            str(project_root / "USER.md"),
            str(project_root / "MEMORY.md"),
            str(prompt_path),
        ],
        "answers": answers,
        "delegate": delegate_payload,
    }
