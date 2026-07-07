"""Chapter-8 public-safe first-run permission for neutrino-like simulations.

This module runs only after Synthia lexical admission and the FNP admission gate
accept the packet. It validates whether a first run may continue. It does not
compute fractal friction and does not produce a fractal candidate.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .neutrino_admission_gate import SYNTHIA_SCHEMA_VERSION, validate_synthia_admission


SCHEMA_VERSION = "fnp.neutrino_chapter8_run_permission.v1"
BOUNDARY = "simulation_not_detection"
SOURCE_LAYER = "fnp_chapter8_run_permission"


def neutrino_chapter8_run_permission(payload: Mapping[str, Any]) -> dict[str, object]:
    """Return a chapter-8 permission contract after Synthia admission."""

    admission = validate_synthia_admission(payload)
    if not admission.can_compute_fnp:
        return _blocked(
            tuple(admission.reason_codes),
            "block_before_chapter8_run_permission",
            admission_decision=admission.as_dict(),
        )
    if admission.admitted_chapter8_run is None:
        return _blocked(
            ("missing_chapter8_run_profile",),
            "rerun_synthia_with_chapter8_run_profile",
            admission_decision=admission.as_dict(),
        )

    overclaim = _overclaim_reason(payload)
    if overclaim is not None:
        return _blocked((overclaim,), "remove_overclaim_and_rerun", admission_decision=admission.as_dict())

    run_profile = dict(admission.admitted_chapter8_run)
    run_decision = dict(run_profile.get("run_decision", {}))
    run_permission = dict(run_profile.get("run_permission", {}))
    run_status = str(run_decision.get("run_status", "")).strip()
    allowed_next_step = str(run_permission.get("allowed_next_step", "")).strip()
    permission_to_continue = run_permission.get("permission_to_continue") is True

    if run_status != "admissible_under_guardrails":
        return _blocked(
            ("chapter8_not_admissible",),
            "repair_or_stop_first_run",
            admission_decision=admission.as_dict(),
            admitted_chapter8_run=run_profile,
        )
    if not permission_to_continue or allowed_next_step != "FNP_QNN_readout":
        return _blocked(
            ("chapter8_missing_permission",),
            "repair_first_run_permission",
            admission_decision=admission.as_dict(),
            admitted_chapter8_run=run_profile,
        )

    return {
        "success": True,
        "type": "fnp_neutrino_chapter8_run_permission",
        "schema_version": SCHEMA_VERSION,
        "required_synthia_schema_version": SYNTHIA_SCHEMA_VERSION,
        "source_layer": SOURCE_LAYER,
        "boundary": BOUNDARY,
        "can_continue_to_fnp_readout": True,
        "can_continue_to_chapter9": True,
        "run_status": run_status,
        "allowed_next_step": allowed_next_step,
        "decision": {
            "status": "accepted",
            "reason_codes": ["chapter8_run_permission_valid"],
            "next_action": "continue_to_fnp_readout_under_guardrails",
        },
        "admitted_chapter8_run": run_profile,
        "blocked_reason_codes": [],
        "claim_boundary": "educational simulation; permission is not proof; simulation is not detection",
    }


def neutrino_chapter8_run_permission_from_file(path: str | Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("neutrino chapter8 run input file must contain a JSON object")
    return neutrino_chapter8_run_permission(payload)


def _blocked(
    reason_codes: tuple[str, ...],
    next_action: str,
    *,
    admission_decision: Mapping[str, object] | None = None,
    admitted_chapter8_run: Mapping[str, object] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "success": True,
        "type": "fnp_neutrino_chapter8_run_permission",
        "schema_version": SCHEMA_VERSION,
        "required_synthia_schema_version": SYNTHIA_SCHEMA_VERSION,
        "source_layer": SOURCE_LAYER,
        "boundary": BOUNDARY,
        "can_continue_to_fnp_readout": False,
        "can_continue_to_chapter9": False,
        "run_status": "blocked",
        "allowed_next_step": "none",
        "decision": {
            "status": "blocked",
            "reason_codes": list(reason_codes),
            "next_action": next_action,
        },
        "blocked_reason_codes": list(reason_codes),
        "claim_boundary": "educational simulation; permission is not proof; simulation is not detection",
    }
    if admission_decision is not None:
        payload["admission_decision"] = dict(admission_decision)
    if admitted_chapter8_run is not None:
        payload["admitted_chapter8_run"] = dict(admitted_chapter8_run)
    return payload


def _overclaim_reason(payload: Mapping[str, Any]) -> str | None:
    claim_surface = {
        key: payload.get(key)
        for key in (
            "chapter8_run_request",
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
    if any(pattern in text for pattern in ("permission_to_continue is proof", "permission_to_continue=proof")):
        return "chapter8_permission_as_proof"
    if any(pattern in text for pattern in ("admissible_as_detection", "admissible means detection")):
        return "chapter8_admissible_as_detection"
    if any(pattern in text for pattern in ("candidate_as_proof", "candidate proves", "physical proof")):
        return "chapter8_candidate_as_proof"
    if any(pattern in text for pattern in ("real_detection", "detected real neutrino", "detector data claim")):
        return "real_detection_claim"
    return None


__all__ = [
    "BOUNDARY",
    "SCHEMA_VERSION",
    "SOURCE_LAYER",
    "neutrino_chapter8_run_permission",
    "neutrino_chapter8_run_permission_from_file",
]
