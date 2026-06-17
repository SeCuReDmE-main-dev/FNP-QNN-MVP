#!/usr/bin/env python3
"""Validate local Datadog API/log intake connectivity without printing secrets."""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, Optional, Tuple


DEFAULT_ENV_PATH = Path(r"C:\Users\jeans\.openclaw\workspace\.env")


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _env_first(*names: str, default: Optional[str] = None) -> Optional[str]:
    for name in names:
        value = os.getenv(name)
        if value:
            return value.strip()
    return default


def _normalize_site(site: str) -> str:
    site = site.strip().replace("https://", "").replace("http://", "").rstrip("/")
    if site.startswith("api."):
        site = site[4:]
    return site


def _request(method: str, url: str, headers: Dict[str, str], payload: Optional[object] = None) -> Tuple[int, str]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return response.getcode(), response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        return 0, str(exc.reason)


def main() -> int:
    _load_env_file(Path(os.getenv("OPENCLAW_DD_ENV_FILE", str(DEFAULT_ENV_PATH))))
    api_key = _env_first("DATADOG_API_KEY", "DD_API_KEY")
    app_key = _env_first("DATADOG_APP_KEY", "DD_APP_KEY")
    site = _normalize_site(_env_first("DATADOG_SITE", "DD_SITE", default="datadoghq.com") or "datadoghq.com")
    service = _env_first("DD_SERVICE", default="fnp-qnn-datadog-smoke") or "fnp-qnn-datadog-smoke"
    env = _env_first("DD_ENV", default="local") or "local"

    print(f"site={site}")
    print(f"service={service}")
    print(f"env={env}")
    print(f"has_api_key={bool(api_key)}")
    print(f"has_app_key={bool(app_key)}")

    if not api_key:
        print("FAIL: missing DATADOG_API_KEY or DD_API_KEY")
        return 2

    validate_url = f"https://api.{site}/api/v1/validate"
    status, body = _request("GET", validate_url, {"DD-API-KEY": api_key})
    if status != 200:
        print(f"FAIL: api key validation returned status={status}")
        if body:
            print(body[:500])
        return 1
    print("PASS: Datadog API key validates")

    intake_url = f"https://http-intake.logs.{site}/api/v2/logs"
    event = {
        "message": "FNP-QNN Datadog local connection smoke test",
        "service": service,
        "ddsource": "fnp_qnn_local",
        "status": "info",
        "ddtags": f"env:{env},component:datadog_connection,source:codex",
        "timestamp": int(time.time() * 1000),
    }
    status, body = _request(
        "POST",
        intake_url,
        {"Content-Type": "application/json", "DD-API-KEY": api_key},
        [event],
    )
    if status not in {200, 202}:
        print(f"FAIL: log intake returned status={status}")
        if body:
            print(body[:500])
        return 1
    print("PASS: Datadog log intake accepted smoke event")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
