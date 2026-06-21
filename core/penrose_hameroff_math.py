"""Bounded Penrose/Hameroff study profiles for the alpha-local simulator.

These functions are source-attributed educational metadata. They do not claim
validated quantum gravity, biological consciousness, clinical behavior, or a
physical Orch OR implementation.
"""

from __future__ import annotations

import math
from statistics import mean
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence


HBAR_JOULE_SECOND = 1.054571817e-34
HIERARCHY = "I -> I_system^S -> D_f -> dF -> i_fractal"
RESEARCH_BOUNDARY = (
    "alpha-local educational simulation only; not a consciousness proof, "
    "clinical system, physical quantum-gravity engine, security system, or "
    "production-public claim"
)


def _finite_float(value: Any, label: str) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be numeric")
    if not math.isfinite(numeric):
        raise ValueError(f"{label} must be finite")
    return numeric


def _optional_nonnegative(value: Any, label: str) -> Optional[float]:
    if value is None:
        return None
    numeric = _finite_float(value, label)
    if numeric < 0.0:
        raise ValueError(f"{label} must be non-negative")
    return numeric


def _bounded(value: Any) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(numeric):
        return 0.0
    return max(0.0, min(1.0, numeric))


def _positive_scale(value: Optional[float], scale: float = 1.0) -> float:
    if value is None or value <= 0.0:
        return 0.0
    scaled = value / max(scale, 1e-300)
    return _bounded(scaled / (1.0 + scaled))


def _mean_duration(events: Sequence[Any]) -> Optional[float]:
    durations = []
    for event in events:
        duration = getattr(event, "duration", None)
        if duration is None:
            continue
        try:
            numeric = float(duration)
        except (TypeError, ValueError):
            continue
        if math.isfinite(numeric) and numeric >= 0.0:
            durations.append(numeric)
    return float(mean(durations)) if durations else None


def _mean_pair_overlap(pairs: Sequence[Any]) -> float:
    overlaps = []
    for pair in pairs:
        value = getattr(pair, "overlap_score", None)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            continue
        if math.isfinite(numeric):
            overlaps.append(_bounded(numeric))
    return float(mean(overlaps)) if overlaps else 0.0


def objective_reduction_profile(E_delta_joule: Any, reference_time_s: Optional[float] = None) -> Dict[str, Any]:
    """Return a bounded profile for Penrose-style objective reduction timing."""

    energy = _finite_float(E_delta_joule, "E_delta_joule")
    reference = _optional_nonnegative(reference_time_s, "reference_time_s")
    if energy <= 0.0:
        return {
            "model": "penrose_objective_reduction_v1",
            "source_ids": ["PENROSE_GRAVITY_REDUCTION_1996", "PENROSE_GRAVITIZATION_QM_2014"],
            "E_delta_joule": energy,
            "hbar_joule_second": HBAR_JOULE_SECOND,
            "tau_s": None,
            "reference_time_s": reference,
            "finite_reduction_threshold": False,
            "reference_meets_threshold": False,
            "reduction_pressure": 0.0,
            "feature_vector": [0.0, 0.0, 0.0, _positive_scale(reference)],
            "hierarchy": HIERARCHY,
            "research_boundary": RESEARCH_BOUNDARY,
            "interpretation": "No finite objective-reduction threshold is produced for non-positive self-energy.",
        }

    tau_s = HBAR_JOULE_SECOND / energy
    if reference is None:
        reduction_pressure = _positive_scale(1.0 / tau_s)
        reference_meets_threshold = False
    else:
        reduction_pressure = _bounded(reference / tau_s)
        reference_meets_threshold = reference >= tau_s
    return {
        "model": "penrose_objective_reduction_v1",
        "source_ids": ["PENROSE_GRAVITY_REDUCTION_1996", "PENROSE_GRAVITIZATION_QM_2014"],
        "E_delta_joule": energy,
        "hbar_joule_second": HBAR_JOULE_SECOND,
        "tau_s": tau_s,
        "reference_time_s": reference,
        "finite_reduction_threshold": True,
        "reference_meets_threshold": reference_meets_threshold,
        "reduction_pressure": reduction_pressure,
        "feature_vector": [
            _positive_scale(energy, HBAR_JOULE_SECOND),
            _positive_scale(1.0 / tau_s),
            reduction_pressure,
            _positive_scale(reference),
        ],
        "hierarchy": HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
        "interpretation": "Uses tau_s = hbar / E_delta as local educational timing metadata.",
    }


def orchestration_profile(coherence_time_s: Any, reduction_time_s: Any, damping: float = 0.0) -> Dict[str, Any]:
    """Compare local coherence metadata to an objective-reduction time scale."""

    coherence = _optional_nonnegative(coherence_time_s, "coherence_time_s")
    reduction = _optional_nonnegative(reduction_time_s, "reduction_time_s")
    damping_value = _bounded(_finite_float(damping, "damping"))
    if coherence is None or reduction is None or reduction <= 0.0:
        alignment_ratio = 0.0
        coherence_meets_threshold = False
    else:
        alignment_ratio = coherence / reduction
        coherence_meets_threshold = coherence >= reduction
    effective_alignment = _bounded(alignment_ratio) * (1.0 - damping_value)
    if not coherence_meets_threshold:
        classification = "coherence_below_or_threshold"
    elif damping_value >= 0.5:
        classification = "damped_orchestration_candidate"
    else:
        classification = "coherence_meets_or_threshold"
    return {
        "model": "hameroff_penrose_orchestration_v1",
        "source_ids": ["HAMEROFF_PENROSE_ORCH_OR_2014"],
        "coherence_time_s": coherence,
        "reduction_time_s": reduction,
        "damping": damping_value,
        "alignment_ratio": alignment_ratio,
        "effective_alignment": effective_alignment,
        "coherence_meets_threshold": coherence_meets_threshold,
        "classification": classification,
        "feature_vector": [
            _positive_scale(coherence),
            _positive_scale(reduction),
            _bounded(alignment_ratio),
            damping_value,
            effective_alignment,
            float(coherence_meets_threshold),
        ],
        "hierarchy": HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
        "interpretation": "Local Orch OR-style timing comparison only; not a consciousness claim.",
    }


def _spin_to_double(value: Any, label: str) -> int:
    numeric = _finite_float(value, label)
    if numeric < 0.0:
        raise ValueError(f"{label} must be non-negative")
    doubled = round(numeric * 2.0)
    if not math.isclose(numeric * 2.0, float(doubled), rel_tol=0.0, abs_tol=1e-9):
        raise ValueError(f"{label} must be an integer or half-integer spin label")
    return int(doubled)


def spin_network_admissibility_profile(vertices: Iterable[Sequence[Any]]) -> Dict[str, Any]:
    """Check 3-valent Penrose-style spin-network admissibility constraints."""

    vertex_list = list(vertices or [])
    reports = []
    for index, vertex in enumerate(vertex_list):
        labels = list(vertex)
        if len(labels) != 3:
            reports.append(
                {
                    "index": index,
                    "labels": labels,
                    "valid": False,
                    "parity_admissible": False,
                    "triangle_admissible": False,
                    "reason": "vertex must contain exactly three spin labels",
                }
            )
            continue
        doubled = [_spin_to_double(label, f"vertices[{index}]") for label in labels]
        parity = sum(doubled) % 2 == 0
        triangle = (
            doubled[0] + doubled[1] >= doubled[2]
            and doubled[0] + doubled[2] >= doubled[1]
            and doubled[1] + doubled[2] >= doubled[0]
        )
        reports.append(
            {
                "index": index,
                "labels": labels,
                "doubled_spin_labels": doubled,
                "valid": parity and triangle,
                "parity_admissible": parity,
                "triangle_admissible": triangle,
            }
        )
    total = len(reports)
    admissible = sum(1 for report in reports if report["valid"])
    parity_count = sum(1 for report in reports if report["parity_admissible"])
    triangle_count = sum(1 for report in reports if report["triangle_admissible"])
    if total == 0:
        admissible_fraction = parity_fraction = triangle_fraction = 0.0
    else:
        admissible_fraction = admissible / total
        parity_fraction = parity_count / total
        triangle_fraction = triangle_count / total
    return {
        "model": "penrose_spin_network_admissibility_v1",
        "source_ids": ["PENROSE_SPIN_NETWORK_SOURCES"],
        "vertex_count": total,
        "admissible_count": admissible,
        "admissible_fraction": admissible_fraction,
        "parity_fraction": parity_fraction,
        "triangle_fraction": triangle_fraction,
        "vertices": reports,
        "feature_vector": [
            admissible_fraction,
            parity_fraction,
            triangle_fraction,
            1.0 - admissible_fraction if total else 0.0,
            _positive_scale(float(total), 16.0),
        ],
        "hierarchy": HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
        "interpretation": "Combinatorial admissibility metadata only, not a space-time reconstruction.",
    }


def twistor_nonlocality_profile(
    entanglement_strength: Any,
    reduction_pressure: Any,
    gravitational_context: Any = None,
) -> Dict[str, Any]:
    """Return bounded metadata for Penrose Bell nonlocality/twistor context."""

    entanglement = _bounded(_finite_float(entanglement_strength, "entanglement_strength"))
    pressure = _bounded(_finite_float(reduction_pressure, "reduction_pressure"))
    if gravitational_context is None:
        context_score = 0.0
    elif isinstance(gravitational_context, Mapping):
        context_score = _bounded(
            mean([_bounded(value) for value in gravitational_context.values()]) if gravitational_context else 0.0
        )
    elif isinstance(gravitational_context, (int, float)):
        context_score = _bounded(gravitational_context)
    else:
        context_score = 0.5 if str(gravitational_context).strip() else 0.0
    nonlocality_score = _bounded((entanglement + pressure + context_score) / 3.0)
    return {
        "model": "penrose_twistor_nonlocality_context_v1",
        "source_ids": ["PENROSE_BELL_NONLOCALITY_2015", "PENROSE_SPIN_NETWORK_SOURCES"],
        "entanglement_strength": entanglement,
        "reduction_pressure": pressure,
        "gravitational_context_score": context_score,
        "nonlocality_context_score": nonlocality_score,
        "feature_vector": [entanglement, pressure, context_score, nonlocality_score],
        "hierarchy": HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
        "interpretation": "Twistor/nonlocality study metadata only; not a validated palatial-twistor model.",
    }


def microtubule_signal_profile(
    frequency_hz: Optional[float] = None,
    diffusion_nm: Optional[float] = None,
    anesthetic_damping: Optional[float] = None,
) -> Dict[str, Any]:
    """Return bounded Hameroff-study metadata for microtubule-like signals."""

    frequency = _optional_nonnegative(frequency_hz, "frequency_hz")
    diffusion = _optional_nonnegative(diffusion_nm, "diffusion_nm")
    damping = _bounded(_finite_float(anesthetic_damping, "anesthetic_damping")) if anesthetic_damping is not None else 0.0
    frequency_score = _positive_scale(frequency, 1e9)
    diffusion_score = _positive_scale(diffusion, 1000.0)
    supplied = [score for score, value in ((frequency_score, frequency), (diffusion_score, diffusion)) if value is not None]
    base_signal = float(mean(supplied)) if supplied else 0.0
    signal_score = _bounded(base_signal * (1.0 - damping))
    return {
        "model": "hameroff_microtubule_signal_context_v1",
        "source_ids": ["HAMEROFF_PENROSE_ORCH_OR_2014"],
        "frequency_hz": frequency,
        "diffusion_nm": diffusion,
        "anesthetic_damping": damping,
        "frequency_score": frequency_score,
        "diffusion_score": diffusion_score,
        "signal_score": signal_score,
        "feature_vector": [frequency_score, diffusion_score, damping, signal_score],
        "hierarchy": HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
        "interpretation": "Microtubule/Orch OR study metadata only; not biological validation.",
    }


def penrose_hameroff_runtime_profile(
    events: Sequence[Any],
    pairs: Sequence[Any],
    *,
    objective_reduction_energy_joule: Optional[float] = None,
    coherence_time_s: Optional[float] = None,
    anesthetic_damping: Optional[float] = None,
    microtubule_frequency_hz: Optional[float] = None,
    spin_network_vertices: Optional[Iterable[Sequence[Any]]] = None,
) -> Dict[str, Any]:
    """Build a combined opt-in Penrose/Hameroff runtime profile."""

    event_list = list(events)
    pair_list = list(pairs)
    coherence = _optional_nonnegative(coherence_time_s, "coherence_time_s")
    if coherence is None:
        coherence = _mean_duration(event_list)
    energy = 0.0 if objective_reduction_energy_joule is None else objective_reduction_energy_joule
    objective = objective_reduction_profile(energy, reference_time_s=coherence)
    orchestration = orchestration_profile(
        coherence,
        objective["tau_s"],
        damping=0.0 if anesthetic_damping is None else anesthetic_damping,
    )
    spin = spin_network_admissibility_profile(spin_network_vertices or [])
    twistor = twistor_nonlocality_profile(
        _mean_pair_overlap(pair_list),
        objective["reduction_pressure"],
        {
            "finite_reduction_threshold": float(objective["finite_reduction_threshold"]),
            "coherence_meets_threshold": float(orchestration["coherence_meets_threshold"]),
        },
    )
    microtubule = microtubule_signal_profile(
        frequency_hz=microtubule_frequency_hz,
        diffusion_nm=None,
        anesthetic_damping=anesthetic_damping,
    )
    feature_vector = [
        objective["reduction_pressure"],
        orchestration["effective_alignment"],
        spin["admissible_fraction"],
        twistor["nonlocality_context_score"],
        microtubule["signal_score"],
        _positive_scale(float(len(event_list)), 100.0),
        _positive_scale(float(len(pair_list)), 200.0),
        microtubule["anesthetic_damping"],
    ]
    return {
        "model": "penrose_hameroff_runtime_profile_v1",
        "source_ids": [
            "PENROSE_GRAVITY_REDUCTION_1996",
            "PENROSE_QC_ENTANGLEMENT_REDUCTION_1998",
            "PENROSE_GRAVITIZATION_QM_2014",
            "PENROSE_BELL_NONLOCALITY_2015",
            "PENROSE_SPIN_NETWORK_SOURCES",
            "HAMEROFF_PENROSE_ORCH_OR_2014",
        ],
        "objective_reduction": objective,
        "orchestration": orchestration,
        "spin_network": spin,
        "twistor_nonlocality": twistor,
        "microtubule_signal": microtubule,
        "feature_vector": [_bounded(item) for item in feature_vector],
        "feature_dimension": len(feature_vector),
        "runtime_mapping": {
            "events": "coherence fallback uses mean runtime event duration when not provided",
            "pairs": "entanglement context uses mean crossmodal overlap as local metadata",
            "qnn": "feature vector is appended only when penrose_hameroff_enabled=true",
        },
        "hierarchy": HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


__all__ = [
    "HBAR_JOULE_SECOND",
    "HIERARCHY",
    "RESEARCH_BOUNDARY",
    "microtubule_signal_profile",
    "objective_reduction_profile",
    "orchestration_profile",
    "penrose_hameroff_runtime_profile",
    "spin_network_admissibility_profile",
    "twistor_nonlocality_profile",
]
