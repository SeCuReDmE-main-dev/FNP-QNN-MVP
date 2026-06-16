"""Validate provenance, boundary, and forbidden-claim policy."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NEGATION_MARKERS = ("not", "no ", "never", "is not", "are not", "non-", "non ", "without")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def pass_line(message: str) -> None:
    print(f"PASS: {message}")


def fail_line(message: str) -> None:
    print(f"FAIL: {message}")


def iter_scan_targets(root: Path, entries: list[str]) -> list[Path]:
    targets: list[Path] = []
    seen: set[Path] = set()
    for entry in entries:
        path = root / entry
        if not path.exists():
            continue
        if path.is_file():
            if path not in seen:
                seen.add(path)
                targets.append(path)
            continue
        for child in path.rglob("*"):
            if child.is_file() and child not in seen:
                seen.add(child)
                targets.append(child)
    return targets


def contains_orcid(text: str, orcid: str) -> bool:
    normalized_text = re.sub(r"[^0-9X]", "", text.upper())
    normalized_orcid = re.sub(r"[^0-9X]", "", orcid.upper())
    return normalized_orcid in normalized_text


def sentence_has_forbidden_claim(text: str, phrase: str) -> bool:
    for sentence in SENTENCE_SPLIT_RE.split(text):
        lowered = sentence.lower()
        idx = lowered.find(phrase.lower())
        if idx == -1:
            continue
        prefix = lowered[:idx]
        if any(marker in prefix for marker in NEGATION_MARKERS):
            continue
        return True
    return False


def check_required_files(policy: dict) -> bool:
    missing = [path for path in policy["required_files"] if not (ROOT / path).exists()]
    if missing:
        fail_line(f"required files missing: {missing}")
        return False
    pass_line("required files exist")
    return True


def check_required_orcid(policy: dict) -> bool:
    missing_orcid: list[str] = []
    for relative_path in policy["required_orcid_in"]:
        path = ROOT / relative_path
        if not path.exists() or not contains_orcid(read_text(path), policy["maintainer_orcid"]):
            missing_orcid.append(relative_path)
    if missing_orcid:
        fail_line(f"ORCID provenance missing in: {missing_orcid}")
        return False
    pass_line("ORCID provenance present in required files")
    return True


def check_boundary_phrases(policy: dict) -> bool:
    phrases = [phrase.lower() for phrase in policy["required_boundary_phrases_any_of"]]
    for relative_path in policy["boundary_files_any_of"]:
        path = ROOT / relative_path
        if not path.exists():
            continue
        text = read_text(path).lower()
        if any(phrase in text for phrase in phrases):
            pass_line(f"boundary phrase found in {relative_path}")
            return True
    fail_line("no boundary phrase found in configured boundary files")
    return False


def check_forbidden_claims(policy: dict) -> bool:
    hits: list[str] = []
    for path in iter_scan_targets(ROOT, policy["scan_files"]):
        text = read_text(path)
        for phrase in policy["forbidden_positive_claims"]:
            if sentence_has_forbidden_claim(text, phrase):
                hits.append(f"{path.relative_to(ROOT)}: {phrase}")
    if hits:
        fail_line("forbidden positive claims detected")
        for hit in hits:
            print(f"FAIL: {hit}")
        return False
    pass_line("no forbidden positive claims detected")
    return True


def main() -> int:
    policy = json.loads(read_text(ROOT / "LICENSE_POLICY.json"))
    checks = [
        check_required_files(policy),
        check_required_orcid(policy),
        check_boundary_phrases(policy),
        check_forbidden_claims(policy),
    ]
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
