"""Chapter-5 public-safe carrier normalization for neutrino-like events.

This module starts only after Synthia lexical admission and FNP admission pass.
It builds a bounded local carrier packet for D_f and D_f_hat. It deliberately
does not compute downstream dF, i_fractal, or an i_fractal candidate.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

from .neutrino_admission_gate import SYNTHIA_SCHEMA_VERSION, validate_synthia_admission
from .neutrosophic_quantum_primitives import normalize_fractal_dimension


SCHEMA_VERSION = "fnp.neutrino_chapter5_carrier.v1"
BOUNDARY = "simulation_not_detection"
SOURCE_LAYER = "fnp_chapter5_carrier"
VALID_CHAPTER5_CARRIER_FAMILIES = {
    "phase_carrier",
    "detector_projection_carrier",
    "secondary_trace_carrier",
    "plithogenic_contradiction_carrier",
    "multi_attribute_tension_carrier",
    "scale_transition_carrier",
    "null_carrier",
}


def neutrino_chapter5_carrier(payload: Mapping[str, Any]) -> dict[str, object]:
    """Return a chapter-5 D_f_hat carrier packet after lexical admission."""

    admission = validate_synthia_admission(payload)
    if not admission.can_compute_fnp:
        return _blocked(
            tuple(admission.reason_codes),
            "block_before_carrier",
            admission_decision=admission.as_dict(),
        )

    if admission.admitted_chapter5_intake is None:
        return _blocked(("missing_chapter5_intake_profile",), "rerun_synthia_with_chapter5_intake")

    carrier_request = payload.get("carrier_request")
    if not isinstance(carrier_request, Mapping):
        return _blocked(("missing_carrier_request",), "provide_carrier_request", admission_decision=admission.as_dict())

    if carrier_request.get("use_excluded_payload") is True or str(carrier_request.get("source", "")).strip() == "excluded_payload":
        return _blocked(("blocked_payload_used_for_carrier",), "use_allowed_payload_only", admission_decision=admission.as_dict())

    carrier_family = _normalize_token(carrier_request.get("carrier_family", carrier_request.get("family", "")))
    if carrier_family not in VALID_CHAPTER5_CARRIER_FAMILIES:
        return _blocked(("invalid_carrier_family",), "select_valid_carrier_family", admission_decision=admission.as_dict())

    d_f = _finite_float(carrier_request.get("D_f"), "D_f")
    d_min = _finite_float(carrier_request.get("D_min"), "D_min")
    d_max = _finite_float(carrier_request.get("D_max"), "D_max")
    if d_f is None or d_min is None or d_max is None:
        return _blocked(("missing_carrier_numeric_value",), "provide_D_f_D_min_D_max", admission_decision=admission.as_dict())
    if d_max <= d_min:
        return _blocked(("normalization_bounds_invalid",), "provide_valid_normalization_bounds", admission_decision=admission.as_dict())

    d_f_hat = normalize_fractal_dimension(d_f, d_min, d_max)
    scale_context = _scale_context(carrier_request, admission.admitted_chapter5_intake)
    d_f_hat_packet = {
        "carrier_family": carrier_family,
        "D_f": d_f,
        "D_min": d_min,
        "D_max": d_max,
        "D_f_hat": d_f_hat,
        "measurement_method": str(carrier_request.get("measurement_method", scale_context.get("measurement_method", "provided"))),
        "scale": str(carrier_request.get("scale", scale_context.get("scale", "local_chamber"))),
        "domain": str(carrier_request.get("domain", scale_context.get("domain", "toy_neutrino_event"))),
        "boundary": "bounded_local_carrier_not_downstream_friction",
    }
    return {
        "success": True,
        "type": "fnp_neutrino_chapter5_carrier",
        "schema_version": SCHEMA_VERSION,
        "required_synthia_schema_version": SYNTHIA_SCHEMA_VERSION,
        "source_layer": SOURCE_LAYER,
        "boundary": BOUNDARY,
        "can_compute_chapter5_carrier": True,
        "can_compute_dF": False,
        "decision": {
            "status": "accepted",
            "reason_codes": ["chapter5_carrier_normalized"],
            "next_action": "hold_for_chapter5_5_dF",
        },
        "E_FNP_neutrino": _e_fnp_neutrino(admission.as_dict()),
        "CarrierAdm": {
            "admitted": True,
            "carrier_family": carrier_family,
            "source": "allowed_payload_only",
        },
        "NormAdm": {
            "admitted": True,
            "method": "clamp01((D_f - D_min) / (D_max - D_min))",
            "bounds_valid": True,
        },
        "D_f_hat_packet": d_f_hat_packet,
        "Q_norm": 1.0,
        "claim_boundary": (
            "educational simulation; simulation is not detection; D_f_hat is a bounded local carrier; "
            "D_f_hat is not downstream friction and is not fractal indeterminacy."
        ),
    }


def neutrino_chapter5_carrier_from_file(path: str | Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("neutrino chapter5 carrier input file must contain a JSON object")
    return neutrino_chapter5_carrier(payload)


def _blocked(
    reason_codes: tuple[str, ...],
    next_action: str,
    *,
    admission_decision: Mapping[str, object] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "success": True,
        "type": "fnp_neutrino_chapter5_carrier",
        "schema_version": SCHEMA_VERSION,
        "required_synthia_schema_version": SYNTHIA_SCHEMA_VERSION,
        "source_layer": SOURCE_LAYER,
        "boundary": BOUNDARY,
        "can_compute_chapter5_carrier": False,
        "can_compute_dF": False,
        "decision": {
            "status": "blocked",
            "reason_codes": list(reason_codes),
            "next_action": next_action,
        },
        "CarrierAdm": {"admitted": False, "reason_codes": list(reason_codes)},
        "NormAdm": {"admitted": False, "reason_codes": list(reason_codes)},
        "D_f_hat_packet": None,
        "Q_norm": 0.0,
    }
    if admission_decision is not None:
        payload["admission_decision"] = dict(admission_decision)
    return payload


def _e_fnp_neutrino(admission_decision: Mapping[str, object]) -> dict[str, object]:
    allowed_payload = admission_decision.get("allowed_payload")
    chapter5 = admission_decision.get("admitted_chapter5_intake")
    chapter5 = chapter5 if isinstance(chapter5, Mapping) else {}
    event_request = chapter5.get("event_request") if isinstance(chapter5.get("event_request"), Mapping) else {}
    return {
        "event_id": event_request.get("event_id", (allowed_payload or {}).get("event_id") if isinstance(allowed_payload, Mapping) else None),
        "simulation_status": event_request.get("simulation_status", "simulation"),
        "allowed_payload_status": event_request.get("allowed_payload_status", "present" if allowed_payload else "missing"),
        "source_trace_status": event_request.get("source_trace_status", "unknown"),
        "object_boundary": "E_FNP_neutrino is a chamber event, not a real neutrino and not detector data.",
    }


def _scale_context(carrier_request: Mapping[str, Any], chapter5_intake: Mapping[str, object]) -> Mapping[str, object]:
    scale_request = chapter5_intake.get("scale_context_request")
    if isinstance(scale_request, Mapping):
        return scale_request
    return {
        "domain": carrier_request.get("domain", "toy_neutrino_event"),
        "scale": carrier_request.get("scale", "local_chamber"),
        "measurement_method": carrier_request.get("measurement_method", "provided"),
    }


def _finite_float(value: object, label: str) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _normalize_token(value: object) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


__all__ = [
    "BOUNDARY",
    "SCHEMA_VERSION",
    "SOURCE_LAYER",
    "VALID_CHAPTER5_CARRIER_FAMILIES",
    "neutrino_chapter5_carrier",
    "neutrino_chapter5_carrier_from_file",
]
