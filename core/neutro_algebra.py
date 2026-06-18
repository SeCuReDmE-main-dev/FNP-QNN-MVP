"""NeutroAlgebra integrity profiles for runtime transformations.

The primitives here are deterministic, dependency-light inspections. They do
not prove algebraic laws globally; they classify the observed carrier,
operation, and sampled axiom behavior into classical, partial, neutro, anti, or
hybrid metadata for the simulator.
"""

from __future__ import annotations

from itertools import product
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


HIERARCHY = "I -> I_system^S -> D_f -> dF -> i_fractal"
UNDEFINED_MARKERS = {"", "undefined", "undef", "none", "null", "nan", "indeterminate", "unknown"}
INNER_LABELS = {"a", "inner", "true", "valid", "defined", "inside", "classical", "t"}
NEUTRO_LABELS = {"neutroa", "neutro", "indeterminate", "undefined", "unknown", "partial", "i"}
ANTI_LABELS = {"antia", "anti", "outer", "false", "invalid", "outside", "f"}


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _json_key(value: Any) -> str:
    if isinstance(value, tuple):
        return "(" + ", ".join(_json_key(item) for item in value) + ")"
    return str(value)


def _safe_call(func: Callable[..., Any], *args: Any) -> Tuple[bool, Any]:
    try:
        return True, func(*args)
    except Exception:
        return False, None


def _normalize_region(raw: Any) -> str:
    if isinstance(raw, Mapping):
        raw = raw.get("region", raw.get("classification", raw.get("status", raw.get("label", raw))))
    text = str(raw).strip().lower()
    if text in INNER_LABELS:
        return "A"
    if text in NEUTRO_LABELS:
        return "neutroA"
    if text in ANTI_LABELS:
        return "antiA"
    return "neutroA"


def _is_undefined(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in UNDEFINED_MARKERS
    return False


def _is_indeterminate_value(value: Any) -> bool:
    if _is_undefined(value):
        return True
    if isinstance(value, Mapping):
        return str(value.get("status", "")).strip().lower() in NEUTRO_LABELS
    if isinstance(value, (set, list, tuple)) and not isinstance(value, (str, bytes, bytearray)):
        return len(value) != 1
    if isinstance(value, str):
        lowered = value.strip().lower()
        return " or " in lowered or "|" in lowered or lowered.startswith("i:")
    return False


def _single_value(value: Any) -> Any:
    if isinstance(value, Mapping) and "value" in value:
        return value["value"]
    if isinstance(value, (set, list, tuple)) and len(value) == 1:
        return next(iter(value))
    return value


def _classify_value(value: Any, inner_space: set[Any], universe: set[Any]) -> str:
    if _is_indeterminate_value(value):
        return "neutroA"
    normalized = _single_value(value)
    if normalized in inner_space:
        return "A"
    if normalized in universe or universe:
        return "antiA"
    return "antiA"


def _triplet_from_regions(regions: Mapping[str, Sequence[Any]]) -> Dict[str, Any]:
    total = sum(len(items) for items in regions.values())
    denominator = max(1, total)
    t = _bounded(len(regions["A"]) / denominator)
    i = _bounded(len(regions["neutroA"]) / denominator)
    f = _bounded(len(regions["antiA"]) / denominator)
    if total == 0:
        classification = "empty_neutro_profile"
    elif t == 1.0:
        classification = "classical"
    elif f == 1.0:
        classification = "anti"
    elif i == 1.0:
        classification = "indeterminate"
    else:
        classification = "neutro"
    return {
        "T": t,
        "I": i,
        "F": f,
        "classification": classification,
        "counts": {key: len(value) for key, value in regions.items()},
        "exhaustive": total == denominator,
    }


def tri_section_space_profile(elements: Iterable[Any], classifier: Callable[[Any], Any]) -> Dict[str, Any]:
    """Map elements into A, neutroA, and antiA regions with bounded T/I/F."""

    regions: Dict[str, List[Any]] = {"A": [], "neutroA": [], "antiA": []}
    witnesses: List[Dict[str, Any]] = []
    for element in list(elements):
        ok, raw_region = _safe_call(classifier, element)
        region = _normalize_region(raw_region if ok else "neutroA")
        regions[region].append(element)
        witnesses.append({"element": element, "region": region})
    triplet = _triplet_from_regions(regions)
    return {
        "model": "neutroalgebra_tri_section_v1",
        **triplet,
        "regions": regions,
        "witnesses": witnesses,
        "hierarchy": HIERARCHY,
        "research_boundary": "alpha-local educational integrity metadata; not a formal proof engine",
    }


def _mapping_value(mapping: Mapping[Any, Any] | Callable[[Any], Any], key: Any) -> Tuple[bool, Any]:
    if callable(mapping):
        return _safe_call(mapping, key)
    if key in mapping:
        return True, mapping[key]
    if str(key) in mapping:
        return True, mapping[str(key)]
    return False, None


def neutro_function_profile(
    domain: Iterable[Any],
    codomain: Iterable[Any],
    universe: Iterable[Any],
    mapping: Mapping[Any, Any] | Callable[[Any], Any],
) -> Dict[str, Any]:
    """Classify a transform as total, partial, neutro, or anti function."""

    domain_values = list(domain)
    codomain_set = set(codomain)
    universe_set = set(universe) | codomain_set
    witnesses: List[Dict[str, Any]] = []

    def classifier(item: Any) -> str:
        defined, value = _mapping_value(mapping, item)
        if not defined:
            witnesses.append({"input": item, "output": None, "region": "neutroA", "reason": "undefined"})
            return "neutroA"
        region = _classify_value(value, codomain_set, universe_set)
        reason = "inside_codomain" if region == "A" else "indeterminate" if region == "neutroA" else "outside_codomain"
        witnesses.append({"input": item, "output": value, "region": region, "reason": reason})
        return region

    tri = tri_section_space_profile(domain_values, classifier)
    undefined_count = sum(1 for witness in witnesses if witness["reason"] == "undefined")
    outer_count = tri["counts"]["antiA"]
    indeterminate_count = tri["counts"]["neutroA"]
    if tri["T"] == 1.0:
        classification = "total_function"
    elif tri["F"] == 1.0:
        classification = "antifunction"
    elif outer_count == 0 and undefined_count == indeterminate_count and indeterminate_count > 0:
        classification = "partial_function"
    elif indeterminate_count == len(domain_values) and domain_values:
        classification = "indeterminate_function"
    else:
        classification = "neutrofunction"
    return {
        "model": "neutro_function_profile_v1",
        "classification": classification,
        "T": tri["T"],
        "I": tri["I"],
        "F": tri["F"],
        "counts": tri["counts"],
        "domain_size": len(domain_values),
        "codomain_size": len(codomain_set),
        "universe_size": len(universe_set),
        "witnesses": witnesses,
        "hierarchy": HIERARCHY,
    }


def _operation_value(operation: Mapping[Any, Any] | Callable[..., Any], args: Tuple[Any, ...]) -> Tuple[bool, Any]:
    if callable(operation):
        return _safe_call(operation, *args)
    for key in (args, str(args), ",".join(str(item) for item in args), _json_key(args)):
        if key in operation:
            return True, operation[key]
    return False, None


def neutro_operation_table_profile(
    carrier: Iterable[Any],
    universe: Iterable[Any],
    operation_table: Mapping[Any, Any] | Callable[..., Any],
) -> Dict[str, Any]:
    """Inspect observed operation outputs as inner, undefined, indeterminate, or outer."""

    carrier_values = list(carrier)
    carrier_set = set(carrier_values)
    universe_set = set(universe) | carrier_set
    tuples = list(product(carrier_values, repeat=2))
    witnesses: List[Dict[str, Any]] = []

    def classifier(args: Tuple[Any, Any]) -> str:
        defined, value = _operation_value(operation_table, args)
        if not defined:
            witnesses.append({"input": args, "output": None, "region": "neutroA", "reason": "undefined"})
            return "neutroA"
        region = _classify_value(value, carrier_set, universe_set)
        reason = "inner_defined" if region == "A" else "indeterminate" if region == "neutroA" else "outer_defined"
        witnesses.append({"input": args, "output": value, "region": region, "reason": reason})
        return region

    tri = tri_section_space_profile(tuples, classifier)
    undefined_count = sum(1 for witness in witnesses if witness["reason"] == "undefined")
    if tri["T"] == 1.0:
        classification = "total_operation"
    elif tri["F"] == 1.0:
        classification = "antioperation"
    elif tri["counts"]["antiA"] == 0 and undefined_count == tri["counts"]["neutroA"] and undefined_count > 0:
        classification = "partial_operation"
    else:
        classification = "neutrooperation"
    return {
        "model": "neutro_operation_table_profile_v1",
        "classification": classification,
        "T": tri["T"],
        "I": tri["I"],
        "F": tri["F"],
        "counts": tri["counts"],
        "arity": 2,
        "carrier_size": len(carrier_values),
        "universe_size": len(universe_set),
        "witnesses": witnesses,
        "hierarchy": HIERARCHY,
    }


def _resolved_operation_value(operation: Mapping[Any, Any] | Callable[..., Any], args: Tuple[Any, ...], carrier: set[Any]) -> Tuple[str, Any]:
    defined, value = _operation_value(operation, args)
    if not defined or _is_indeterminate_value(value):
        return "neutroA", None
    value = _single_value(value)
    if value in carrier:
        return "A", value
    return "antiA", value


def neutro_axiom_profile(
    carrier: Iterable[Any],
    operation: Mapping[Any, Any] | Callable[..., Any],
    axiom_name: str,
) -> Dict[str, Any]:
    """Sample closure, commutativity, associativity, idempotence, or identity laws."""

    carrier_values = list(carrier)
    carrier_set = set(carrier_values)
    axiom = axiom_name.strip().lower()
    witnesses: List[Dict[str, Any]] = []
    samples: List[Any]
    if axiom == "associativity":
        samples = list(product(carrier_values, repeat=3))
    elif axiom == "idempotence":
        samples = [(item,) for item in carrier_values]
    elif axiom == "identity":
        samples = [(candidate, item) for candidate in carrier_values for item in carrier_values]
    else:
        samples = list(product(carrier_values, repeat=2))

    def classifier(sample: Any) -> str:
        if axiom == "closure":
            region, value = _resolved_operation_value(operation, tuple(sample), carrier_set)
            result = "A" if region == "A" else region
            witnesses.append({"sample": sample, "region": result, "left": value, "right": None})
            return result
        if axiom == "commutativity":
            a, b = sample
            left_region, left = _resolved_operation_value(operation, (a, b), carrier_set)
            right_region, right = _resolved_operation_value(operation, (b, a), carrier_set)
            result = "neutroA" if "neutroA" in {left_region, right_region} else "A" if left_region == right_region == "A" and left == right else "antiA"
            witnesses.append({"sample": sample, "region": result, "left": left, "right": right})
            return result
        if axiom == "associativity":
            a, b, c = sample
            bc_region, bc = _resolved_operation_value(operation, (b, c), carrier_set)
            ab_region, ab = _resolved_operation_value(operation, (a, b), carrier_set)
            if "neutroA" in {bc_region, ab_region}:
                result = "neutroA"
                witnesses.append({"sample": sample, "region": result, "left": None, "right": None})
                return result
            left_region, left = _resolved_operation_value(operation, (a, bc), carrier_set)
            right_region, right = _resolved_operation_value(operation, (ab, c), carrier_set)
            result = "neutroA" if "neutroA" in {left_region, right_region} else "A" if left_region == right_region == "A" and left == right else "antiA"
            witnesses.append({"sample": sample, "region": result, "left": left, "right": right})
            return result
        if axiom == "idempotence":
            (a,) = sample
            region, value = _resolved_operation_value(operation, (a, a), carrier_set)
            result = "neutroA" if region == "neutroA" else "A" if region == "A" and value == a else "antiA"
            witnesses.append({"sample": sample, "region": result, "left": value, "right": a})
            return result
        if axiom == "identity":
            candidate, item = sample
            left_region, left = _resolved_operation_value(operation, (candidate, item), carrier_set)
            right_region, right = _resolved_operation_value(operation, (item, candidate), carrier_set)
            result = "neutroA" if "neutroA" in {left_region, right_region} else "A" if left == right == item else "antiA"
            witnesses.append({"sample": sample, "region": result, "left": left, "right": right})
            return result
        witnesses.append({"sample": sample, "region": "neutroA", "left": None, "right": None})
        return "neutroA"

    tri = tri_section_space_profile(samples, classifier)
    if tri["T"] == 1.0:
        classification = "classical_axiom"
    elif tri["F"] == 1.0:
        classification = "antiaxiom"
    else:
        classification = "neutroaxiom"
    return {
        "model": "neutro_axiom_profile_v1",
        "axiom": axiom,
        "classification": classification,
        "T": tri["T"],
        "I": tri["I"],
        "F": tri["F"],
        "counts": tri["counts"],
        "sample_count": len(samples),
        "witnesses": witnesses[:24],
        "hierarchy": HIERARCHY,
    }


def neutroalgebra_structure_profile(
    carrier: Iterable[Any],
    operations: Mapping[str, Mapping[Any, Any] | Callable[..., Any]],
    axioms: Iterable[str],
) -> Dict[str, Any]:
    """Aggregate operation and axiom profiles into a structure classification."""

    carrier_values = list(carrier)
    universe = set(carrier_values)
    for operation in operations.values():
        if isinstance(operation, Mapping):
            for value in operation.values():
                if not _is_indeterminate_value(value):
                    universe.add(_single_value(value))
    operation_profiles = {
        name: neutro_operation_table_profile(carrier_values, universe, operation)
        for name, operation in operations.items()
    }
    axiom_profiles: Dict[str, Dict[str, Any]] = {}
    for operation_name, operation in operations.items():
        for axiom in axioms:
            axiom_profiles[f"{operation_name}.{axiom}"] = neutro_axiom_profile(carrier_values, operation, axiom)

    op_classes = {profile["classification"] for profile in operation_profiles.values()}
    axiom_classes = {profile["classification"] for profile in axiom_profiles.values()}
    has_anti = "antioperation" in op_classes or "antiaxiom" in axiom_classes
    has_neutro = "neutrooperation" in op_classes or "neutroaxiom" in axiom_classes
    has_partial = "partial_operation" in op_classes
    all_classical = op_classes <= {"total_operation"} and axiom_classes <= {"classical_axiom"}
    if all_classical:
        classification = "classical_algebra"
    elif has_partial and not has_anti:
        classification = "partial_algebra"
    elif has_anti and not has_neutro and not has_partial:
        classification = "antialgebra"
    elif has_anti and (has_neutro or has_partial):
        classification = "hybrid_neutroalgebra"
    else:
        classification = "neutroalgebra"

    op_t = [profile["T"] for profile in operation_profiles.values()] or [0.0]
    op_i = [profile["I"] for profile in operation_profiles.values()] or [1.0]
    op_f = [profile["F"] for profile in operation_profiles.values()] or [0.0]
    ax_t = [profile["T"] for profile in axiom_profiles.values()] or [0.0]
    ax_i = [profile["I"] for profile in axiom_profiles.values()] or [1.0]
    ax_f = [profile["F"] for profile in axiom_profiles.values()] or [0.0]
    feature_vector = [
        _bounded(sum(op_t) / len(op_t)),
        _bounded(sum(op_i) / len(op_i)),
        _bounded(sum(op_f) / len(op_f)),
        _bounded(sum(ax_t) / len(ax_t)),
        _bounded(sum(ax_i) / len(ax_i)),
        _bounded(sum(ax_f) / len(ax_f)),
        _bounded(float(has_neutro or has_partial)),
        _bounded(float(has_anti)),
    ]
    return {
        "model": "neutroalgebra_structure_profile_v1",
        "classification": classification,
        "is_neutroalgebra_generalization": classification in {"partial_algebra", "neutroalgebra", "hybrid_neutroalgebra"},
        "carrier": carrier_values,
        "operation_profiles": operation_profiles,
        "axiom_profiles": axiom_profiles,
        "feature_vector": feature_vector,
        "feature_dimension": len(feature_vector),
        "hierarchy": HIERARCHY,
        "research_boundary": "alpha-local educational algebraic-integrity annotation; not a symbolic proof engine",
    }


def neutroalgebra_runtime_profile(
    events: Sequence[Any],
    pairs: Sequence[Any],
    plithogenic_topology_profile: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a compact algebraic integrity profile from runtime modalities."""

    modalities = sorted({str(getattr(event, "modality", "stimuli")) for event in events}) or ["stimuli"]
    carrier = modalities
    universe = sorted(set(modalities) | {"outer_runtime_state"})
    operation_table: Dict[Tuple[str, str], Any] = {}
    for pair in pairs:
        source = str(getattr(pair, "source_modality", "stimuli"))
        target = str(getattr(pair, "target_modality", "stimuli"))
        output = target if source in carrier and target in carrier else "outer_runtime_state"
        key = (source, target)
        if key in operation_table and operation_table[key] != output:
            operation_table[key] = {operation_table[key], output}
        else:
            operation_table[key] = output
    if plithogenic_topology_profile is not None:
        decision = str((plithogenic_topology_profile.get("deterministic_decision") or {}).get("class", ""))
        if decision and decision not in carrier:
            operation_table[(carrier[0], carrier[-1])] = "outer_runtime_state"

    operation_profile = neutro_operation_table_profile(carrier, universe, operation_table)
    structure = neutroalgebra_structure_profile(
        carrier,
        {"runtime_fusion": operation_table},
        ["closure", "commutativity", "associativity"],
    )
    structure["runtime_mapping"] = {
        "carrier": "event modalities",
        "operation": "observed crossmodal transition/fusion table",
        "axioms": ["closure", "commutativity", "associativity"],
        "plithogenic_topology_annotated": plithogenic_topology_profile is not None,
    }
    structure["operation_profile"] = operation_profile
    return structure
