"""Pure models used by the chapter-12 internal validation surface."""

from __future__ import annotations

import hashlib
import json
import math
import random
import statistics
from typing import Any, Mapping, Sequence

from .plithogenic_logic import plithogenic_weighted_cumulative_truth


REQUIRED_CARRIERS = (
    "I_source",
    "I_flavor",
    "I_mass",
    "I_mix",
    "I_phase",
    "I_medium",
    "I_interaction",
    "I_secondary",
    "I_detector",
    "I_uncertainty",
)


class Chapter12ValidationError(ValueError):
    """A stable public-safe validation error."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def ten_carrier_profile(carriers: Sequence[Mapping[str, Any]]) -> dict[str, object]:
    if not isinstance(carriers, Sequence) or isinstance(carriers, (str, bytes)):
        raise Chapter12ValidationError("invalid_ten_carrier_payload")
    by_name: dict[str, Mapping[str, Any]] = {}
    for carrier in carriers:
        if not isinstance(carrier, Mapping):
            raise Chapter12ValidationError("invalid_ten_carrier_payload")
        name = str(carrier.get("name", "")).strip()
        if not name:
            raise Chapter12ValidationError("missing_carrier_name")
        if name in by_name:
            raise Chapter12ValidationError("duplicate_carrier")
        by_name[name] = carrier
    if set(by_name) != set(REQUIRED_CARRIERS):
        raise Chapter12ValidationError("missing_or_unknown_carrier")

    total_weight = 0.0
    weighted_sum = 0.0
    prepared: list[dict[str, object]] = []
    tif_profiles: list[dict[str, object]] = []
    for name in REQUIRED_CARRIERS:
        carrier = by_name[name]
        tension = _finite_float(carrier.get("tension"), "invalid_carrier_tension")
        weight = _finite_float(carrier.get("weight"), "invalid_carrier_weight")
        role = str(carrier.get("role", "")).strip()
        source_fields = carrier.get("source_fields")
        if not 0.0 <= tension <= 1.0:
            raise Chapter12ValidationError("invalid_carrier_tension")
        if weight <= 0.0:
            raise Chapter12ValidationError("invalid_carrier_weight")
        if not role:
            raise Chapter12ValidationError("missing_carrier_role")
        if not isinstance(source_fields, list) or not source_fields:
            raise Chapter12ValidationError("missing_carrier_source_fields")
        tif = carrier.get("TIF") if isinstance(carrier.get("TIF"), Mapping) else {
            "T": 1.0 - tension,
            "I": tension,
            "F": 0.0,
        }
        total_weight += weight
        weighted_sum += weight * tension
        prepared.append(
            {
                "name": name,
                "tension": tension,
                "weight": weight,
                "role": role,
                "source_fields": [str(item) for item in source_fields],
                "weighted_tension": weight * tension,
                "TIF": {
                    "T": _bounded_float(tif.get("T"), "invalid_carrier_tif"),
                    "I": _bounded_float(tif.get("I"), "invalid_carrier_tif"),
                    "F": _bounded_float(tif.get("F"), "invalid_carrier_tif"),
                },
            }
        )
        tif_profiles.append({**prepared[-1]["TIF"], "weight": weight})

    composite = weighted_sum / total_weight
    for item in prepared:
        item["normalized_weight"] = float(item["weight"]) / total_weight
        item["normalized_contribution"] = float(item["weighted_tension"]) / total_weight
    tif_result = plithogenic_weighted_cumulative_truth(tif_profiles)
    return {
        "formula_version": "chapter12.ten_carrier_weighted_tension.v1",
        "carrier_order": list(REQUIRED_CARRIERS),
        "carrier_count": len(prepared),
        "total_weight": total_weight,
        "composite_tension": composite,
        "contributions": prepared,
        "TIF_diagnostic": {
            "operator": tif_result["operator"],
            "T": tif_result["T"],
            "I": tif_result["I"],
            "F": tif_result["F"],
            "total_weight": tif_result["total_weight"],
            "boundary": "secondary diagnostic; T/I/F does not replace I_neutrino_vec",
        },
    }


def toy_medium_profile(request: Mapping[str, Any]) -> dict[str, object]:
    level = str(request.get("level", "")).strip()
    if level == "vacuum":
        theta = _finite_float(request.get("theta_rad"), "missing_medium_parameter")
        vacuum_mixing = math.sin(2.0 * theta) ** 2
        return {
            "status": "computed",
            "level": "vacuum",
            "particle_kind": str(request.get("particle_kind", "neutrino")),
            "signed_matter_potential_ev": 0.0,
            "A": 0.0,
            "sin2_2theta_vacuum": vacuum_mixing,
            "sin2_2theta_medium": vacuum_mixing,
            "resonance_residual": abs(math.cos(2.0 * theta)),
            "medium_tension": 0.0,
            "boundary": "toy medium calculation; not MSW measurement",
        }
    if level == "context_only":
        return {
            "status": "suspended",
            "level": level,
            "reason_code": "matter_context_without_model",
            "boundary": "named matter context is not a computed matter model",
        }
    if level != "toy_matter_model":
        raise Chapter12ValidationError("invalid_medium_level")

    energy_gev = _positive_float(request.get("energy_gev"), "missing_medium_parameter")
    delta_m2 = _positive_float(request.get("delta_m2_ev2"), "missing_medium_parameter")
    theta = _finite_float(request.get("theta_rad"), "missing_medium_parameter")
    potential = _finite_float(request.get("matter_potential_ev"), "missing_explicit_matter_potential")
    particle_kind = str(request.get("particle_kind", "")).strip()
    if particle_kind not in {"neutrino", "antineutrino"}:
        raise Chapter12ValidationError("invalid_particle_kind")
    signed_potential = potential if particle_kind == "neutrino" else -potential
    a_value = 2.0 * energy_gev * 1.0e9 * signed_potential / delta_m2
    sin2 = math.sin(2.0 * theta) ** 2
    cos2 = math.cos(2.0 * theta)
    denominator = (cos2 - a_value) ** 2 + sin2
    if denominator <= 0.0:
        raise Chapter12ValidationError("invalid_medium_denominator")
    medium_mixing = sin2 / denominator
    return {
        "status": "computed",
        "level": level,
        "particle_kind": particle_kind,
        "energy_gev": energy_gev,
        "delta_m2_ev2": delta_m2,
        "theta_rad": theta,
        "signed_matter_potential_ev": signed_potential,
        "A": a_value,
        "sin2_2theta_vacuum": sin2,
        "sin2_2theta_medium": medium_mixing,
        "resonance_residual": abs(cos2 - a_value),
        "medium_tension": min(1.0, abs(medium_mixing - sin2)),
        "boundary": "toy medium calculation; not MSW measurement",
    }


def detector_projection_profile(request: Mapping[str, Any]) -> dict[str, object]:
    x_true = _float_vector(request.get("x_true"), "invalid_detector_true_vector")
    matrix = request.get("response_matrix")
    if not isinstance(matrix, list) or not matrix:
        raise Chapter12ValidationError("missing_detector_response_matrix")
    rows = [_float_vector(row, "invalid_detector_response_matrix") for row in matrix]
    if any(len(row) != len(x_true) for row in rows):
        raise Chapter12ValidationError("detector_dimension_mismatch")
    if any(value < 0.0 or value > 1.0 for row in rows for value in row):
        raise Chapter12ValidationError("invalid_detector_response_coefficient")
    for column in range(len(x_true)):
        if sum(row[column] for row in rows) > 1.0 + 1e-12:
            raise Chapter12ValidationError("detector_response_column_exceeds_one")

    background_status = str(request.get("background_status", "")).strip()
    if background_status == "explicit":
        background = _float_vector(request.get("background"), "missing_detector_background")
        if len(background) != len(rows):
            raise Chapter12ValidationError("detector_dimension_mismatch")
    elif background_status == "none_by_model":
        background = [0.0] * len(rows)
    else:
        raise Chapter12ValidationError("missing_detector_background")

    noise_request = request.get("noise") if isinstance(request.get("noise"), Mapping) else {}
    mode = str(noise_request.get("mode", "deterministic_zero"))
    if mode == "deterministic_zero":
        noise = [0.0] * len(rows)
        seed = None
    elif mode == "gaussian_seeded":
        if "seed" not in noise_request:
            raise Chapter12ValidationError("hidden_detector_randomness")
        seed = int(noise_request["seed"])
        std = _float_vector(noise_request.get("std"), "invalid_detector_noise")
        if len(std) != len(rows) or any(value < 0.0 for value in std):
            raise Chapter12ValidationError("invalid_detector_noise")
        rng = random.Random(seed)
        noise = [rng.gauss(0.0, value) for value in std]
    else:
        raise Chapter12ValidationError("invalid_detector_noise_mode")

    reconstructed = [
        max(0.0, sum(coefficient * value for coefficient, value in zip(row, x_true)) + bg + eps)
        for row, bg, eps in zip(rows, background, noise)
    ]
    labels = request.get("labels")
    if not isinstance(labels, list) or len(labels) != len(rows):
        raise Chapter12ValidationError("invalid_detector_labels")
    thresholds = _float_vector(request.get("thresholds", [0.0] * len(rows)), "invalid_detector_thresholds")
    if len(thresholds) != len(rows) or any(value < 0.0 for value in thresholds):
        raise Chapter12ValidationError("invalid_detector_thresholds")
    eligible = [index for index, value in enumerate(reconstructed) if value >= thresholds[index]]
    total_reconstructed = sum(reconstructed)
    if not eligible or total_reconstructed <= 0.0:
        classification = "no_trace"
        ambiguity = 1.0
    else:
        best = max(eligible, key=lambda index: reconstructed[index])
        classification = str(labels[best])
        ambiguity = 1.0 - reconstructed[best] / total_reconstructed
    total_true = sum(x_true)
    efficiency = min(1.0, total_reconstructed / total_true) if total_true > 0.0 else 0.0
    detector_tension = 0.5 * (1.0 - efficiency) + 0.5 * ambiguity
    return {
        "status": "computed",
        "formula_version": "chapter12.detector_projection.v1",
        "x_true": x_true,
        "response_matrix": rows,
        "background_status": background_status,
        "background": background,
        "noise_mode": mode,
        "seed": seed,
        "noise": noise,
        "y_reco": reconstructed,
        "classification": classification,
        "signal_efficiency": efficiency,
        "classification_ambiguity": ambiguity,
        "detector_tension": detector_tension,
        "boundary": "simulated detector projection; trace is not the neutrino object",
    }


def canonical_fingerprint(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def summarize_numeric_runs(rows: Sequence[Sequence[float]]) -> dict[str, object]:
    if not rows:
        raise Chapter12ValidationError("empty_run_series")
    width = len(rows[0])
    if width == 0 or any(len(row) != width for row in rows):
        raise Chapter12ValidationError("inconsistent_run_series")
    baseline = [float(value) for value in rows[0]]
    flat_deltas = [float(value) - baseline[index] for row in rows for index, value in enumerate(row)]
    delta_max = max(abs(value) for value in flat_deltas)
    rmse = math.sqrt(sum(value * value for value in flat_deltas) / len(flat_deltas))
    columns = [[float(row[index]) for row in rows] for index in range(width)]
    summaries = []
    for values in columns:
        mean = statistics.fmean(values)
        variance = statistics.pvariance(values)
        std = math.sqrt(variance)
        summaries.append(
            {
                "mean": mean,
                "variance": variance,
                "std": std,
                "cv": std / abs(mean) if mean != 0.0 else None,
                "q05": _quantile(values, 0.05),
                "q50": _quantile(values, 0.50),
                "q95": _quantile(values, 0.95),
            }
        )
    return {"run_count": len(rows), "delta_max": delta_max, "rmse": rmse, "columns": summaries}


def _quantile(values: Sequence[float], probability: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _float_vector(value: object, code: str) -> list[float]:
    if not isinstance(value, list) or not value:
        raise Chapter12ValidationError(code)
    return [_finite_float(item, code) for item in value]


def _positive_float(value: object, code: str) -> float:
    parsed = _finite_float(value, code)
    if parsed <= 0.0:
        raise Chapter12ValidationError(code)
    return parsed


def _bounded_float(value: object, code: str) -> float:
    parsed = _finite_float(value, code)
    if not 0.0 <= parsed <= 1.0:
        raise Chapter12ValidationError(code)
    return parsed


def _finite_float(value: object, code: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise Chapter12ValidationError(code) from None
    if not math.isfinite(parsed):
        raise Chapter12ValidationError(code)
    return parsed


__all__ = [
    "Chapter12ValidationError",
    "REQUIRED_CARRIERS",
    "canonical_fingerprint",
    "detector_projection_profile",
    "summarize_numeric_runs",
    "ten_carrier_profile",
    "toy_medium_profile",
]
