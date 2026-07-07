"""Chapter-7 public-safe FNP readout for neutrino-like simulation events.

This module runs only after Synthia lexical admission and FNP admission pass.
It produces a local simulation readout for D_f, D_f_hat, dF, and a conditional
i_fractal candidate. It is not detector data and it is not physical proof.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

from .neutrino_admission_gate import SYNTHIA_SCHEMA_VERSION, validate_synthia_admission
from .neutrosophic_quantum_primitives import normalize_fractal_dimension


SCHEMA_VERSION = "fnp.neutrino_chapter7_readout.v1"
BOUNDARY = "simulation_not_detection"
SOURCE_LAYER = "fnp_chapter7_readout"
REQUIRED_TENSIONS = (
    "basis_frustration",
    "phase_frustration",
    "energy_scale_frustration",
    "detector_projection_tension",
    "gravity_relation_tension",
    "source_truth_tension",
    "lexicon_gap_tension",
    "composite_friction_tension",
)


def neutrino_chapter7_readout(payload: Mapping[str, Any]) -> dict[str, object]:
    """Return a chapter-7 readout after Synthia and FNP admission gates."""

    admission = validate_synthia_admission(payload)
    if not admission.can_compute_fnp:
        return _blocked(
            tuple(admission.reason_codes),
            "block_before_chapter7_readout",
            admission_decision=admission.as_dict(),
        )
    if admission.admitted_chapter7_transition is None:
        return _blocked(
            ("missing_chapter7_transition_profile",),
            "rerun_synthia_with_chapter7_transition",
            admission_decision=admission.as_dict(),
        )

    request = payload.get("chapter7_readout_request", payload.get("readout_request"))
    if not isinstance(request, Mapping):
        return _blocked(
            ("missing_chapter7_readout_request",),
            "provide_chapter7_readout_request",
            admission_decision=admission.as_dict(),
        )
    overclaim = _overclaim_reason(request)
    if overclaim is not None:
        return _blocked((overclaim,), "remove_overclaim_and_rerun", admission_decision=admission.as_dict())

    tensions = _friction_tensions(request)
    if tensions is None:
        return _blocked(
            ("missing_friction_tension",),
            "provide_all_chapter7_friction_tensions",
            admission_decision=admission.as_dict(),
        )
    lexicon_gap = tensions["lexicon_gap_tension"]
    if admission.dL_lex is None or abs(lexicon_gap - admission.dL_lex) > 1e-8:
        return _blocked(
            ("chapter7_lexicon_gap_mismatch",),
            "align_lexicon_gap_tension_with_dL_lex",
            admission_decision=admission.as_dict(),
        )

    d_f = _finite_float(request.get("D_f"))
    d_min = _finite_float(request.get("D_min"))
    d_max = _finite_float(request.get("D_max"))
    if d_f is None or d_min is None or d_max is None:
        return _blocked(
            ("missing_fractal_dimension_value",),
            "provide_D_f_D_min_D_max",
            admission_decision=admission.as_dict(),
        )
    if d_max <= d_min:
        return _blocked(
            ("normalization_bounds_invalid",),
            "provide_valid_normalization_bounds",
            admission_decision=admission.as_dict(),
        )

    d_f_hat = normalize_fractal_dimension(d_f, d_min, d_max)
    d_friction = d_f_hat
    i_fractal_candidate = d_f_hat
    return {
        "success": True,
        "type": "fnp_neutrino_chapter7_readout",
        "schema_version": SCHEMA_VERSION,
        "required_synthia_schema_version": SYNTHIA_SCHEMA_VERSION,
        "source_layer": SOURCE_LAYER,
        "boundary": BOUNDARY,
        "can_compute_chapter7_readout": True,
        "ready_for_FNP": "true_after_Synthia",
        "decision": {
            "status": "accepted",
            "reason_codes": ["chapter7_readout_computed"],
            "next_action": "chapter8_first_run_interpretation",
        },
        "admitted_chapter7_transition": dict(admission.admitted_chapter7_transition),
        "friction_tensions": tensions,
        "D_f": d_f,
        "D_f_hat": d_f_hat,
        "dF": d_friction,
        "i_fractal_candidate": i_fractal_candidate,
        "hierarchy": "I -> I_system^S -> D_f -> dF -> i_fractal",
        "chapter8_entry_status": "ready_for_first_run_interpretation",
        "claim_boundary": "educational simulation; candidate is not proof; simulation is not detection",
    }


def neutrino_chapter7_readout_from_file(path: str | Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("neutrino chapter7 readout input file must contain a JSON object")
    return neutrino_chapter7_readout(payload)


def _blocked(
    reason_codes: tuple[str, ...],
    next_action: str,
    *,
    admission_decision: Mapping[str, object] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "success": True,
        "type": "fnp_neutrino_chapter7_readout",
        "schema_version": SCHEMA_VERSION,
        "required_synthia_schema_version": SYNTHIA_SCHEMA_VERSION,
        "source_layer": SOURCE_LAYER,
        "boundary": BOUNDARY,
        "can_compute_chapter7_readout": False,
        "ready_for_FNP": "false",
        "decision": {
            "status": "blocked",
            "reason_codes": list(reason_codes),
            "next_action": next_action,
        },
        "friction_tensions": None,
        "D_f": None,
        "D_f_hat": None,
        "dF": None,
        "i_fractal_candidate": None,
        "chapter8_entry_status": "blocked",
    }
    if admission_decision is not None:
        payload["admission_decision"] = dict(admission_decision)
    return payload


def _friction_tensions(request: Mapping[str, Any]) -> dict[str, float] | None:
    raw = request.get("friction_tensions")
    if not isinstance(raw, Mapping):
        return None
    tensions: dict[str, float] = {}
    for key in REQUIRED_TENSIONS:
        value = _finite_float(raw.get(key))
        if value is None:
            return None
        tensions[key] = value
    return tensions


def _overclaim_reason(request: Mapping[str, Any]) -> str | None:
    text = json.dumps(request, sort_keys=True, ensure_ascii=True, default=str).lower()
    if any(pattern in text for pattern in ("real_detection", "detected real neutrino", "detector data claim")):
        return "real_detection_claim"
    if any(pattern in text for pattern in ("candidate_as_proof", "candidate proves", "physical proof")):
        return "candidate_confused_with_proof"
    return None


def _finite_float(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


__all__ = [
    "BOUNDARY",
    "SCHEMA_VERSION",
    "SOURCE_LAYER",
    "neutrino_chapter7_readout",
    "neutrino_chapter7_readout_from_file",
]
