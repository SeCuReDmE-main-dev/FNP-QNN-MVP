"""Read-only glymphatic cleanup scan."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

CACHE_DIR_NAMES = ("__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "build", "dist", ".cache", "tmp", ".tmp")
TUNNEL_PATTERNS = ("e2b_sandbox_", "ngrok_")
QUANTUM_PATTERNS = ("qiskit_session_", "ibmq_session_")
TORCH_PATTERNS = ("torch_worker_",)
ONE_MIB = 1024 * 1024


@dataclass
class Item:
    path: str
    kind: str
    size_bytes: int
    age_days: int
    tag: str


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_filename_timestamp() -> str:
    return utc_now().strftime("%Y-%m-%dT%H-%M-%SZ")


def file_age_days(path: Path, now: datetime) -> int:
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return max(0, int((now - modified).days))


def dir_size_and_count(path: Path) -> tuple[int, int]:
    total_size = 0
    file_count = 0
    for root, _, files in os.walk(path):
        for name in files:
            file_path = Path(root) / name
            try:
                total_size += file_path.stat().st_size
                file_count += 1
            except OSError:
                continue
    return total_size, file_count


def classify_filename(path: Path) -> tuple[str, str] | None:
    name = path.name
    if any(name.startswith(prefix) and name.endswith(".json") for prefix in TUNNEL_PATTERNS):
        return ("tunnel_artifact", "safe-to-close")
    if any(name.startswith(prefix) and name.endswith(".json") for prefix in QUANTUM_PATTERNS):
        return ("quantum_session", "human-only")
    if any(name.startswith(prefix) and name.endswith(".pid") for prefix in TORCH_PATTERNS):
        return ("torch_worker", "human-only")
    return None


def scan(root: Path) -> dict:
    now = utc_now()
    items: list[Item] = []
    seen_cache_dirs: set[Path] = set()

    for current_root, dirs, files in os.walk(root):
        current_path = Path(current_root)
        for dirname in dirs:
            if dirname in CACHE_DIR_NAMES:
                cache_dir = current_path / dirname
                if cache_dir not in seen_cache_dirs:
                    seen_cache_dirs.add(cache_dir)
                    size_bytes, file_count = dir_size_and_count(cache_dir)
                    items.append(
                        Item(
                            path=str(cache_dir.relative_to(root)).replace("\\", "/"),
                            kind="cache_dir",
                            size_bytes=size_bytes,
                            age_days=file_count,
                            tag="safe-to-close",
                        )
                    )

        for filename in files:
            file_path = current_path / filename
            relative = str(file_path.relative_to(root)).replace("\\", "/")
            try:
                stat = file_path.stat()
            except OSError as exc:
                raise OSError(f"filesystem error while scanning {file_path}") from exc

            if file_path.suffix == ".log" and stat.st_size > ONE_MIB:
                items.append(Item(path=relative, kind="log_file", size_bytes=stat.st_size, age_days=0, tag="safe-to-close"))

            if relative.startswith("reports/") and file_path.suffix == ".json":
                age_days = file_age_days(file_path, now)
                if age_days > 30:
                    items.append(Item(path=relative, kind="old_report", size_bytes=stat.st_size, age_days=age_days, tag="confirm-required"))

            classified = classify_filename(file_path)
            if classified:
                kind, tag = classified
                age_days = file_age_days(file_path, now)
                items.append(Item(path=relative, kind=kind, size_bytes=stat.st_size, age_days=age_days, tag=tag))

    safe_to_close = sum(1 for item in items if item.tag == "safe-to-close")
    confirm_required = sum(1 for item in items if item.tag == "confirm-required")
    human_only = sum(1 for item in items if item.tag == "human-only")
    generated_at = utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "agent": "SeCuReDmE SPOFRE E2B Gate",
        "mode": "glymphatic_cleanup",
        "phase": "SCAN",
        "triggered_by": "user_request",
        "service": "fnp-qnn-local-research-simulator",
        "boundary": "alpha-local, non-clinical, educational/research simulator",
        "generated_at_utc": generated_at,
        "items": [
            {
                "path": item.path,
                "kind": item.kind,
                "size_bytes": item.size_bytes,
                "age_days": item.age_days,
                "tag": item.tag,
            }
            for item in items
        ],
        "summary": {
            "scanned_items": len(items),
            "safe_to_close": safe_to_close,
            "confirm_required": confirm_required,
            "human_only": human_only,
            "auto_cleaned_items": 0,
            "pending_human_approval_items": confirm_required + human_only,
            "estimated_cost_avoided": "n/a",
        },
        "notes": [
            "Read-only SCAN. No process killed. No file deleted. No network call.",
            "Destructive actions require human-in-the-loop approval outside this script.",
        ],
    }


def write_report(root: Path, report: dict) -> Path:
    report_dir = root / "reports" / "glymphatic"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"scan-{iso_filename_timestamp()}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Root directory to scan.")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    try:
        report = scan(root)
        report_path = write_report(root, report)
    except OSError as exc:
        print(f"FAIL: {exc}")
        return 1

    summary = report["summary"]
    print(
        "SCAN OK:",
        f"items={summary['scanned_items']}",
        f"safe_to_close={summary['safe_to_close']}",
        f"confirm_required={summary['confirm_required']}",
        f"human_only={summary['human_only']}",
        f"report={report_path.relative_to(root)}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
