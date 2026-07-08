"""Chapter-10 public-safe chamber/container/run-contract validation.

This module runs only after Synthia lexical admission and the FNP admission
gate accept the chapter-10 chamber profile. It validates that the chamber,
container, simulated event, and run contract are ready for a chapter-11
first passage. It does not compute D_f, dF, or any fractal candidate.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .neutrino_admission_gate import SYNTHIA_SCHEMA_VERSION, validate_synthia_admission


SCHEMA_VERSION = "fnp.neutrino_chapter10_run_contract.v1"
BOUNDARY = "simulation_not_detection"
SOURCE_LAYER = "fnp_chapter10_run_contract"
FORBIDDEN_COMPUTATION_KEYS = {"D_f", "D_f_hat", "dF", "i_fractal", "i_fractal_candidate"}


def neutrino_chapter10_run_contract(payload: Mapping[str, Any]) -> dict[str, object]:
    """Return a chapter-10 run-preparation contract after Synthia admission."""

    admission = validate_synthia_admission(payload)
    if not admission.can_compute_fnp:
        return _blocked(
            tuple(admission.reason_codes),
            "block_before_chapter10_run_contract",
            admission_decision=admission.as_dict(),
        )
    if admission.admitted_chapter10_chamber is None:
        return _blocked(
            ("missing_chapter10_chamber_profile",),
            "rerun_synthia_with_chapter10_chamber_profile",
            admission_decision=admission.as_dict(),
        )

    overclaim = _overclaim_reason(payload)
    if overclaim is not None:
        return _blocked((overclaim,), "remove_overclaim_and_rerun", admission_decision=admission.as_dict())

    chapter10 = dict(admission.admitted_chapter10_chamber)
    if _contains_forbidden_computation(chapter10):
        return _blocked(
            ("synthia_packet_contains_fnp_computation_fields",),
            "rerun_synthia_without_fnp_fields",
            admission_decision=admission.as_dict(),
        )

    run_prepared = dict(chapter10.get("RunPrepared_10", {}))
    run_contract = dict(chapter10.get("RunContract_10", {}))
    event = dict(chapter10.get("SimulatedNeutrinoEvent_10", {}))
    container = dict(chapter10.get("EventContainer_10", {}))

    decision_reasons: list[str] = []
    if chapter10.get("chapter10_status") != "run_prepared_for_chapter11":
        decision_reasons.append("chapter10_not_ready_after_synthia")
    if run_prepared.get("chapter11_execution_ready") is not True:
        decision_reasons.append("chapter10_not_ready_after_synthia")
    if run_prepared.get("physical_claim_allowed") is not False:
        decision_reasons.append("chapter10_unbounded_manipulation")
    if run_prepared.get("FNP_after_Synthia_only") is not True:
        decision_reasons.append("chapter10_fnp_before_synthia")
    if container.get("required_fields_present") is not True:
        decision_reasons.append("chapter10_missing_container_contract")
    if event.get("event_status") != "educational_simulation":
        decision_reasons.append("chapter10_missing_simulated_event")
    if event.get("detection_status") != "no_real_detection_claim":
        decision_reasons.append("chapter10_event_as_detection")
    if event.get("reproduction_status") != "not_T2K_reproduction":
        decision_reasons.append("chapter10_t2k_reproduction_claim")
    if event.get("measurement_status") != "no_CP_measurement_claim":
        decision_reasons.append("chapter10_cp_measurement_claim")
    if run_contract.get("run_contract_status") != "declared":
        decision_reasons.append("chapter10_missing_run_contract")
    if run_contract.get("contract_boundary") != "prepared_tension_slot != dF":
        decision_reasons.append("chapter10_prepared_tension_as_df")

    if decision_reasons:
        return _blocked(
            tuple(decision_reasons),
            "repair_chapter10_run_contract",
            admission_decision=admission.as_dict(),
            admitted_chapter10_chamber=chapter10,
        )

    return {
        "success": True,
        "type": "fnp_neutrino_chapter10_run_contract",
        "schema_version": SCHEMA_VERSION,
        "required_synthia_schema_version": SYNTHIA_SCHEMA_VERSION,
        "source_layer": SOURCE_LAYER,
        "boundary": BOUNDARY,
        "can_prepare_chapter11_run": True,
        "chapter11_entry_status": "ready_for_first_passage_under_declared_contract",
        "run_contract": run_contract,
        "run_prepared": run_prepared,
        "admitted_chapter10_chamber": chapter10,
        "decision": {
            "status": "accepted",
            "reason_codes": ["chapter10_run_contract_valid"],
            "next_action": "execute_chapter11_first_passage_under_guardrails",
        },
        "blocked_reason_codes": [],
        "claim_boundary": (
            "educational simulation; chamber is not detector; container is not proof; "
            "simulated event is not detection; no T2K reproduction; no CP measurement; "
            "prepared tension slots are not dF"
        ),
    }


def neutrino_chapter10_run_contract_from_file(path: str | Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("neutrino chapter10 run-contract input file must contain a JSON object")
    return neutrino_chapter10_run_contract(payload)


def _blocked(
    reason_codes: tuple[str, ...],
    next_action: str,
    *,
    admission_decision: Mapping[str, object] | None = None,
    admitted_chapter10_chamber: Mapping[str, object] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "success": True,
        "type": "fnp_neutrino_chapter10_run_contract",
        "schema_version": SCHEMA_VERSION,
        "required_synthia_schema_version": SYNTHIA_SCHEMA_VERSION,
        "source_layer": SOURCE_LAYER,
        "boundary": BOUNDARY,
        "can_prepare_chapter11_run": False,
        "chapter11_entry_status": "blocked",
        "decision": {
            "status": "blocked",
            "reason_codes": list(reason_codes),
            "next_action": next_action,
        },
        "blocked_reason_codes": list(reason_codes),
        "claim_boundary": (
            "educational simulation; chamber is not detector; container is not proof; "
            "simulated event is not detection; no T2K reproduction; no CP measurement; "
            "prepared tension slots are not dF"
        ),
    }
    if admission_decision is not None:
        payload["admission_decision"] = dict(admission_decision)
    if admitted_chapter10_chamber is not None:
        payload["admitted_chapter10_chamber"] = dict(admitted_chapter10_chamber)
    return payload


def _overclaim_reason(payload: Mapping[str, Any]) -> str | None:
    claim_surface = {
        key: payload.get(key)
        for key in (
            "chapter10_run_request",
            "run_request",
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
    if any(pattern in text for pattern in ("chamber = detector", "chamber is detector")):
        return "chapter10_chamber_as_detector"
    if any(pattern in text for pattern in ("container valid is proof", "container_valid = physical_proof")):
        return "chapter10_container_as_proof"
    if any(pattern in text for pattern in ("simulated event is detection", "event is real detection")):
        return "chapter10_event_as_detection"
    if any(pattern in text for pattern in ("t2k reproduced", "t2k reproduction claim", "t2k_like = t2k")):
        return "chapter10_t2k_reproduction_claim"
    if any(pattern in text for pattern in ("cp measurement claim", "path_comparison = cp_measurement")):
        return "chapter10_cp_measurement_claim"
    if any(pattern in text for pattern in ("background missing equals zero", "background_missing = background_zero")):
        return "chapter10_background_missing_as_zero"
    if any(pattern in text for pattern in ("prepared_tension_slot = df", "prepared tension is df")):
        return "chapter10_prepared_tension_as_df"
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
    "neutrino_chapter10_run_contract",
    "neutrino_chapter10_run_contract_from_file",
]
