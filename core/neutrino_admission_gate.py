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
    "literal_mass_change_claim",
    "decay_as_internal_flavor_mechanism",
    "fusion_as_internal_flavor_mechanism",
    "choice_or_intention_language",
    "dL_lex_equals_dF",
    "I_lexicon_equals_i_fractal",
    "missing_source_truth",
    "missing_interaction_channel",
    "detector_trace_confused_with_particle",
    "candidate_confused_with_proof",
    "unknown_flavor_as_truth",
    "flavor_mass_collapse",
    "mass_basis_equals_flavor_basis",
    "pmns_measured_claim",
    "invalid_energy_gev",
    "phase_tension_as_new_physics",
    "visible_neutrino_claim",
    "simulation_trace_as_detection",
    "trace_as_neutrino_total",
    "secondary_response_as_primary_force",
    "new_force_from_nuclear_activity",
    "gravity_detection_channel_claim",
    "metaphor_as_physics",
    "speculation_as_physical_conclusion",
    "missing_source_for_physical_claim",
    "invalid_chapter3_profile",
    "invalid_chapter4_profile",
    "chapter4_not_approved_for_fnp",
    "chapter4_guard_blocked",
    "missing_chapter4_allowed_payload",
    "invalid_chapter5_intake_profile",
    "chapter5_not_approved_for_fnp_intake",
    "missing_chapter5_allowed_payload",
    "missing_carrier_request",
    "invalid_carrier_family",
    "missing_scale_context",
    "synthia_packet_contains_fnp_computation_fields",
)
VALID_INTERACTION_CHANNELS = {"weak_CC", "weak_NC"}
VALID_CHAPTER5_CARRIER_FAMILIES = {
    "phase_carrier",
    "detector_projection_carrier",
    "secondary_trace_carrier",
    "plithogenic_contradiction_carrier",
    "multi_attribute_tension_carrier",
    "scale_transition_carrier",
    "null_carrier",
}


@dataclass(frozen=True)
class FNPAdmissionDecision:
    can_compute_fnp: bool
    status: str
    reason_codes: tuple[str, ...]
    next_action: str
    dL_lex: float | None
    admitted_chapter3_carriers: Mapping[str, object] | None
    admitted_chapter4_guard: Mapping[str, object] | None = None
    admitted_chapter5_intake: Mapping[str, object] | None = None
    allowed_payload: Mapping[str, object] | None = None
    excluded_payload_summary: Mapping[str, object] | None = None

    def as_dict(self) -> dict[str, object]:
        payload = {
            "can_compute_fnp": self.can_compute_fnp,
            "status": self.status,
            "reason_codes": list(self.reason_codes),
            "next_action": self.next_action,
            "source_layer": SOURCE_LAYER,
            "dL_lex": self.dL_lex,
        }
        if self.admitted_chapter3_carriers is not None:
            payload["admitted_chapter3_carriers"] = dict(self.admitted_chapter3_carriers)
        if self.admitted_chapter4_guard is not None:
            payload["admitted_chapter4_guard"] = dict(self.admitted_chapter4_guard)
        if self.admitted_chapter5_intake is not None:
            payload["admitted_chapter5_intake"] = dict(self.admitted_chapter5_intake)
        if self.allowed_payload is not None:
            payload["allowed_payload"] = dict(self.allowed_payload)
        if self.excluded_payload_summary is not None:
            payload["excluded_payload_summary"] = dict(self.excluded_payload_summary)
        return payload


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

    chapter3_reasons, admitted_chapter3_carriers = _validate_chapter3_profile(packet)
    for code in chapter3_reasons:
        if code not in reason_codes:
            reason_codes.append(code)

    chapter4_reasons, admitted_chapter4_guard, allowed_payload, excluded_payload_summary = _validate_chapter4_profile(packet)
    for code in chapter4_reasons:
        if code not in reason_codes:
            reason_codes.append(code)

    chapter5_reasons, admitted_chapter5_intake = _validate_chapter5_intake_profile(packet)
    for code in chapter5_reasons:
        if code not in reason_codes:
            reason_codes.append(code)

    if reason_codes:
        return FNPAdmissionDecision(
            can_compute_fnp=False,
            status="blocked",
            reason_codes=tuple(reason_codes),
            next_action="block_fnp",
            dL_lex=d_l_lex,
            admitted_chapter3_carriers=None,
        )
    return FNPAdmissionDecision(
        can_compute_fnp=True,
        status="accepted",
        reason_codes=("synthia_admission_valid",),
        next_action="compute_fnp",
        dL_lex=d_l_lex,
        admitted_chapter3_carriers=admitted_chapter3_carriers,
        admitted_chapter4_guard=admitted_chapter4_guard,
        admitted_chapter5_intake=admitted_chapter5_intake,
        allowed_payload=allowed_payload,
        excluded_payload_summary=excluded_payload_summary,
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
        "admitted_chapter3_carriers": decision.admitted_chapter3_carriers,
        "admitted_chapter4_guard": decision.admitted_chapter4_guard,
        "admitted_chapter5_intake": decision.admitted_chapter5_intake,
        "allowed_payload": decision.allowed_payload,
        "excluded_payload_summary": decision.excluded_payload_summary,
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
        admitted_chapter3_carriers=None,
    )


def _reason_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, tuple):
        return [str(item) for item in value]
    return []


def _contains_fnp_computation_fields(packet: Mapping[str, Any]) -> bool:
    return _contains_key_recursive(packet, {"D_f", "D_f_hat", "dF", "i_fractal", "i_fractal_candidate"})


def _validate_chapter3_profile(packet: Mapping[str, Any]) -> tuple[list[str], Mapping[str, object] | None]:
    profile = packet.get("chapter3_profile")
    if profile is None:
        return [], None
    if not isinstance(profile, Mapping):
        return ["invalid_chapter3_profile"], None

    reason_codes: list[str] = []
    carriers = _admitted_chapter3_carriers(profile)

    if _contains_fnp_computation_fields(profile):
        reason_codes.append("synthia_packet_contains_fnp_computation_fields")

    flavor_basis = _nested_mapping(profile, "flavor_profile", "I_flavor", "flavor_basis")
    mass_basis = _nested_mapping(profile, "mass_profile", "I_mass", "mass_basis")
    if _basis_vectors_equal(flavor_basis, mass_basis):
        reason_codes.append("mass_basis_equals_flavor_basis")

    interaction = _nested_mapping(profile, "interaction_profile", "I_interaction")
    channel = str(interaction.get("channel", "")).strip()
    if channel and channel not in VALID_INTERACTION_CHANNELS:
        reason_codes.append("strong_primary_interaction_claim")

    detector = _nested_mapping(profile, "detector_profile", "I_detector")
    detector_text = _json_text(detector)
    if str(detector.get("detector_projection_status", "")).strip().lower() == "direct":
        reason_codes.append("visible_neutrino_claim")
    if _contains_any(detector_text, ("i_detector = i_neutrino", "neutrino_seen_directly", "neutrino_total")):
        reason_codes.append("trace_as_neutrino_total")

    secondary = _nested_mapping(profile, "secondary_profile", "I_secondary")
    secondary_text = _json_text(secondary)
    if _contains_any(secondary_text, ("primary_force", "strong_primary", "secondary_response = primary_force")):
        reason_codes.append("secondary_response_as_primary_force")

    return reason_codes, carriers


def _validate_chapter4_profile(
    packet: Mapping[str, Any],
) -> tuple[list[str], Mapping[str, object] | None, Mapping[str, object] | None, Mapping[str, object] | None]:
    profile = packet.get("chapter4_profile")
    if profile is None:
        return [], None, None, None
    if not isinstance(profile, Mapping):
        return ["invalid_chapter4_profile"], None, None, None

    reason_codes: list[str] = []
    if _contains_fnp_computation_fields(profile):
        reason_codes.append("synthia_packet_contains_fnp_computation_fields")

    protection = _nested_mapping(profile, "protection_profile")
    guard = _nested_mapping(protection, "SynthiaGuard_neutrino")
    protection_packet = _nested_mapping(protection, "ProtectionPacket_neutrino")
    if not guard or not protection_packet:
        reason_codes.append("invalid_chapter4_profile")
        return reason_codes, None, None, None

    approved = guard.get("approved_for_fnp")
    approved_for_fnp = approved is True or str(approved).strip().lower() == "true_for_allowed_payload_only"
    if not approved_for_fnp:
        reason_codes.append("chapter4_not_approved_for_fnp")

    if _chapter4_guard_has_block(protection_packet):
        reason_codes.append("chapter4_guard_blocked")

    allowed_payload = guard.get("allowed_payload") if isinstance(guard.get("allowed_payload"), Mapping) else None
    decision = packet.get("decision") if isinstance(packet.get("decision"), Mapping) else {}
    if str(decision.get("status", "")).strip() == "accepted_with_partition" and not allowed_payload:
        reason_codes.append("missing_chapter4_allowed_payload")

    excluded_payload = guard.get("excluded_payload") if isinstance(guard.get("excluded_payload"), Mapping) else {}
    admitted_guard = _admitted_chapter4_guard(profile, protection_packet, guard)
    return reason_codes, admitted_guard, allowed_payload, dict(excluded_payload)


def _chapter4_guard_has_block(protection_packet: Mapping[str, Any]) -> bool:
    for value in protection_packet.values():
        if isinstance(value, Mapping) and str(value.get("action", "")).strip().lower() == "block":
            return True
    hard_blocks = protection_packet.get("hard_block_reason_codes", [])
    return isinstance(hard_blocks, list) and bool(hard_blocks)


def _admitted_chapter4_guard(
    profile: Mapping[str, Any],
    protection_packet: Mapping[str, Any],
    guard: Mapping[str, Any],
) -> dict[str, object]:
    lex_metrics = _nested_mapping(profile, "lex_metrics")
    return {
        "profile_version": profile.get("profile_version"),
        "approval_scope": guard.get("approval_scope"),
        "approved_for_fnp": guard.get("approved_for_fnp"),
        "lex_metrics": {
            "H_lex": lex_metrics.get("H_lex"),
            "G_lex": lex_metrics.get("G_lex"),
            "I_lexicon": lex_metrics.get("I_lexicon"),
            "dL_lex": lex_metrics.get("dL_lex"),
        },
        "protection_actions": {
            key: value.get("action")
            for key, value in protection_packet.items()
            if isinstance(value, Mapping) and "action" in value
        },
    }


def _validate_chapter5_intake_profile(packet: Mapping[str, Any]) -> tuple[list[str], Mapping[str, object] | None]:
    profile = packet.get("chapter5_intake_profile")
    if profile is None:
        return [], None
    if not isinstance(profile, Mapping):
        return ["invalid_chapter5_intake_profile"], None

    reason_codes: list[str] = []
    if _contains_fnp_computation_fields(profile):
        reason_codes.append("synthia_packet_contains_fnp_computation_fields")

    guard_state = _nested_mapping(profile, "guard_state")
    if guard_state.get("approved_for_fnp_intake") is not True:
        reason_codes.append("chapter5_not_approved_for_fnp_intake")

    event_request = _nested_mapping(profile, "E_FNP_neutrino_request")
    if str(event_request.get("allowed_payload_status", "")).strip().lower() != "present":
        reason_codes.append("missing_chapter5_allowed_payload")

    policy = _nested_mapping(profile, "carrier_request_policy")
    family = str(policy.get("requested_family", "")).strip()
    if not family:
        reason_codes.append("missing_carrier_request")
    elif family not in VALID_CHAPTER5_CARRIER_FAMILIES:
        reason_codes.append("invalid_carrier_family")

    scale = _nested_mapping(profile, "scale_context_request")
    if str(scale.get("status", "")).strip().lower() != "present":
        reason_codes.append("missing_scale_context")

    if reason_codes:
        return reason_codes, None
    return [], {
        "profile_version": profile.get("profile_version"),
        "event_request": dict(event_request),
        "carrier_request_policy": dict(policy),
        "scale_context_request": dict(scale),
        "guard_state": dict(guard_state),
        "Adm_FNP_required": bool(profile.get("Adm_FNP_required")),
    }


def _admitted_chapter3_carriers(profile: Mapping[str, Any]) -> dict[str, object]:
    return {
        "profile_version": profile.get("profile_version"),
        "I_flavor": dict(_nested_mapping(profile, "flavor_profile", "I_flavor")),
        "I_mass": dict(_nested_mapping(profile, "mass_profile", "I_mass")),
        "I_phase": dict(_nested_mapping(profile, "phase_profile", "I_phase")),
        "I_interaction": dict(_nested_mapping(profile, "interaction_profile", "I_interaction")),
        "I_secondary": dict(_nested_mapping(profile, "secondary_profile", "I_secondary")),
        "I_detector": dict(_nested_mapping(profile, "detector_profile", "I_detector")),
    }


def _nested_mapping(payload: Mapping[str, Any], *path: str) -> Mapping[str, Any]:
    current: object = payload
    for key in path:
        if not isinstance(current, Mapping):
            return {}
        current = current.get(key)
    return current if isinstance(current, Mapping) else {}


def _basis_vectors_equal(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    if not left or not right:
        return False
    left_values = [_optional_float(value) for value in left.values()]
    right_values = [_optional_float(value) for value in right.values()]
    if len(left_values) != len(right_values):
        return False
    if any(value is None for value in left_values + right_values):
        return False
    return all(abs(float(a) - float(b)) < 1e-12 for a, b in zip(left_values, right_values))


def _contains_key_recursive(value: object, forbidden_keys: set[str]) -> bool:
    if isinstance(value, Mapping):
        return any(str(key) in forbidden_keys or _contains_key_recursive(item, forbidden_keys) for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_key_recursive(item, forbidden_keys) for item in value)
    return False


def _json_text(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, default=str).lower()


def _contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(pattern.lower() in text for pattern in patterns)


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
