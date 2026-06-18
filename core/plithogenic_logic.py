"""Plithogenic runtime fusion primitives for the local simulator.

These helpers implement a bounded educational simulation grammar inspired by
Smarandache's plithogenic logic article. They attach to the runtime event
fusion path; they do not claim clinical, production, or validated physical
behavior.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Mapping, Optional, Sequence


SOURCE_LABEL = "Introduction to Plithogenic Logic as generalization of MultiVariate Logic"
SOURCE_URL = "https://fs.unm.edu/NSS/IntroductionPlithogenicLogic1.pdf"
SOURCE_HIERARCHY = "I -> I_system^S -> D_f -> dF -> i_fractal"
RESEARCH_BOUNDARY = (
    "alpha-local educational simulation only; not clinical, diagnostic, "
    "therapeutic, security, production-public, or validated physical behavior"
)
CONCEPTS = [
    "multi_attribute_proposition_P_V1_to_Vn",
    "attribute_truth_triplet_T_I_F",
    "attribute_source_weight",
    "dependence_contradiction_profile",
    "cumulative_plithogenic_truth",
]


def _finite_float(value: Any, fallback: float = 0.0) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return fallback
    if not math.isfinite(numeric):
        return fallback
    return numeric


def _clamp01(value: Any) -> float:
    return float(min(1.0, max(0.0, _finite_float(value))))


def _field(item: Any, name: str, default: Any = None) -> Any:
    if isinstance(item, Mapping):
        return item.get(name, default)
    return getattr(item, name, default)


def _event_duration(event: Any) -> float:
    duration = _field(event, "duration", None)
    if duration is not None:
        return max(0.0, _finite_float(duration))
    start = _field(event, "starting_time", _field(event, "timestamp", 0.0))
    end = _field(event, "ending_time", _field(event, "end_time", start))
    return max(0.0, _finite_float(end) - _finite_float(start))


def _event_timestamp(event: Any) -> float:
    return _finite_float(_field(event, "starting_time", _field(event, "timestamp", 0.0)))


def _event_weight(event: Any) -> float:
    explicit = _field(event, "weight", None)
    if explicit is not None:
        return max(0.0, _finite_float(explicit, 1.0))
    return max(1.0, _event_duration(event))


def _truth_triplet(event: Any) -> Dict[str, float]:
    truth = _clamp01(_field(event, "value", 0.0))
    falsity = _clamp01(1.0 - truth)
    D_f = _clamp01(1.0 - abs(truth - falsity))
    dF = _clamp01(_event_duration(event) / 4.0)
    i_system = _clamp01((D_f + dF) / 2.0)
    return {
        "T": truth,
        "I": i_system,
        "F": falsity,
        "I_system_component": i_system,
        "D_f": D_f,
        "dF": dF,
    }


def _normalize_weights(attributes: Sequence[Dict[str, Any]]) -> None:
    total = sum(float(item["weight"]) for item in attributes)
    if total <= 0.0:
        equal = 1.0 / len(attributes) if attributes else 0.0
        for item in attributes:
            item["normalized_weight"] = equal
        return
    for item in attributes:
        item["normalized_weight"] = float(item["weight"]) / total


def plithogenic_attribute_profile(events: Sequence[Any]) -> Dict[str, Any]:
    """Represent runtime events as plithogenic attribute-value observations."""
    attributes: list[Dict[str, Any]] = []
    for index, event in enumerate(events):
        modality = str(_field(event, "modality", "stimuli"))
        label = str(_field(event, "label", ""))
        source = str(_field(event, "source", ""))
        timestamp = _event_timestamp(event)
        triplet = _truth_triplet(event)
        attribute_id = f"V{index + 1}:{modality}:{timestamp:.6f}"
        attributes.append(
            {
                "attribute_id": attribute_id,
                "variable": f"V{index + 1}",
                "modality": modality,
                "label": label,
                "source": source,
                "timestamp": timestamp,
                "duration": _event_duration(event),
                "weight": _event_weight(event),
                "truth": triplet["T"],
                "indeterminacy": triplet["I"],
                "falsity": triplet["F"],
                "hierarchy_components": {
                    "I_system_component": triplet["I_system_component"],
                    "D_f": triplet["D_f"],
                    "dF": triplet["dF"],
                    "i_fractal": None,
                },
            }
        )
    _normalize_weights(attributes)
    return {
        "model": "plithogenic_attribute_profile",
        "source": SOURCE_LABEL,
        "source_url": SOURCE_URL,
        "attribute_count": len(attributes),
        "attributes": attributes,
        "concept": "P(V1, V2, ..., Vn) runtime event proposition",
        "hierarchy": SOURCE_HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


def _as_profile_triplet(profile: Mapping[str, Any]) -> tuple[float, float, float]:
    truth = _clamp01(profile.get("truth", profile.get("T", 0.0)))
    indeterminacy = _clamp01(profile.get("indeterminacy", profile.get("I", 0.0)))
    falsity = _clamp01(profile.get("falsity", profile.get("F", 0.0)))
    return truth, indeterminacy, falsity


def plithogenic_neutrosophic_conjunction(profiles: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Compute source-direct neutrosophic cumulative truth: min T, max I, max F."""
    if not profiles:
        truth = indeterminacy = falsity = 0.0
    else:
        triplets = [_as_profile_triplet(profile) for profile in profiles]
        truth = min(item[0] for item in triplets)
        indeterminacy = max(item[1] for item in triplets)
        falsity = max(item[2] for item in triplets)
    return {
        "operator": "plithogenic_neutrosophic_conjunction_min_max_max",
        "T": truth,
        "I": indeterminacy,
        "F": falsity,
        "source": SOURCE_LABEL,
        "source_url": SOURCE_URL,
        "interpretation": "Cumulative neutrosophic truth uses min(T), max(I), max(F).",
        "hierarchy": SOURCE_HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


def plithogenic_weighted_cumulative_truth(profiles: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Compute a bounded weighted cumulative profile from attribute weights."""
    if not profiles:
        return {
            "operator": "plithogenic_weighted_cumulative_truth",
            "T": 0.0,
            "I": 0.0,
            "F": 0.0,
            "total_weight": 0.0,
            "source": SOURCE_LABEL,
            "source_url": SOURCE_URL,
            "hierarchy": SOURCE_HIERARCHY,
            "research_boundary": RESEARCH_BOUNDARY,
        }
    total_weight = sum(max(0.0, _finite_float(profile.get("weight", 1.0), 1.0)) for profile in profiles)
    if total_weight <= 0.0:
        total_weight = float(len(profiles))
        weights = [1.0 for _ in profiles]
    else:
        weights = [max(0.0, _finite_float(profile.get("weight", 1.0), 1.0)) for profile in profiles]
    weighted = [(_as_profile_triplet(profile), weight) for profile, weight in zip(profiles, weights)]
    return {
        "operator": "plithogenic_weighted_cumulative_truth",
        "T": _clamp01(sum(triplet[0] * weight for triplet, weight in weighted) / total_weight),
        "I": _clamp01(sum(triplet[1] * weight for triplet, weight in weighted) / total_weight),
        "F": _clamp01(sum(triplet[2] * weight for triplet, weight in weighted) / total_weight),
        "total_weight": total_weight,
        "source": SOURCE_LABEL,
        "source_url": SOURCE_URL,
        "interpretation": "Truth-variable weights change the local cumulative simulator readout.",
        "hierarchy": SOURCE_HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


def plithogenic_contradiction_degree(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    overlap_score: float = 1.0,
) -> Dict[str, Any]:
    """Return a bounded dependence/contradiction profile for two attributes."""
    left_truth, _, left_falsity = _as_profile_triplet(left)
    right_truth, _, right_falsity = _as_profile_triplet(right)
    value_contradiction = _clamp01((abs(left_truth - right_truth) + abs(left_falsity - right_falsity)) / 2.0)
    modality_contradiction = 0.0 if left.get("modality") == right.get("modality") else 0.15
    dependence_degree = _clamp01(overlap_score)
    contradiction_degree = _clamp01((0.85 * value_contradiction + 0.15 * modality_contradiction) * dependence_degree)
    return {
        "source_attribute_id": left.get("attribute_id", ""),
        "target_attribute_id": right.get("attribute_id", ""),
        "dependence_degree": dependence_degree,
        "independence_degree": _clamp01(1.0 - dependence_degree),
        "value_contradiction": value_contradiction,
        "modality_contradiction": modality_contradiction,
        "contradiction_degree": contradiction_degree,
        "interpretation": (
            "Local simulator metric: higher dependence plus divergent attribute truth-values "
            "increases contradiction load before QNN feature encoding."
        ),
    }


def _find_attribute(
    attributes: Sequence[Mapping[str, Any]],
    modality: str,
    timestamp: float,
) -> Optional[Mapping[str, Any]]:
    candidates = [item for item in attributes if item.get("modality") == modality]
    if not candidates:
        return None
    return min(candidates, key=lambda item: abs(_finite_float(item.get("timestamp", 0.0)) - timestamp))


def _pair_contradictions(
    attributes: Sequence[Mapping[str, Any]],
    pairs: Sequence[Any],
) -> list[Dict[str, Any]]:
    contradictions: list[Dict[str, Any]] = []
    for pair in pairs:
        source_modality = str(_field(pair, "source_modality", ""))
        target_modality = str(_field(pair, "target_modality", ""))
        source_timestamp = _finite_float(_field(pair, "timestamp1", 0.0))
        target_timestamp = _finite_float(_field(pair, "timestamp2", 0.0))
        left = _find_attribute(attributes, source_modality, source_timestamp)
        right = _find_attribute(attributes, target_modality, target_timestamp)
        if left is None or right is None:
            continue
        profile = plithogenic_contradiction_degree(
            left,
            right,
            overlap_score=_finite_float(_field(pair, "overlap_score", 1.0), 1.0),
        )
        profile["direction"] = str(_field(pair, "direction", ""))
        contradictions.append(profile)
    return contradictions


def plithogenic_runtime_fusion_profile(events: Sequence[Any], pairs: Sequence[Any]) -> Dict[str, Any]:
    """Compute the opt-in plithogenic profile at the runtime fusion boundary."""
    attribute_payload = plithogenic_attribute_profile(events)
    attributes = attribute_payload["attributes"]
    source_direct = plithogenic_neutrosophic_conjunction(attributes)
    weighted = plithogenic_weighted_cumulative_truth(attributes)
    contradictions = _pair_contradictions(attributes, pairs)
    contradiction_values = [item["contradiction_degree"] for item in contradictions]
    avg_contradiction = (
        float(sum(contradiction_values) / len(contradiction_values)) if contradiction_values else 0.0
    )
    max_contradiction = max(contradiction_values) if contradiction_values else 0.0
    dependence_values = [item["dependence_degree"] for item in contradictions]
    avg_dependence = float(sum(dependence_values) / len(dependence_values)) if dependence_values else 0.0
    feature_vector = [
        source_direct["T"],
        source_direct["I"],
        source_direct["F"],
        weighted["T"],
        weighted["I"],
        weighted["F"],
        _clamp01(avg_contradiction),
        _clamp01(max_contradiction),
        _clamp01(avg_dependence),
        _clamp01(len(attributes) / 16.0),
    ]
    return {
        "model": "plithogenic_runtime_fusion_v1",
        "source": SOURCE_LABEL,
        "source_url": SOURCE_URL,
        "concepts": CONCEPTS,
        "simulator_gap": (
            "Runtime events were previously weighted and overlapped, but attribute-value "
            "contradiction/dependence was not surfaced before LVFM/QNN features."
        ),
        "attribute_profile": attribute_payload,
        "cumulative_truth": source_direct,
        "weighted_cumulative_truth": weighted,
        "pairwise_contradictions": contradictions,
        "contradiction_summary": {
            "pair_count": len(contradictions),
            "average_contradiction": _clamp01(avg_contradiction),
            "max_contradiction": _clamp01(max_contradiction),
            "average_dependence": _clamp01(avg_dependence),
        },
        "feature_vector": feature_vector,
        "feature_dimension": len(feature_vector),
        "hierarchy": SOURCE_HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


__all__ = [
    "CONCEPTS",
    "RESEARCH_BOUNDARY",
    "SOURCE_HIERARCHY",
    "SOURCE_LABEL",
    "SOURCE_URL",
    "plithogenic_attribute_profile",
    "plithogenic_contradiction_degree",
    "plithogenic_neutrosophic_conjunction",
    "plithogenic_runtime_fusion_profile",
    "plithogenic_weighted_cumulative_truth",
]
