"""Redacted JSON and Markdown exports for human education review."""

import json
from collections.abc import Iterable, Mapping
from typing import Any

from core.education_run_contract import EducationRunContract


EXPORT_SCHEMA = "fnp-qnn.education.review-export"
EXPORT_VERSION = 1
REDACTION_MARKER = "[REDACTED]"
SENSITIVE_KEY_MARKERS = (
    "api_key",
    "app_key",
    "authorization",
    "password",
    "private_key",
    "secret",
    "token",
)
PRIVATE_VALUE_MARKERS = ("c:\\users\\", "/home/", "begin private key", ".env")


def _sensitive_key(key: object) -> bool:
    normalized = str(key).lower().replace("-", "_")
    return any(marker in normalized for marker in SENSITIVE_KEY_MARKERS)


def redact_for_export(value: Any) -> Any:
    """Recursively redact sensitive keys and private-path-like string values."""

    if isinstance(value, Mapping):
        return {
            key: REDACTION_MARKER if _sensitive_key(key) else redact_for_export(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact_for_export(item) for item in value]
    if isinstance(value, str) and any(marker in value.lower() for marker in PRIVATE_VALUE_MARKERS):
        return REDACTION_MARKER
    return value


def build_redacted_review_export(
    run: EducationRunContract,
    evidence_records: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build a versioned export without mutating the source records."""

    if not isinstance(run, EducationRunContract):
        raise TypeError("run must be an EducationRunContract")
    evidence = [redact_for_export(record) for record in evidence_records]
    return {
        "schema": EXPORT_SCHEMA,
        "version": EXPORT_VERSION,
        "redaction_policy": "sensitive-keys-and-private-paths-v1",
        "run": redact_for_export(run.to_dict()),
        "evidence": evidence,
    }


def export_review_json(export: Mapping[str, Any]) -> str:
    """Serialize an already-redacted export deterministically."""

    return json.dumps(export, sort_keys=True, separators=(",", ":"))


def _markdown_value(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ").strip()


def render_review_markdown(export: Mapping[str, Any]) -> str:
    """Render a concise, redacted human-review record."""

    run = export["run"]
    progress = run["progress"]
    review = run["review"]
    lines = [
        "# FNP-QNN Education Review",
        "",
        f"- Lab: `{_markdown_value(run['lab_id'])}`",
        f"- Seed: `{_markdown_value(review['seed'])}`",
        f"- Progress: `{_markdown_value(progress['state'])}` ({_markdown_value(progress['percent_complete'])}%)",
        f"- Export status: `{_markdown_value(review['export_status'])}`",
        f"- Human review required: `{_markdown_value(review['human_review_required'])}`",
        "",
        "## Trace labels",
        "",
    ]
    lines.extend(f"- {_markdown_value(label)}" for label in review["trace_labels"])
    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            _markdown_value(review["claim_boundary"]),
            "",
            f"Evidence records: `{len(export['evidence'])}`",
        ]
    )
    return "\n".join(lines) + "\n"
