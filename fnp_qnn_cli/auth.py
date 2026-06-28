"""Responsible local token login helpers for CLI testing."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUTH_HOME_ENV = "FNP_QNN_AUTH_HOME"
TOKEN_ENV = "FNP_QNN_CLI_TOKEN"

PROVIDER_GUIDES = {
    "openai": {
        "display": "OpenAI / ChatGPT",
        "url": "https://platform.openai.com/api-keys",
        "mode": "api-key",
        "note": "OpenAI API access uses project API keys; this CLI does not capture ChatGPT web-session cookies.",
    },
    "google": {
        "display": "Google AI / Gemini",
        "url": "https://aistudio.google.com/app/apikey",
        "mode": "api-key-or-gcloud-oauth",
        "gcloud_command": "gcloud auth application-default login",
        "note": "Gemini supports API keys and OAuth/application-default credentials for stricter access control.",
    },
}


def auth_home() -> Path:
    override = os.environ.get(AUTH_HOME_ENV)
    if override:
        return Path(override)
    return Path.home() / ".codex" / "fnp-qnn-cli"


def auth_path() -> Path:
    return auth_home() / "auth.json"


def token_fingerprint(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _token_preview(token: str) -> str:
    if len(token) <= 8:
        return "***"
    return token[:4] + "..." + token[-4:]


def login(token: str, label: str = "local-test", provider: str = "local") -> dict[str, Any]:
    if not token or not token.strip():
        raise ValueError("token must not be empty")
    path = auth_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "label": label,
        "provider": provider,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "token_sha256": token_fingerprint(token.strip()),
        "token_preview": _token_preview(token.strip()),
        "storage": "fingerprint-only",
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return status()


def logout() -> dict[str, Any]:
    path = auth_path()
    if path.exists():
        path.unlink()
    return status()


def load_auth() -> dict[str, Any] | None:
    path = auth_path()
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("auth file must contain a JSON object")
    return payload


def status() -> dict[str, Any]:
    payload = load_auth()
    return {
        "success": True,
        "authenticated": payload is not None,
        "auth_path": str(auth_path()),
        "token_env_present": bool(os.environ.get(TOKEN_ENV)),
        "storage": None if payload is None else payload.get("storage", "fingerprint-only"),
        "label": None if payload is None else payload.get("label"),
        "provider": None if payload is None else payload.get("provider"),
        "token_preview": None if payload is None else payload.get("token_preview"),
    }


def validate_token(token: str | None = None) -> dict[str, Any]:
    payload = load_auth()
    if payload is None:
        return {"success": False, "authenticated": False, "reason": "no local auth fingerprint"}
    candidate = token or os.environ.get(TOKEN_ENV)
    if not candidate:
        return {"success": False, "authenticated": False, "reason": f"no token supplied and {TOKEN_ENV} is absent"}
    expected = payload.get("token_sha256")
    matched = token_fingerprint(candidate.strip()) == expected
    return {
        "success": matched,
        "authenticated": matched,
        "reason": "matched" if matched else "token mismatch",
        "token_preview": payload.get("token_preview"),
    }


def web_login(
    provider: str,
    open_browser: bool = False,
    run_gcloud: bool = False,
    run_ollama: bool = False,
) -> dict[str, Any]:
    normalized = provider.strip().lower()
    if normalized not in PROVIDER_GUIDES:
        raise ValueError(f"unsupported provider '{provider}'")
    guide = dict(PROVIDER_GUIDES[normalized])
    opened = False
    if open_browser:
        opened = bool(webbrowser.open(guide["url"]))
    gcloud_result = None
    if run_gcloud:
        if normalized != "google":
            raise ValueError("--run-gcloud is only valid for google")
        process = subprocess.run(("gcloud", "auth", "application-default", "login"), text=True, check=False)
        gcloud_result = {"returncode": process.returncode}
    ollama_result = None
    if run_ollama:
        raise ValueError("Ollama Cloud is not an official school provider for FNP-QNN; use Codex/OpenAI or Antigravity/Gemini.")
    return {
        "success": True,
        "provider": normalized,
        "display": guide["display"],
        "mode": guide["mode"],
        "url": guide["url"],
        "opened_browser": opened,
        "gcloud_command": guide.get("gcloud_command"),
        "ollama_command": guide.get("ollama_command"),
        "gcloud_result": gcloud_result,
        "ollama_result": ollama_result,
        "note": guide["note"],
        "next_step": f"Run: fnp-qnn auth login-provider {normalized} --token <token>",
        "raw_token_stored": False,
    }
