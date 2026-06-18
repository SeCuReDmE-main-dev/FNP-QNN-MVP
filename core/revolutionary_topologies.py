"""Revolutionary topology primitives for the local simulator.

The functions in this module are bounded educational simulation helpers
inspired by Smarandache's revolutionary topologies monograph. They do not
implement a complete mathematical topology engine; they expose small,
source-attributed profiles that help the runtime decide whether observations
preserve structure under local deformation.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
import math
from typing import Any, Dict, Mapping, Optional, Sequence


SOURCE_LABEL = "Foundation of Revolutionary Topologies"
SOURCE_URL = "https://fs.unm.edu/TT/RevolutionaryTopologies.pdf"
SOURCE_HIERARCHY = "I -> I_system^S -> D_f -> dF -> i_fractal"
RESEARCH_BOUNDARY = (
    "alpha-local educational simulation only; not clinical, diagnostic, "
    "therapeutic, security, production-public, or validated physical topology"
)
CONCEPTS = [
    "neutro_anti_topological_axiom_profile",
    "refined_neutrosophic_topology_components",
    "superhyper_nested_topology_profile",
    "nonstandard_neighborhood_deformation_tolerance",
    "over_under_off_multiset_recurrence_topology",
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


def _event_value(event: Any) -> float:
    return _finite_float(_field(event, "value", 0.0))


def _event_key(event: Any) -> tuple[str, float]:
    return (str(_field(event, "modality", "stimuli")), round(_event_timestamp(event), 6))


def _powerset_sets(items: Sequence[Any]) -> set[frozenset[Any]]:
    values = list(dict.fromkeys(items))
    result: set[frozenset[Any]] = set()
    for mask in range(1 << len(values)):
        result.add(frozenset(values[index] for index in range(len(values)) if mask & (1 << index)))
    return result


def topological_axiom_profile(universe: Sequence[Any], open_sets: Sequence[Sequence[Any]]) -> Dict[str, Any]:
    """Score basic topology axioms as classical, neutro, or anti behavior."""
    universe_set = frozenset(universe)
    normalized = {frozenset(item) for item in open_sets}
    empty_present = frozenset() in normalized
    universe_present = universe_set in normalized
    pair_count = 0
    intersection_hits = 0
    union_hits = 0
    for left in normalized:
        for right in normalized:
            pair_count += 1
            if left.intersection(right) in normalized:
                intersection_hits += 1
            if left.union(right) in normalized:
                union_hits += 1
    total_checks = 2 + (2 * pair_count)
    passed = int(empty_present) + int(universe_present) + intersection_hits + union_hits
    truth = _clamp01(passed / total_checks if total_checks else 0.0)
    missing_foundations = int(not empty_present) + int(not universe_present)
    closure_failures = (2 * pair_count) - intersection_hits - union_hits
    anti = _clamp01((missing_foundations + closure_failures) / total_checks if total_checks else 0.0)
    neutro = _clamp01(1.0 - truth - anti)
    classification = "CT"
    if anti >= 0.5:
        classification = "ACT"
    elif truth < 1.0 or neutro > 0.0:
        classification = "NCT"
    return {
        "model": "revolutionary_topological_axiom_profile",
        "source": SOURCE_LABEL,
        "source_url": SOURCE_URL,
        "classification": classification,
        "CT": truth,
        "NCT": neutro,
        "ACT": anti,
        "empty_present": empty_present,
        "universe_present": universe_present,
        "finite_intersection_score": _clamp01(intersection_hits / pair_count if pair_count else 0.0),
        "union_score": _clamp01(union_hits / pair_count if pair_count else 0.0),
        "open_set_count": len(normalized),
        "hierarchy": SOURCE_HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


def nonstandard_neighborhood_profile(
    value: float,
    center: float,
    epsilon: float,
    mode: str = "binad",
) -> Dict[str, Any]:
    """Return a bounded left/right/binad neighborhood membership profile."""
    eps = max(abs(_finite_float(epsilon, 0.0)), 1e-12)
    distance = _finite_float(value) - _finite_float(center)
    mode = str(mode or "binad").lower()
    if mode == "left":
        in_neighborhood = -eps <= distance <= 0.0
    elif mode == "right":
        in_neighborhood = 0.0 <= distance <= eps
    elif mode == "pierced_binad":
        in_neighborhood = 0.0 < abs(distance) <= eps
    else:
        mode = "binad"
        in_neighborhood = abs(distance) <= eps
    closeness = _clamp01(1.0 - (abs(distance) / eps))
    return {
        "model": "nonstandard_neighborhood_profile",
        "source": SOURCE_LABEL,
        "source_url": SOURCE_URL,
        "mode": mode,
        "value": _finite_float(value),
        "center": _finite_float(center),
        "epsilon": eps,
        "signed_distance": distance,
        "in_neighborhood": bool(in_neighborhood),
        "membership": closeness if in_neighborhood else 0.0,
        "hierarchy": SOURCE_HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


def _component_count(nodes: set[int], adjacency: Mapping[int, set[int]]) -> int:
    if not nodes:
        return 0
    unseen = set(nodes)
    count = 0
    while unseen:
        count += 1
        start = unseen.pop()
        queue: deque[int] = deque([start])
        while queue:
            current = queue.popleft()
            for neighbor in adjacency.get(current, set()):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    queue.append(neighbor)
    return count


def _attribute_index(events: Sequence[Any]) -> dict[tuple[str, float], int]:
    return {_event_key(event): index for index, event in enumerate(events)}


def _nearest_index(events: Sequence[Any], modality: str, timestamp: float) -> Optional[int]:
    candidates = [
        (index, abs(_event_timestamp(event) - timestamp))
        for index, event in enumerate(events)
        if str(_field(event, "modality", "stimuli")) == modality
    ]
    if not candidates:
        return None
    index, delta = min(candidates, key=lambda item: item[1])
    return index if delta <= 1.0 else None


def deformation_invariant_signature(events: Sequence[Any], pairs: Sequence[Any]) -> Dict[str, Any]:
    """Build graph invariants used as deformation-stability metadata."""
    nodes = set(range(len(events)))
    adjacency: dict[int, set[int]] = defaultdict(set)
    index_by_key = _attribute_index(events)
    edge_keys: set[tuple[int, int]] = set()
    for pair in pairs:
        source_modality = str(_field(pair, "source_modality", ""))
        target_modality = str(_field(pair, "target_modality", ""))
        source_time = round(_finite_float(_field(pair, "timestamp1", 0.0)), 6)
        target_time = round(_finite_float(_field(pair, "timestamp2", 0.0)), 6)
        left = index_by_key.get((source_modality, source_time))
        right = index_by_key.get((target_modality, target_time))
        if left is None:
            left = _nearest_index(events, source_modality, source_time)
        if right is None:
            right = _nearest_index(events, target_modality, target_time)
        if left is None or right is None or left == right:
            continue
        edge = tuple(sorted((left, right)))
        edge_keys.add(edge)
        adjacency[left].add(right)
        adjacency[right].add(left)
    component_count = _component_count(nodes, adjacency)
    edge_count = len(edge_keys)
    cycle_rank = max(0, edge_count - len(nodes) + component_count)
    modality_counts = Counter(str(_field(event, "modality", "stimuli")) for event in events)
    values = [_clamp01(_event_value(event)) for event in events]
    durations = [_clamp01(_event_duration(event) / 4.0) for event in events]
    stability = _clamp01(1.0 - (cycle_rank / max(1.0, len(nodes))))
    return {
        "model": "deformation_invariant_signature",
        "source": SOURCE_LABEL,
        "source_url": SOURCE_URL,
        "node_count": len(nodes),
        "edge_count": edge_count,
        "connected_components": component_count,
        "cycle_rank": cycle_rank,
        "modality_coverage": dict(sorted(modality_counts.items())),
        "average_value": _clamp01(sum(values) / len(values) if values else 0.0),
        "average_duration_signal": _clamp01(sum(durations) / len(durations) if durations else 0.0),
        "deformation_stability": stability,
        "equivalence_hint": "same selected invariants can be treated as same structure under local deformation",
        "hierarchy": SOURCE_HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


def refined_topology_components(events: Sequence[Any], pairs: Sequence[Any]) -> Dict[str, Any]:
    """Split runtime evidence into refined T/I/F topology subcomponents."""
    values = [_event_value(event) for event in events]
    bounded_values = [_clamp01(value) for value in values]
    durations = [_event_duration(event) for event in events]
    source_count = len({str(_field(event, "source", "")) for event in events if str(_field(event, "source", ""))})
    modality_count = len({str(_field(event, "modality", "stimuli")) for event in events})
    pair_overlaps = [_clamp01(_field(pair, "overlap_score", 0.0)) for pair in pairs]
    raw_over = sum(1 for value in values if value > 1.0)
    raw_under = sum(1 for value in values if 0.0 <= value <= 1.0)
    raw_off = sum(1 for value in values if value < 0.0)
    repeated_labels = Counter(str(_field(event, "label", "")) for event in events)
    recurrence = sum(count - 1 for count in repeated_labels.values() if count > 1)
    value_truth = _clamp01(sum(bounded_values) / len(bounded_values) if bounded_values else 0.0)
    temporal_truth = _clamp01(sum(_clamp01(duration / 4.0) for duration in durations) / len(durations) if durations else 0.0)
    source_truth = _clamp01(source_count / max(1, len(events)))
    local_indeterminacy = _clamp01(1.0 - abs(value_truth - (1.0 - value_truth)))
    contradiction_indeterminacy = _clamp01(sum(pair_overlaps) / max(1, len(pair_overlaps)))
    recurrence_indeterminacy = _clamp01(recurrence / max(1, len(events)))
    value_falsity = _clamp01(1.0 - value_truth)
    topology_falsity = _clamp01((raw_over + raw_off) / max(1, len(values)))
    return {
        "model": "refined_neutrosophic_topology_components",
        "source": SOURCE_LABEL,
        "source_url": SOURCE_URL,
        "T_components": {
            "T_value": value_truth,
            "T_temporal": temporal_truth,
            "T_source": source_truth,
        },
        "I_components": {
            "I_system_component": local_indeterminacy,
            "I_pair_overlap": contradiction_indeterminacy,
            "I_multiset_recurrence": recurrence_indeterminacy,
            "D_f": local_indeterminacy,
            "dF": _clamp01((local_indeterminacy + recurrence_indeterminacy) / 2.0),
            "i_fractal": None,
        },
        "F_components": {
            "F_value": value_falsity,
            "F_over_under_off_load": topology_falsity,
        },
        "over_under_off": {
            "over_count": raw_over,
            "under_count": raw_under,
            "off_count": raw_off,
            "over_load": _clamp01(raw_over / max(1, len(values))),
            "under_load": _clamp01(raw_under / max(1, len(values))),
            "off_load": _clamp01(raw_off / max(1, len(values))),
        },
        "multiset_recurrence": {
            "repeated_label_count": recurrence,
            "recurrence_load": recurrence_indeterminacy,
        },
        "nested_profile": {
            "event_level_count": len(events),
            "modality_level_count": modality_count,
            "pair_level_count": len(pairs),
        },
        "hierarchy": SOURCE_HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


def _runtime_open_sets(events: Sequence[Any]) -> tuple[list[str], list[list[str]]]:
    universe = [f"e{index}" for index in range(len(events))]
    open_sets: list[list[str]] = [[]]
    if universe:
        open_sets.append(universe)
    by_modality: dict[str, list[str]] = defaultdict(list)
    for index, event in enumerate(events):
        by_modality[str(_field(event, "modality", "stimuli"))].append(f"e{index}")
    open_sets.extend(by_modality.values())
    return universe, open_sets


def revolutionary_topology_runtime_profile(events: Sequence[Any], pairs: Sequence[Any]) -> Dict[str, Any]:
    """Compute the opt-in topology profile at the runtime fusion boundary."""
    universe, open_sets = _runtime_open_sets(events)
    axiom_profile = topological_axiom_profile(universe, open_sets)
    signature = deformation_invariant_signature(events, pairs)
    refined = refined_topology_components(events, pairs)
    values = [_event_value(event) for event in events]
    center = sum(values) / len(values) if values else 0.0
    neighborhoods = [
        nonstandard_neighborhood_profile(value, center, epsilon=0.15, mode="binad")
        for value in values[:16]
    ]
    neighborhood_memberships = [item["membership"] for item in neighborhoods]
    T = refined["T_components"]
    I = refined["I_components"]
    F = refined["F_components"]
    feature_vector = [
        axiom_profile["CT"],
        axiom_profile["NCT"],
        axiom_profile["ACT"],
        _clamp01(signature["deformation_stability"]),
        _clamp01(signature["cycle_rank"] / max(1.0, signature["node_count"])),
        _clamp01(signature["connected_components"] / max(1.0, signature["node_count"])),
        _clamp01(sum(T.values()) / len(T)),
        _clamp01((I["I_system_component"] + I["I_pair_overlap"] + I["I_multiset_recurrence"]) / 3.0),
        _clamp01(sum(F.values()) / len(F)),
        _clamp01(sum(neighborhood_memberships) / len(neighborhood_memberships) if neighborhood_memberships else 0.0),
        refined["over_under_off"]["over_load"],
        refined["over_under_off"]["off_load"],
    ]
    return {
        "model": "revolutionary_topology_runtime_v1",
        "source": SOURCE_LABEL,
        "source_url": SOURCE_URL,
        "concepts": CONCEPTS,
        "simulator_gap": (
            "Runtime could encode values, contradiction, and fractal carriers, but it did not "
            "surface whether selected structural invariants survive local deformation before LVFM/QNN."
        ),
        "topological_axiom_profile": axiom_profile,
        "deformation_signature": signature,
        "refined_components": refined,
        "nonstandard_neighborhoods": neighborhoods,
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
    "deformation_invariant_signature",
    "nonstandard_neighborhood_profile",
    "refined_topology_components",
    "revolutionary_topology_runtime_profile",
    "topological_axiom_profile",
]
