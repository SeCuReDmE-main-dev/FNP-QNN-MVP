"""Controlled local operator command builders."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class OperatorCommand:
    name: str
    argv: tuple[str, ...]
    cwd: Path = PROJECT_ROOT

    def display(self) -> str:
        return " ".join(self.argv)


def api_serve_command(port: int = 8000) -> OperatorCommand:
    return OperatorCommand("api-serve", ("uvicorn", "api.main:app", "--reload", "--port", str(port)))


def panel_serve_command(port: int = 5006) -> OperatorCommand:
    return OperatorCommand("panel-serve", ("panel", "serve", "panel_app.py", "--port", str(port)))


def tests_command() -> OperatorCommand:
    return OperatorCommand(
        "validate-tests",
        (sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"),
    )


def alpha_command() -> OperatorCommand:
    return OperatorCommand("validate-alpha", (sys.executable, "scripts/validate_alpha_readiness.py"))


def run_operator_command(command: OperatorCommand) -> int:
    process = subprocess.run(command.argv, cwd=str(command.cwd), check=False)
    return int(process.returncode)


def run_capture(command: OperatorCommand, timeout_seconds: int = 60) -> dict[str, object]:
    process = subprocess.run(
        command.argv,
        cwd=str(command.cwd),
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        check=False,
    )
    return {
        "name": command.name,
        "command": command.display(),
        "returncode": process.returncode,
        "stdout": process.stdout[-4000:],
        "stderr": process.stderr[-4000:],
    }


def command_exists(argv: Sequence[str]) -> bool:
    try:
        process = subprocess.run(
            tuple(argv),
            cwd=str(PROJECT_ROOT),
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return process.returncode in (0, 1, 2)
