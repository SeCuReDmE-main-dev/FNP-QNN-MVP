"""
Plithogenic probability/statistics bridge for runtime topology profiles.

Source: Florentin Smarandache, "Plithogenic Probability & Statistics are
generalizations of MultiVariate Probability & Statistics", Neutrosophic Sets
and Systems, Vol. 43, 2021. Local source path used for implementation planning:
C:\\Users\\jeans\\Desktop\\livre pdf\\PlithogenicProbabilityStatistics20.pdf

The functions here are deterministic educational primitives. They compute
empirical statistics over runtime observations; they do not perform stochastic
simulation or make validated predictive claims.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List, Mapping, Sequence


HIERARCHY = "I -> I_system^S -> D_f -> dF -> i_fractal"


def _clamp01(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if number != number:
        return 0.0
    return max(0.0, min(1.0, number))


def _safe_float(value: Any, fallback: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return fallback
    if number != number:
        return fallback
    return number


def _to_observation(event: Any) -> Dict[str, Any]:
    if hasattr(event, "to_observation"):
        return dict(event.to_observation())
    if isinstance(event, Mapping):
        return dict(event)
    return {"value": event, "modality": "stimuli", "weight": 1.0}


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _variance(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    average = _mean(values)
    return _mean([(item - average) ** 2 for item in values])


def plithogenic_variate_sample_profile(events: Iterable[Any]) -> Dict[str, Any]:
    """Represent runtime observations as a plithogenic variate sample."""

    observations = [_to_observation(event) for event in events]
    memberships: List[float] = []
    weights: List[float] = []
    modalities: List[str] = []
    values: List[float] = []
    for observation in observations:
        values.append(_safe_float(observation.get("value"), 0.0))
        modalities.append(str(observation.get("modality") or "stimuli"))
        raw_membership = observation.get("membership", observation.get("weight", 1.0))
        membership = max(0.0, _safe_float(raw_membership, 1.0))
        memberships.append(membership)
        weights.append(max(0.0, _safe_float(observation.get("weight", membership), membership)))

    sample_size = len(observations)
    total_membership = sum(memberships)
    known_size_score = 1.0 if sample_size else 0.0
    partial_membership_load = 0.0
    if sample_size:
        partial_membership_load = _clamp01(
            sum(abs(item - 1.0) for item in memberships) / max(sample_size, 1)
        )

    modality_counts = Counter(modalities)
    return {
        "model": "plithogenic_variate_sample_v1",
        "sample_size": sample_size,
        "known_size_score": known_size_score,
        "total_membership": total_membership,
        "effective_sample_size": min(float(sample_size), total_membership),
        "partial_membership_load": partial_membership_load,
        "modality_counts": dict(modality_counts),
        "modality_coverage": _clamp01(len(modality_counts) / 4.0),
        "value_mean": _clamp01(_mean([_clamp01(value) for value in values])),
        "value_variance": _clamp01(_variance([_clamp01(value) for value in values])),
    }


def plithogenic_probability_family_profile(plithogenic_profile: Mapping[str, Any]) -> Dict[str, Any]:
    """Classify the bounded probability family carried by a plithogenic profile."""

    attributes = list((plithogenic_profile.get("attribute_profile") or {}).get("attributes") or [])
    families = []
    truth_values: List[float] = []
    indeterminacy_values: List[float] = []
    falsity_values: List[float] = []
    for attribute in attributes:
        truth = _clamp01(attribute.get("truth"))
        indeterminacy = _clamp01(attribute.get("indeterminacy"))
        falsity = _clamp01(attribute.get("falsity"))
        truth_values.append(truth)
        indeterminacy_values.append(indeterminacy)
        falsity_values.append(falsity)
        if indeterminacy > 0.0 and falsity > 0.0:
            families.append("plithogenic_neutrosophic_probability")
        elif indeterminacy > 0.0:
            families.append("plithogenic_indeterminate_probability")
        elif falsity > 0.0:
            families.append("plithogenic_intuitionistic_fuzzy_probability")
        else:
            families.append("classical_multivariate_probability")

    family_counts = Counter(families)
    if not families:
        dominant = "empty_probability_profile"
    elif len(family_counts) == 1:
        dominant = next(iter(family_counts))
    else:
        dominant = "plithogenic_hybrid_probability"

    return {
        "model": "plithogenic_probability_family_v1",
        "attribute_count": len(attributes),
        "dominant_family": dominant,
        "family_counts": dict(family_counts),
        "empirical_truth_probability": _clamp01(_mean(truth_values)),
        "empirical_indeterminate_probability": _clamp01(_mean(indeterminacy_values)),
        "empirical_false_probability": _clamp01(_mean(falsity_values)),
    }


def refined_plithogenic_statistical_components(
    plithogenic_profile: Mapping[str, Any],
    topology_profile: Mapping[str, Any],
) -> Dict[str, Any]:
    """Preserve refined T/I/F subcomponents as sample statistics."""

    attributes = list((plithogenic_profile.get("attribute_profile") or {}).get("attributes") or [])
    topology_components = topology_profile.get("refined_components") or {}
    t_components = dict(topology_components.get("T_components") or {})
    i_components = dict(topology_components.get("I_components") or {})
    f_components = dict(topology_components.get("F_components") or {})

    truth_values = [_clamp01(item.get("truth")) for item in attributes]
    indeterminacy_values = [_clamp01(item.get("indeterminacy")) for item in attributes]
    falsity_values = [_clamp01(item.get("falsity")) for item in attributes]
    weights = [max(0.0, _safe_float(item.get("weight"), 1.0)) for item in attributes]
    total_weight = sum(weights) or float(len(attributes) or 1)

    def weighted_average(values: Sequence[float]) -> float:
        if not values:
            return 0.0
        local_weights = weights[: len(values)] or [1.0 for _ in values]
        denominator = sum(local_weights) or float(len(values))
        return _clamp01(sum(value * weight for value, weight in zip(values, local_weights)) / denominator)

    refined_t = {
        "T1_attribute_truth_mean": _clamp01(_mean(truth_values)),
        "T2_weighted_truth_mean": weighted_average(truth_values),
        "T3_topology_closure_truth": _clamp01(
            t_components.get("value_truth", t_components.get("temporal_truth", 0.0))
        ),
    }
    refined_i = {
        "I1_attribute_indeterminacy_mean": _clamp01(_mean(indeterminacy_values)),
        "I2_truth_variance_load": _clamp01(_variance(truth_values) * 4.0),
        "I_system^S": _clamp01(i_components.get("I_system^S", i_components.get("source_indeterminacy", 0.0))),
        "D_f": _clamp01(i_components.get("D_f", 0.0)),
        "dF": _clamp01(i_components.get("dF", 0.0)),
        "i_fractal": i_components.get("i_fractal"),
    }
    refined_f = {
        "F1_attribute_false_mean": _clamp01(_mean(falsity_values)),
        "F2_weighted_false_mean": weighted_average(falsity_values),
        "F3_topology_falsity": _clamp01(
            f_components.get("closure_falsity", f_components.get("contradiction_falsity", 0.0))
        ),
    }

    return {
        "model": "plithogenic_refined_statistics_v1",
        "T_components": refined_t,
        "I_components": refined_i,
        "F_components": refined_f,
        "total_weight": total_weight,
        "hierarchy": HIERARCHY,
    }


def plithogenic_multi_to_uni_decision(
    profiles: Sequence[Mapping[str, Any]],
    operator: str = "conjunction",
) -> Dict[str, Any]:
    """Convert multivariate triplets to one decision triplet using source operators."""

    triplets = list(profiles)
    if not triplets:
        return {"operator": operator, "T": 0.0, "I": 1.0, "F": 1.0}
    truth_values = [_clamp01(item.get("truth", item.get("T"))) for item in triplets]
    indeterminacy_values = [_clamp01(item.get("indeterminacy", item.get("I"))) for item in triplets]
    falsity_values = [_clamp01(item.get("falsity", item.get("F"))) for item in triplets]
    if operator == "disjunction":
        truth = max(truth_values)
        indeterminacy = min(indeterminacy_values)
        falsity = min(falsity_values)
    else:
        truth = min(truth_values)
        indeterminacy = max(indeterminacy_values)
        falsity = max(falsity_values)
        operator = "conjunction"
    return {"operator": operator, "T": truth, "I": indeterminacy, "F": falsity}


def plithogenic_topology_wiring_profile(
    events: Iterable[Any],
    pairs: Iterable[Any],
    plithogenic_profile: Mapping[str, Any],
    topology_profile: Mapping[str, Any],
) -> Dict[str, Any]:
    """Complete topology variables with deterministic plithogenic statistics."""

    del pairs  # Pair-derived signals are already present in the two source profiles.
    sample_profile = plithogenic_variate_sample_profile(events)
    probability_profile = plithogenic_probability_family_profile(plithogenic_profile)
    refined = refined_plithogenic_statistical_components(plithogenic_profile, topology_profile)
    attributes = list((plithogenic_profile.get("attribute_profile") or {}).get("attributes") or [])
    deterministic_decision = plithogenic_multi_to_uni_decision(attributes, operator="conjunction")

    topology_axiom = topology_profile.get("topological_axiom_profile") or {}
    deformation = topology_profile.get("deformation_signature") or {}
    topology_refined = topology_profile.get("refined_components") or {}
    over_under_off = topology_refined.get("over_under_off") or {}
    multiset_recurrence = topology_refined.get("multiset_recurrence") or {}
    feature_vector_source = topology_profile.get("feature_vector") or []
    topology_dispersion = _clamp01(_variance([_clamp01(item) for item in feature_vector_source]) * 4.0)
    sample_confidence = _clamp01(sample_profile["effective_sample_size"] / max(sample_profile["sample_size"], 1))
    coherence = _clamp01(1.0 - refined["I_components"]["I2_truth_variance_load"])
    deterministic_confidence = _clamp01(
        (deterministic_decision["T"] + (1.0 - deterministic_decision["I"]) + (1.0 - deterministic_decision["F"])) / 3.0
    )
    statistical_confidence = _clamp01((sample_confidence + coherence + (1.0 - topology_dispersion)) / 3.0)

    class_scores = {
        "CT": _clamp01(topology_axiom.get("CT")),
        "NCT": _clamp01(topology_axiom.get("NCT")),
        "ACT": _clamp01(topology_axiom.get("ACT")),
    }
    class_total = sum(class_scores.values()) or 1.0
    topology_class_probability = {
        key: _clamp01(value / class_total)
        for key, value in class_scores.items()
    }
    equivalence_probability = _clamp01(
        _clamp01(deformation.get("deformation_stability")) * statistical_confidence
    )
    neighborhood_stability = _clamp01(
        (1.0 - topology_dispersion + _clamp01(sample_profile["modality_coverage"])) / 2.0
    )

    topology_variable_completion = {
        "topology_class_probability": topology_class_probability,
        "deformation_equivalence_probability": equivalence_probability,
        "neighborhood_statistical_stability": neighborhood_stability,
        "membership_dispersion": _clamp01(sample_profile["partial_membership_load"]),
        "over_under_off_dispersion": _clamp01(
            (
                _safe_float(over_under_off.get("over_count"), 0.0)
                + _safe_float(over_under_off.get("under_count"), 0.0)
                + _safe_float(over_under_off.get("off_count"), 0.0)
            )
            / max(sample_profile["sample_size"], 1)
        ),
        "recurrence_sample_weight": _clamp01(multiset_recurrence.get("recurrence_load")),
    }

    feature_vector = [
        probability_profile["empirical_truth_probability"],
        probability_profile["empirical_indeterminate_probability"],
        probability_profile["empirical_false_probability"],
        _clamp01(refined["T_components"]["T2_weighted_truth_mean"]),
        _clamp01(refined["I_components"]["I2_truth_variance_load"]),
        _clamp01(refined["F_components"]["F2_weighted_false_mean"]),
        deterministic_confidence,
        statistical_confidence,
        topology_variable_completion["topology_class_probability"]["CT"],
        topology_variable_completion["topology_class_probability"]["NCT"],
        topology_variable_completion["topology_class_probability"]["ACT"],
        equivalence_probability,
        neighborhood_stability,
        topology_variable_completion["recurrence_sample_weight"],
    ]

    return {
        "model": "plithogenic_probability_statistics_topology_wiring_v1",
        "source": "Plithogenic Probability & Statistics, Neutrosophic Sets and Systems Vol. 43, 2021",
        "sample_profile": sample_profile,
        "probability_profile": probability_profile,
        "refined_statistical_components": refined,
        "deterministic_decision": deterministic_decision,
        "deterministic_confidence": deterministic_confidence,
        "statistical_confidence": statistical_confidence,
        "topology_variable_completion": topology_variable_completion,
        "feature_vector": [_clamp01(item) for item in feature_vector],
        "feature_dimension": len(feature_vector),
        "hierarchy": HIERARCHY,
        "research_boundary": (
            "alpha-local educational simulation only; empirical deterministic statistics, "
            "not clinical, diagnostic, predictive, production, or validated physical topology"
        ),
    }
