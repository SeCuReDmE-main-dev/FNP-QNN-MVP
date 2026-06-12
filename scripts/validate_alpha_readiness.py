"""Validate the alpha-local readiness gate."""

from __future__ import annotations

import importlib
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "pyproject.toml",
    "requirements.txt",
    ".gitignore",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "docs/alpha-readiness.md",
    ".github/workflows/ci.yml",
]

CLAIM_PATTERNS = [
    "revolutionary medical ai",
    "mission accomplished",
    "medical cure",
    "cure algorithm",
    "recovery achieved",
    "life-saving capability",
    "therapeutic frequency",
    "parkinson's disease cure",
]

SCAN_PATHS = ["README.md", "api", "core", "examples"]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def pass_line(message: str) -> None:
    print(f"PASS: {message}")


def check_required_files() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        fail(f"missing required files: {missing}")
    pass_line("required alpha files exist")


def check_no_public_shell() -> None:
    api_main = (ROOT / "api" / "main.py").read_text(encoding="utf-8").lower()
    forbidden = ["subprocess.run", "shell=true", "os.system", "popen("]
    hits = [item for item in forbidden if item in api_main]
    if hits:
        fail(f"public API contains shell execution markers: {hits}")
    pass_line("public API has no shell execution markers")


def check_claim_language() -> None:
    hits: list[str] = []
    for scan_path in SCAN_PATHS:
        path = ROOT / scan_path
        files = [path] if path.is_file() else [item for item in path.rglob("*") if item.is_file()]
        for file_path in files:
            if file_path.suffix.lower() not in {".py", ".md", ".txt"}:
                continue
            text = file_path.read_text(encoding="utf-8", errors="ignore").lower()
            for pattern in CLAIM_PATTERNS:
                if pattern in text:
                    hits.append(f"{file_path.relative_to(ROOT)}: {pattern}")
    if hits:
        fail("claim boundary violations: " + "; ".join(hits))
    pass_line("public claim boundary is clean")


def check_imports() -> None:
    sys.path.insert(0, str(ROOT))
    for module_name in ["api.main", "api.schemas", "core.cerebrum_adapter", "core.cerebrum_runtime_bridge", "core.qnn_nucleus"]:
        importlib.import_module(module_name)
    pass_line("core/API imports are valid")


def check_tests() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        fail("unit tests failed")
    pass_line("unit tests pass")


def main() -> None:
    check_required_files()
    check_no_public_shell()
    check_claim_language()
    check_imports()
    check_tests()
    pass_line("alpha-local readiness gate complete")


if __name__ == "__main__":
    main()
