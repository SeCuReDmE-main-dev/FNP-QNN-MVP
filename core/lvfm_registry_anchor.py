"""Windows Registry anchoring for LVFM gate decisions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping
import json
import uuid

try:
    import winreg  # type: ignore
except ImportError:  # pragma: no cover
    winreg = None  # type: ignore


REGISTRY_BASE_KEY = "Software\\SeCuReDmE\\LVFM"
DEFAULT_LOCK_THRESHOLD = -0.10
REGISTRY_HISTORY_SCHEMA_VERSION = "lvfm.registry.history.v1"
DEFAULT_HISTORY_PATH = "output/lvfm_registry_history.jsonl"


def _build_registry_payload(gate: Mapping[str, Any]) -> Dict[str, Any]:
    decision = gate.get("decision", {})
    snapshot = gate.get("snapshot", {})
    exact_bits = snapshot.get("exact_bits", {})
    register_keys = snapshot.get("register_keys", {})

    node_ids = sorted(set(exact_bits) | set(register_keys))
    bit_table = []
    for node_id in node_ids:
        exact = exact_bits.get(node_id, {})
        register_entry = register_keys.get(node_id, {})
        metadata = register_entry.get("metadata", {})
        register_weight = register_entry.get("bit", {}).get("register_weight")
        if register_weight is None:
            register_weight = register_entry.get("register_weight", 1.0)

        bit_table.append(
            {
                "node_id": node_id,
                "T": float(exact.get("T", 0.0)),
                "I": float(exact.get("I", 0.0)),
                "dF": float(exact.get("dF", 0.0)),
                "F": float(exact.get("F", 0.0)),
                "register_weight": float(register_weight),
                "metadata": dict(metadata),
            }
        )

    return {
        "schema_version": REGISTRY_HISTORY_SCHEMA_VERSION,
        "gate_id": str(gate.get("gate_id", "")),
        "sequence_fingerprint": str(gate.get("sequence_fingerprint", "")),
        "created_at": str(gate.get("created_at", "")),
        "lock_score": float(decision.get("lock_score", 0.0)),
        "lock_reason": str(decision.get("lock_reason", "")),
        "t_mass": float(decision.get("t_mass", 0.0)),
        "i_mass": float(decision.get("i_mass", 0.0)),
        "dF_mass": float(decision.get("dF_mass", 0.0)),
        "f_mass": float(decision.get("f_mass", 0.0)),
        "trace_line": str(decision.get("trace_line", "")),
        "bit_table": bit_table,
    }


def _append_registry_history(
    gate: Mapping[str, Any],
    registry_payload: Mapping[str, Any],
    lock: Mapping[str, Any],
    registry_subkey: str,
    history_path: str,
) -> Dict[str, Any]:
    history_file = Path(history_path)
    history_file.parent.mkdir(parents=True, exist_ok=True)
    event_id = str(uuid.uuid4())
    event_written_at = datetime.now(timezone.utc).isoformat()
    event = {
        "schema_version": REGISTRY_HISTORY_SCHEMA_VERSION,
        "event_id": event_id,
        "event_written_at": event_written_at,
        "registry_subkey": registry_subkey,
        "gate_id": str(gate.get("gate_id", "")),
        "sequence_fingerprint": str(gate.get("sequence_fingerprint", "")),
        "created_at": str(gate.get("created_at", "")),
        "decision": dict(gate.get("decision", {})),
        "snapshot": dict(gate.get("snapshot", {})),
        "payload_metrics": dict(gate.get("payload_metrics", {})),
        "registry_payload": dict(registry_payload),
        "lock_state": {
            "locked": bool(lock.get("locked")),
            "score": float(lock.get("score", 0.0)),
            "lock_reason": str(lock.get("lock_reason", "")),
        },
    }
    with history_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True))
        handle.write("\n")
    return {
        "schema_version": REGISTRY_HISTORY_SCHEMA_VERSION,
        "event_id": event_id,
        "history_path": str(history_file.resolve()),
        "event_written_at": event_written_at,
    }


def compute_lock_state(decision: Mapping[str, Any], threshold: float = DEFAULT_LOCK_THRESHOLD) -> Dict[str, Any]:
    confidence = float(decision.get("confidence", 0.0) or 0.0)
    verdict = str(decision.get("verdict", "hold")).lower()
    i_mass = float(decision.get("i_mass", 0.0) or 0.0)
    f_mass = float(decision.get("f_mass", 0.0) or 0.0)
    d_f_mass = float(decision.get("dF_mass", i_mass) or i_mass)
    t_mass = float(decision.get("t_mass", confidence + f_mass) or 0.0)
    score = max(-1.0, min(1.0, (t_mass - i_mass + d_f_mass) / 2.0))
    locked = verdict != "allow" or score < threshold or f_mass > 0.75 or i_mass > 0.95
    lock_reason = (
        "verdict_disallow"
        if verdict != "allow"
        else "low_confidence"
        if score < threshold
        else "high_f_mass"
        if f_mass > 0.75
        else "high_i_mass"
        if i_mass > 0.95
        else "none"
    )
    return {"locked": bool(locked), "score": score, "lock_reason": lock_reason}


@dataclass(frozen=True)
class RegistryAnchoringResult:
    key_path: str
    published: bool
    locked: bool
    score: float
    lock_reason: str
    schema_version: str
    history_path: str
    history_event_id: str
    history_written_at: str
    error: str | None = None


def publish_gate_state(
    gate: Mapping[str, Any],
    registry_subkey: str = REGISTRY_BASE_KEY,
    threshold: float = DEFAULT_LOCK_THRESHOLD,
    history_path: str = DEFAULT_HISTORY_PATH,
) -> RegistryAnchoringResult:
    decision = gate.get("decision", {})
    lock = compute_lock_state(decision, threshold=threshold)
    lock_score = int((lock["score"] + 1.0) * 500)
    registry_payload = _build_registry_payload(gate)
    history_state = _append_registry_history(
        gate=gate,
        registry_payload=registry_payload,
        lock=lock,
        registry_subkey=registry_subkey,
        history_path=history_path,
    )

    if winreg is None:
        return RegistryAnchoringResult(
            key_path=registry_subkey,
            published=False,
            locked=bool(lock["locked"]),
            score=float(lock["score"]),
            lock_reason=str(lock["lock_reason"]),
            schema_version=history_state["schema_version"],
            history_path=history_state["history_path"],
            history_event_id=history_state["event_id"],
            history_written_at=history_state["event_written_at"],
            error="winreg module unavailable on this platform",
        )

    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, registry_subkey) as reg_key:
            winreg.SetValueEx(reg_key, "GateId", 0, winreg.REG_SZ, str(gate.get("gate_id", "")))
            winreg.SetValueEx(reg_key, "SequenceFingerprint", 0, winreg.REG_SZ, str(gate.get("sequence_fingerprint", "")))
            winreg.SetValueEx(reg_key, "Verdict", 0, winreg.REG_SZ, str(decision.get("verdict", "")))
            winreg.SetValueEx(reg_key, "DecisionConfidence", 0, winreg.REG_DWORD, max(0, min(65535, lock_score)))
            winreg.SetValueEx(reg_key, "LockScoreRaw", 0, winreg.REG_SZ, str(lock["score"]))
            winreg.SetValueEx(reg_key, "LockState", 0, winreg.REG_DWORD, 1 if lock["locked"] else 0)
            winreg.SetValueEx(reg_key, "LockReason", 0, winreg.REG_SZ, str(lock["lock_reason"]))
            winreg.SetValueEx(reg_key, "CreatedAt", 0, winreg.REG_SZ, str(gate.get("created_at", "")))
            winreg.SetValueEx(reg_key, "LockScore", 0, winreg.REG_DWORD, max(0, min(65535, int((lock["score"] + 1.0) * 500))))
            winreg.SetValueEx(reg_key, "TiDfLockScore", 0, winreg.REG_DWORD, max(0, min(65535, int((float(lock["score"]) + 1.0) * 500))))
            winreg.SetValueEx(reg_key, "TiDfRaw", 0, winreg.REG_SZ, str(lock["score"]))
            exact_bits = gate.get("snapshot", {}).get("exact_bits", {})
            exact_bits_json = json.dumps(exact_bits, sort_keys=True, ensure_ascii=False)
            compact = gate.get("snapshot", {}).get("compact", {})
            compact_json = json.dumps(compact, sort_keys=True, ensure_ascii=False)
            register_keys = gate.get("snapshot", {}).get("register_keys", {})
            register_keys_json = json.dumps(register_keys, sort_keys=True, ensure_ascii=False)
            decision = gate.get("decision", {})
            metrics = gate.get("payload_metrics", {})
            winreg.SetValueEx(reg_key, "ExactBitsJson", 0, winreg.REG_SZ, exact_bits_json)
            winreg.SetValueEx(reg_key, "CompactJson", 0, winreg.REG_SZ, compact_json)
            winreg.SetValueEx(reg_key, "RegisterKeysJson", 0, winreg.REG_SZ, register_keys_json)
            winreg.SetValueEx(reg_key, "BitTableJson", 0, winreg.REG_SZ, json.dumps(registry_payload["bit_table"], ensure_ascii=False, sort_keys=True))
            winreg.SetValueEx(reg_key, "TraceLine", 0, winreg.REG_SZ, str(decision.get("trace_line", "")))
            winreg.SetValueEx(reg_key, "RegistryPayloadJson", 0, winreg.REG_SZ, json.dumps(registry_payload, ensure_ascii=False, sort_keys=True))
            winreg.SetValueEx(reg_key, "DecisionJson", 0, winreg.REG_SZ, json.dumps(decision, sort_keys=True))
            winreg.SetValueEx(reg_key, "PayloadMetricsJson", 0, winreg.REG_SZ, json.dumps(metrics, sort_keys=True))
            winreg.SetValueEx(reg_key, "RegistrySchemaVersion", 0, winreg.REG_SZ, history_state["schema_version"])
            winreg.SetValueEx(reg_key, "HistoryEventId", 0, winreg.REG_SZ, history_state["event_id"])
            winreg.SetValueEx(reg_key, "HistoryPath", 0, winreg.REG_SZ, history_state["history_path"])
            winreg.SetValueEx(reg_key, "HistoryWrittenAt", 0, winreg.REG_SZ, history_state["event_written_at"])

        return RegistryAnchoringResult(
            key_path=f"HKCU\\{registry_subkey}",
            published=True,
            locked=bool(lock["locked"]),
            score=float(lock["score"]),
            lock_reason=str(lock["lock_reason"]),
            schema_version=history_state["schema_version"],
            history_path=history_state["history_path"],
            history_event_id=history_state["event_id"],
            history_written_at=history_state["event_written_at"],
        )
    except OSError as exc:  # pragma: no cover
        return RegistryAnchoringResult(
            key_path=f"HKCU\\{registry_subkey}",
            published=False,
            locked=bool(lock["locked"]),
            score=float(lock["score"]),
            lock_reason=str(lock["lock_reason"]),
            schema_version=history_state["schema_version"],
            history_path=history_state["history_path"],
            history_event_id=history_state["event_id"],
            history_written_at=history_state["event_written_at"],
            error=f"registry_write_failed: {exc}",
        )
