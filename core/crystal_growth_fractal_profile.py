"""Crystal growth and fractal-growth profiles for the alpha-local simulator.

These helpers provide bounded deterministic metrics for educational material
science simulations. They do not measure real crystal growth, validate a DFT
calculation, or prove physical quantum behavior.
"""

from __future__ import annotations

import math
from statistics import mean
from typing import Any, Dict, Iterable, Sequence

import numpy as np


HIERARCHY = "I -> I_system^S -> D_crystal -> dC -> i_crystal"
FRACTAL_HIERARCHY = "I -> I_system^S -> D_f -> dF -> i_fractal"
RESEARCH_BOUNDARY = (
    "alpha-local educational simulation only; not DFT, not validated material "
    "discovery, not microscopy measurement, and not quantum hardware output"
)


def _finite_float(value: Any, label: str, fallback: float | None = None) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        if fallback is not None:
            return fallback
        raise ValueError(f"{label} must be numeric")
    if not math.isfinite(numeric):
        if fallback is not None:
            return fallback
        raise ValueError(f"{label} must be finite")
    return numeric


def _clamp01(value: Any) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(numeric):
        return 0.0
    return max(0.0, min(1.0, numeric))


def _positive_scale(value: float, scale: float) -> float:
    value = max(0.0, float(value))
    scale = max(float(scale), 1e-12)
    return _clamp01((value / scale) / (1.0 + value / scale))


def _as_float_array(values: Iterable[Any], label: str) -> np.ndarray:
    array = np.asarray([_finite_float(item, label) for item in values], dtype=np.float32).reshape(-1)
    if array.size == 0:
        raise ValueError(f"{label} must contain at least one value")
    return array


def growth_rate_profile(times: Sequence[Any], sizes: Sequence[Any]) -> Dict[str, Any]:
    """Return bounded rate/acceleration/jerk metrics from a growth series."""

    t = _as_float_array(times, "times")
    y = _as_float_array(sizes, "sizes")
    if t.size != y.size:
        raise ValueError("times and sizes must have the same length")
    if t.size < 2:
        raise ValueError("at least two growth observations are required")
    order = np.argsort(t)
    t = t[order]
    y = y[order]
    dt = np.diff(t)
    if np.any(dt <= 0.0):
        raise ValueError("times must be strictly increasing after sorting")

    rates = np.diff(y) / dt
    accelerations = np.diff(rates) / dt[1:] if rates.size > 1 else np.zeros(0, dtype=np.float32)
    jerks = np.diff(accelerations) / dt[2:] if accelerations.size > 1 else np.zeros(0, dtype=np.float32)
    rate_abs_mean = float(mean([abs(float(item)) for item in rates])) if rates.size else 0.0
    rate_variance = float(np.var(rates)) if rates.size else 0.0
    acceleration_load = float(mean([abs(float(item)) for item in accelerations])) if accelerations.size else 0.0
    jerk_load = float(mean([abs(float(item)) for item in jerks])) if jerks.size else 0.0
    instability = _clamp01(
        _positive_scale(rate_variance, max(rate_abs_mean, 1.0))
        + 0.35 * _positive_scale(acceleration_load, max(rate_abs_mean, 1.0))
        + 0.20 * _positive_scale(jerk_load, max(rate_abs_mean, 1.0))
    )
    feature_vector = [
        _positive_scale(rate_abs_mean, 10.0),
        _positive_scale(rate_variance, 10.0),
        _positive_scale(acceleration_load, 10.0),
        _positive_scale(jerk_load, 10.0),
        instability,
    ]
    return {
        "model": "crystal_growth_rate_profile_v1",
        "sample_count": int(t.size),
        "growth_rate_mean_abs": rate_abs_mean,
        "growth_rate_variance": rate_variance,
        "acceleration_load": acceleration_load,
        "jerk_load": jerk_load,
        "i_rate": instability,
        "feature_vector": feature_vector,
        "feature_dimension": len(feature_vector),
        "hierarchy": HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


def branch_drift_profile(
    branch_vectors: Sequence[Sequence[Any]],
    attractor_vector: Sequence[Any],
) -> Dict[str, Any]:
    """Return a bounded micro-branch deviation profile."""

    branches = np.asarray(branch_vectors, dtype=np.float32)
    attractor = np.asarray(attractor_vector, dtype=np.float32).reshape(-1)
    if branches.ndim != 2 or branches.shape[0] == 0:
        raise ValueError("branch_vectors must be a non-empty 2D sequence")
    if branches.shape[1] != attractor.size:
        raise ValueError("branch_vectors and attractor_vector dimensions must match")
    attractor_norm = np.linalg.norm(attractor)
    if attractor_norm <= 0.0:
        raise ValueError("attractor_vector must be non-zero")
    normalized_attractor = attractor / attractor_norm
    drifts = []
    for branch in branches:
        norm = np.linalg.norm(branch)
        if norm <= 0.0:
            drifts.append(1.0)
            continue
        cosine = float(np.dot(branch / norm, normalized_attractor))
        drifts.append(_clamp01((1.0 - cosine) / 2.0))
    drift_mean = float(mean(drifts))
    drift_max = float(max(drifts))
    drift_variance = float(np.var(drifts))
    feature_vector = [
        drift_mean,
        drift_max,
        _clamp01(drift_variance * 4.0),
        _clamp01(sum(1 for item in drifts if item >= 0.55) / len(drifts)),
    ]
    return {
        "model": "crystal_branch_drift_profile_v1",
        "branch_count": int(branches.shape[0]),
        "branch_drift": drift_mean,
        "branch_drift_max": drift_max,
        "branch_drift_variance": drift_variance,
        "divergent_branch_fraction": feature_vector[-1],
        "feature_vector": feature_vector,
        "feature_dimension": len(feature_vector),
        "hierarchy": HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


def fractal_dimension_proxy(points_or_surface: Sequence[Any]) -> Dict[str, Any]:
    """Return a simple box-counting style proxy for 1D/2D synthetic data."""

    values = np.asarray(points_or_surface, dtype=np.float32)
    if values.size == 0:
        raise ValueError("points_or_surface must not be empty")
    if values.ndim == 1:
        occupied = values.reshape(-1, 1)
    elif values.ndim == 2:
        occupied = values
    else:
        occupied = values.reshape(values.shape[0], -1)
    occupied = occupied[np.isfinite(occupied).all(axis=1)]
    if occupied.size == 0:
        raise ValueError("points_or_surface must contain finite values")
    mins = occupied.min(axis=0)
    ranges = np.maximum(occupied.max(axis=0) - mins, 1e-12)
    normalized = (occupied - mins) / ranges
    box_sizes = np.asarray([2, 4, 8, 16], dtype=np.float32)
    counts = []
    for size in box_sizes:
        bins = np.floor(normalized * size).astype(int)
        bins = np.clip(bins, 0, int(size) - 1)
        counts.append(len({tuple(row.tolist()) for row in bins}))
    log_inv_size = np.log(box_sizes)
    log_counts = np.log(np.maximum(counts, 1))
    if len(set(counts)) <= 1:
        d_f = 0.0
    else:
        d_f = float(np.polyfit(log_inv_size, log_counts, 1)[0])
    d_min = 0.0
    d_max = float(max(1, occupied.shape[1]))
    d_f_hat = _clamp01((d_f - d_min) / max(d_max - d_min, 1e-12))
    feature_vector = [d_f_hat, _clamp01(float(counts[-1]) / max(float(occupied.shape[0]), 1.0))]
    return {
        "model": "crystal_fractal_dimension_proxy_v1",
        "D_f": d_f,
        "D_min": d_min,
        "D_max": d_max,
        "D_f_hat": d_f_hat,
        "box_counts": [int(item) for item in counts],
        "measurement_method": "synthetic-box-counting-proxy",
        "feature_vector": feature_vector,
        "feature_dimension": len(feature_vector),
        "hierarchy": FRACTAL_HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


def fractal_growth_rate_profile(fractal_dimensions: Sequence[Any], times: Sequence[Any]) -> Dict[str, Any]:
    """Return the rate of change for a sequence of fractal-dimension proxies."""

    base = growth_rate_profile(times, fractal_dimensions)
    base["model"] = "crystal_fractal_growth_rate_profile_v1"
    base["fractal_growth_rate"] = base["growth_rate_mean_abs"]
    base["hierarchy"] = FRACTAL_HIERARCHY
    return base


def crystal_growth_window_profile(
    *,
    growth_rate: float,
    branch_drift: float,
    surface_roughness: float,
    defect_density: float,
    phase_stability_margin: float,
) -> Dict[str, Any]:
    """Fuse growth-window signals into a bounded instability profile."""

    rate = _clamp01(growth_rate)
    drift = _clamp01(branch_drift)
    roughness = _clamp01(surface_roughness)
    defects = _clamp01(defect_density)
    stability = _clamp01(phase_stability_margin)
    instability_load = _clamp01(0.30 * drift + 0.25 * roughness + 0.25 * defects + 0.20 * (1.0 - stability))
    near_chaos_margin = _clamp01(instability_load * (0.5 + 0.5 * rate))
    if near_chaos_margin >= 0.80:
        regime = "rejected_growth_window"
    elif near_chaos_margin >= 0.55:
        regime = "near-chaotic suspended crystal growth state"
    else:
        regime = "admitted_growth_window"
    feature_vector = [rate, drift, roughness, defects, stability, instability_load, near_chaos_margin]
    return {
        "model": "crystal_growth_window_profile_v1",
        "growth_rate": rate,
        "branch_drift": drift,
        "surface_roughness": roughness,
        "defect_density": defects,
        "phase_stability_margin": stability,
        "instability_load": instability_load,
        "near_chaos_margin": near_chaos_margin,
        "regime": regime,
        "feature_vector": feature_vector,
        "feature_dimension": len(feature_vector),
        "hierarchy": HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


__all__ = [
    "FRACTAL_HIERARCHY",
    "HIERARCHY",
    "RESEARCH_BOUNDARY",
    "branch_drift_profile",
    "crystal_growth_window_profile",
    "fractal_dimension_proxy",
    "fractal_growth_rate_profile",
    "growth_rate_profile",
]
