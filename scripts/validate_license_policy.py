"""Validate provenance, boundary, and risky-claim policy for public-facing artifacts."""

from __future__ import annotations

import json
import pathlib
import re
import sys
from typing import Dict, Iterable, List


PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _collect_scan_files(patterns: Iterable[str], root: pathlib.Path) -> List[pathlib.Path]:
    files: List[pathlib.Path] = []
    for pattern in patterns:
        for candidate in root.glob(pattern):
            if candidate.is_file():
                files.append(candidate)
    return files


def _normalize(text: str) -> str:
    return re.sub(r"[^0-9A-Za-z]", "", text).lower()


def _normalize_orcid(text: str) -> str:
    return re.sub(r"[^0-9X]", "", text.upper())


def _contains_orcid(text: str, orcid: str) -> bool:
    return _normalize_orcid(orcid) in _normalize_orcid(text)


def _contains_phrases(text: str, phrases: Iterable[str]) -> bool:
    lowered = text.lower()
    return all(phrase.lower() in lowered for phrase in phrases)


def _scan_for_risky_text(text: str, risks: Iterable[str]) -> List[str]:
    found: List[str] = []
    negation_tokens = (
        "not ",
        " no ",
        "without ",
        "never ",
        "avoid ",
        "avoidances ",
        "non ",
        "non-",
        "no-",
        "must not",
        "should not",
        "do not",
    )
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        lowered = line.lower()
        for risk in risks:
            if risk in lowered:
                context = " ".join(lines[max(0, idx - 8) : idx + 8]).lower()
                if any(token in context for token in negation_tokens):
                    continue
                found.append(risk)
    return found


def _validate_paths(policy: Dict[str, List[str]], root: pathlib.Path) -> bool:
    missing = [path for path in policy["required_files"] if not (root / path).exists()]
    if missing:
        for path in missing:
            print(f"Missing required file: {path}")
        return False
    return True


def _validate_orcid(policy: Dict[str, List[str]], root: pathlib.Path, orcid: str) -> bool:
    failures = []
    for path in policy["required_orcid_files"]:
        file_path = root / path
        if not file_path.exists():
            failures.append(path)
            continue
        if not _contains_orcid(_read_text(file_path), orcid):
            failures.append(path)
    if failures:
        print("ORCID check failed for:")
        for path in failures:
            print(f"- {path}")
        print("Expected ORCID:", orcid)
        return False
    return True


def _validate_readme_orcid(policy: Dict[str, List[str]], root: pathlib.Path, orcid: str) -> bool:
    del policy
    readme = _read_text(root / "README.md")
    if not _contains_orcid(readme, orcid):
        print("ORCID not found in README.md:", orcid)
        return False
    return True


def _validate_boundary(policy: Dict[str, List[str]], root: pathlib.Path) -> bool:
    phrases = policy["required_boundary_phrases"]
    readme = _read_text(root / "README.md")
    security = _read_text(root / "SECURITY_MODEL.md") if (root / "SECURITY_MODEL.md").exists() else ""
    if not (_contains_phrases(readme, phrases) or _contains_phrases(security, phrases)):
        print("Boundary validation failed: required phrases not found in README.md or SECURITY_MODEL.md.")
        return False
    return True


def _validate_risk_phrases(policy: Dict[str, List[str]], root: pathlib.Path) -> bool:
    risky = [risk.lower() for risk in policy["risky_phrases"]]
    seen: List[str] = []
    for file_path in _collect_scan_files(policy["scan_public_docs"], root):
        text = _read_text(file_path).lower()
        for hit in _scan_for_risky_text(text, risky):
            line = f"{file_path}: {hit}"
            if line not in seen:
                seen.append(line)
    if seen:
        print("Risky phrases detected:")
        for hit in seen:
            print(f"- {hit}")
        return False
    return True


def main() -> int:
    policy_path = PROJECT_ROOT / "LICENSE_POLICY.json"
    policy = json.loads(_read_text(policy_path))

    orcid = policy["maintainer_orcid"]
    ok = True
    ok &= _validate_paths(policy, PROJECT_ROOT)
    ok &= _validate_orcid(policy, PROJECT_ROOT, orcid)
    ok &= _validate_readme_orcid(policy, PROJECT_ROOT, orcid)
    ok &= _validate_boundary(policy, PROJECT_ROOT)
    ok &= _validate_risk_phrases(policy, PROJECT_ROOT)

    if ok:
        print("LICENSE_POLICY validation: PASS")
        return 0

    print("LICENSE_POLICY validation: FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
