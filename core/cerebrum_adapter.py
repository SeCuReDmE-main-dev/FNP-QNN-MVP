"""
Crossmodal Cerebrum adapter.

This module turns heterogeneous perception events into deterministic
feature bundles that can be consumed by a QNN or a classical surrogate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Sequence

import numpy as np

MODALITIES = ("audio", "video", "text", "stimuli")
MODALITY_INDEX = {name: idx for idx, name in enumerate(MODALITIES)}


@dataclass(frozen=True)
class CrossModalEvent:
    modality: str
    value: float
    timestamp: float
    label: str = ""
    source: str = ""
    weight: float = 1.0


@dataclass
class CerebrumFeatureBundle:
    events: List[CrossModalEvent]
    modality_counts: Dict[str, int]
    modality_means: Dict[str, float]
    modality_stds: Dict[str, float]
    transition_matrix: np.ndarray
    recency_weighted_intensity: float
    temporal_span: float
    sequence_length: int
    summary: Dict[str, float] = field(default_factory=dict)


class CerebrumAdapter:
    """Convert crossmodal observations into a fixed feature vector."""

    def coerce_events(self, raw_events: Iterable[Any]) -> List[CrossModalEvent]:
        events: List[CrossModalEvent] = []
        for index, item in enumerate(raw_events):
            events.append(self._coerce_event(item, index))
        return sorted(events, key=lambda event: event.timestamp)

    def build_bundle(self, raw_events: Iterable[Any]) -> CerebrumFeatureBundle:
        events = self.coerce_events(raw_events)
        return self._bundle_from_events(events)

    def to_feature_vector(self, raw_events: Iterable[Any]) -> np.ndarray:
        bundle = self.build_bundle(raw_events)
        return self.bundle_to_vector(bundle)

    def bundle_to_vector(self, bundle: CerebrumFeatureBundle) -> np.ndarray:
        counts = np.array([bundle.modality_counts[name] for name in MODALITIES], dtype=float)
        total = float(bundle.sequence_length) if bundle.sequence_length else 1.0
        counts = counts / total

        means = np.array([bundle.modality_means[name] for name in MODALITIES], dtype=float)
        stds = np.array([bundle.modality_stds[name] for name in MODALITIES], dtype=float)
        transition = bundle.transition_matrix.reshape(-1).astype(float)

        vector = np.concatenate(
            [
                counts,
                means,
                stds,
                transition,
                np.array(
                    [
                        bundle.recency_weighted_intensity,
                        bundle.temporal_span,
                        float(bundle.sequence_length),
                    ],
                    dtype=float,
                ),
            ]
        )
        return vector

    def default_observations(self) -> List[Dict[str, Any]]:
        return [
            {"modality": "audio", "value": 0.72, "timestamp": 0.0, "label": "rhythm", "source": "demo"},
            {"modality": "video", "value": 0.48, "timestamp": 0.8, "label": "motion", "source": "demo"},
            {"modality": "text", "value": 0.61, "timestamp": 1.6, "label": "token", "source": "demo"},
            {"modality": "stimuli", "value": 0.85, "timestamp": 2.4, "label": "trigger", "source": "demo"},
        ]

    def _bundle_from_events(self, events: List[CrossModalEvent]) -> CerebrumFeatureBundle:
        if not events:
            empty_counts = {name: 0 for name in MODALITIES}
            empty_means = {name: 0.0 for name in MODALITIES}
            empty_stds = {name: 0.0 for name in MODALITIES}
            return CerebrumFeatureBundle(
                events=[],
                modality_counts=empty_counts,
                modality_means=empty_means,
                modality_stds=empty_stds,
                transition_matrix=np.zeros((len(MODALITIES), len(MODALITIES)), dtype=float),
                recency_weighted_intensity=0.0,
                temporal_span=0.0,
                sequence_length=0,
                summary={"sequence_length": 0.0, "diversity": 0.0, "stability": 0.0},
            )

        by_modality: Dict[str, List[float]] = {name: [] for name in MODALITIES}
        for event in events:
            by_modality[event.modality].append(float(event.value))

        modality_counts = {name: len(values) for name, values in by_modality.items()}
        modality_means = {name: float(np.mean(values)) if values else 0.0 for name, values in by_modality.items()}
        modality_stds = {name: float(np.std(values)) if values else 0.0 for name, values in by_modality.items()}

        transition_matrix = np.zeros((len(MODALITIES), len(MODALITIES)), dtype=float)
        for previous, current in zip(events, events[1:]):
            previous_idx = MODALITY_INDEX.get(previous.modality, 0)
            current_idx = MODALITY_INDEX.get(current.modality, 0)
            transition_matrix[previous_idx, current_idx] += 1.0
        if transition_matrix.sum() > 0:
            transition_matrix = transition_matrix / transition_matrix.sum()

        timestamps = np.array([event.timestamp for event in events], dtype=float)
        values = np.array([event.value * event.weight for event in events], dtype=float)
        span = float(timestamps.max() - timestamps.min()) if len(timestamps) > 1 else 0.0
        time_scale = max(span, 1.0)
        recency_weights = np.exp(-(timestamps.max() - timestamps) / time_scale)
        recency_weighted_intensity = float(np.average(values, weights=recency_weights))

        counts_array = np.array(list(modality_counts.values()), dtype=float)
        diversity = float(np.count_nonzero(counts_array) / len(MODALITIES))
        stability = float(1.0 / (1.0 + np.mean(list(modality_stds.values()))))

        summary = {
            "sequence_length": float(len(events)),
            "temporal_span": span,
            "diversity": diversity,
            "stability": stability,
            "recency_weighted_intensity": recency_weighted_intensity,
        }

        return CerebrumFeatureBundle(
            events=events,
            modality_counts=modality_counts,
            modality_means=modality_means,
            modality_stds=modality_stds,
            transition_matrix=transition_matrix,
            recency_weighted_intensity=recency_weighted_intensity,
            temporal_span=span,
            sequence_length=len(events),
            summary=summary,
        )

    def _coerce_event(self, item: Any, index: int) -> CrossModalEvent:
        if isinstance(item, CrossModalEvent):
            return item

        if isinstance(item, Mapping):
            modality = str(item.get("modality") or item.get("channel") or item.get("type") or "stimuli").lower()
            if modality not in MODALITIES:
                modality = "stimuli"
            value = self._coerce_value(item.get("value", item.get("intensity", item.get("payload", 0.0))), modality)
            timestamp = float(item.get("timestamp", item.get("time", index)))
            label = str(item.get("label", item.get("stimulus", "")))
            source = str(item.get("source", item.get("origin", "")))
            weight = float(item.get("weight", 1.0))
            return CrossModalEvent(modality=modality, value=value, timestamp=timestamp, label=label, source=source, weight=weight)

        if isinstance(item, (int, float, np.floating, np.integer)):
            return CrossModalEvent(modality="stimuli", value=float(item), timestamp=float(index))

        return CrossModalEvent(modality="text", value=self._coerce_value(item, "text"), timestamp=float(index))

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
                length_scale = max(len(stripped), 1)
                modality_scale = 1.0 + 0.1 * MODALITY_INDEX.get(modality, 0)
                return min(1.0, (length_scale / 100.0) * modality_scale)

        if isinstance(raw_value, Sequence) and not isinstance(raw_value, (bytes, bytearray)):
            array = np.asarray(list(raw_value), dtype=float)
            return float(np.mean(array)) if array.size else 0.0

        return float(len(str(raw_value)) % 100) / 100.0
