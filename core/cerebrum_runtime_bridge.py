"""
Runtime bridge for Cerebrum-shaped memory streams.

The original Cerebrum package is kept isolated because it is a Python 2 era
runtime with RethinkDB, audio, and GUI dependencies. This bridge implements the
portable contract the simulator needs: interval memories, crossmodal overlap
pairs, feature bundles, and QNN-ready observations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
from importlib.util import find_spec
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from .cerebrum_adapter import CerebrumAdapter, CerebrumFeatureBundle, MODALITIES
from .qnn_nucleus import QNNNucleus


MODALITY_ALIASES = {
    "hearing": "audio",
    "audio": "audio",
    "h": "audio",
    "vision": "video",
    "visual": "video",
    "video": "video",
    "v": "video",
    "language": "text",
    "caption": "text",
    "captions": "text",
    "text": "text",
    "l": "text",
    "stimulus": "stimuli",
    "stimuli": "stimuli",
    "s": "stimuli",
}

PAIR_CODE = {"audio": "H", "video": "V", "text": "L", "stimuli": "S"}
COLLECTION_MODALITIES = {
    "hearing_memory": "audio",
    "hearing": "audio",
    "audio": "audio",
    "vision_memory": "video",
    "vision": "video",
    "video": "video",
    "language_memory": "text",
    "language": "text",
    "text": "text",
    "stimuli": "stimuli",
    "stimulus": "stimuli",
}

PAIR_DIRECTION_ALIASES = {
    "H2V": ("audio", "video"),
    "V2H": ("video", "audio"),
    "H2L": ("audio", "text"),
    "L2H": ("text", "audio"),
    "V2L": ("video", "text"),
    "L2V": ("text", "video"),
}

LEGACY_TABLE_MODALITIES = {
    "hearing_timestamps": "audio",
    "vision_timestamps": "video",
    "language_timestamps": "text",
    "stimuli_timestamps": "stimuli",
}


@dataclass(frozen=True)
class CerebrumMemoryEvent:
    modality: str
    starting_time: float
    ending_time: float
    value: float
    source: str = ""
    label: str = ""
    payload_ref: str = ""
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return max(0.0, self.ending_time - self.starting_time)

    def to_observation(self) -> Dict[str, Any]:
        return {
            "modality": self.modality,
            "value": self.value,
            "timestamp": self.starting_time,
            "ending_time": self.ending_time,
            "weight": max(self.duration, 1.0),
            "label": self.label,
            "source": self.source,
            "payload_ref": self.payload_ref,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "modality": self.modality,
            "starting_time": self.starting_time,
            "ending_time": self.ending_time,
            "duration": self.duration,
            "value": self.value,
            "source": self.source,
            "label": self.label,
            "payload_ref": self.payload_ref,
            "provenance": self.provenance,
        }


@dataclass(frozen=True)
class CrossModalPair:
    timestamp1: float
    timestamp2: float
    direction: str
    source_modality: str
    target_modality: str
    overlap_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp1": self.timestamp1,
            "timestamp2": self.timestamp2,
            "direction": self.direction,
            "source_modality": self.source_modality,
            "target_modality": self.target_modality,
            "overlap_score": self.overlap_score,
        }


@dataclass
class CerebrumRuntimeState:
    events: List[CerebrumMemoryEvent]
    pairs: List[CrossModalPair]
    observations: List[Dict[str, Any]]
    feature_bundle: CerebrumFeatureBundle
    feature_vector: np.ndarray
    qnn_result: Optional[Dict[str, Any]] = None
    warnings: List[str] = field(default_factory=list)

    def to_dict(self, include_bundle: bool = True) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "events": [event.to_dict() for event in self.events],
            "pairs": [pair.to_dict() for pair in self.pairs],
            "observations": self.observations,
            "feature_vector": self.feature_vector.tolist(),
            "feature_dimension": int(self.feature_vector.shape[0]),
            "qnn_result": self.qnn_result,
            "warnings": self.warnings,
        }
        if include_bundle:
            payload["bundle"] = {
                "sequence_length": self.feature_bundle.sequence_length,
                "summary": self.feature_bundle.summary,
                "modality_counts": self.feature_bundle.modality_counts,
                "modality_means": self.feature_bundle.modality_means,
                "modality_stds": self.feature_bundle.modality_stds,
                "transition_matrix": self.feature_bundle.transition_matrix.tolist(),
            }
        return payload


class CerebrumRuntimeBridge:
    """Normalize Cerebrum-shaped memory intervals and run the simulator path."""

    def __init__(
        self,
        adapter: Optional[CerebrumAdapter] = None,
        legacy_cerebrum_path: Optional[str] = None,
    ):
        self.adapter = adapter or CerebrumAdapter()
        self.legacy_cerebrum_path = Path(legacy_cerebrum_path) if legacy_cerebrum_path else None

    def status(self, qnn_nucleus: Optional[QNNNucleus] = None) -> Dict[str, Any]:
        optional_modules = {
            "rethinkdb": find_spec("rethinkdb") is not None,
            "pyaudio": find_spec("pyaudio") is not None,
            "cv2": find_spec("cv2") is not None,
            "hpelm": find_spec("hpelm") is not None,
        }
        qnn_backend = "not-attached"
        if qnn_nucleus is not None:
            fallback = next((item for item in qnn_nucleus.candidate_matrix() if item.name == "torch_surrogate"), None)
            primary = next((item for item in qnn_nucleus.candidate_matrix() if item.role == "primary"), None)
            qnn_backend = primary.backend if primary and primary.available else fallback.backend if fallback else "unknown"
        return {
            "status": "ok",
            "bridge": "operational",
            "supported_modalities": list(MODALITIES),
            "supported_pair_directions": ["H2V", "V2H", "H2L", "L2H", "V2L", "L2V"],
            "legacy_cerebrum_path": str(self.legacy_cerebrum_path) if self.legacy_cerebrum_path else None,
            "legacy_cerebrum_path_exists": bool(self.legacy_cerebrum_path and self.legacy_cerebrum_path.exists()),
            "optional_dependency_available": optional_modules,
            "qnn_backend": qnn_backend,
        }

    def ingest(self, payload: Mapping[str, Any] | Sequence[Any] | None) -> Tuple[List[CerebrumMemoryEvent], List[CrossModalPair], List[str]]:
        warnings: List[str] = []
        records = self._extract_records(payload, warnings)
        parsed = [self._parse_record(record, index, warnings) for index, record in enumerate(records)]
        events = self._normalize_event_times([event for event in parsed if event is not None])
        pairs = self._extract_pairs(payload, events, warnings)
        if not events:
            warnings.append("No runtime memory events were provided.")
        return events, pairs, warnings

    def build_state(
        self,
        payload: Mapping[str, Any] | Sequence[Any] | None,
        qnn_nucleus: Optional[QNNNucleus] = None,
        label: float = 1.0,
        max_epochs: int = 12,
    ) -> CerebrumRuntimeState:
        events, pairs, warnings = self.ingest(payload)
        observations = [event.to_observation() for event in events]
        bundle = self.adapter.build_bundle(observations)
        vector = self.adapter.bundle_to_vector(bundle)
        qnn_result = None
        if qnn_nucleus is not None:
            qnn_result = qnn_nucleus.smoke_run(observations, label=label, max_epochs=max_epochs, test_size=0.0)
            qnn_result.pop("bundle", None)
        return CerebrumRuntimeState(
            events=events,
            pairs=pairs,
            observations=observations,
            feature_bundle=bundle,
            feature_vector=vector,
            qnn_result=qnn_result,
            warnings=warnings,
        )

    def build_pairs(self, events: Sequence[CerebrumMemoryEvent]) -> List[CrossModalPair]:
        pairs: List[CrossModalPair] = []
        for left_index, left in enumerate(events):
            for right in events[left_index + 1 :]:
                if left.modality == right.modality:
                    continue
                overlap_score = self._overlap_score(left, right)
                if overlap_score <= 0.0:
                    continue
                pairs.append(self._pair(left, right, overlap_score))
                pairs.append(self._pair(right, left, overlap_score))
        return sorted(pairs, key=lambda pair: (pair.timestamp1, pair.direction, pair.timestamp2))

    def _pair(self, source: CerebrumMemoryEvent, target: CerebrumMemoryEvent, overlap_score: float) -> CrossModalPair:
        direction = f"{PAIR_CODE[source.modality]}2{PAIR_CODE[target.modality]}"
        return CrossModalPair(
            timestamp1=source.starting_time,
            timestamp2=target.starting_time,
            direction=direction,
            source_modality=source.modality,
            target_modality=target.modality,
            overlap_score=overlap_score,
        )

    def _extract_records(self, payload: Mapping[str, Any] | Sequence[Any] | None, warnings: List[str]) -> List[Mapping[str, Any]]:
        if payload is None:
            if self.legacy_cerebrum_path is not None:
                legacy_records = self._load_legacy_snapshot(self.legacy_cerebrum_path, warnings=warnings)
                if legacy_records:
                    return legacy_records
            return self.default_payload()["memories"]
        if isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray, Mapping)):
            return [record if isinstance(record, Mapping) else {"value": record} for record in payload]
        if not isinstance(payload, Mapping):
            return [{"value": payload}]

        if "memories" in payload:
            return [record if isinstance(record, Mapping) else {"value": record} for record in payload.get("memories", [])]
        if "events" in payload:
            return [record if isinstance(record, Mapping) else {"value": record} for record in payload.get("events", [])]
        if "observations" in payload:
            return [record if isinstance(record, Mapping) else {"value": record} for record in payload.get("observations", [])]
        if any(table_name in payload for table_name in LEGACY_TABLE_MODALITIES) or "crossmodal_mappings" in payload:
            return self._legacy_table_payload_to_records(payload)
        if "legacy_snapshot" in payload:
            snapshot_records = self._load_legacy_snapshot(payload.get("legacy_snapshot"), warnings=warnings)
            if snapshot_records:
                return snapshot_records

        records: List[Mapping[str, Any]] = []
        for key, modality in COLLECTION_MODALITIES.items():
            items = payload.get(key)
            if items is None:
                continue
            if not isinstance(items, Sequence) or isinstance(items, (str, bytes, bytearray)):
                items = [items]
            for item in items:
                if isinstance(item, Mapping):
                    record = dict(item)
                    record.setdefault("modality", modality)
                else:
                    record = {"modality": modality, "value": item}
                records.append(record)
        return records

    def _extract_pairs(
        self,
        payload: Mapping[str, Any] | Sequence[Any] | None,
        events: Sequence[CerebrumMemoryEvent],
        warnings: List[str],
    ) -> List[CrossModalPair]:
        if isinstance(payload, Mapping) and "pairs" in payload:
            pairs = self._normalize_pairs(payload.get("pairs"), warnings)
            if pairs:
                return pairs
        if isinstance(payload, Mapping) and "crossmodal_mappings" in payload:
            pairs = self._normalize_pairs(payload.get("crossmodal_mappings"), warnings)
            if pairs:
                return pairs
        return self.build_pairs(events)

    def _parse_record(self, record: Mapping[str, Any], index: int, warnings: List[str]) -> Optional[CerebrumMemoryEvent]:
        modality_raw = str(record.get("modality") or record.get("channel") or record.get("type") or "stimuli").lower()
        modality = MODALITY_ALIASES.get(modality_raw, "stimuli")
        if modality_raw not in MODALITY_ALIASES:
            warnings.append(f"Unknown modality '{modality_raw}' mapped to stimuli.")

        start_raw = record.get("starting_time", record.get("timestamp", record.get("time", index)))
        end_raw = record.get("ending_time", record.get("end_time", record.get("ending", None)))
        start = self._parse_time(start_raw, float(index), warnings)
        if end_raw is None:
            duration = self._coerce_float(record.get("duration", 1.0), 1.0)
            end = start + max(duration, 0.0)
        else:
            end = self._parse_time(end_raw, start + 1.0, warnings)
        if end < start:
            warnings.append(f"Event {index} had ending_time before starting_time; values were swapped.")
            start, end = end, start

        value_raw = record.get("value", record.get("intensity", record.get("payload", record.get("data", 0.0))))
        value = self._coerce_value(value_raw, modality)
        label = str(record.get("label", record.get("stimulus", record.get("direction", ""))))
        source = str(record.get("source", record.get("origin", "cerebrum-runtime")))
        payload_ref = str(record.get("payload_ref", record.get("memory_id", record.get("id", ""))))
        provenance = record.get("provenance") if isinstance(record.get("provenance"), Mapping) else {}
        return CerebrumMemoryEvent(
            modality=modality,
            starting_time=start,
            ending_time=end,
            value=value,
            source=source,
            label=label,
            payload_ref=payload_ref,
            provenance=dict(provenance),
        )

    def _normalize_event_times(self, events: Sequence[CerebrumMemoryEvent]) -> List[CerebrumMemoryEvent]:
        if not events:
            return []
        origin = min(event.starting_time for event in events)
        normalized = [
            CerebrumMemoryEvent(
                modality=event.modality,
                starting_time=event.starting_time - origin,
                ending_time=event.ending_time - origin,
                value=event.value,
                source=event.source,
                label=event.label,
                payload_ref=event.payload_ref,
                provenance=event.provenance,
            )
            for event in events
        ]
        return sorted(normalized, key=lambda event: (event.starting_time, event.modality))

    def _normalize_pairs(self, payload: Any, warnings: List[str]) -> List[CrossModalPair]:
        if payload is None:
            return []
        records = payload if isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray)) else [payload]
        pairs: List[CrossModalPair] = []
        for record in records:
            if not isinstance(record, Mapping):
                continue
            direction = str(record.get("direction", "")).upper()
            if direction not in PAIR_DIRECTION_ALIASES:
                warnings.append(f"Unknown pair direction '{direction}' ignored.")
                continue
            source_modality, target_modality = PAIR_DIRECTION_ALIASES[direction]
            pairs.append(
                CrossModalPair(
                    timestamp1=self._coerce_float(record.get("timestamp1", record.get("starting_time", 0.0)), 0.0),
                    timestamp2=self._coerce_float(record.get("timestamp2", record.get("ending_time", 0.0)), 0.0),
                    direction=direction,
                    source_modality=source_modality,
                    target_modality=target_modality,
                    overlap_score=max(0.0, min(1.0, self._coerce_float(record.get("overlap_score", 1.0), 1.0))),
                )
            )
        return sorted(pairs, key=lambda pair: (pair.timestamp1, pair.direction, pair.timestamp2))

    def _overlap_score(self, left: CerebrumMemoryEvent, right: CerebrumMemoryEvent) -> float:
        overlap = min(left.ending_time, right.ending_time) - max(left.starting_time, right.starting_time)
        if overlap <= 0.0:
            return 0.0
        denominator = max(min(left.duration, right.duration), 1e-9)
        return float(min(1.0, overlap / denominator))

    def _parse_time(self, raw_value: Any, fallback: float, warnings: List[str]) -> float:
        if isinstance(raw_value, (int, float, np.floating, np.integer)):
            return float(raw_value)
        if isinstance(raw_value, datetime):
            return raw_value.timestamp()
        if isinstance(raw_value, str):
            stripped = raw_value.strip()
            if not stripped:
                return fallback
            try:
                return float(stripped)
            except ValueError:
                pass
            for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
                try:
                    return datetime.strptime(stripped, fmt).timestamp()
                except ValueError:
                    pass
            try:
                return datetime.fromisoformat(stripped.replace("Z", "+00:00")).timestamp()
            except ValueError:
                warnings.append(f"Could not parse time '{stripped}', using fallback {fallback}.")
        return fallback

    def _coerce_value(self, raw_value: Any, modality: str) -> float:
        if raw_value is None:
            return 0.0
        if isinstance(raw_value, (int, float, np.floating, np.integer)):
            return float(raw_value)
        if isinstance(raw_value, str):
            stripped = raw_value.strip()
            if not stripped:
                return 0.0
            try:
                return float(stripped)
            except ValueError:
                return min(1.0, len(stripped) / 100.0)
        if isinstance(raw_value, Mapping):
            numeric_values = [self._coerce_float(value, np.nan) for value in raw_value.values()]
            numeric_values = [value for value in numeric_values if np.isfinite(value)]
            return float(np.mean(numeric_values)) if numeric_values else min(1.0, len(str(raw_value)) / 100.0)
        if isinstance(raw_value, Sequence) and not isinstance(raw_value, (bytes, bytearray)):
            values = [self._coerce_float(value, np.nan) for value in raw_value]
            values = [value for value in values if np.isfinite(value)]
            return float(np.mean(values)) if values else 0.0
        return min(1.0, len(str(raw_value)) / 100.0)

    def _coerce_float(self, raw_value: Any, fallback: float) -> float:
        try:
            return float(raw_value)
        except (TypeError, ValueError):
            return fallback

    def _load_legacy_snapshot(self, snapshot: Any, warnings: Optional[List[str]] = None) -> List[Mapping[str, Any]]:
        warnings = warnings if warnings is not None else []
        if snapshot is None:
            return []
        path = Path(str(snapshot))
        if not path.exists():
            warnings.append(f"Legacy snapshot path '{path}' does not exist.")
            return []

        records: List[Mapping[str, Any]] = []
        candidates = [path] if path.is_file() else sorted(
            item for item in path.rglob("*") if item.is_file() and item.suffix.lower() in {".json", ".jsonl", ".ndjson"}
        )
        for candidate in candidates:
            try:
                if candidate.suffix.lower() == ".json":
                    loaded = json.loads(candidate.read_text(encoding="utf-8"))
                    records.extend(self._legacy_payload_to_records(loaded, candidate))
                    continue
                for line in candidate.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    records.extend(self._legacy_payload_to_records(json.loads(line), candidate))
            except Exception as exc:  # pragma: no cover - best-effort legacy path
                warnings.append(f"Legacy snapshot file '{candidate}' could not be read: {exc}")
        return records

    def _legacy_payload_to_records(self, loaded: Any, source: Path) -> List[Mapping[str, Any]]:
        if isinstance(loaded, Mapping):
            if any(table_name in loaded for table_name in LEGACY_TABLE_MODALITIES):
                return self._legacy_table_payload_to_records(loaded)
            if "memories" in loaded:
                return [record if isinstance(record, Mapping) else {"value": record} for record in loaded.get("memories", [])]
            if "pairs" in loaded:
                return [record if isinstance(record, Mapping) else {"value": record} for record in loaded.get("pairs", [])]
            return [dict(loaded)]
        if isinstance(loaded, Sequence) and not isinstance(loaded, (str, bytes, bytearray)):
            records: List[Mapping[str, Any]] = []
            for item in loaded:
                if isinstance(item, Mapping):
                    records.append(dict(item))
                else:
                    records.append({"value": item, "source": source.stem})
            return records
        return [{"value": loaded, "source": source.stem}]

    def _legacy_table_payload_to_records(self, tables: Mapping[str, Any]) -> List[Mapping[str, Any]]:
        records: List[Mapping[str, Any]] = []
        for table_name, modality in LEGACY_TABLE_MODALITIES.items():
            entries = tables.get(table_name, [])
            if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes, bytearray)):
                entries = [entries]
            for entry in entries:
                if not isinstance(entry, Mapping):
                    continue
                records.append(
                    {
                        "modality": modality,
                        "starting_time": entry.get("starting_time", entry.get("timestamp", 0.0)),
                        "ending_time": entry.get("ending_time", entry.get("timestamp", entry.get("starting_time", 0.0))),
                        "value": entry.get("value", entry.get("data", 0.0)),
                        "label": entry.get("label", table_name),
                        "source": entry.get("source", table_name),
                        "payload_ref": entry.get("payload_ref", entry.get("memory_id", "")),
                    }
                )
        return records

    def default_payload(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "memories": [
                {
                    "modality": "hearing",
                    "starting_time": 0.0,
                    "ending_time": 1.4,
                    "value": 0.73,
                    "label": "rhythm",
                    "source": "demo-hearing",
                    "payload_ref": "hearing-001",
                },
                {
                    "modality": "vision",
                    "starting_time": 0.8,
                    "ending_time": 2.2,
                    "value": 0.61,
                    "label": "motion",
                    "source": "demo-vision",
                    "payload_ref": "vision-001",
                },
                {
                    "modality": "language",
                    "starting_time": 1.6,
                    "ending_time": 2.9,
                    "value": 0.54,
                    "label": "caption",
                    "source": "demo-language",
                    "payload_ref": "language-001",
                },
                {
                    "modality": "stimuli",
                    "starting_time": 2.4,
                    "ending_time": 3.0,
                    "value": 0.82,
                    "label": "trigger",
                    "source": "demo-stimuli",
                    "payload_ref": "stimuli-001",
                },
            ]
        }
