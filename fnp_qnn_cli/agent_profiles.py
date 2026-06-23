"""Wake prompts that place each external agent in its native system."""

from __future__ import annotations

from typing import Any

from .mcp_bridge import normalize_provider, tool_for_provider

SYSTEM_PROFILES: dict[str, dict[str, str]] = {
    "openai": {
        "system": "Codex",
        "interface": "Codex CLI / Codex app with native Codex skills, plugins, MCP servers, and repo tools.",
        "native_assets": "Use the Codex skills/plugins/MCP servers already installed or enabled by the user in Codex.",
        "boundary": "Do not assume Antigravity or Ollama tools exist unless the user explicitly routes through them.",
    },
    "google": {
        "system": "Antigravity / Gemini",
        "interface": "Google Antigravity or Gemini-oriented CLI surface with its native project and agent tools.",
        "native_assets": "Use the Antigravity/Gemini skills, tools, and project integrations already enabled by the user there.",
        "boundary": "Do not assume Codex plugins or Ollama cloud models exist unless the user explicitly routes through them.",
    },
    "ollama": {
        "system": "Ollama Cloud / OpenClaw",
        "interface": "Ollama CLI/cloud model surface, optionally mediated by OpenClaw when configured by the user.",
        "native_assets": "Use the Ollama/OpenClaw models, plugins, MCP servers, and agent runtimes already enabled by the user.",
        "boundary": "Do not assume Codex or Antigravity capabilities exist unless the user explicitly routes through them.",
    },
}


def agent_profile(provider: str) -> dict[str, Any]:
    normalized = normalize_provider(provider)
    profile = dict(SYSTEM_PROFILES[normalized])
    profile["provider"] = normalized
    profile["tool"] = tool_for_provider(normalized)
    return profile


def wake_prompt(provider: str, answers: dict[str, str] | None = None) -> str:
    profile = agent_profile(provider)
    answer_lines = []
    for key, value in (answers or {}).items():
        answer_lines.append(f"- {key}: {value}")
    answer_block = "\n".join(answer_lines) if answer_lines else "- No user onboarding answers supplied yet."
    return "\n".join(
        [
            f"You are now operating as the user's {profile['system']} agent.",
            "",
            "Native interface:",
            profile["interface"],
            "",
            "Native skills/plugins/tools:",
            profile["native_assets"],
            "Treat those native assets as belonging to your original system. FNP-QNN does not copy or emulate them.",
            "",
            "What FNP-QNN is:",
            "FNP-QNN is a local alpha-local, non-clinical research simulator. It provides deterministic Python CLI/TUI/API commands, onboarding context files, and optional MCP adapters.",
            "",
            "What FNP-QNN is not:",
            "It is not clinical, diagnostic, therapeutic, emergency, safety-critical, or production-public software.",
            "",
            "Agent boundary:",
            profile["boundary"],
            "Keep base simulator functions usable without AI providers. Use AI only as an optional adapter after provider connection and fingerprint approval.",
            "Preserve I -> I_system^S -> D_f -> dF -> i_fractal.",
            "",
            "User onboarding answers:",
            answer_block,
            "",
            "Working instruction:",
            "Read AGENTS.md, SOUL.md, USER.md, MEMORY.md, and config/user_wiring.json when present. Then wire only the narrow simulator utility requested by the user.",
        ]
    )
