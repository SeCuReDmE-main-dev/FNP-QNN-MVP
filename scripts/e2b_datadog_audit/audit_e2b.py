#!/usr/bin/env python3
"""Audit temporary E2B sandboxes and emit Datadog structured logs.

The implementation is intentionally defensive:
- no broad state is kept between runs
- audit sandbox is always cleaned up in a finally block
- errors are captured and sent as structured audit status
- optional dependencies are loaded lazily to avoid hard runtime requirements

Public-facing behavior:
- returns JSON on stdout with summary and per-check details
- sends one Datadog log event when API token is available
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple
from urllib import error as urllib_error
from urllib import request as urllib_request


DEFAULT_TIMEOUT_SECONDS = 300
DEFAULT_SERVICE = "e2b-vm-auditor"
DEFAULT_DATADOG_SITE = "datadoghq.com"


def _env_first(*names: str, default: Optional[str] = None) -> Optional[str]:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


@dataclass
class CheckResult:
    name: str
    command: str
    exit_code: Optional[int]
    passed: bool
    output: str
    error_output: str
    duration_ms: int
    error: Optional[str] = None


@dataclass
class AuditSummary:
    run_id: str
    audit_status: str
    service: str
    env: str
    sandbox_id: Optional[str]
    template_id: Optional[str]
    checks_passed: int
    checks_total: int
    started_at: str
    ended_at: str
    duration_ms: int
    results: List[Dict[str, Any]]
    extra_tags: Dict[str, str]
    metadata: Dict[str, Any]


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _coalesce_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _first_dict_json_payload(text: str) -> Optional[Dict[str, Any]]:
    for line in reversed(text.strip().splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            candidate = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict):
            return candidate
    return None


def _mask_sensitive_env_lines(lines: Sequence[str]) -> str:
    sensitive_patterns = [r"(?i)key|secret|token|password|credential|api_key"]
    flagged_prefixes = [
        "DD_API_KEY",
        "E2B_API_KEY",
        "API_KEY",
        "SECRET",
    ]

    out: List[str] = []
    for line in lines:
        if "=" not in line:
            out.append(line)
            continue
        key, value = line.split("=", 1)
        if any(re.search(pattern, key) for pattern in sensitive_patterns):
            out.append(f"{key}=(redacted)")
            continue
        if key in flagged_prefixes:
            out.append(f"{key}=(redacted)")
            continue
        out.append(f"{key}={value}")
    return "\n".join(out)


def _safe_json_dumps(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


class DatadogEmitter:
    def __init__(
        self,
        api_key: str,
        site: str = DEFAULT_DATADOG_SITE,
        timeout: int = 15,
        service: str = DEFAULT_SERVICE,
    ) -> None:
        self.api_key = api_key
        self.site = site
        self.timeout = timeout
        self.service = service
        self._last_status: Optional[int] = None
        self._sdk_unavailable: Optional[str] = None

    @staticmethod
    def _tag_dict_to_datadog_tags(tags: Dict[str, str]) -> List[str]:
        ordered = []
        for key in sorted(tags):
            value = str(tags[key]).strip()
            if value == "":
                continue
            ordered.append(f"{key}:{value}")
        return ordered

    @staticmethod
    def _normalize_site(site: str) -> str:
        normalized = site.strip().lower()
        if normalized.startswith("http://") or normalized.startswith("https://"):
            return normalized
        return f"https://api.{normalized}"

    @staticmethod
    def _normalize_intake_site(site: str) -> str:
        normalized = site.strip().lower()
        if normalized.startswith("http://") or normalized.startswith("https://"):
            normalized = normalized.split("://", 1)[1]
        if normalized.startswith("api."):
            normalized = normalized[len("api.") :]
        return f"https://http-intake.logs.{normalized}/api/v2/logs"

    def _build_datadog_payload(self, summary: AuditSummary) -> Tuple[List[str], Dict[str, Any]]:
        checks_failed = [entry["name"] for entry in summary.results if not entry.get("passed", False)]
        base_tags = {
            "service": self.service,
            "env": summary.env,
            "sandbox_id": summary.sandbox_id or "n/a",
            "template_id": summary.template_id or "n/a",
            "audit_status": summary.audit_status,
        }
        base_tags.update(summary.extra_tags)
        datadog_tags = self._tag_dict_to_datadog_tags(base_tags)
        details = asdict(summary)
        details["checks_failures"] = checks_failed
        message = (
            f"E2B sandbox audit {summary.audit_status.upper()} "
            f"({summary.checks_passed}/{summary.checks_total} checks passed). "
            f"Failures: {', '.join(checks_failed) or 'none'}"
        )
        return datadog_tags, {
            "service": summary.service,
            "timestamp": summary.ended_at,
            "status": "error" if summary.audit_status != "pass" else "info",
            "message": message,
            "ddsource": "e2b_audit",
            "details": details,
        }

    def emit_log(self, summary: AuditSummary) -> Tuple[bool, str]:
        try:
            from datadog_api_client import ApiClient as _DatadogApiClient
            from datadog_api_client import Configuration
            from datadog_api_client.v2.api.logs_api import LogsApi
            from datadog_api_client.v2.model.http_log import HTTPLog
            from datadog_api_client.v2.model.http_log_item import HTTPLogItem

            datadog_tags, payload = self._build_datadog_payload(summary)
            host = self._normalize_site(self.site)
            config = Configuration()
            config.host = host
            config.api_key["apiKeyAuth"] = self.api_key
            config.connection_pool_maxsize = 5
            log_item = HTTPLogItem(
                message=payload["message"],
                ddsource=payload["ddsource"],
                service=self.service,
                status=payload["status"],
                details=payload["details"],
            )
            body = HTTPLog([log_item])
            with _DatadogApiClient(configuration=config) as api_client:
                logs_api = LogsApi(api_client)
                logs_api.submit_log(body=body, ddtags=",".join(datadog_tags))
            self._last_status = 202
            return True, self._last_status_response(self._last_status)
        except ImportError as exc:
            self._sdk_unavailable = str(exc)
            try:
                return self._emit_http_fallback(summary)
            except Exception as exc_fallback:
                return False, f"Datadog SDK and fallback both unavailable: {exc_fallback!r}"
        except Exception as exc:  # pragma: no cover - environment/network variation
            return False, f"Datadog transport error: {exc!r}"

    def _emit_http_fallback(self, summary: AuditSummary) -> Tuple[bool, str]:
        datadog_tags, payload = self._build_datadog_payload(summary)
        endpoint = self._normalize_intake_site(self.site)
        request_body = json.dumps([payload]).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "DD-API-KEY": self.api_key,
        }
        req = urllib_request.Request(endpoint, data=request_body, headers=headers, method="POST")
        try:
            with urllib_request.urlopen(req, timeout=self.timeout) as response:
                self._last_status = int(response.getcode())
                return self._last_status in {200, 202}, self._last_status_response(self._last_status)
        except urllib_error.HTTPError as exc:
            return False, f"Datadog HTTP error {exc.code}: {exc.reason}"
        except urllib_error.URLError as exc:
            return False, f"Datadog network error: {exc.reason}"

    def _last_status_response(self, status: int) -> str:
        if status in {200, 202}:
            return "Datadog logs accepted"
        return f"Datadog response status {status}"


class E2BSandbox:
    def __init__(self, template_id: Optional[str], api_key: Optional[str], timeout: int) -> None:
        self.template_id = template_id
        self.api_key = api_key
        self.timeout = timeout
        self.sandbox = None
        self.sandbox_id: Optional[str] = None
        self._impl = self._load_impl()

    @staticmethod
    def _load_impl() -> Any:
        try:
            from e2b_code_interpreter import Sandbox as E2BSandboxSync
            return E2BSandboxSync
        except Exception:
            pass
        try:
            from e2b_code_interpreter import AsyncSandbox as E2BSandboxAsync
            return E2BSandboxAsync
        except Exception:
            return None

    def _instantiate(self):
        if self._impl is None:
            raise RuntimeError(
                "e2b-code-interpreter is not installed or unsupported. "
                "Install with: pip install e2b-code-interpreter"
            )

        if hasattr(self._impl, "create"):
            try:
                return self._instantiate_with_factory_or_ctor(self._impl.create)
            except TypeError:
                return self._impl()
        return self._impl()

    def _instantiate_with_factory_or_ctor(self, creator: Callable[..., Any]) -> Any:
        candidate_kwargs = [
            {},
            {"api_key": self.api_key, "template": self.template_id},
            {"api_key": self.api_key, "template_id": self.template_id},
            {"api_key": self.api_key},
            {"template": self.template_id},
            {"template_id": self.template_id},
        ]
        for kwargs in candidate_kwargs:
            cleaned = {k: v for k, v in kwargs.items() if v}
            try:
                return self._resolve_awaitable(creator(**cleaned))
            except TypeError:
                continue
            except Exception:
                continue
        return self._resolve_awaitable(creator())

    def __enter__(self) -> "E2BSandbox":
        instance = self._instantiate()
        sandbox = self._resolve_awaitable(instance)
        self.sandbox = sandbox
        self.sandbox_id = getattr(sandbox, "id", None) or getattr(sandbox, "sandbox_id", None)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.sandbox is None:
            return
        close_candidates = [getattr(self.sandbox, "close", None), getattr(self.sandbox, "__aexit__", None)]
        for closer in close_candidates:
            if callable(closer):
                try:
                    self._resolve_awaitable(closer())
                except Exception:
                    pass
                break

    def _resolve_awaitable(self, value: Any) -> Any:
        if asyncio.iscoroutine(value):
            return asyncio.run(value)
        return value

    def _as_text(self, result: Any) -> str:
        if isinstance(result, str):
            return result
        if result is None:
            return ""
        if isinstance(result, dict):
            return result.get("text", "") or result.get("output", "") or json.dumps(result)
        if isinstance(result, (tuple, list)):
            return "\n".join([_coalesce_text(item) for item in result])
        if hasattr(result, "text") and isinstance(getattr(result, "text"), str):
            return getattr(result, "text")
        if hasattr(result, "stdout") and hasattr(result, "stderr"):
            stdout = _coalesce_text(getattr(result, "stdout"))
            stderr = _coalesce_text(getattr(result, "stderr"))
            text = stdout
            if stderr:
                text = f"{text}\n{stderr}".strip()
            return text
        return _coalesce_text(result)

    def run(self, command: str, timeout: int) -> str:
        if self.sandbox is None:
            raise RuntimeError("sandbox not initialized")
        runner = self._resolve_awaitable(_pick_command_runner(self.sandbox))
        if not callable(runner):
            raise RuntimeError("No compatible E2B run API found on sandbox object")
        return self._coerce_run_output(self._resolve_awaitable(runner(command, timeout=timeout)))

    def _coerce_run_output(self, output: Any) -> str:
        text = self._as_text(output)
        if text.strip():
            return text
        return _coalesce_text(output)


def _pick_command_runner(sandbox: Any) -> Callable[..., Any]:
    for name in ("run_code", "runCode", "exec", "execute", "run_cell", "run"):
        method = getattr(sandbox, name, None)
        if callable(method):
            return _make_runner(method)
    raise RuntimeError("No command runner available on E2B sandbox object")


def _make_runner(method: Callable[..., Any]) -> Callable[..., Any]:
    def run(command: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> Any:
        try:
            return method(command)
        except TypeError:
            return method(command=command, timeout=timeout)
    return run


def _build_check_snippet(command: str, timeout: int) -> str:
    safe_command = json.dumps(command)
    snippet = """
import json
import subprocess
import sys

command = __SAFE_COMMAND__
try:
    completed = subprocess.run(
        command,
        shell=True,
        executable="/bin/bash",
        capture_output=True,
        text=True,
        timeout=__TIMEOUT__,
    )
    print(
        json.dumps(
            {
                "command": command,
                "exit_code": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        )
    )
except Exception as exc:
    print(json.dumps({"command": command, "exit_code": 1, "stdout": "", "stderr": str(exc)}))
    sys.exit(1)
"""
    return snippet.replace("__SAFE_COMMAND__", safe_command).replace("__TIMEOUT__", str(int(timeout)))


def _run_sandbox_check(
    sandbox: E2BSandbox,
    check: Tuple[str, str],
    timeout: int,
    redact_sensitive_values: bool,
) -> CheckResult:
    name, command = check
    started = time.perf_counter()
    try:
        output = sandbox.run(_build_check_snippet(command, timeout), timeout=timeout)
        parsed = _first_dict_json_payload(output) or {}
        exit_code = parsed.get("exit_code")
        stdout = _coalesce_text(parsed.get("stdout", output))
        stderr = _coalesce_text(parsed.get("stderr", ""))
        if name == "environment" and redact_sensitive_values:
            stdout = _mask_sensitive_env_lines(stdout.splitlines())
        passed = exit_code == 0
        if name == "permissions":
            passed = stderr == "" or exit_code == 0
        return CheckResult(
            name=name,
            command=command,
            exit_code=int(exit_code) if isinstance(exit_code, int) else None,
            passed=bool(passed),
            output=stdout,
            error_output=stderr,
            duration_ms=int((time.perf_counter() - started) * 1000),
            error=None,
        )
    except Exception as exc:  # pragma: no cover - transport / environment variance
        return CheckResult(
            name=name,
            command=command,
            exit_code=None,
            passed=False,
            output="",
            error_output="",
            duration_ms=int((time.perf_counter() - started) * 1000),
            error=str(exc),
        )


def _build_checks() -> List[Tuple[str, str]]:
    return [
        ("packages", "dpkg -l | head -n 200 || true; pip list --format=columns"),
        ("ports", "ss -tlnp || netstat -tlnp"),
        ("processes", "ps aux | head -n 120"),
        ("environment", "env"),
        (
            "permissions",
            "python - <<'PY'\n"
            "import json\n"
            "import os\n"
            "import stat\n"
            "\n"
            "paths = [\n"
            "    '/etc/shadow',\n"
            "    '/etc/sudoers',\n"
            "    '/etc/cron.d',\n"
            "    '/root/.ssh',\n"
            "    '/tmp',\n"
            "]\n"
            "report = []\n"
            "for path in paths:\n"
            "    try:\n"
            "        mode = oct(os.lstat(path).st_mode & 0o777)\n"
            "        report.append({'path': path, 'mode': mode, 'exists': True})\n"
            "    except FileNotFoundError:\n"
            "        report.append({'path': path, 'exists': False})\n"
            "    except PermissionError:\n"
            "        report.append({'path': path, 'exists': True, 'error': 'permission denied'})\n"
            "print(json.dumps(report))\n"
            "PY",
        ),
    ]


def _build_payload(
    summary: AuditSummary,
    args: argparse.Namespace,
    include_full_output: bool = True,
) -> Dict[str, Any]:
    tags = {
        "env": args.dd_env,
        "sandbox_id": summary.sandbox_id or "n/a",
        "template_id": summary.template_id or "n/a",
        "audit_status": summary.audit_status,
    }
    payload = {
        "run_id": summary.run_id,
        "service": args.service,
        "status": summary.audit_status,
        "checks_passed": summary.checks_passed,
        "checks_total": summary.checks_total,
        "started_at": summary.started_at,
        "ended_at": summary.ended_at,
        "duration_ms": summary.duration_ms,
        "sandbox_id": summary.sandbox_id,
        "template_id": summary.template_id,
        "environment": args.dd_env,
        "tags": tags,
        "extra_tags": summary.extra_tags,
        "metadata": summary.metadata,
        "checks": [],
    }
    for result in summary.results:
        if include_full_output:
            payload["checks"].append(result)
        else:
            payload["checks"].append(
                {key: result[key] for key in ("name", "command", "exit_code", "passed", "duration_ms", "error")}
            )
    return payload


def _parse_key_value_pairs(values: Optional[Sequence[str]], field_name: str) -> Dict[str, str]:
    parsed: Dict[str, str] = {}
    for raw in values or []:
        if "=" not in raw:
            raise ValueError(f"{field_name} entries must use key=value format: {raw}")
        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"{field_name} key cannot be empty: {raw}")
        parsed[key] = value
    return parsed


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit an ephemeral E2B sandbox and emit Datadog logs.")
    parser.add_argument("--template-id", default=os.getenv("E2B_TEMPLATE_ID", "python"), help="E2B template to use")
    parser.add_argument(
        "--e2b-timeout",
        default=DEFAULT_TIMEOUT_SECONDS,
        type=int,
        help="Per-command timeout inside sandbox (seconds)",
    )
    parser.add_argument("--e2b-api-key", default=os.getenv("E2B_API_KEY"), help="E2B API key")
    parser.add_argument(
        "--datadog-api-key",
        default=_env_first("DATADOG_API_KEY", "DD_API_KEY"),
        help="Datadog API key used by log intake. Accepts DATADOG_API_KEY or DD_API_KEY.",
    )
    parser.add_argument(
        "--datadog-site",
        default=_env_first("DATADOG_SITE", "DD_SITE", default=DEFAULT_DATADOG_SITE),
        help="Datadog site. Accepts DATADOG_SITE or DD_SITE.",
    )
    parser.add_argument("--service", default=DEFAULT_SERVICE, help="Datadog service tag")
    parser.add_argument("--dd-env", default=os.getenv("DD_ENV", "local"), help="Datadog env tag")
    parser.add_argument(
        "--timeout",
        default=DEFAULT_TIMEOUT_SECONDS,
        type=int,
        help="Global audit timeout (seconds)",
    )
    parser.add_argument(
        "--no-datadog",
        action="store_true",
        help="Run the audit and print JSON without sending logs to Datadog",
    )
    parser.add_argument(
        "--skip-sensitive-redaction",
        action="store_true",
        help="Do not redact env values for local debugging (not recommended)",
    )
    parser.add_argument(
        "--extra-tag",
        action="append",
        default=[],
        help="Additional Datadog tag in key=value format. Can be repeated.",
    )
    parser.add_argument(
        "--metadata",
        action="append",
        default=[],
        help="Additional audit metadata in key=value format. Can be repeated.",
    )
    return parser.parse_args(argv)


def run_audit(args: argparse.Namespace) -> AuditSummary:
    if args.e2b_timeout <= 0:
        raise ValueError("e2b-timeout must be > 0")
    if args.timeout <= 0:
        raise ValueError("timeout must be > 0")

    checks = _build_checks()
    start_time = time.perf_counter()
    started_at = _utc_now_iso()
    run_id = uuid.uuid4().hex
    extra_tags = _parse_key_value_pairs(args.extra_tag, "extra-tag")
    metadata = _parse_key_value_pairs(args.metadata, "metadata")
    passed = 0
    results: List[Dict[str, Any]] = []
    sandbox_id: Optional[str] = None
    end_time = started_at

    try:
        with E2BSandbox(template_id=args.template_id, api_key=args.e2b_api_key, timeout=args.timeout) as e2b:
            sandbox_id = e2b.sandbox_id
            for check_name, command in checks:
                res = _run_sandbox_check(
                    e2b,
                    (check_name, command),
                    min(args.e2b_timeout, args.timeout),
                    redact_sensitive_values=not args.skip_sensitive_redaction,
                )
                if res.passed:
                    passed += 1
                results.append(asdict(res))
            audit_status = "pass" if passed == len(checks) else "fail"
    except Exception as exc:
        audit_status = "fail"
        results.append(
            asdict(
                CheckResult(
                    name="bootstrap",
                    command="sandbox_bootstrap",
                    exit_code=None,
                    passed=False,
                    output="",
                    error_output="",
                    duration_ms=0,
                    error=str(exc),
                )
            )
        )
    finally:
        end_time = _utc_now_iso()

    duration_ms = int((time.perf_counter() - start_time) * 1000)
    return AuditSummary(
        run_id=run_id,
        audit_status=audit_status,
        service=args.service,
        env=args.dd_env,
        sandbox_id=sandbox_id,
        template_id=args.template_id,
        checks_passed=passed,
        checks_total=len(checks),
        started_at=started_at,
        ended_at=end_time,
        duration_ms=duration_ms,
        results=results,
        extra_tags=extra_tags,
        metadata=metadata,
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if not args.e2b_api_key:
        print("Missing E2B_API_KEY (set environment variable or --e2b-api-key).", file=sys.stderr)
        return 2

    summary = run_audit(args)
    payload = _build_payload(summary, args)
    print(_safe_json_dumps({"audit": payload}))

    if args.no_datadog:
        return 0 if summary.audit_status == "pass" else 1

    dd_key = args.datadog_api_key
    if not dd_key:
        print("Missing DATADOG_API_KEY or DD_API_KEY, skipped Datadog emission.", file=sys.stderr)
        return 0 if summary.audit_status == "pass" else 1

    emitter = DatadogEmitter(dd_key, site=args.datadog_site, service=args.service)
    ok, message = emitter.emit_log(summary)
    print(message)
    return 0 if (ok and summary.audit_status == "pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
