"""AI-neutral allowlisted simulator control commands."""

from __future__ import annotations

import platform
import shlex
import subprocess
import sys
from typing import Any

from .operator import PROJECT_ROOT


def python_module_command(*args: str) -> tuple[str, ...]:
    return (sys.executable, "-m", "fnp_qnn_cli", "--json", *args)


SIMULATOR_CONTROL_TASKS: dict[str, dict[str, Any]] = {
    "status": {
        "description": "Read the simulator runtime bridge status.",
        "command": python_module_command("status"),
    },
    "doctor": {
        "description": "Run bounded diagnostics without probing long-running services.",
        "command": python_module_command("doctor", "--full", "--no-probe-services"),
    },
    "runtime": {
        "description": "Run a short Cerebrum runtime bridge smoke path.",
        "command": python_module_command("runtime", "run", "--epochs", "2"),
    },
    "qnn": {
        "description": "Run a deterministic QNN smoke path.",
        "command": python_module_command("qnn", "smoke", "--epochs", "2", "--test-size", "0"),
    },
    "neurobit": {
        "description": "Run a NeuroBit gate profile.",
        "command": python_module_command("neurobit", "gates", "--truth", "0.5"),
    },
    "validate": {
        "description": "Run alpha readiness validation.",
        "command": (sys.executable, "scripts/validate_alpha_readiness.py"),
    },
    "external-status": {
        "description": "Read optional external runtime availability.",
        "command": python_module_command("external-ai", "status"),
    },
}

CONTROL_TASK_NAMES = tuple(SIMULATOR_CONTROL_TASKS)


def display_command(argv: tuple[str, ...]) -> str:
    if platform.system().lower() == "windows":
        return subprocess.list2cmdline(argv)
    return " ".join(shlex.quote(part) for part in argv)


def simulator_control_tasks() -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "description": spec["description"],
            "command": display_command(spec["command"]),
        }
        for name, spec in SIMULATOR_CONTROL_TASKS.items()
    ]


def simulator_command_for(task: str) -> tuple[str, ...]:
    if task not in SIMULATOR_CONTROL_TASKS:
        raise KeyError(task)
    return SIMULATOR_CONTROL_TASKS[task]["command"]


def run_simulator_command(argv: tuple[str, ...], timeout: int) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            argv,
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (FileNotFoundError, OSError) as exc:
        return {"returncode": None, "stdout": "", "stderr": f"{type(exc).__name__}: {exc}"}
    except subprocess.TimeoutExpired as exc:
        return {"returncode": None, "stdout": (exc.stdout or "")[-4000:], "stderr": "command timed out"}
    return {"returncode": proc.returncode, "stdout": proc.stdout[-8000:], "stderr": proc.stderr[-8000:]}
