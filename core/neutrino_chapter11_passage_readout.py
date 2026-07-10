"""Conditional chapter-11 readout for an admitted neutrino path pair."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

from .neutrino_admission_gate import validate_synthia_admission
from .neutrosophic_quantum_primitives import normalize_fractal_dimension


SCHEMA_VERSION = "fnp.neutrino_chapter11_passage.v1"
CLAIM_BOUNDARY = (
    "educational simulation; chamber comparison is not CP measurement; "
    "candidate is not proof; simulation is not detection"
)
FORBIDDEN_REQUEST_FIELDS = {
    "D_f",
    "D_f_hat",
    "dF",
    "i_fractal",
    "i_fractal_candidate",
    "D_f_11",
    "D_f_hat_11",
    "dF_11",
    "i_fractal_candidate_11",
}


def neutrino_chapter11_passage_readout(payload: Mapping[str, Any]) -> dict[str, object]:
    admission = validate_synthia_admission(payload)
    if not admission.can_compute_fnp:
        return _blocked(list(admission.reason_codes), "block_before_chapter11_passage")
    if admission.admitted_chapter11_passage is None:
        return _blocked(["missing_chapter11_passage_profile"], "rerun_synthia_with_chapter11_profile")

    request = payload.get("chapter11_readout_request")
    if not isinstance(request, Mapping):
        return _blocked(["missing_chapter11_readout_request"], "supply_explicit_chapter11_readout_request")

    reasons = _validate_request(request)
    if reasons:
        return _blocked(reasons, "repair_chapter11_readout_request")

    phase_delta = float(request["phase_delta"])
    d_min = float(request.get("D_min_11", 1.0))
    d_max = float(request.get("D_max_11", 2.0))
    d_l_lex = float(admission.dL_lex)
    effective_phase_tension = _clamp01(0.75 * phase_delta + 0.25 * d_l_lex)
    d_f = 1.0 + effective_phase_tension
    d_f_hat = normalize_fractal_dimension(d_f, d_min, d_max)

    profile = dict(admission.admitted_chapter11_passage)
    synthia_reading = dict(profile.get("SynthiaReading_11", {}))
    return {
        "success": True,
        "type": "fnp_neutrino_chapter11_passage",
        "schema_version": SCHEMA_VERSION,
        "Chapter11InjectionPacket": dict(profile.get("Chapter11InjectionPacket", {})),
        "SynthiaReading_11": synthia_reading,
        "FNPReadout_11": {
            "status": "conditional_readout_constructed",
            "formula_version": "chapter11.phase_lexical_tension.v1",
            "phase_delta": phase_delta,
            "dL_lex": d_l_lex,
            "effective_phase_tension": effective_phase_tension,
            "D_f_11": d_f,
            "D_f_hat_11": d_f_hat,
            "dF_11": d_f_hat,
            "i_fractal_candidate_11": d_f_hat,
        },
        "PathComparison_11": "chamber_comparison",
        "CarrierAdm_11": {"status": "admitted", "carrier": "effective_phase_tension"},
        "NormAdm_11": {"status": "admitted", "D_min_11": d_min, "D_max_11": d_max},
        "D_f_11": d_f,
        "D_f_hat_11": d_f_hat,
        "dF_11": d_f_hat,
        "i_fractal_candidate_11": d_f_hat,
        "chapter12_entry_status": "ready_for_variation_tests",
        "proof_state": "P1_software_execution",
        "physical_model_validated": False,
        "decision": {
            "status": "accepted",
            "reason_codes": ["chapter11_conditional_readout_valid"],
            "next_action": "prepare_chapter12_internal_validation",
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }


def neutrino_chapter11_passage_readout_from_file(path: str | Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("neutrino chapter11 passage input file must contain a JSON object")
    return neutrino_chapter11_passage_readout(payload)


def _validate_request(request: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    if any(key in request for key in FORBIDDEN_REQUEST_FIELDS):
        reasons.append("chapter11_caller_supplied_fnp_output")
    phase_delta = _finite_float(request.get("phase_delta"))
    if phase_delta is None or not 0.0 <= phase_delta <= 1.0:
        reasons.append("invalid_phase_delta")
    d_min = _finite_float(request.get("D_min_11", 1.0))
    d_max = _finite_float(request.get("D_max_11", 2.0))
    if d_min is None or d_max is None or d_max <= d_min:
        reasons.append("normalization_bounds_invalid")
    if str(request.get("background_model_status", "")) in {"", "missing", "missing_or_simplified"}:
        reasons.append("chapter11_background_missing_as_zero")
    if request.get("t2k_reproduction_claim") is True:
        reasons.append("chapter11_t2k_reproduction_claim")
    if request.get("cp_measurement_claim") is True:
        reasons.append("chapter11_cp_measurement_claim")
    if request.get("real_detection_claim") is True:
        reasons.append("chapter11_result_claim_as_detection")
    if request.get("candidate_as_proof") is True:
        reasons.append("chapter11_candidate_as_proof")
    return reasons


def _finite_float(value: object) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def _blocked(reason_codes: list[str], next_action: str) -> dict[str, object]:
    return {
        "success": True,
        "type": "fnp_neutrino_chapter11_passage",
        "schema_version": SCHEMA_VERSION,
        "FNPReadout_11": {"status": "blocked"},
        "chapter12_entry_status": "blocked",
        "physical_model_validated": False,
        "decision": {
            "status": "blocked",
            "reason_codes": list(dict.fromkeys(reason_codes)),
            "next_action": next_action,
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }


__all__ = [
    "SCHEMA_VERSION",
    "neutrino_chapter11_passage_readout",
    "neutrino_chapter11_passage_readout_from_file",
]
