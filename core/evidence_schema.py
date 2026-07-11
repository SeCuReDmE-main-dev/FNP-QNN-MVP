"""Versioned evidence record schema and conservative legacy migration."""

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any


EVIDENCE_SCHEMA = "fnp-qnn.education.evidence"
CURRENT_EVIDENCE_VERSION = 1
APPROVAL_STATES = frozenset({"pending", "approved", "rejected", "quarantined"})


@dataclass(frozen=True)
class EvidenceRecord:
    """Canonical evidence record used by local exports and review tooling."""

    record_id: str
    run_id: str
    subject: str
    claim: str
    text: str
    provenance: str
    approval_state: str = "pending"

    def to_dict(self) -> dict[str, Any]:
        """Return the current versioned representation."""

        return {
            "schema": EVIDENCE_SCHEMA,
            "version": CURRENT_EVIDENCE_VERSION,
            **asdict(self),
        }


def _required_text(payload: Mapping[str, Any], field: str, aliases: tuple[str, ...] = ()) -> str:
    for candidate in (field, *aliases):
        value = payload.get(candidate)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise ValueError(f"Evidence field is required: {field}")


def migrate_evidence_payload(payload: Mapping[str, Any]) -> EvidenceRecord:
    """Normalize v0 or v1 evidence without accepting unknown future versions."""

    if not isinstance(payload, Mapping):
        raise TypeError("Evidence payload must be a mapping")
    raw_version = payload.get("version", 0)
    if isinstance(raw_version, bool) or not isinstance(raw_version, int):
        raise ValueError("Evidence version must be an integer")
    if raw_version > CURRENT_EVIDENCE_VERSION:
        raise ValueError(f"Unsupported future evidence version: {raw_version}")
    if raw_version < 0:
        raise ValueError("Evidence version cannot be negative")
    if raw_version == CURRENT_EVIDENCE_VERSION and payload.get("schema") != EVIDENCE_SCHEMA:
        raise ValueError("Evidence schema identifier does not match the current version")

    approval_state = _required_text(payload, "approval_state", ("status",)).lower()
    if approval_state not in APPROVAL_STATES:
        raise ValueError(f"Unsupported evidence approval state: {approval_state}")
    return EvidenceRecord(
        record_id=_required_text(payload, "record_id", ("id",)),
        run_id=_required_text(payload, "run_id", ("experiment_id",)),
        subject=_required_text(payload, "subject"),
        claim=_required_text(payload, "claim"),
        text=_required_text(payload, "text", ("evidence",)),
        provenance=_required_text(payload, "provenance", ("source",)),
        approval_state=approval_state,
    )
