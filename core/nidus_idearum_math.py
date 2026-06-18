"""Nidus Idearum II inspired math primitives for the local simulator.

These helpers are bounded educational simulation grammar. They preserve
indeterminacy as an explicit local signal and do not claim clinical,
production, security, or validated physical behavior.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Mapping, Sequence


SOURCE_HIERARCHY = "I -> I_system^S -> D_f -> dF -> i_fractal"
RESEARCH_BOUNDARY = (
    "alpha-local educational simulation only; not clinical, diagnostic, "
    "therapeutic, security, production-public, or validated physical behavior"
)
SOURCE_LABEL = "Nidus Idearum II, 2nd ed."


def _finite_float(value: Any, label: str) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be numeric")
    if not math.isfinite(numeric):
        raise ValueError(f"{label} must be finite")
    return numeric


def _nonnegative(value: Any, label: str) -> float:
    numeric = _finite_float(value, label)
    if numeric < 0.0:
        raise ValueError(f"{label} must be non-negative")
    return numeric


def _bounded01(value: float) -> float:
    return float(min(1.0, max(0.0, value)))


def _triplet_from_mapping(source: Mapping[str, Any], label: str) -> tuple[float, float, float]:
    truth = _nonnegative(source.get("T", source.get("truth", 0.0)), f"{label}.T")
    indeterminacy = _nonnegative(
        source.get("I", source.get("indeterminacy", 0.0)),
        f"{label}.I",
    )
    falsity = _nonnegative(source.get("F", source.get("falsity", 0.0)), f"{label}.F")
    return truth, indeterminacy, falsity


def _normalized_triplet(truth: float, indeterminacy: float, falsity: float) -> tuple[float, float, float]:
    total = truth + indeterminacy + falsity
    if total <= 0.0:
        return 1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0
    return truth / total, indeterminacy / total, falsity / total


def triplet_quality_profile(truth: Any, indeterminacy: Any, falsity: Any) -> Dict[str, Any]:
    """Return bounded quality metadata for a dynamic T/I/F triplet."""
    truth_value = _nonnegative(truth, "truth")
    indeterminacy_value = _nonnegative(indeterminacy, "indeterminacy")
    falsity_value = _nonnegative(falsity, "falsity")
    total = truth_value + indeterminacy_value + falsity_value
    t_norm, i_norm, f_norm = _normalized_triplet(
        truth_value,
        indeterminacy_value,
        falsity_value,
    )
    contradiction_load = min(t_norm, f_norm)
    uncertainty_load = i_norm
    return {
        "model": "nidus_idearum_triplet_quality",
        "source": SOURCE_LABEL,
        "raw": {
            "T": truth_value,
            "I": indeterminacy_value,
            "F": falsity_value,
            "sum": total,
        },
        "normalized": {
            "T": t_norm,
            "I": i_norm,
            "F": f_norm,
        },
        "score": float(t_norm - f_norm),
        "accuracy": _bounded01(t_norm + f_norm),
        "certainty": _bounded01(1.0 - i_norm),
        "positiveness": _bounded01(t_norm),
        "negativeness": _bounded01(f_norm),
        "contradiction_load": _bounded01(contradiction_load),
        "indeterminacy_load": _bounded01(uncertainty_load),
        "incomplete_load": _bounded01(max(0.0, 1.0 - total)),
        "overdefined_load": _bounded01(max(0.0, total - 1.0)),
        "interpretation": (
            "T/I/F remains a dynamic triplet. Normalized values are local "
            "readout metadata, not replacement probabilities."
        ),
        "hierarchy": SOURCE_HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


def source_weighted_triplet_fusion(sources: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Fuse source triplets while preserving local incomplete-model indeterminacy."""
    if not sources:
        raise ValueError("sources must contain at least one source triplet")

    weighted_truth = 0.0
    weighted_indeterminacy = 0.0
    weighted_falsity = 0.0
    missing_mass = 0.0
    intersection_indeterminacy = 0.0
    conflict_mass = 0.0
    total_weight = 0.0
    source_trace = []

    for index, source in enumerate(sources):
        if not isinstance(source, Mapping):
            raise TypeError("each source must be a mapping")
        weight = _nonnegative(
            source.get("beta", source.get("source_importance", source.get("weight", 1.0))),
            f"sources[{index}].weight",
        )
        if weight == 0.0:
            continue
        truth, indeterminacy, falsity = _triplet_from_mapping(source, f"sources[{index}]")
        source_sum = truth + indeterminacy + falsity
        source_missing = max(0.0, 1.0 - source_sum)
        source_conflict = min(truth, falsity)
        source_intersection = _nonnegative(
            source.get(
                "intersection_indeterminacy",
                source.get("indeterminate_intersection", source.get("intersection_unknown", 0.0)),
            ),
            f"sources[{index}].intersection_indeterminacy",
        )

        total_weight += weight
        weighted_truth += weight * truth
        weighted_indeterminacy += weight * indeterminacy
        weighted_falsity += weight * falsity
        missing_mass += weight * source_missing
        intersection_indeterminacy += weight * source_intersection
        conflict_mass += weight * source_conflict
        source_trace.append(
            {
                "index": index,
                "weight": weight,
                "T": truth,
                "I": indeterminacy,
                "F": falsity,
                "missing_mass": source_missing,
                "intersection_indeterminacy": source_intersection,
                "conflict_mass": source_conflict,
            }
        )

    if total_weight <= 0.0:
        raise ValueError("at least one source must have a positive weight")

    fused_truth = weighted_truth / total_weight
    base_indeterminacy = weighted_indeterminacy / total_weight
    fused_falsity = weighted_falsity / total_weight
    incomplete_component = missing_mass / total_weight
    intersection_component = intersection_indeterminacy / total_weight
    conflict_component = conflict_mass / total_weight
    i_system_component = base_indeterminacy + incomplete_component + intersection_component
    quality = triplet_quality_profile(fused_truth, i_system_component, fused_falsity)

    return {
        "model": "nidus_idearum_source_weighted_triplet_fusion",
        "source": SOURCE_LABEL,
        "source_count": len(source_trace),
        "total_weight": total_weight,
        "fused": {
            "T": fused_truth,
            "I": i_system_component,
            "F": fused_falsity,
        },
        "components": {
            "base_indeterminacy": base_indeterminacy,
            "incomplete_model_component": incomplete_component,
            "indeterminate_intersection_component": intersection_component,
            "conflict_component": conflict_component,
            "I_system_component": i_system_component,
        },
        "quality": quality,
        "source_trace": source_trace,
        "interpretation": (
            "Incomplete intersections and source uncertainty are preserved as "
            "local I_system_component instead of being discarded."
        ),
        "hierarchy": SOURCE_HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


def partial_membership_mean(values: Sequence[Any], memberships: Sequence[Any]) -> Dict[str, Any]:
    """Compute an overset/underset-style weighted mean for partial membership."""
    if len(values) != len(memberships):
        raise ValueError("values and memberships must have the same length")
    if not values:
        raise ValueError("values must not be empty")

    numeric_values = [_finite_float(value, f"values[{index}]") for index, value in enumerate(values)]
    numeric_memberships = [
        _nonnegative(value, f"memberships[{index}]") for index, value in enumerate(memberships)
    ]
    membership_sum = sum(numeric_memberships)
    if membership_sum <= 0.0:
        raise ValueError("membership sum must be positive")

    weighted_sum = sum(value * membership for value, membership in zip(numeric_values, numeric_memberships))
    classical_mean = sum(numeric_values) / len(numeric_values)
    neutrosophic_mean = weighted_sum / membership_sum
    over_membership_load = sum(max(0.0, membership - 1.0) for membership in numeric_memberships)
    under_membership_load = sum(max(0.0, 1.0 - membership) for membership in numeric_memberships)

    return {
        "model": "nidus_idearum_partial_membership_mean",
        "source": SOURCE_LABEL,
        "count": len(numeric_values),
        "values": numeric_values,
        "memberships": numeric_memberships,
        "membership_sum": membership_sum,
        "classical_mean": classical_mean,
        "partial_membership_mean": neutrosophic_mean,
        "difference_from_classical": neutrosophic_mean - classical_mean,
        "over_membership_load": over_membership_load,
        "under_membership_load": under_membership_load,
        "has_overset_membership": any(membership > 1.0 for membership in numeric_memberships),
        "has_underset_membership": any(0.0 <= membership < 1.0 for membership in numeric_memberships),
        "interpretation": (
            "Membership weights may be below, equal to, or above 1.0 for a "
            "local educational overset/underset sample readout."
        ),
        "hierarchy": SOURCE_HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


__all__ = [
    "RESEARCH_BOUNDARY",
    "SOURCE_HIERARCHY",
    "SOURCE_LABEL",
    "partial_membership_mean",
    "source_weighted_triplet_fusion",
    "triplet_quality_profile",
]
