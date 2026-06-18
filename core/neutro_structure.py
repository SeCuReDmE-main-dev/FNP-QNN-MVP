"""NeutroStructure system metrics for runtime structures.

Source: Florentin Smarandache, "Structure, NeutroStructure, and AntiStructure
in Science". A structure is treated as a non-empty space with relations and
attributes; this module computes bounded structural T/I/F metrics from those
relations and attributes without replacing lower-level evidence.
"""

from __future__ import annotations

from itertools import product
from statistics import mean, pvariance
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence

from .neutro_algebra import HIERARCHY, tri_section_space_profile


INNER_LABELS = {"a", "inner", "true", "valid", "defined", "inside", "classical", "t", "relation", "attribute"}
NEUTRO_LABELS = {"neutroa", "neutro", "indeterminate", "undefined", "unknown", "partial", "i"}
ANTI_LABELS = {"antia", "anti", "outer", "false", "invalid", "outside", "f"}


def _bounded(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if number != number:
        return 0.0
    return max(0.0, min(1.0, number))


def _normalize_region(value: Any) -> str:
    if isinstance(value, Mapping):
        value = value.get("region", value.get("classification", value.get("status", value.get("label", value))))
    text = str(value).strip().lower()
    if text in INNER_LABELS:
        return "A"
    if text in NEUTRO_LABELS:
        return "neutroA"
    if text in ANTI_LABELS:
        return "antiA"
    return "neutroA"


def _safe_check(check: Any, sample: Any) -> str:
    if not callable(check):
        return _normalize_region(check)
    try:
        return _normalize_region(check(sample))
    except TypeError:
        if isinstance(sample, tuple):
            try:
                return _normalize_region(check(*sample))
            except Exception:
                return "neutroA"
        return "neutroA"
    except Exception:
        return "neutroA"


def _profile_classification(prefix: str, triplet: Mapping[str, Any]) -> str:
    if _bounded(triplet.get("T")) == 1.0:
        return f"classical_{prefix}"
    if _bounded(triplet.get("F")) == 1.0:
        return f"anti{prefix}"
    return f"neutro{prefix}"


def _profile_triplet(profile: Mapping[str, Any]) -> Dict[str, float]:
    return {
        "T": _bounded(profile.get("T", profile.get("T_system", 0.0))),
        "I": _bounded(profile.get("I", profile.get("I_system", 0.0))),
        "F": _bounded(profile.get("F", profile.get("F_system", 0.0))),
    }


def neutro_relation_profile(elements: Iterable[Any], relation_checks: Mapping[str, Any] | Sequence[Any]) -> Dict[str, Any]:
    """Classify relation checks over structure elements as T/I/F evidence."""

    element_list = list(elements)
    checks = relation_checks
    if isinstance(checks, Mapping):
        check_items = list(checks.items())
    else:
        check_items = [(f"relation_{index}", check) for index, check in enumerate(checks)]
    samples = list(product(element_list, repeat=2)) if element_list else [("empty", "empty")]
    witnesses: List[Dict[str, Any]] = []

    def classifier(item: tuple[str, Any]) -> str:
        name, sample = item
        check = dict(check_items).get(name)
        region = _safe_check(check, sample)
        witnesses.append({"relation": name, "sample": sample, "region": region})
        return region

    items = [(name, sample) for name, _ in check_items for sample in samples]
    if not items:
        items = [("missing_relation", ("empty", "empty"))]
        check_items = [("missing_relation", "neutroA")]
    profile = tri_section_space_profile(items, classifier)
    return {
        "model": "neutro_relation_profile_v1",
        "classification": _profile_classification("relation", profile),
        "T": profile["T"],
        "I": profile["I"],
        "F": profile["F"],
        "counts": profile["counts"],
        "relation_count": len(check_items),
        "sample_count": len(items),
        "witnesses": witnesses[:24],
        "hierarchy": HIERARCHY,
    }


def neutro_attribute_profile(elements: Iterable[Any], attribute_checks: Mapping[str, Any] | Sequence[Any]) -> Dict[str, Any]:
    """Classify attribute checks over structure elements as T/I/F evidence."""

    element_list = list(elements) or ["empty"]
    if isinstance(attribute_checks, Mapping):
        check_items = list(attribute_checks.items())
    else:
        check_items = [(f"attribute_{index}", check) for index, check in enumerate(attribute_checks)]
    witnesses: List[Dict[str, Any]] = []

    def classifier(item: tuple[str, Any]) -> str:
        name, element = item
        check = dict(check_items).get(name)
        region = _safe_check(check, element)
        witnesses.append({"attribute": name, "element": element, "region": region})
        return region

    items = [(name, element) for name, _ in check_items for element in element_list]
    if not items:
        items = [("missing_attribute", "empty")]
        check_items = [("missing_attribute", "neutroA")]
    profile = tri_section_space_profile(items, classifier)
    return {
        "model": "neutro_attribute_profile_v1",
        "classification": _profile_classification("attribute", profile),
        "T": profile["T"],
        "I": profile["I"],
        "F": profile["F"],
        "counts": profile["counts"],
        "attribute_count": len(check_items),
        "sample_count": len(items),
        "witnesses": witnesses[:24],
        "hierarchy": HIERARCHY,
    }


def neutrostructure_profile(
    space: Iterable[Any],
    relations: Mapping[str, Any] | Sequence[Any],
    attributes: Mapping[str, Any] | Sequence[Any],
) -> Dict[str, Any]:
    """Aggregate relation and attribute evidence into system T/I/F."""

    space_list = list(space) or ["empty"]
    relation_profile = relations if isinstance(relations, Mapping) and {"T", "I", "F"} <= set(relations) else neutro_relation_profile(space_list, relations)
    attribute_profile = attributes if isinstance(attributes, Mapping) and {"T", "I", "F"} <= set(attributes) else neutro_attribute_profile(space_list, attributes)
    relation_triplet = _profile_triplet(relation_profile)
    attribute_triplet = _profile_triplet(attribute_profile)

    t_system = _bounded((relation_triplet["T"] + attribute_triplet["T"]) / 2.0)
    i_system = _bounded((relation_triplet["I"] + attribute_triplet["I"]) / 2.0)
    f_system = _bounded((relation_triplet["F"] + attribute_triplet["F"]) / 2.0)
    has_neutro = relation_triplet["I"] > 0.0 or attribute_triplet["I"] > 0.0
    has_anti = relation_triplet["F"] > 0.0 or attribute_triplet["F"] > 0.0
    if t_system == 1.0 and i_system == 0.0 and f_system == 0.0:
        system_classification = "classical_structure"
    elif has_anti and has_neutro:
        system_classification = "hybrid_structure"
    elif has_anti:
        system_classification = "antistructure"
    elif has_neutro:
        system_classification = "neutrostructure"
    else:
        system_classification = "empty_structure_profile"

    feature_vector = [
        t_system,
        i_system,
        f_system,
        relation_triplet["T"],
        relation_triplet["I"],
        relation_triplet["F"],
        attribute_triplet["T"],
        attribute_triplet["I"],
        attribute_triplet["F"],
        _bounded(float(system_classification in {"neutrostructure", "hybrid_structure"})),
        _bounded(float(system_classification in {"antistructure", "hybrid_structure"})),
    ]
    return {
        "model": "neutrostructure_system_metrics_v1",
        "space_size": len(space_list),
        "T_system": t_system,
        "I_system": i_system,
        "F_system": f_system,
        "system_classification": system_classification,
        "relation_profile": relation_profile,
        "attribute_profile": attribute_profile,
        "feature_vector": [_bounded(item) for item in feature_vector],
        "feature_dimension": len(feature_vector),
        "hierarchy": HIERARCHY,
        "research_boundary": (
            "alpha-local structural health/readiness metadata only; not clinical truth, "
            "production reliability, validated quantum physics, or a proof engine"
        ),
    }


def _event_value(event: Any) -> float:
    value = getattr(event, "value", 0.0)
    return _bounded(value)


def _event_source(event: Any) -> str:
    return str(getattr(event, "source", ""))


def _event_duration(event: Any) -> float:
    return max(0.0, float(getattr(event, "duration", 0.0)))


def runtime_neutrostructure_profile(
    events: Sequence[Any],
    pairs: Sequence[Any],
    neutro_algebra_profile: Optional[Mapping[str, Any]] = None,
    plithogenic_topology_profile: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Build structural system metrics from runtime relations and attributes."""

    event_list = list(events)
    pair_list = list(pairs)
    space = [f"{getattr(event, 'modality', 'stimuli')}:{index}" for index, event in enumerate(event_list)] or ["empty"]
    event_by_space = dict(zip(space, event_list))
    pair_keys = {
        (str(getattr(pair, "source_modality", "")), str(getattr(pair, "target_modality", "")))
        for pair in pair_list
    }
    modalities = {str(getattr(event, "modality", "stimuli")) for event in event_list}

    def crossmodal_relation(left: str, right: str) -> str:
        if left == "empty" or right == "empty":
            return "neutroA"
        left_mod = left.split(":", 1)[0]
        right_mod = right.split(":", 1)[0]
        if left_mod == right_mod:
            return "A"
        return "A" if (left_mod, right_mod) in pair_keys else "neutroA"

    def algebraic_relation(_left: str, _right: str) -> str:
        if not neutro_algebra_profile:
            return "neutroA"
        classification = str(neutro_algebra_profile.get("classification", ""))
        if classification == "classical_algebra":
            return "A"
        if classification in {"antialgebra", "hybrid_neutroalgebra"}:
            return "antiA"
        return "neutroA"

    def plithogenic_topology_relation(_left: str, _right: str) -> str:
        if not plithogenic_topology_profile:
            return "neutroA"
        confidence = _bounded(plithogenic_topology_profile.get("deterministic_confidence", 0.0))
        if confidence >= 0.66:
            return "A"
        if confidence <= 0.2:
            return "antiA"
        return "neutroA"

    def modality_coverage_attribute(element: str) -> str:
        if element == "empty":
            return "neutroA"
        coverage = _bounded(len(modalities) / 4.0)
        if coverage >= 0.75:
            return "A"
        if coverage <= 0.25:
            return "antiA"
        return "neutroA"

    def value_stability_attribute(element: str) -> str:
        event = event_by_space.get(element)
        if event is None:
            return "neutroA"
        values = [_event_value(item) for item in event_list]
        dispersion = _bounded(pvariance(values) * 4.0) if len(values) > 1 else 0.0
        if dispersion <= 0.2:
            return "A"
        if dispersion >= 0.75:
            return "antiA"
        return "neutroA"

    def source_completeness_attribute(element: str) -> str:
        event = event_by_space.get(element)
        if event is None:
            return "neutroA"
        if _event_source(event):
            return "A"
        return "neutroA"

    def temporal_quality_attribute(element: str) -> str:
        event = event_by_space.get(element)
        if event is None:
            return "neutroA"
        duration = _event_duration(event)
        if duration > 0.0:
            return "A"
        return "neutroA"

    algebra_features = list((neutro_algebra_profile or {}).get("feature_vector") or [])
    algebra_integrity = mean([_bounded(item) for item in algebra_features]) if algebra_features else 0.5

    def algebra_integrity_attribute(_element: str) -> str:
        if algebra_integrity >= 0.66:
            return "A"
        if algebra_integrity <= 0.25:
            return "antiA"
        return "neutroA"

    profile = neutrostructure_profile(
        space,
        {
            "crossmodal_pair_relation": crossmodal_relation,
            "algebraic_operation_relation": algebraic_relation,
            "plithogenic_topology_relation": plithogenic_topology_relation,
        },
        {
            "modality_coverage_attribute": modality_coverage_attribute,
            "value_stability_attribute": value_stability_attribute,
            "source_completeness_attribute": source_completeness_attribute,
            "temporal_overlap_quality_attribute": temporal_quality_attribute,
            "algebraic_integrity_attribute": algebra_integrity_attribute,
        },
    )
    profile["runtime_mapping"] = {
        "space": "runtime events plus modality-index nodes",
        "relations": [
            "crossmodal pair relation",
            "algebraic operation relation",
            "plithogenic-topology decision relation",
        ],
        "attributes": [
            "modality coverage",
            "value stability",
            "source completeness",
            "temporal overlap quality",
            "algebraic integrity",
        ],
        "plithogenic_topology_annotated": plithogenic_topology_profile is not None,
        "neutro_algebra_annotated": neutro_algebra_profile is not None,
    }
    return profile
