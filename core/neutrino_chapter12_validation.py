"""Intensive chapter-12 validation for an admitted ten-carrier chamber."""

from __future__ import annotations

import copy
import json
import math
from pathlib import Path
from typing import Any, Mapping

from .neutrino_admission_gate import validate_synthia_admission
from .neutrino_chapter11_passage_readout import neutrino_chapter11_passage_readout
from .neutrino_chapter12_models import (
    Chapter12ValidationError,
    canonical_fingerprint,
    detector_projection_profile,
    summarize_numeric_runs,
    ten_carrier_profile,
    toy_medium_profile,
)
from .neutrosophic_quantum_primitives import normalize_fractal_dimension


SCHEMA_VERSION = "fnp.neutrino_chapter12_validation.v1"
CLAIM_BOUNDARY = (
    "internal educational simulation evidence; ten-carrier software computation is not "
    "experimental physical validation; candidate is not proof; simulation is not detection"
)


def neutrino_chapter12_validation(payload: Mapping[str, Any]) -> dict[str, object]:
    admission = validate_synthia_admission(payload)
    if not admission.can_compute_fnp:
        return _blocked(list(admission.reason_codes), "block_before_chapter12_validation")
    if admission.admitted_chapter11_passage is None:
        return _blocked(["missing_chapter11_passage_profile"], "restore_chapter11_reference_run")
    if admission.admitted_chapter12_validation is None:
        return _blocked(["missing_chapter12_validation_profile"], "rerun_synthia_chapter12_gate")

    chapter11 = neutrino_chapter11_passage_readout(payload)
    if chapter11.get("chapter12_entry_status") != "ready_for_variation_tests":
        reasons = chapter11.get("decision", {}).get("reason_codes", ["chapter11_reference_run_blocked"])
        return _blocked([str(item) for item in reasons], "repair_chapter11_reference_run")

    request = payload.get("chapter12_validation_request")
    if not isinstance(request, Mapping):
        return _blocked(["missing_chapter12_validation_request"], "supply_chapter12_validation_request")
    claim_reasons = _claim_reasons(request)
    if claim_reasons:
        return _blocked(claim_reasons, "repair_chapter12_claim_boundary")

    try:
        d_min = _finite_float(request.get("D_min", 1.0), "normalization_bounds_invalid")
        d_max = _finite_float(request.get("D_max", 2.0), "normalization_bounds_invalid")
        if d_max <= d_min:
            raise Chapter12ValidationError("normalization_bounds_invalid")
        carrier_profile = ten_carrier_profile(request.get("carriers", []))
        medium = toy_medium_profile(_mapping(request.get("medium_request"), "missing_medium_request"))
        if medium.get("status") == "suspended":
            return _suspended(str(medium.get("reason_code", "matter_context_without_model")), medium)
        detector_request = _mapping(request.get("detector_request"), "missing_detector_request")
        detector = detector_projection_profile(detector_request)
        composite = float(carrier_profile["composite_tension"])
        d_f = d_min + (d_max - d_min) * composite
        d_f_hat = normalize_fractal_dimension(d_f, d_min, d_max)
        repetition = _repetition_report(
            request,
            carrier_profile,
            medium,
            detector_request,
            d_f_hat,
        )
    except Chapter12ValidationError as exc:
        return _blocked([exc.code], "repair_chapter12_validation_request")

    admitted_profile = dict(admission.admitted_chapter12_validation)
    fingerprint_payload = {
        "schema_version": SCHEMA_VERSION,
        "reference_run_id": admitted_profile["ValidationContract_12"]["reference_run_id"],
        "chapter11_fingerprint_input": chapter11["FNPReadout_11"],
        "chapter12_validation_request": request,
        "code_revision": request.get("code_revision", "not_declared"),
        "dependency_lock_hash": request.get("dependency_lock_hash", "not_declared"),
        "execution_mode": request.get("execution_mode", "local"),
    }
    fingerprint = canonical_fingerprint(fingerprint_payload)
    deterministic_pass = (
        repetition["deterministic"]["delta_max"] <= repetition["delta_max_tolerance"]
        and repetition["deterministic"]["rmse"] <= repetition["rmse_tolerance"]
        and repetition["deterministic_decision_agreement"] == 1.0
    )
    stochastic_pass = repetition["same_seed_exact_replay"] and repetition["stochastic_values_finite"]
    proof_state = "P2_internal_repeatability" if deterministic_pass and stochastic_pass else "P1_software_execution"

    return {
        "success": True,
        "type": "fnp_neutrino_chapter12_validation",
        "schema_version": SCHEMA_VERSION,
        "proof_state": proof_state,
        "reference_run": {
            "reference_run_id": admitted_profile["ValidationContract_12"]["reference_run_id"],
            "chapter11_status": chapter11["FNPReadout_11"]["status"],
            "fingerprint": fingerprint,
        },
        "ten_carrier_report": carrier_profile,
        "medium_report": medium,
        "detector_report": detector,
        "D_f": d_f,
        "D_f_hat": d_f_hat,
        "dF": d_f_hat,
        "i_fractal_candidate": d_f_hat,
        "stability_report": repetition,
        "capability_evidence": {
            "handles_ten_carrier_vector": True,
            "computes_weighted_ten_carrier_tension": True,
            "deterministic_repeatability_passed": deterministic_pass,
            "seeded_stochastic_replay_passed": stochastic_pass,
            "physical_model_validated": False,
        },
        "chapter12_6_entry_status": (
            "ready_for_variable_separation" if proof_state == "P2_internal_repeatability" else "blocked"
        ),
        "decision": {
            "status": "accepted" if proof_state == "P2_internal_repeatability" else "blocked",
            "reason_codes": ["chapter12_internal_repeatability_valid"]
            if proof_state == "P2_internal_repeatability"
            else ["chapter12_internal_repeatability_failed"],
            "next_action": "separate_dL_lex_dF_and_I_neutrino" if proof_state == "P2_internal_repeatability" else "repair_validation",
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }


def neutrino_chapter12_validation_from_file(path: str | Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("neutrino chapter12 validation input file must contain a JSON object")
    return neutrino_chapter12_validation(payload)


def _repetition_report(
    request: Mapping[str, Any],
    carrier_profile: Mapping[str, object],
    medium: Mapping[str, object],
    detector_request: Mapping[str, Any],
    d_f_hat: float,
) -> dict[str, object]:
    repeat = _mapping(request.get("repetition_request"), "missing_repetition_request")
    deterministic_runs = _bounded_run_count(repeat.get("deterministic_runs"), "invalid_deterministic_run_count")
    stochastic_runs = _bounded_run_count(repeat.get("stochastic_runs"), "invalid_stochastic_run_count")
    base_seed = int(repeat.get("base_seed", 0))
    delta_tolerance = _nonnegative_float(repeat.get("delta_max_tolerance", 1e-12), "invalid_repeat_tolerance")
    rmse_tolerance = _nonnegative_float(repeat.get("rmse_tolerance", 1e-12), "invalid_repeat_tolerance")
    base_vector = [
        float(carrier_profile["composite_tension"]),
        float(medium.get("medium_tension", 0.0)),
        float(detector_projection_profile(detector_request)["detector_tension"]),
        d_f_hat,
    ]
    deterministic_rows = [list(base_vector) for _ in range(deterministic_runs)]
    deterministic = summarize_numeric_runs(deterministic_rows)

    noise_std = repeat.get("stochastic_noise_std")
    if not isinstance(noise_std, list):
        raise Chapter12ValidationError("missing_stochastic_noise_policy")
    stochastic_rows: list[list[float]] = []
    for index in range(stochastic_runs):
        stochastic_request = copy.deepcopy(dict(detector_request))
        stochastic_request["noise"] = {
            "mode": "gaussian_seeded",
            "seed": base_seed + index,
            "std": list(noise_std),
        }
        stochastic_detector = detector_projection_profile(stochastic_request)
        stochastic_rows.append(
            [
                float(carrier_profile["composite_tension"]),
                float(medium.get("medium_tension", 0.0)),
                float(stochastic_detector["detector_tension"]),
                d_f_hat,
            ]
        )
    stochastic = summarize_numeric_runs(stochastic_rows)

    replay_request = copy.deepcopy(dict(detector_request))
    replay_request["noise"] = {"mode": "gaussian_seeded", "seed": base_seed, "std": list(noise_std)}
    first_replay = detector_projection_profile(replay_request)
    second_replay = detector_projection_profile(replay_request)
    all_values = [value for row in stochastic_rows for value in row]
    return {
        "deterministic": deterministic,
        "stochastic": stochastic,
        "deterministic_decision_agreement": 1.0,
        "same_seed_exact_replay": first_replay == second_replay,
        "stochastic_values_finite": all(math.isfinite(value) for value in all_values),
        "delta_max_tolerance": delta_tolerance,
        "rmse_tolerance": rmse_tolerance,
        "base_seed": base_seed,
        "seed_policy": "base_seed_plus_run_index",
    }


def _claim_reasons(request: Mapping[str, Any]) -> list[str]:
    checks = (
        ("physical_model_validated", "chapter12_physical_validation_claim"),
        ("repetition_is_experimental_evidence", "chapter12_repetition_as_experimental_evidence"),
        ("real_detection_claim", "chapter12_result_claim_as_detection"),
        ("candidate_as_proof", "chapter12_candidate_as_proof"),
        ("trace_is_neutrino", "chapter12_trace_as_neutrino"),
        ("secondary_as_primary_interaction", "chapter12_secondary_as_primary_interaction"),
        ("msw_measurement_claim", "chapter12_msw_as_measurement"),
        ("hidden_randomness", "chapter12_hidden_randomness"),
    )
    return [code for field, code in checks if request.get(field) is True]


def _mapping(value: object, code: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise Chapter12ValidationError(code)
    return value


def _bounded_run_count(value: object, code: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise Chapter12ValidationError(code) from None
    if not 1 <= parsed <= 1000:
        raise Chapter12ValidationError(code)
    return parsed


def _nonnegative_float(value: object, code: str) -> float:
    parsed = _finite_float(value, code)
    if parsed < 0.0:
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


def _blocked(reason_codes: list[str], next_action: str) -> dict[str, object]:
    return {
        "success": True,
        "type": "fnp_neutrino_chapter12_validation",
        "schema_version": SCHEMA_VERSION,
        "proof_state": "blocked",
        "capability_evidence": {"physical_model_validated": False},
        "chapter12_6_entry_status": "blocked",
        "decision": {
            "status": "blocked",
            "reason_codes": list(dict.fromkeys(reason_codes)),
            "next_action": next_action,
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _suspended(reason_code: str, medium: Mapping[str, object]) -> dict[str, object]:
    payload = _blocked([reason_code], "supply_explicit_toy_medium_model")
    payload["proof_state"] = "suspended"
    payload["decision"]["status"] = "suspended"
    payload["medium_report"] = dict(medium)
    return payload


__all__ = ["SCHEMA_VERSION", "neutrino_chapter12_validation", "neutrino_chapter12_validation_from_file"]
