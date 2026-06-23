"""Real external AI runtime discovery and login helpers."""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .operator import PROJECT_ROOT
from .simulator_control import (
    CONTROL_TASK_NAMES,
    display_command,
    run_simulator_command,
    simulator_command_for,
    simulator_control_tasks,
)


SENSITIVE_KEYS = ("token", "secret", "password", "credential", "cookie", "apiKey", "api_key", "key")
OLLAMA_MODEL_ENV = "FNP_QNN_OLLAMA_CLOUD_MODEL"
OLLAMA_API_KEY_ENV = "OLLAMA_API_KEY"
CONTROL_TOOLS = ("auto", "codex", "antigravity", "ollama")


def user_openclaw_home() -> Path:
    return Path(os.environ.get("OPENCLAW_HOME") or (Path.home() / ".openclaw"))


def command_path(command: str) -> str | None:
    return shutil.which(command)


def _run_capture(argv: tuple[str, ...], timeout: int = 20) -> dict[str, Any]:
    try:
        if platform.system().lower() == "windows":
            proc = subprocess.run(" ".join(argv), text=True, capture_output=True, timeout=timeout, check=False, shell=True)
        else:
            proc = subprocess.run(argv, text=True, capture_output=True, timeout=timeout, check=False)
    except FileNotFoundError:
        return {"available": False, "returncode": None, "stdout": "", "stderr": "command not found"}
    except OSError as exc:
        return {"available": True, "returncode": None, "stdout": "", "stderr": f"{type(exc).__name__}: {exc}"}
    except subprocess.TimeoutExpired as exc:
        return {
            "available": True,
            "returncode": None,
            "stdout": (exc.stdout or "")[-2000:],
            "stderr": "command timed out",
        }
    return {
        "available": True,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def _redact_shape(value: Any, key: str = "") -> Any:
    if any(marker.lower() in key.lower() for marker in SENSITIVE_KEYS):
        return "[redacted]"
    if isinstance(value, dict):
        return {str(k): _redact_shape(v, str(k)) for k, v in value.items()}
    if isinstance(value, list):
        preview = [_redact_shape(item, key) for item in value[:5]]
        if len(value) > 5:
            preview.append(f"... {len(value) - 5} more")
        return preview
    return value


def inspect_openclaw(home: Path | None = None) -> dict[str, Any]:
    root = home or user_openclaw_home()
    config_path = root / "openclaw.json"
    credentials_dir = root / "credentials"
    auth_profiles_dir = credentials_dir / "auth-profiles"
    payload: dict[str, Any] = {
        "success": True,
        "openclaw_home": str(root),
        "exists": root.exists(),
        "config_path": str(config_path),
        "config_exists": config_path.exists(),
        "credential_profiles": [],
        "providers": {},
        "agent_runtimes": [],
        "plugins_enabled": [],
    }
    if auth_profiles_dir.exists():
        payload["credential_profiles"] = [
            {"file": item.name, "size": item.stat().st_size} for item in sorted(auth_profiles_dir.glob("*.json"))
        ]
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            providers = ((data.get("models") or {}).get("providers") or {})
            payload["providers"] = {
                name: {
                    "api": provider.get("api"),
                    "baseUrl": provider.get("baseUrl"),
                    "models": [model.get("id") for model in (provider.get("models") or [])[:10]],
                }
                for name, provider in providers.items()
                if isinstance(provider, dict)
            }
            agents = ((data.get("agents") or {}).get("defaults") or {}).get("models") or {}
            payload["agent_runtimes"] = [
                {
                    "model": model,
                    "agentRuntime": ((spec or {}).get("agentRuntime") or {}).get("id"),
                    "alias": (spec or {}).get("alias"),
                }
                for model, spec in agents.items()
                if isinstance(spec, dict) and (spec.get("agentRuntime") or spec.get("alias"))
            ]
            plugins = ((data.get("plugins") or {}).get("entries") or {})
            payload["plugins_enabled"] = sorted([name for name, spec in plugins.items() if (spec or {}).get("enabled")])
            payload["redacted_config_preview"] = _redact_shape(data)
        except Exception as exc:
            payload["config_error"] = f"{type(exc).__name__}: {exc}"
    return payload


def external_ai_status() -> dict[str, Any]:
    codex = command_path("codex")
    antigravity = command_path("antigravity")
    ollama = command_path("ollama")
    gcloud = command_path("gcloud")
    openclaw = inspect_openclaw()
    status: dict[str, Any] = {
        "success": True,
        "codex": {"available": bool(codex), "path": codex},
        "antigravity": {"available": bool(antigravity), "path": antigravity},
        "ollama": {
            "available": bool(ollama),
            "path": ollama,
            "api_key_env_present": bool(os.environ.get(OLLAMA_API_KEY_ENV)),
            "cloud_model": os.environ.get(OLLAMA_MODEL_ENV, "gpt-oss:120b-cloud"),
        },
        "gcloud": {"available": bool(gcloud), "path": gcloud},
        "openclaw": {
            "exists": openclaw["exists"],
            "config_exists": openclaw["config_exists"],
            "credential_profile_count": len(openclaw["credential_profiles"]),
            "providers": list((openclaw.get("providers") or {}).keys()),
            "agent_runtimes": openclaw.get("agent_runtimes", []),
        },
        "no_simulation": True,
    }
    if codex:
        status["codex"]["login_status"] = _run_capture(("codex", "login", "status"), timeout=20)
    if ollama:
        status["ollama"]["version"] = _run_capture(("ollama", "--version"), timeout=20)
    return status


def _resolve_control_tool(tool: str) -> tuple[str | None, str | None]:
    if tool not in CONTROL_TOOLS:
        return None, f"unsupported control tool: {tool}"
    codex = command_path("codex")
    antigravity = command_path("antigravity")
    ollama = command_path("ollama")
    if tool == "codex":
        return "codex", None
    if tool == "antigravity":
        return "antigravity", None
    if tool == "ollama":
        return "ollama", None
    if codex:
        return "codex", None
    if antigravity:
        return "antigravity", None
    if ollama:
        return "ollama", None
    return None, "none of codex, antigravity, or ollama is installed on PATH"


def _control_prompt(task: str, simulator_command: tuple[str, ...], extra_prompt: str | None = None) -> str:
    instructions = [
        "You are controlling the local FNP-QNN alpha-local research simulator.",
        f"Project root: {PROJECT_ROOT}",
        "Run exactly this allowlisted simulator command from the project root:",
        display_command(simulator_command),
        "Do not invent substitute commands. Do not edit files for this control task.",
        "Preserve the non-clinical research boundary and the I -> I_system^S -> D_f -> dF -> i_fractal hierarchy.",
        f"Task intent: {task}",
    ]
    if extra_prompt:
        instructions.append(f"Additional operator note: {extra_prompt}")
    return "\n".join(instructions)


def _agent_command(tool: str, prompt: str) -> tuple[str, ...]:
    if tool == "codex":
        executable = command_path("codex") or "codex"
        return (
            executable,
            "exec",
            "-C",
            str(PROJECT_ROOT),
            "--ask-for-approval",
            "never",
            "--sandbox",
            "workspace-write",
            prompt,
        )
    executable = command_path("antigravity") or "antigravity"
    if tool == "ollama":
        executable = command_path("ollama") or "ollama"
        return (
            executable,
            "run",
            os.environ.get(OLLAMA_MODEL_ENV, "gpt-oss:120b-cloud"),
            prompt,
        )
    return (
        executable,
        "run",
        "--cwd",
        str(PROJECT_ROOT),
        "--prompt",
        prompt,
    )


def _run_agent_command(argv: tuple[str, ...], timeout: int) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            argv,
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return {"available": False, "returncode": None, "stdout": "", "stderr": "command not found"}
    except OSError as exc:
        return {"available": True, "returncode": None, "stdout": "", "stderr": f"{type(exc).__name__}: {exc}"}
    except subprocess.TimeoutExpired as exc:
        return {
            "available": True,
            "returncode": None,
            "stdout": (exc.stdout or "")[-4000:],
            "stderr": "command timed out",
        }
    return {
        "available": True,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-8000:],
        "stderr": proc.stderr[-8000:],
    }


def control_simulator(
    task: str,
    tool: str = "auto",
    execute: bool = False,
    timeout: int = 300,
    extra_prompt: str | None = None,
) -> dict[str, Any]:
    if task == "list":
        return {"success": True, "tasks": simulator_control_tasks(), "tools": list(CONTROL_TOOLS)}
    if task not in CONTROL_TASK_NAMES:
        return {
            "success": False,
            "error": f"unknown simulator control task: {task}",
            "allowed_tasks": sorted(CONTROL_TASK_NAMES),
        }
    selected_tool, error = _resolve_control_tool(tool)
    if not selected_tool:
        return {"success": False, "task": task, "tool": tool, "error": error, "allowed_tools": list(CONTROL_TOOLS)}

    simulator_command = simulator_command_for(task)
    prompt = _control_prompt(task, simulator_command, extra_prompt=extra_prompt)
    agent_command = _agent_command(selected_tool, prompt)
    payload: dict[str, Any] = {
        "success": True,
        "task": task,
        "tool": selected_tool,
        "requested_tool": tool,
        "execute": execute,
        "project_root": str(PROJECT_ROOT),
        "simulator_command": list(simulator_command),
        "simulator_command_display": display_command(simulator_command),
        "agent_command": list(agent_command),
        "agent_command_display": display_command(agent_command),
        "prompt": prompt,
        "no_simulation": True,
    }
    if not command_path(selected_tool):
        payload["tool_available"] = False
        payload["success"] = not execute
        payload["error"] = f"{selected_tool} CLI is not installed on PATH"
        return payload
    payload["tool_available"] = True
    if execute:
        result = _run_agent_command(agent_command, timeout=timeout)
        payload["agent_result"] = result
        if selected_tool == "ollama" and result["available"] and result["returncode"] == 0:
            simulator_result = run_simulator_command(simulator_command, timeout=timeout)
            payload["simulator_result"] = simulator_result
            payload["success"] = simulator_result["returncode"] == 0
        else:
            payload["success"] = bool(result["available"] and result["returncode"] == 0)
    return payload


def connect_codex(device_auth: bool = False, api_key: str | None = None) -> dict[str, Any]:
    if not command_path("codex"):
        return {"success": False, "provider": "codex", "error": "codex CLI is not installed on PATH"}
    if api_key:
        proc = subprocess.run(
            ("codex", "login", "--with-api-key"),
            input=api_key,
            text=True,
            capture_output=True,
            timeout=120,
            check=False,
        )
        return {
            "success": proc.returncode == 0,
            "provider": "codex",
            "method": "api-key-stdin",
            "returncode": proc.returncode,
            "stdout": proc.stdout[-2000:],
            "stderr": proc.stderr[-2000:],
            "raw_token_stored_by_fnp_qnn": False,
        }
    argv = ("codex", "login", "--device-auth") if device_auth else ("codex", "login")
    proc = subprocess.run(argv, text=True, check=False)
    return {"success": proc.returncode == 0, "provider": "codex", "method": "device-auth" if device_auth else "browser", "returncode": proc.returncode}


def connect_antigravity() -> dict[str, Any]:
    path = command_path("antigravity")
    if not path:
        return {
            "success": False,
            "provider": "antigravity",
            "error": "antigravity CLI is not installed on PATH",
            "next_step": "Install Google Antigravity, then rerun this command.",
        }
    proc = subprocess.run(("antigravity", "--help"), text=True, capture_output=True, timeout=20, check=False)
    return {
        "success": proc.returncode == 0,
        "provider": "antigravity",
        "path": path,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-2000:],
        "stderr": proc.stderr[-2000:],
    }


def connect_ollama() -> dict[str, Any]:
    path = command_path("ollama")
    if not path:
        return {
            "success": False,
            "provider": "ollama",
            "error": "ollama CLI is not installed on PATH",
            "next_step": "Install Ollama, then run `ollama signin`.",
        }
    proc = subprocess.run(("ollama", "signin"), text=True, check=False)
    return {
        "success": proc.returncode == 0,
        "provider": "ollama",
        "method": "ollama-signin",
        "path": path,
        "returncode": proc.returncode,
        "api_key_env_present": bool(os.environ.get(OLLAMA_API_KEY_ENV)),
        "cloud_model": os.environ.get(OLLAMA_MODEL_ENV, "gpt-oss:120b-cloud"),
    }
