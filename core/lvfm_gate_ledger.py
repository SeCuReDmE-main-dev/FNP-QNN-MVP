"""LVFM gate persistence helpers for deterministic RegisterKey traces."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional
import uuid


def _normalize_payload_metadata(payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    if payload is None:
        return {}
    output: Dict[str, Any] = {}
    for key in ("label", "epochs", "run_qnn"):
        if key in payload:
            output[key] = payload[key]
    if "memories" in payload and isinstance(payload["memories"], list):
        output["input_memories"] = len(payload["memories"])
    if "events" in payload and isinstance(payload["events"], list):
        output["input_events"] = len(payload["events"])
    if "observations" in payload and isinstance(payload["observations"], list):
        output["input_observations"] = len(payload["observations"])
    return output


@dataclass(frozen=True)
class LVFMGateRecord:
    gate_id: str
    sequence_fingerprint: str
    decision: Dict[str, Any]
    compact: Dict[str, Dict[str, float]]
    exact_bits: Dict[str, Dict[str, float]]
    register_keys: Dict[str, Dict[str, Any]]
    created_at: str
    payload_metrics: Dict[str, Any] = field(default_factory=dict)
    source_path: Optional[str] = None

    @classmethod
    def from_snapshot(cls, lvfm_snapshot: Mapping[str, Any], payload: Optional[Mapping[str, Any]] = None) -> "LVFMGateRecord":
        snapshot = lvfm_snapshot.get("snapshot", {})
        compact = snapshot.get("compact", {})
        exact_bits = snapshot.get("exact_bits", {})
        register_keys = snapshot.get("register_keys", {})
        decision = lvfm_snapshot.get("decision", {})
        fingerprint_payload = {"compact": compact, "exact_bits": exact_bits, "decision": decision}
        fingerprint = hashlib.sha256(json.dumps(fingerprint_payload, sort_keys=True).encode("utf-8")).hexdigest()
        created_at = datetime.now(timezone.utc).isoformat()
        gate_id = str(uuid.uuid4())
        payload_metrics = _normalize_payload_metadata(payload)
        return cls(
            gate_id=gate_id,
            sequence_fingerprint=fingerprint,
            decision=dict(decision),
            compact={k: dict(v) for k, v in compact.items()},
            exact_bits={k: dict(v) for k, v in exact_bits.items()},
            register_keys={k: dict(v) for k, v in register_keys.items()},
            created_at=created_at,
            payload_metrics=payload_metrics,
        )

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "gate_id": self.gate_id,
            "sequence_fingerprint": self.sequence_fingerprint,
            "created_at": self.created_at,
            "decision": self.decision,
            "snapshot": {
                "compact": self.compact,
                "exact_bits": self.exact_bits,
                "register_keys": self.register_keys,
            },
            "register_keys": self.register_keys,
            "payload_metrics": self.payload_metrics,
        }
        if self.source_path is not None:
            payload["source_path"] = self.source_path
        return payload


class LVFMGateLedger:
    """Append gate records to a local JSONL trail for audit + deterministic replay."""

    def __init__(self, path: str = "output/lvfm_gate_history.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: LVFMGateRecord) -> LVFMGateRecord:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.to_dict(), ensure_ascii=False))
            handle.write("\n")
        return LVFMGateRecord(
            gate_id=record.gate_id,
            sequence_fingerprint=record.sequence_fingerprint,
            decision=dict(record.decision),
            compact={k: dict(v) for k, v in record.compact.items()},
            exact_bits={k: dict(v) for k, v in record.exact_bits.items()},
            register_keys={k: dict(v) for k, v in record.register_keys.items()},
            created_at=record.created_at,
            payload_metrics=dict(record.payload_metrics),
            source_path=str(self.path.resolve()),
        )

    def recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        if limit <= 0 or not self.path.exists():
            return []
        lines: List[str] = self.path.read_text(encoding="utf-8").splitlines()
        records = []
        for line in lines[-limit:]:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
        return records
