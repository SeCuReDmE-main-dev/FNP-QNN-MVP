"""Small plugin scaffold helper exposed through the FNP-QNN CLI."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from .operator import PROJECT_ROOT


def normalize_plugin_name(name: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower())
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    if not normalized:
        raise ValueError("plugin name must contain at least one alphanumeric character")
    if len(normalized) > 64:
        raise ValueError("plugin name must be <= 64 characters after normalization")
    return normalized


def create_plugin_scaffold(name: str, parent_path: str | None = None, force: bool = False) -> dict[str, Any]:
    plugin_name = normalize_plugin_name(name)
    parent = Path(parent_path) if parent_path else PROJECT_ROOT / "plugins"
    plugin_root = parent / plugin_name
    manifest_dir = plugin_root / ".codex-plugin"
    manifest_path = manifest_dir / "plugin.json"
    if plugin_root.exists() and not force:
        raise FileExistsError(f"plugin path already exists: {plugin_root}")

    manifest_dir.mkdir(parents=True, exist_ok=True)
    (plugin_root / "scripts").mkdir(exist_ok=True)
    manifest = {
        "name": plugin_name,
        "version": "0.1.0",
        "description": "Local FNP-QNN CeLeBrUm CLI bridge for responsible AI logic testing.",
        "author": {"name": "FNP-QNN local maintainer"},
        "license": "SEE-REPOSITORY",
        "interface": {
            "displayName": "FNP-QNN CeLeBrUm CLI",
            "shortDescription": "Local FNP-QNN CLI bridge.",
            "longDescription": "Local non-clinical FNP-QNN CLI bridge for responsible simulator experiments.",
            "developerName": "FNP-QNN local maintainer",
            "category": "Developer",
            "capabilities": ["Local", "Write"],
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    runner_path = plugin_root / "scripts" / "run_fnp_qnn_cli.py"
    runner_path.write_text(
        (
            "from fnp_qnn_cli.celebrum import celebrum_clip_function\n\n"
            "def run(payload=None):\n"
            "    return celebrum_clip_function(payload or {}, require_auth=False)\n"
        ),
        encoding="utf-8",
    )
    return {
        "success": True,
        "name": plugin_name,
        "plugin_root": str(plugin_root),
        "manifest_path": str(manifest_path),
        "runner_path": str(runner_path),
        "marketplace_updated": False,
    }


def create_ai_control_mcp_plugin(parent_path: str | None = None, force: bool = False) -> dict[str, Any]:
    plugin_name = "fnp-qnn-ai-control-mcp"
    parent = Path(parent_path) if parent_path else PROJECT_ROOT / "plugins"
    plugin_root = parent / plugin_name
    manifest_dir = plugin_root / ".codex-plugin"
    manifest_path = manifest_dir / "plugin.json"
    mcp_path = plugin_root / ".mcp.json"
    if plugin_root.exists() and not force:
        raise FileExistsError(f"plugin path already exists: {plugin_root}")

    manifest_dir.mkdir(parents=True, exist_ok=True)
    (plugin_root / "scripts").mkdir(exist_ok=True)
    manifest = {
        "name": plugin_name,
        "version": "0.1.0",
        "description": "MCP bridge that lets authenticated OpenAI/ChatGPT or Google/Gemini providers control the FNP-QNN simulator through Codex or Antigravity.",
        "author": {"name": "FNP-QNN local maintainer"},
        "license": "SEE-REPOSITORY",
        "mcpServers": "./.mcp.json",
        "interface": {
            "displayName": "FNP-QNN AI Control MCP",
            "shortDescription": "Provider-approved simulator onboarding and control.",
            "longDescription": "Local MCP bridge for provider-approved FNP-QNN onboarding and optional simulator control through Codex or Antigravity.",
            "developerName": "FNP-QNN local maintainer",
            "category": "Developer",
            "capabilities": ["Interactive", "Write"],
            "defaultPrompt": [
                "Onboard my simulator with OpenAI.",
                "Show FNP-QNN control tasks.",
                "Apply onboarding without AI dependency."
            ],
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    mcp = {
        "mcpServers": {
            "fnp-qnn-ai-control": {
                "command": sys.executable,
                "args": ["-m", "fnp_qnn_cli.mcp_server"],
                "cwd": str(PROJECT_ROOT),
                "env": {"FNP_QNN_MCP_PLUGIN": "1"},
            }
        }
    }
    mcp_path.write_text(json.dumps(mcp, indent=2, sort_keys=True), encoding="utf-8")
    runner_path = plugin_root / "scripts" / "run_mcp_server.py"
    runner_path.write_text(
        (
            "from fnp_qnn_cli.mcp_server import main\n\n"
            "if __name__ == \"__main__\":\n"
            "    raise SystemExit(main())\n"
        ),
        encoding="utf-8",
    )
    readme_path = plugin_root / "README.md"
    readme_path.write_text(
        (
            "# FNP-QNN AI Control MCP\n\n"
            "This local plugin exposes an MCP server for authenticated simulator control.\n\n"
            "- OpenAI/ChatGPT routes to Codex.\n"
            "- Google/Gemini routes to Antigravity.\n"
            "- Ollama Cloud is not an official school route for this simulator.\n"
            "- Onboarding writes AGENTS.md, SOUL.md, USER.md, MEMORY.md, and config/user_wiring.json after fingerprint approval.\n"
            "- Simulator commands are allowlisted and dry-run by default.\n"
            "- Base simulator functions do not depend on AI providers.\n"
            "- Raw tokens are not stored by this plugin.\n"
        ),
        encoding="utf-8",
    )
    return {
        "success": True,
        "name": plugin_name,
        "plugin_root": str(plugin_root),
        "manifest_path": str(manifest_path),
        "mcp_path": str(mcp_path),
        "runner_path": str(runner_path),
        "marketplace_updated": False,
    }
