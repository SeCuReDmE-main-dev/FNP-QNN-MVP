"""Hydra-EM GPCN chamber profiles for hypothetical Orch OR simulations.

The functions in this module are deterministic alpha-local simulator metadata.
They formalize a GPCN-Set_phi chamber for microtubule-like proxies, but do not
claim biological validation, clinical behavior, consciousness, or physical
quantum-gravity behavior.
"""

from __future__ import annotations

import math
from statistics import mean
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from .penrose_hameroff_math import (
    HIERARCHY,
    RESEARCH_BOUNDARY,
    microtubule_signal_profile,
    objective_reduction_profile,
    orchestration_profile,
)


PHI = (1.0 + math.sqrt(5.0)) / 2.0
HYDRA_EM_RESEARCH_BOUNDARY = (
    RESEARCH_BOUNDARY
    + "; Hydra-EM-GPCN outputs are axiomatic proxy simulations only, not biological "
    "microtubule validation or anesthesia guidance"
)
HYDRA_EM_SOURCE_IDS = [
    "FNG_GPCN_SET_PHI_FINAL_PDF",
    "HAMEROFF_PENROSE_ORCH_OR_2014",
    "PENROSE_GRAVITY_REDUCTION_1996",
    "PENROSE_QC_ENTANGLEMENT_REDUCTION_1998",
    "QUASICRYSTAL_CUT_PROJECT_METHOD",
    "PLITHOGENIC_NEUTROSOPHIC_SET_SOURCES",
]
VERDICTS = {"communicates", "decoheres", "suspended", "rejected"}


def _finite_float(value: Any, label: str) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be numeric")
    if not math.isfinite(numeric):
        raise ValueError(f"{label} must be finite")
    return numeric


def _bounded(value: Any) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(numeric):
        return 0.0
    return max(0.0, min(1.0, numeric))


def _optional_nonnegative(value: Any, label: str) -> Optional[float]:
    if value is None:
        return None
    numeric = _finite_float(value, label)
    if numeric < 0.0:
        raise ValueError(f"{label} must be non-negative")
    return numeric


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


def _nonnegative_int(value: Any, label: str, *, default: int, maximum: int = 256) -> int:
    if value is None:
        return default
    numeric = _finite_float(value, label)
    if numeric < 0.0:
        raise ValueError(f"{label} must be non-negative")
    return max(0, min(maximum, int(round(numeric))))


def gpcn_set_phi_profile(
    *,
    local_point_count: int = 8,
    observation_scale_min: float = 0.01,
    observation_scale_max: float = 1.0,
    d_f: Optional[float] = None,
    d_min: float = 1.0,
    d_max: float = 2.0,
    adm: bool = True,
    i_system_source: str = "fractal_projection",
) -> Dict[str, Any]:
    """Return a bounded GPCN-Set_phi chamber profile."""

    point_count = _nonnegative_int(local_point_count, "local_point_count", default=8)
    scale_min = _finite_float(observation_scale_min, "observation_scale_min")
    scale_max = _finite_float(observation_scale_max, "observation_scale_max")
    d_min_value = _finite_float(d_min, "d_min")
    d_max_value = _finite_float(d_max, "d_max")
    if scale_min <= 0.0 or scale_max <= scale_min:
        raise ValueError("observation scale must satisfy 0 < min < max")
    if d_max_value <= d_min_value:
        raise ValueError("d_max must be greater than d_min")
    if d_f is None:
        # Deterministic local synthetic carrier tied to phi and chamber occupancy.
        occupancy = _positive_scale(float(point_count), 64.0)
        d_f_value = d_min_value + (d_max_value - d_min_value) * _bounded((1.0 / PHI + occupancy) / 2.0)
    else:
        d_f_value = _finite_float(d_f, "d_f")
    raw_hat = (d_f_value - d_min_value) / (d_max_value - d_min_value)
    d_f_hat = _bounded(raw_hat)
    same_chamber = d_min_value <= d_f_value <= d_max_value
    source = str(i_system_source or "unclassified_projection")
    fractal_sources = {"fractal_boundary", "fractal_growth", "fractal_graph", "fractal_projection", "geometric_multiscale"}
    admissible = bool(adm) and same_chamber and source in fractal_sources
    status = "admitted" if admissible else "suspended" if same_chamber else "rejected"
    return {
        "model": "gpcn_set_phi_chamber_v1",
        "source_ids": ["FNG_GPCN_SET_PHI_FINAL_PDF", "PLITHOGENIC_NEUTROSOPHIC_SET_SOURCES"],
        "axiom": "GPCN-Set_phi = (P, Omega, C_phi, Attr, Val, Dom, Contr, CubNu, S, M, D_f, D_f_hat, I_system, Adm)",
        "P_count": point_count,
        "Omega": "hydra_em_gpcn_observation_domain",
        "C_phi": {
            "side_length": PHI,
            "face_diagonal": PHI * math.sqrt(2.0),
            "space_diagonal": PHI * math.sqrt(3.0),
            "volume": PHI**3,
        },
        "S": [scale_min, scale_max],
        "M": "deterministic local proxy measurement",
        "D_f": d_f_value,
        "D_min": d_min_value,
        "D_max": d_max_value,
        "D_f_hat": d_f_hat,
        "I_system": {
            "source_i": source,
            "carrier_i": "D_f_hat" if admissible else "suspended_carrier",
            "value_i": d_f_hat if admissible else None,
            "status_i": status,
        },
        "Adm": status,
        "i_fractal_candidate": d_f_hat if admissible else None,
        "feature_vector": [
            _positive_scale(float(point_count), 64.0),
            _bounded(scale_min / scale_max),
            d_f_hat,
            float(admissible),
            1.0 - float(admissible),
        ],
        "feature_dimension": 5,
        "hierarchy": HIERARCHY,
        "research_boundary": HYDRA_EM_RESEARCH_BOUNDARY,
    }


def quasicrystal_gpcn_projection_profile(
    *,
    seed: int = 0,
    proxy_count: int = 8,
    coupling_strength: float = 0.5,
    projection_enabled: bool = True,
) -> Dict[str, Any]:
    """Generate deterministic Penrose-like quasicrystal neighborhood metadata."""

    count = _nonnegative_int(proxy_count, "proxy_count", default=8)
    coupling = _bounded(_finite_float(coupling_strength, "coupling_strength"))
    seed_value = int(round(_finite_float(seed, "seed")))
    points: List[Dict[str, Any]] = []
    for index in range(count):
        if projection_enabled:
            angle = ((index + seed_value) * 2.0 * math.pi) / (PHI**2)
            radius = math.sqrt(index + 1.0) / max(math.sqrt(max(count, 1)), 1e-12)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            phase = ((index + 1) * PHI + seed_value) % 1.0
        else:
            angle = (index * 2.0 * math.pi) / max(count, 1)
            radius = (index + 1.0) / max(count, 1)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            phase = 0.0
        points.append(
            {
                "index": index,
                "x": x,
                "y": y,
                "phase": phase,
                "neighbor_weight": _bounded(coupling * (1.0 - abs(phase - 0.5))),
            }
        )
    weights = [point["neighbor_weight"] for point in points]
    mean_weight = float(mean(weights)) if weights else 0.0
    dispersion = float(mean([(weight - mean_weight) ** 2 for weight in weights])) if weights else 0.0
    return {
        "model": "quasicrystal_gpcn_projection_v1",
        "source_ids": ["QUASICRYSTAL_CUT_PROJECT_METHOD", "FNG_GPCN_SET_PHI_FINAL_PDF"],
        "seed": seed_value,
        "proxy_count": count,
        "projection_enabled": bool(projection_enabled),
        "coupling_strength": coupling,
        "points": points,
        "neighborhood_score": _bounded(mean_weight),
        "projection_dispersion": _bounded(dispersion * 4.0),
        "feature_vector": [
            _positive_scale(float(count), 64.0),
            coupling,
            _bounded(mean_weight),
            _bounded(dispersion * 4.0),
            float(bool(projection_enabled)),
        ],
        "feature_dimension": 5,
        "hierarchy": HIERARCHY,
        "research_boundary": HYDRA_EM_RESEARCH_BOUNDARY,
        "interpretation": "Deterministic quasicrystal-style proxy neighborhood, not physical tissue geometry.",
    }


def microtubule_proxy_phi_profile(
    *,
    proxy_index: int,
    frequency_hz: Optional[float],
    coherence_time_s: Optional[float],
    anesthetic_damping: float,
    coupling_strength: float,
    neighborhood_weight: float,
    reduction_pressure: float,
    contradiction_threshold: float,
) -> Dict[str, Any]:
    """Return one bounded MicrotubuleProxy_phi state inside the GPCN chamber."""

    index = _nonnegative_int(proxy_index, "proxy_index", default=0)
    frequency = _optional_nonnegative(frequency_hz, "frequency_hz")
    coherence = _optional_nonnegative(coherence_time_s, "coherence_time_s")
    damping = _bounded(_finite_float(anesthetic_damping, "anesthetic_damping"))
    coupling = _bounded(_finite_float(coupling_strength, "coupling_strength"))
    neighborhood = _bounded(_finite_float(neighborhood_weight, "neighborhood_weight"))
    pressure = _bounded(_finite_float(reduction_pressure, "reduction_pressure"))
    threshold = _bounded(_finite_float(contradiction_threshold, "contradiction_threshold"))
    signal = microtubule_signal_profile(frequency_hz=frequency, anesthetic_damping=damping)
    coherence_score = _positive_scale(coherence, 1.0)
    communication_score = _bounded(signal["signal_score"] * coupling * neighborhood * (1.0 - damping))
    decoherence_score = _bounded(damping + max(0.0, pressure - coherence_score) + (1.0 - neighborhood)) / 3.0
    contradiction = _bounded(abs(communication_score - decoherence_score))
    if contradiction > threshold:
        adm = "suspended"
    elif communication_score >= 0.55 and communication_score >= decoherence_score:
        adm = "admitted"
    elif decoherence_score >= 0.55:
        adm = "rejected"
    else:
        adm = "suspended"
    cub_t = _bounded(communication_score)
    cub_f = _bounded(decoherence_score)
    cub_i = _bounded((contradiction + (1.0 - max(cub_t, cub_f))) / 2.0)
    return {
        "model": "microtubule_proxy_phi_v1",
        "source_ids": ["FNG_GPCN_SET_PHI_FINAL_PDF", "HAMEROFF_PENROSE_ORCH_OR_2014"],
        "proxy_index": index,
        "P_phi": {
            "w": _bounded(cub_t),
            "x_h": _bounded(neighborhood),
            "y": _bounded(coupling),
            "z": _bounded(pressure),
        },
        "frequency_hz": frequency,
        "coherence_time_s": coherence,
        "anesthetic_damping": damping,
        "coupling_strength": coupling,
        "neighborhood_weight": neighborhood,
        "reduction_pressure": pressure,
        "communication_score": communication_score,
        "decoherence_score": decoherence_score,
        "plithogenic_contradiction": contradiction,
        "CubNu": {
            "Cub_T": [[max(0.0, cub_t - 0.05), min(1.0, cub_t + 0.05)], cub_t],
            "Cub_I": [[max(0.0, cub_i - 0.05), min(1.0, cub_i + 0.05)], cub_i],
            "Cub_F": [[max(0.0, cub_f - 0.05), min(1.0, cub_f + 0.05)], cub_f],
        },
        "Adm": adm,
        "feature_vector": [cub_t, cub_i, cub_f, contradiction, float(adm == "admitted")],
        "feature_dimension": 5,
        "hierarchy": HIERARCHY,
        "research_boundary": HYDRA_EM_RESEARCH_BOUNDARY,
    }


def hydra_em_gpcn_orch_profile(
    events: Sequence[Any],
    pairs: Sequence[Any],
    *,
    microtubule_proxy_count: int = 8,
    microtubule_coupling_strength: float = 0.5,
    anesthetic_damping: Optional[float] = None,
    coherence_time_s: Optional[float] = None,
    objective_reduction_energy_joule: Optional[float] = None,
    microtubule_frequency_hz: Optional[float] = None,
    quasicrystal_projection_enabled: bool = True,
    plithogenic_contradiction_threshold: float = 0.35,
    lattice_seed: int = 0,
    observation_scale_min: float = 0.01,
    observation_scale_max: float = 1.0,
) -> Dict[str, Any]:
    """Combine GPCN, quasicrystal, Penrose/Hameroff, and anesthesia proxies."""

    event_list = list(events)
    pair_list = list(pairs)
    count = _nonnegative_int(microtubule_proxy_count, "microtubule_proxy_count", default=8)
    coupling = _bounded(_finite_float(microtubule_coupling_strength, "microtubule_coupling_strength"))
    damping = _bounded(_finite_float(0.0 if anesthetic_damping is None else anesthetic_damping, "anesthetic_damping"))
    coherence = _optional_nonnegative(coherence_time_s, "coherence_time_s")
    if coherence is None:
        coherence = _mean_duration(event_list)
    energy = 0.0 if objective_reduction_energy_joule is None else objective_reduction_energy_joule
    objective = objective_reduction_profile(energy, reference_time_s=coherence)
    orchestration = orchestration_profile(coherence, objective["tau_s"], damping=damping)
    projection = quasicrystal_gpcn_projection_profile(
        seed=lattice_seed,
        proxy_count=count,
        coupling_strength=coupling,
        projection_enabled=quasicrystal_projection_enabled,
    )
    gpcn = gpcn_set_phi_profile(
        local_point_count=count,
        observation_scale_min=observation_scale_min,
        observation_scale_max=observation_scale_max,
        d_f=1.0 + projection["projection_dispersion"],
        d_min=1.0,
        d_max=2.0,
        adm=True,
        i_system_source="fractal_projection" if quasicrystal_projection_enabled else "unclassified_projection",
    )
    threshold = _bounded(_finite_float(plithogenic_contradiction_threshold, "plithogenic_contradiction_threshold"))
    base_frequency = _optional_nonnegative(microtubule_frequency_hz, "microtubule_frequency_hz")
    proxies = [
        microtubule_proxy_phi_profile(
            proxy_index=point["index"],
            frequency_hz=None if base_frequency is None else base_frequency * (1.0 + point["phase"] / max(PHI, 1e-12)),
            coherence_time_s=coherence,
            anesthetic_damping=damping,
            coupling_strength=coupling,
            neighborhood_weight=point["neighbor_weight"],
            reduction_pressure=objective["reduction_pressure"],
            contradiction_threshold=threshold,
        )
        for point in projection["points"]
    ]
    communication_scores = [proxy["communication_score"] for proxy in proxies]
    decoherence_scores = [proxy["decoherence_score"] for proxy in proxies]
    contradiction_scores = [proxy["plithogenic_contradiction"] for proxy in proxies]
    communication = float(mean(communication_scores)) if communication_scores else 0.0
    decoherence = float(mean(decoherence_scores)) if decoherence_scores else 0.0
    contradiction = float(mean(contradiction_scores)) if contradiction_scores else 0.0
    admitted_fraction = (
        sum(1 for proxy in proxies if proxy["Adm"] == "admitted") / len(proxies) if proxies else 0.0
    )
    pair_overlap = _mean_pair_overlap(pair_list)
    if gpcn["Adm"] == "rejected" or count <= 0:
        verdict = "rejected"
    elif gpcn["Adm"] != "admitted" or contradiction > threshold:
        verdict = "suspended"
    elif decoherence >= max(communication, 0.55):
        verdict = "decoheres"
    elif communication >= 0.20 and admitted_fraction > 0.0:
        verdict = "communicates"
    else:
        verdict = "suspended"
    feature_vector = [
        communication,
        decoherence,
        contradiction,
        admitted_fraction,
        damping,
        objective["reduction_pressure"],
        orchestration["effective_alignment"],
        projection["neighborhood_score"],
        gpcn["D_f_hat"],
        pair_overlap,
    ]
    return {
        "model": "hydra_em_gpcn_orch_profile_v1",
        "source_ids": HYDRA_EM_SOURCE_IDS,
        "axiomatic_container": gpcn,
        "objective_reduction": objective,
        "orchestration": orchestration,
        "quasicrystal_projection": projection,
        "microtubule_proxies": proxies,
        "simulation_scores": {
            "communication_score": _bounded(communication),
            "decoherence_score": _bounded(decoherence),
            "plithogenic_contradiction": _bounded(contradiction),
            "admitted_proxy_fraction": _bounded(admitted_fraction),
            "pair_overlap_context": _bounded(pair_overlap),
        },
        "verdict": verdict,
        "feature_vector": [_bounded(item) for item in feature_vector],
        "feature_dimension": len(feature_vector),
        "runtime_mapping": {
            "gpcn": "GPCN-Set_phi is the axiomatic chamber for microtubule proxy states",
            "qnn": "feature vector is appended only when hydra_em_enabled and gpcn_set_phi_enabled are true",
            "anesthesia": "anesthetic_damping is a computational damping parameter, not clinical anesthesia guidance",
        },
        "hierarchy": HIERARCHY,
        "research_boundary": HYDRA_EM_RESEARCH_BOUNDARY,
    }


def anesthesia_sweep_profile(
    events: Sequence[Any],
    pairs: Sequence[Any],
    *,
    damping_values: Optional[Iterable[float]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Run a bounded deterministic anesthesia damping sweep."""

    values = list(damping_values if damping_values is not None else [0.0, 0.25, 0.5, 0.75, 1.0])
    profiles = [
        hydra_em_gpcn_orch_profile(events, pairs, anesthetic_damping=_bounded(_finite_float(value, "damping")), **kwargs)
        for value in values
    ]
    communication_values = [profile["simulation_scores"]["communication_score"] for profile in profiles]
    monotonic_nonincreasing = all(
        left >= right - 1e-12 for left, right in zip(communication_values, communication_values[1:])
    )
    return {
        "model": "hydra_em_gpcn_anesthesia_sweep_v1",
        "source_ids": HYDRA_EM_SOURCE_IDS,
        "damping_values": [_bounded(value) for value in values],
        "profiles": profiles,
        "communication_scores": communication_values,
        "monotonic_nonincreasing_communication": monotonic_nonincreasing,
        "feature_vector": [
            communication_values[0] if communication_values else 0.0,
            communication_values[-1] if communication_values else 0.0,
            _bounded((communication_values[0] - communication_values[-1]) if communication_values else 0.0),
            float(monotonic_nonincreasing),
        ],
        "feature_dimension": 4,
        "hierarchy": HIERARCHY,
        "research_boundary": HYDRA_EM_RESEARCH_BOUNDARY,
    }


__all__ = [
    "HYDRA_EM_RESEARCH_BOUNDARY",
    "HYDRA_EM_SOURCE_IDS",
    "PHI",
    "VERDICTS",
    "anesthesia_sweep_profile",
    "gpcn_set_phi_profile",
    "hydra_em_gpcn_orch_profile",
    "microtubule_proxy_phi_profile",
    "quasicrystal_gpcn_projection_profile",
]
