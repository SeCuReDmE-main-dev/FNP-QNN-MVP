"""Local diagnostics for the FNP-QNN CLI and TUI."""

from __future__ import annotations

import importlib
import os
import socket
import sys
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from .auth import status as auth_status
from .external_ai import external_ai_status
from .operator import PROJECT_ROOT, alpha_command, command_exists, tests_command
from .registry import RESEARCH_BOUNDARY, command_response, neurobit_gates, qnn_smoke, runtime_run

SECRET_NAMES = (
    "DATADOG_API_KEY",
    "DD_API_KEY",
    "E2B_API_KEY",
    "OPENAI_API_KEY",
    "GITHUB_TOKEN",
    "REDIS_URL",
)


@dataclass(frozen=True)
class DoctorCheck:
    name: str
    status: str
    detail: str
    data: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"name": self.name, "status": self.status, "detail": self.detail}
        if self.data:
            payload["data"] = self.data
        return payload


def _check(name: str, status: str, detail: str, data: dict[str, Any] | None = None) -> DoctorCheck:
    return DoctorCheck(name=name, status=status, detail=detail, data=data)


def _package_version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def _import_check(module_name: str) -> DoctorCheck:
    try:
        importlib.import_module(module_name)
    except Exception as exc:  # pragma: no cover - exact import failures vary by environment.
        return _check(f"import:{module_name}", "fail", f"{type(exc).__name__}: {exc}")
    return _check(f"import:{module_name}", "pass", "import ok")


def _file_check(relative_path: str) -> DoctorCheck:
    path = PROJECT_ROOT / relative_path
    if path.exists():
        kind = "directory" if path.is_dir() else "file"
        return _check(f"path:{relative_path}", "pass", f"{kind} exists")
    return _check(f"path:{relative_path}", "fail", "missing")


def _service_probe(name: str, url: str, timeout_seconds: float = 1.5) -> DoctorCheck:
    request = Request(url, headers={"User-Agent": "fnp-qnn-doctor/0.1"})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            return _check(f"service:{name}", "pass", f"HTTP {response.status}", {"url": url})
    except (URLError, OSError, TimeoutError) as exc:
        return _check(f"service:{name}", "warn", f"not reachable: {type(exc).__name__}", {"url": url})


def _port_probe(name: str, host: str, port: int) -> DoctorCheck:
    try:
        with socket.create_connection((host, port), timeout=1.0):
            return _check(f"port:{name}", "pass", f"{host}:{port} accepts TCP")
    except OSError as exc:
        return _check(f"port:{name}", "warn", f"{host}:{port} closed or unavailable: {type(exc).__name__}")


def _smoke_check(name: str, runner) -> DoctorCheck:
    try:
        payload = runner()
    except Exception as exc:
        return _check(f"smoke:{name}", "fail", f"{type(exc).__name__}: {exc}")
    if payload.get("success", True):
        return _check(f"smoke:{name}", "pass", "smoke ok")
    return _check(f"smoke:{name}", "fail", str(payload.get("error", "smoke failed")))


def run_doctor(full: bool = False, probe_services: bool = True) -> dict[str, Any]:
    checks: list[DoctorCheck] = []
    in_venv = bool(os.environ.get("VIRTUAL_ENV")) or sys.prefix != sys.base_prefix

    checks.append(
        _check(
            "python",
            "pass" if sys.version_info >= (3, 10) else "fail",
            sys.version.split()[0],
            {"executable": sys.executable, "in_virtualenv": in_venv, "prefix": sys.prefix},
        )
    )
    checks.append(
        _check(
            "project-root",
            "pass" if (PROJECT_ROOT / "pyproject.toml").exists() else "fail",
            str(PROJECT_ROOT),
            {"cwd": str(Path.cwd())},
        )
    )

    package_names = [
        "numpy",
        "torch",
        "scikit-learn",
        "fastapi",
        "uvicorn",
        "python-multipart",
        "panel",
        "textual",
        "httpx",
        "qiskit",
        "ddtrace",
    ]
    for package_name in package_names:
        version = _package_version(package_name)
        optional = package_name in {"qiskit", "ddtrace"}
        if version:
            checks.append(_check(f"package:{package_name}", "pass", version))
        else:
            checks.append(_check(f"package:{package_name}", "warn" if optional else "fail", "not installed"))

    for module_name in ["api.main", "panel_app", "core", "ui.network_designer", "fnp_qnn_cli"]:
        checks.append(_import_check(module_name))

    for relative_path in [
        "pyproject.toml",
        "requirements.txt",
        "AGENTS.md",
        "README.md",
        "panel_app.py",
        "api/main.py",
        "tests",
    ]:
        checks.append(_file_check(relative_path))

    checks.append(
        _check(
            "secrets",
            "pass",
            "presence only; values redacted",
            {name: bool(os.environ.get(name)) for name in SECRET_NAMES},
        )
    )
    auth_payload = auth_status()
    checks.append(
        _check(
            "auth:fnp-qnn-cli",
            "pass" if auth_payload["authenticated"] or auth_payload["token_env_present"] else "warn",
            "fingerprint present or token env available"
            if auth_payload["authenticated"] or auth_payload["token_env_present"]
            else "no local auth fingerprint and no token env",
            auth_payload,
        )
    )
    external_payload = external_ai_status()
    checks.append(
        _check(
            "external-ai:codex",
            "pass" if external_payload["codex"]["available"] else "warn",
            "codex CLI available" if external_payload["codex"]["available"] else "codex CLI not found on PATH",
            external_payload["codex"],
        )
    )
    checks.append(
        _check(
            "external-ai:openclaw",
            "pass" if external_payload["openclaw"]["config_exists"] else "warn",
            "OpenClaw config found" if external_payload["openclaw"]["config_exists"] else "OpenClaw config not found",
            external_payload["openclaw"],
        )
    )
    checks.append(
        _check(
            "external-ai:antigravity",
            "pass" if external_payload["antigravity"]["available"] else "warn",
            "antigravity CLI available"
            if external_payload["antigravity"]["available"]
            else "antigravity CLI not found on PATH",
            external_payload["antigravity"],
        )
    )
    checks.append(
        _check(
            "validation:tests-command",
            "pass",
            tests_command().display(),
            {"exists": command_exists((sys.executable, "--version"))},
        )
    )
    checks.append(
        _check(
            "validation:alpha-command",
            "pass" if (PROJECT_ROOT / "scripts/validate_alpha_readiness.py").exists() else "fail",
            alpha_command().display(),
        )
    )

    if probe_services:
        checks.append(_port_probe("api", "127.0.0.1", 8000))
        checks.append(_port_probe("panel", "127.0.0.1", 5006))
        checks.append(_service_probe("api-health", "http://127.0.0.1:8000/health"))
        checks.append(_service_probe("panel", "http://127.0.0.1:5006/"))

    if full:
        checks.append(_smoke_check("runtime-status", lambda: command_response("cerebrum-runtime-status")))
        checks.append(_smoke_check("runtime-run", lambda: runtime_run({"epochs": 2})))
        checks.append(_smoke_check("qnn-smoke", lambda: qnn_smoke({"epochs": 2, "test_size": 0.0})))
        checks.append(_smoke_check("neurobit-gates", lambda: neurobit_gates({"truth": 0.5})))
        checks.append(_smoke_check("legacy-demo", lambda: command_response("cerebrum-runtime-legacy-demo")))

    totals = {
        "pass": sum(1 for item in checks if item.status == "pass"),
        "warn": sum(1 for item in checks if item.status == "warn"),
        "fail": sum(1 for item in checks if item.status == "fail"),
    }
    status = "fail" if totals["fail"] else "warn" if totals["warn"] else "pass"

    return {
        "success": status != "fail",
        "status": status,
        "research_boundary": RESEARCH_BOUNDARY,
        "project_root": str(PROJECT_ROOT),
        "totals": totals,
        "checks": [item.as_dict() for item in checks],
    }
