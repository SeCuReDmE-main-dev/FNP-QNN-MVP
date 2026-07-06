"""Public-safe FNP-QNN admission gate for neutrino-like simulation events.

This module validates the Synthia lexical admission packet before any FNP-QNN
friction or fractal computation can run. It does not compute D_f, dF, or
i_fractal; it only decides whether a downstream simulation may proceed.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any, Mapping


SCHEMA_VERSION = "fnp.neutrino_admission.v1"
SYNTHIA_SCHEMA_VERSION = "synthia.lex_neutrino.v1"
BOUNDARY = "simulation_not_detection"
SOURCE_LAYER = "fnp_admission"

ACCEPTED_SYNTHIA_STATUSES = {"accepted", "accepted_with_partition"}
BLOCKING_SYNTHIA_STATUSES = {"corrected", "suspended", "rejected"}
REFUSAL_CATEGORIES = (
    "real_detection_claim",
    "strong_primary_interaction_claim",
    "literal_mass_gain_loss_claim",
    "decay_as_internal_flavor_mechanism",
    "fusion_as_internal_flavor_mechanism",
    "choice_or_intention_language",
    "dL_lex_equals_dF",
    "I_lexicon_equals_i_fractal",
    "missing_source_truth",
    "missing_interaction_channel",
    "detector_trace_confused_with_particle",
    "candidate_confused_with_proof",
)


@dataclass(frozen=True)
class FNPAdmissionDecision:
    can_compute_fnp: bool
    status: str
    reason_codes: tuple[str, ...]
    next_action: str
    dL_lex: float | None

    def as_dict(self) -> dict[str, object]:
        return {
            "can_compute_fnp": self.can_compute_fnp,
            "status": self.status,
            "reason_codes": list(self.reason_codes),
            "next_action": self.next_action,
            "source_layer": SOURCE_LAYER,
            "dL_lex": self.dL_lex,
        }


def validate_synthia_admission(payload: Mapping[str, Any]) -> FNPAdmissionDecision:
    packet = _extract_lex_packet(payload)
    if packet is None:
        return _blocked("missing_synthia_lex_packet", "block_fnp")

    reason_codes: list[str] = []
    if packet.get("schema_version") != SYNTHIA_SCHEMA_VERSION:
        reason_codes.append("invalid_synthia_schema_version")

    d_l_lex = _optional_float(packet.get("dL_lex"))
    if d_l_lex is None or not 0.0 <= d_l_lex <= 1.0:
        reason_codes.append("invalid_dL_lex")

    if packet.get("Adm_lex") is not True:
        reason_codes.append("adm_lex_false")

    decision = packet.get("decision") if isinstance(packet.get("decision"), Mapping) else {}
    synthia_status = str(decision.get("status", "")).strip()
    if not synthia_status:
        reason_codes.append("missing_synthia_decision_status")
    elif synthia_status in BLOCKING_SYNTHIA_STATUSES:
        reason_codes.append("synthia_decision_not_admitted")
    elif synthia_status not in ACCEPTED_SYNTHIA_STATUSES:
        reason_codes.append("unknown_synthia_decision_status")

    refusal_packet = packet.get("refusal_packet") if isinstance(packet.get("refusal_packet"), Mapping) else {}
    packet_reason_codes = refusal_packet.get("reason_codes", decision.get("reason_codes", []))
    for code in _reason_list(packet_reason_codes):
        if code in REFUSAL_CATEGORIES and code not in reason_codes:
            reason_codes.append(code)

    if _contains_fnp_computation_fields(packet):
        reason_codes.append("synthia_packet_contains_fnp_computation_fields")
    if _numeric_equal(packet.get("dL_lex"), packet.get("dF")) or "dL_lex_equals_dF" in reason_codes:
        if "dL_lex_equals_dF" not in reason_codes:
            reason_codes.append("dL_lex_equals_dF")
    if _numeric_equal(packet.get("I_lexicon"), packet.get("i_fractal")) or "I_lexicon_equals_i_fractal" in reason_codes:
        if "I_lexicon_equals_i_fractal" not in reason_codes:
            reason_codes.append("I_lexicon_equals_i_fractal")

    if reason_codes:
        return FNPAdmissionDecision(
            can_compute_fnp=False,
            status="blocked",
            reason_codes=tuple(reason_codes),
            next_action="block_fnp",
            dL_lex=d_l_lex,
        )
    return FNPAdmissionDecision(
        can_compute_fnp=True,
        status="accepted",
        reason_codes=("synthia_admission_valid",),
        next_action="compute_fnp",
        dL_lex=d_l_lex,
    )


def neutrino_guardrail_check(payload: Mapping[str, Any]) -> dict[str, object]:
    decision = validate_synthia_admission(payload)
    return {
        "success": True,
        "type": "fnp_neutrino_admission_gate",
        "schema_version": SCHEMA_VERSION,
        "required_synthia_schema_version": SYNTHIA_SCHEMA_VERSION,
        "can_compute_fnp": decision.can_compute_fnp,
        "decision": decision.as_dict(),
        "source_layer": SOURCE_LAYER,
        "boundary": BOUNDARY,
        "claim_boundary": (
            "educational simulation; simulation is not detection; weak interaction primary guardrail; "
            "Synthia classifies before FNP-QNN computes; dL_lex remains separate from downstream friction; "
            "I_lexicon remains separate from downstream fractal admission."
        ),
    }


def neutrino_guardrail_check_from_file(path: str | Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("neutrino admission input file must contain a JSON object")
    return neutrino_guardrail_check(payload)


def _extract_lex_packet(payload: Mapping[str, Any]) -> Mapping[str, Any] | None:
    if not isinstance(payload, Mapping):
        return None
    for key in ("lex_packet", "LexPacket_neutrino"):
        value = payload.get(key)
        if isinstance(value, Mapping):
            return value
    if payload.get("schema_version") == SYNTHIA_SCHEMA_VERSION:
        return payload
    return None


def _blocked(reason_code: str, next_action: str) -> FNPAdmissionDecision:
    return FNPAdmissionDecision(
        can_compute_fnp=False,
        status="blocked",
        reason_codes=(reason_code,),
        next_action=next_action,
        dL_lex=None,
    )


def _reason_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, tuple):
        return [str(item) for item in value]
    return []


def _contains_fnp_computation_fields(packet: Mapping[str, Any]) -> bool:
    return any(key in packet for key in ("D_f", "dF", "i_fractal"))


def _optional_float(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _numeric_equal(left: object, right: object) -> bool:
    left_number = _optional_float(left)
    right_number = _optional_float(right)
    if left_number is None or right_number is None:
        return False
    return abs(left_number - right_number) < 1e-12


__all__ = [
    "BOUNDARY",
    "REFUSAL_CATEGORIES",
    "SCHEMA_VERSION",
    "SYNTHIA_SCHEMA_VERSION",
    "FNPAdmissionDecision",
    "neutrino_guardrail_check",
    "neutrino_guardrail_check_from_file",
    "validate_synthia_admission",
]
