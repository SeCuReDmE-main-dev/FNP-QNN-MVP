"""Chapter-9 public-safe central experiment choice for neutrino simulations.

This module runs only after Synthia lexical admission and the FNP admission gate
accept the chapter-9 source-choice profile. It validates the selected
experiment container for the next chapter. It does not compute D_f, dF, or any
fractal candidate.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .neutrino_admission_gate import (
    CHAPTER9_EXPERIMENT_ID,
    CHAPTER9_REQUIRED_SOURCE_IDS,
    SYNTHIA_SCHEMA_VERSION,
    validate_synthia_admission,
)


SCHEMA_VERSION = "fnp.neutrino_chapter9_experiment_choice.v1"
BOUNDARY = "simulation_not_detection"
SOURCE_LAYER = "fnp_chapter9_experiment_choice"
FORBIDDEN_COMPUTATION_KEYS = {"D_f", "D_f_hat", "dF", "i_fractal", "i_fractal_candidate"}


def neutrino_chapter9_experiment_choice(payload: Mapping[str, Any]) -> dict[str, object]:
    """Return a chapter-9 experiment-choice contract after Synthia admission."""

    admission = validate_synthia_admission(payload)
    if not admission.can_compute_fnp:
        return _blocked(
            tuple(admission.reason_codes),
            "block_before_chapter9_experiment_choice",
            admission_decision=admission.as_dict(),
        )
    if admission.admitted_chapter9_source_choice is None:
        return _blocked(
            ("missing_chapter9_source_choice_profile",),
            "rerun_synthia_with_chapter9_source_choice_profile",
            admission_decision=admission.as_dict(),
        )

    overclaim = _overclaim_reason(payload)
    if overclaim is not None:
        return _blocked((overclaim,), "remove_overclaim_and_rerun", admission_decision=admission.as_dict())

    source_choice = dict(admission.admitted_chapter9_source_choice)
    central_experiment = dict(source_choice.get("central_experiment", {}))
    source_visibility = dict(source_choice.get("source_visibility", {}))
    paths = dict(source_choice.get("paths", {}))
    if _contains_forbidden_computation(source_choice):
        return _blocked(
            ("synthia_packet_contains_fnp_computation_fields",),
            "rerun_synthia_without_fnp_fields",
            admission_decision=admission.as_dict(),
        )

    decision_reasons: list[str] = []
    source_ids = source_visibility.get("provided_source_ids", [])
    source_set = {str(item).strip() for item in source_ids} if isinstance(source_ids, list) else set()
    if not CHAPTER9_REQUIRED_SOURCE_IDS <= source_set:
        decision_reasons.append("chapter9_missing_source_registry")
    if central_experiment.get("experiment_id") != CHAPTER9_EXPERIMENT_ID:
        decision_reasons.append("chapter9_unbounded_experiment_choice")
    if central_experiment.get("reproduction_status") != "not_T2K_reproduction":
        decision_reasons.append("chapter9_t2k_reproduction_claim")
    if central_experiment.get("detection_status") != "no_real_detection_claim":
        decision_reasons.append("chapter9_experiment_choice_as_detection")
    if central_experiment.get("ready_for_container") is not True:
        decision_reasons.append("chapter9_missing_central_experiment")
    if central_experiment.get("ready_for_physical_claim") is True:
        decision_reasons.append("chapter9_experiment_choice_as_detection")

    if decision_reasons:
        return _blocked(tuple(decision_reasons), "repair_chapter9_source_choice", admission_decision=admission.as_dict())

    return {
        "success": True,
        "type": "fnp_neutrino_chapter9_experiment_choice",
        "schema_version": SCHEMA_VERSION,
        "required_synthia_schema_version": SYNTHIA_SCHEMA_VERSION,
        "source_layer": SOURCE_LAYER,
        "boundary": BOUNDARY,
        "can_prepare_chapter10_container": True,
        "central_experiment_id": CHAPTER9_EXPERIMENT_ID,
        "chapter10_entry_status": "ready_for_experimental_container_design",
        "source_ids": sorted(source_set),
        "paths": paths,
        "admitted_chapter9_source_choice": source_choice,
        "decision": {
            "status": "accepted",
            "reason_codes": ["chapter9_experiment_choice_valid"],
            "next_action": "prepare_chapter10_container_under_guardrails",
        },
        "blocked_reason_codes": [],
        "claim_boundary": (
            "educational simulation; selected experiment is not T2K reproduction; "
            "no CP measurement; simulation is not detection; source stack is not proof"
        ),
    }


def neutrino_chapter9_experiment_choice_from_file(path: str | Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("neutrino chapter9 choice input file must contain a JSON object")
    return neutrino_chapter9_experiment_choice(payload)


def _blocked(
    reason_codes: tuple[str, ...],
    next_action: str,
    *,
    admission_decision: Mapping[str, object] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "success": True,
        "type": "fnp_neutrino_chapter9_experiment_choice",
        "schema_version": SCHEMA_VERSION,
        "required_synthia_schema_version": SYNTHIA_SCHEMA_VERSION,
        "source_layer": SOURCE_LAYER,
        "boundary": BOUNDARY,
        "can_prepare_chapter10_container": False,
        "central_experiment_id": "none",
        "chapter10_entry_status": "blocked",
        "decision": {
            "status": "blocked",
            "reason_codes": list(reason_codes),
            "next_action": next_action,
        },
        "blocked_reason_codes": list(reason_codes),
        "claim_boundary": (
            "educational simulation; selected experiment is not T2K reproduction; "
            "no CP measurement; simulation is not detection; source stack is not proof"
        ),
    }
    if admission_decision is not None:
        payload["admission_decision"] = dict(admission_decision)
    return payload


def _overclaim_reason(payload: Mapping[str, Any]) -> str | None:
    claim_surface = {
        key: payload.get(key)
        for key in (
            "chapter9_experiment_request",
            "experiment_request",
            "claim",
            "claims",
            "assertion",
            "assertions",
            "operator_claim",
            "operator_notes",
        )
        if key in payload
    }
    text = json.dumps(claim_surface, sort_keys=True, ensure_ascii=True, default=str).lower()
    if any(pattern in text for pattern in ("t2k reproduced", "t2k reproduction claim", "t2k_like = t2k")):
        return "chapter9_t2k_reproduction_claim"
    if any(pattern in text for pattern in ("cp measurement claim", "cp violation measured", "measures cp violation")):
        return "chapter9_cp_measurement_claim"
    if any(pattern in text for pattern in ("real_detection", "selected experiment is real detection", "detected real neutrino")):
        return "chapter9_experiment_choice_as_detection"
    if any(pattern in text for pattern in ("math source as physical proof", "mathematical source proves physical")):
        return "chapter9_math_source_as_physical_proof"
    if any(pattern in text for pattern in ("source stack proves", "sources prove the experiment")):
        return "chapter9_source_stack_as_proof"
    if any(pattern in text for pattern in ("background missing equals zero", "missing background is zero")):
        return "chapter9_background_missing_as_zero"
    return None


def _contains_forbidden_computation(value: object) -> bool:
    if isinstance(value, Mapping):
        return any(str(key) in FORBIDDEN_COMPUTATION_KEYS or _contains_forbidden_computation(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_forbidden_computation(item) for item in value)
    return False


__all__ = [
    "BOUNDARY",
    "SCHEMA_VERSION",
    "SOURCE_LAYER",
    "neutrino_chapter9_experiment_choice",
    "neutrino_chapter9_experiment_choice_from_file",
]
