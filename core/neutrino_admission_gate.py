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
    "invalid_chapter6_vector_profile",
    "missing_i_neutrino_vector_carrier",
    "i_neutrino_vec_equals_dL_lex",
    "i_neutrino_vec_equals_dF",
    "i_neutrino_vec_equals_detector_signature",
    "i_uncertainty_missing",
    "uncertainty_collapsed_to_zero",
    "ready_for_fnp_before_synthia",
    "guardrail_check_missing",
    "vector_claim_as_physical_detection",
    "vector_claim_as_physical_proof",
    "synthia_packet_contains_fnp_computation_fields",
    "invalid_chapter7_transition_profile",
    "chapter7_not_ready_after_synthia",
    "chapter7_lexicon_gap_mismatch",
    "invalid_chapter8_run_profile",
    "chapter8_not_admissible",
    "chapter8_missing_permission",
    "chapter8_permission_as_proof",
    "chapter8_admissible_as_detection",
    "chapter8_suspended_as_zero",
    "chapter8_rejected_as_noise",
    "chapter8_unbounded_next_step",
    "chapter8_candidate_as_proof",
    "invalid_chapter9_source_choice_profile",
    "chapter9_missing_source_registry",
    "chapter9_missing_central_experiment",
    "chapter9_not_ready_after_synthia",
    "chapter9_t2k_reproduction_claim",
    "chapter9_cp_measurement_claim",
    "chapter9_experiment_choice_as_detection",
    "chapter9_math_source_as_physical_proof",
    "chapter9_background_missing_as_zero",
    "chapter9_source_stack_as_proof",
    "chapter9_unbounded_experiment_choice",
    "invalid_chapter10_chamber_profile",
    "chapter10_missing_source_registry",
    "chapter10_missing_container_contract",
    "chapter10_missing_simulated_event",
    "chapter10_missing_run_contract",
    "chapter10_not_ready_after_synthia",
    "chapter10_fnp_before_synthia",
    "chapter10_chamber_as_detector",
    "chapter10_container_as_proof",
    "chapter10_event_as_detection",
    "chapter10_t2k_reproduction_claim",
    "chapter10_cp_measurement_claim",
    "chapter10_background_missing_as_zero",
    "chapter10_prepared_tension_as_df",
    "chapter10_unbounded_manipulation",
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
CHAPTER6_REQUIRED_CARRIERS = (
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
CHAPTER9_REQUIRED_SOURCE_IDS = {"SB60-002", "CH9-T2K-OSC-001", "SB60-052"}
CHAPTER9_EXPERIMENT_ID = "chapter11_t2k_like_flavor_antiflavor_phase_projection"
CHAPTER10_REQUIRED_SOURCE_IDS = {"CH10-GEANT4-001", "CH10-SCHEMA-001"}


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
    admitted_chapter6_vector: Mapping[str, object] | None = None
    chapter6_guardrail_check: Mapping[str, object] | None = None
    admitted_chapter7_transition: Mapping[str, object] | None = None
    admitted_chapter8_run: Mapping[str, object] | None = None
    admitted_chapter9_source_choice: Mapping[str, object] | None = None
    admitted_chapter10_chamber: Mapping[str, object] | None = None
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
        if self.admitted_chapter6_vector is not None:
            payload["admitted_chapter6_vector"] = dict(self.admitted_chapter6_vector)
        if self.chapter6_guardrail_check is not None:
            payload["chapter6_guardrail_check"] = dict(self.chapter6_guardrail_check)
        if self.admitted_chapter7_transition is not None:
            payload["admitted_chapter7_transition"] = dict(self.admitted_chapter7_transition)
        if self.admitted_chapter8_run is not None:
            payload["admitted_chapter8_run"] = dict(self.admitted_chapter8_run)
        if self.admitted_chapter9_source_choice is not None:
            payload["admitted_chapter9_source_choice"] = dict(self.admitted_chapter9_source_choice)
        if self.admitted_chapter10_chamber is not None:
            payload["admitted_chapter10_chamber"] = dict(self.admitted_chapter10_chamber)
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

    chapter6_reasons, admitted_chapter6_vector, chapter6_guardrail_check = _validate_chapter6_vector_profile(packet)
    for code in chapter6_reasons:
        if code not in reason_codes:
            reason_codes.append(code)

    chapter7_reasons, admitted_chapter7_transition = _validate_chapter7_transition_profile(packet, d_l_lex)
    for code in chapter7_reasons:
        if code not in reason_codes:
            reason_codes.append(code)

    chapter8_reasons, admitted_chapter8_run = _validate_chapter8_run_profile(packet)
    for code in chapter8_reasons:
        if code not in reason_codes:
            reason_codes.append(code)

    chapter9_reasons, admitted_chapter9_source_choice = _validate_chapter9_source_choice_profile(packet)
    for code in chapter9_reasons:
        if code not in reason_codes:
            reason_codes.append(code)

    chapter10_reasons, admitted_chapter10_chamber = _validate_chapter10_chamber_profile(packet)
    for code in chapter10_reasons:
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
        admitted_chapter6_vector=admitted_chapter6_vector,
        chapter6_guardrail_check=chapter6_guardrail_check,
        admitted_chapter7_transition=admitted_chapter7_transition,
        admitted_chapter8_run=admitted_chapter8_run,
        admitted_chapter9_source_choice=admitted_chapter9_source_choice,
        admitted_chapter10_chamber=admitted_chapter10_chamber,
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
        "admitted_chapter6_vector": decision.admitted_chapter6_vector,
        "chapter6_guardrail_check": decision.chapter6_guardrail_check,
        "admitted_chapter7_transition": decision.admitted_chapter7_transition,
        "admitted_chapter8_run": decision.admitted_chapter8_run,
        "admitted_chapter9_source_choice": decision.admitted_chapter9_source_choice,
        "admitted_chapter10_chamber": decision.admitted_chapter10_chamber,
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


def _validate_chapter6_vector_profile(
    packet: Mapping[str, Any],
) -> tuple[list[str], Mapping[str, object] | None, Mapping[str, object] | None]:
    profile = packet.get("chapter6_vector_profile")
    if profile is None:
        return [], None, None
    if not isinstance(profile, Mapping):
        return ["invalid_chapter6_vector_profile"], None, None

    reason_codes: list[str] = []
    if profile.get("profile_version") != "chapter6.i_neutrino_vector_public_safe.v1":
        reason_codes.append("invalid_chapter6_vector_profile")
    if _contains_fnp_computation_fields(profile):
        reason_codes.append("synthia_packet_contains_fnp_computation_fields")

    vector = _nested_mapping(profile, "I_neutrino_vec")
    carriers = _nested_mapping(vector, "carriers")
    carrier_order = vector.get("carrier_order")
    if not vector or not carriers or not isinstance(carrier_order, list):
        reason_codes.append("invalid_chapter6_vector_profile")
    else:
        missing = [name for name in CHAPTER6_REQUIRED_CARRIERS if name not in carriers or not carriers.get(name)]
        if missing:
            reason_codes.append("missing_i_neutrino_vector_carrier")
        if "I_uncertainty" in missing or not isinstance(carriers.get("I_uncertainty"), Mapping):
            reason_codes.append("i_uncertainty_missing")
        if list(carrier_order) != list(CHAPTER6_REQUIRED_CARRIERS):
            reason_codes.append("invalid_chapter6_vector_profile")

    guardrail = _nested_mapping(profile, "GuardrailCheck")
    if not guardrail:
        reason_codes.append("guardrail_check_missing")
    else:
        if guardrail.get("ready_for_Synthia") is not True:
            reason_codes.append("guardrail_check_missing")
        if guardrail.get("ready_for_FNP") is True or str(guardrail.get("ready_for_FNP", "")).lower() == "true":
            reason_codes.append("ready_for_fnp_before_synthia")
        if guardrail.get("strong_primary_claim") is True:
            reason_codes.append("strong_primary_interaction_claim")
        if guardrail.get("no_real_detection_claim") is False:
            reason_codes.append("real_detection_claim")
        if guardrail.get("detector_trace_not_object") is False:
            reason_codes.append("trace_as_neutrino_total")

    text = _json_text(profile)
    if _contains_any(text, ("i_neutrino_vec = dl_lex", "i_neutrino_vec equals dl_lex")):
        reason_codes.append("i_neutrino_vec_equals_dL_lex")
    if _contains_any(text, ("i_neutrino_vec = df", "i_neutrino_vec equals df")):
        reason_codes.append("i_neutrino_vec_equals_dF")
    if _contains_any(text, ("i_neutrino_vec = detector_signature", "i_neutrino_vec equals detector_signature")):
        reason_codes.append("i_neutrino_vec_equals_detector_signature")

    if reason_codes:
        return reason_codes, None, dict(guardrail) if guardrail else None
    return [], {
        "profile_version": profile.get("profile_version"),
        "vector_definition": profile.get("vector_definition"),
        "I_neutrino_vec": dict(vector),
        "readiness": dict(_nested_mapping(profile, "readiness")),
        "projection_policy": dict(_nested_mapping(profile, "projection_policy")),
        "vector_invariants": list(profile.get("vector_invariants", []))
        if isinstance(profile.get("vector_invariants"), list)
        else [],
    }, dict(guardrail)


def _validate_chapter7_transition_profile(
    packet: Mapping[str, Any],
    packet_d_l_lex: float | None,
) -> tuple[list[str], Mapping[str, object] | None]:
    profile = packet.get("chapter7_transition_profile")
    if profile is None:
        return [], None
    if not isinstance(profile, Mapping):
        return ["invalid_chapter7_transition_profile"], None

    reason_codes: list[str] = []
    if profile.get("profile_version") != "chapter7.synthia_transition_public_safe.v1":
        reason_codes.append("invalid_chapter7_transition_profile")
    if _contains_fnp_computation_fields(profile):
        reason_codes.append("synthia_packet_contains_fnp_computation_fields")

    passage = _nested_mapping(profile, "passage_test")
    reading = _nested_mapping(profile, "synthia_reading")
    gate = _nested_mapping(profile, "chapter7_gate")
    if not passage or not reading or not gate:
        reason_codes.append("invalid_chapter7_transition_profile")
    if passage.get("ready_for_FNP") != "false_before_Synthia":
        reason_codes.append("invalid_chapter7_transition_profile")
    if gate.get("ready_for_FNP") != "true_after_Synthia" or gate.get("approved_for_fnp") is not True:
        reason_codes.append("chapter7_not_ready_after_synthia")

    reading_d_l_lex = _optional_float(reading.get("dL_lex"))
    if packet_d_l_lex is None or reading_d_l_lex is None or abs(packet_d_l_lex - reading_d_l_lex) > 1e-8:
        reason_codes.append("chapter7_lexicon_gap_mismatch")

    if reason_codes:
        return reason_codes, None
    return [], {
        "profile_version": profile.get("profile_version"),
        "I_neutrino_definition": profile.get("I_neutrino_definition"),
        "passage_test": dict(passage),
        "synthia_reading": dict(reading),
        "chapter7_gate": dict(gate),
        "transition_invariants": list(profile.get("transition_invariants", []))
        if isinstance(profile.get("transition_invariants"), list)
        else [],
    }


def _validate_chapter8_run_profile(packet: Mapping[str, Any]) -> tuple[list[str], Mapping[str, object] | None]:
    profile = packet.get("chapter8_run_profile")
    if profile is None:
        return [], None
    if not isinstance(profile, Mapping):
        return ["invalid_chapter8_run_profile"], None

    reason_codes: list[str] = []
    if profile.get("profile_version") != "chapter8.first_run_public_safe.v1":
        reason_codes.append("invalid_chapter8_run_profile")
    if _contains_fnp_computation_fields(profile):
        reason_codes.append("synthia_packet_contains_fnp_computation_fields")

    run_input = _nested_mapping(profile, "run_input")
    synthia_gate = _nested_mapping(profile, "synthia_gate")
    run_decision = _nested_mapping(profile, "run_decision")
    run_permission = _nested_mapping(profile, "run_permission")
    if not run_input or not synthia_gate or not run_decision or not run_permission:
        reason_codes.append("invalid_chapter8_run_profile")

    if run_input.get("ready_for_FNP") != "false_before_Synthia":
        reason_codes.append("invalid_chapter8_run_profile")
    if synthia_gate.get("ready_for_FNP") != "true_after_Synthia" or synthia_gate.get("approved_for_fnp") is not True:
        reason_codes.append("chapter8_not_admissible")

    run_status = str(run_decision.get("run_status", "")).strip()
    if run_status not in {"admissible_under_guardrails", "suspended", "rejected"}:
        reason_codes.append("invalid_chapter8_run_profile")
    if run_status != "admissible_under_guardrails":
        reason_codes.append("chapter8_not_admissible")

    if run_permission.get("permission_to_continue") is not True:
        reason_codes.append("chapter8_missing_permission")
    if run_permission.get("allowed_next_step") != "FNP_QNN_readout":
        reason_codes.append("chapter8_unbounded_next_step")

    forbidden = run_permission.get("forbidden_upgrades")
    forbidden_set = set(forbidden) if isinstance(forbidden, list) else set()
    required_forbidden = {
        "permission_to_continue_as_proof",
        "admissible_as_detection",
        "simulation_as_real_detection",
        "candidate_as_proof",
        "FNP_before_Synthia",
    }
    if not required_forbidden <= forbidden_set:
        reason_codes.append("invalid_chapter8_run_profile")

    if reason_codes:
        return reason_codes, None
    return [], {
        "profile_version": profile.get("profile_version"),
        "run_input": dict(run_input),
        "synthia_gate": dict(synthia_gate),
        "run_decision": dict(run_decision),
        "run_permission": dict(run_permission),
        "invariants": list(profile.get("invariants", [])) if isinstance(profile.get("invariants"), list) else [],
    }


def _validate_chapter9_source_choice_profile(packet: Mapping[str, Any]) -> tuple[list[str], Mapping[str, object] | None]:
    profile = packet.get("chapter9_source_choice_profile")
    if profile is None:
        return [], None
    if not isinstance(profile, Mapping):
        return ["invalid_chapter9_source_choice_profile"], None

    reason_codes: list[str] = []
    if profile.get("profile_version") != "chapter9.source_choice_public_safe.v1":
        reason_codes.append("invalid_chapter9_source_choice_profile")
    if _contains_fnp_computation_fields(profile):
        reason_codes.append("synthia_packet_contains_fnp_computation_fields")

    source_visibility = _nested_mapping(profile, "source_visibility")
    central_experiment = _nested_mapping(profile, "central_experiment")
    paths = _nested_mapping(profile, "paths")
    chapter8_dependency = _nested_mapping(profile, "chapter8_dependency")
    synthia_gate = _nested_mapping(profile, "synthia_gate")
    if not source_visibility or not central_experiment or not paths or not synthia_gate:
        reason_codes.append("invalid_chapter9_source_choice_profile")

    provided_sources = source_visibility.get("provided_source_ids")
    provided_source_ids = {str(item).strip() for item in provided_sources} if isinstance(provided_sources, list) else set()
    if source_visibility.get("registry_status") != "present" or not CHAPTER9_REQUIRED_SOURCE_IDS <= provided_source_ids:
        reason_codes.append("chapter9_missing_source_registry")

    experiment_id = str(central_experiment.get("experiment_id", "")).strip()
    if not experiment_id:
        reason_codes.append("chapter9_missing_central_experiment")
    elif experiment_id != CHAPTER9_EXPERIMENT_ID:
        reason_codes.append("chapter9_unbounded_experiment_choice")

    if str(central_experiment.get("status", "")).strip() != "selected_for_simulation":
        reason_codes.append("chapter9_missing_central_experiment")
    if str(central_experiment.get("reproduction_status", "")).strip() != "not_T2K_reproduction":
        reason_codes.append("chapter9_t2k_reproduction_claim")
    if str(central_experiment.get("detection_status", "")).strip() != "no_real_detection_claim":
        reason_codes.append("chapter9_experiment_choice_as_detection")
    if central_experiment.get("ready_for_container") is not True:
        reason_codes.append("chapter9_missing_central_experiment")
    if central_experiment.get("ready_for_physical_claim") is True:
        reason_codes.append("chapter9_experiment_choice_as_detection")

    path_a = _nested_mapping(paths, "Path_A")
    path_b = _nested_mapping(paths, "Path_B")
    if (
        path_a.get("initial_flavor") != "nu_mu"
        or path_b.get("initial_flavor") != "anti_nu_mu"
        or path_a.get("status") != "simulation_path"
        or path_b.get("status") != "simulation_path"
    ):
        reason_codes.append("invalid_chapter9_source_choice_profile")

    if (
        synthia_gate.get("approved_for_container_validation") is not True
        or synthia_gate.get("ready_for_FNP") != "true_after_Synthia_for_container_validation"
    ):
        reason_codes.append("chapter9_not_ready_after_synthia")
    if chapter8_dependency and chapter8_dependency.get("can_continue_to_chapter9") is not True:
        reason_codes.append("chapter9_not_ready_after_synthia")

    forbidden = profile.get("forbidden_upgrades")
    forbidden_set = set(forbidden) if isinstance(forbidden, list) else set()
    required_forbidden = {
        "T2K_like_as_T2K_reproduction",
        "CP_asymmetry_toy_as_CP_measurement",
        "central_experiment_as_real_detection",
        "source_stack_as_proof",
        "background_missing_as_zero",
        "FNP_before_Synthia",
    }
    if not required_forbidden <= forbidden_set:
        reason_codes.append("invalid_chapter9_source_choice_profile")

    text = _json_text(profile)
    if _contains_any(text, ("t2k reproduced", "t2k reproduction claim", "t2k_like = t2k")):
        reason_codes.append("chapter9_t2k_reproduction_claim")
    if _contains_any(text, ("cp measurement claim", "cp violation measured", "measures cp violation")):
        reason_codes.append("chapter9_cp_measurement_claim")
    if _contains_any(text, ("experiment choice is detection", "selected experiment is real detection")):
        reason_codes.append("chapter9_experiment_choice_as_detection")
    if _contains_any(text, ("mathematical source proves physical", "math source as physical proof")):
        reason_codes.append("chapter9_math_source_as_physical_proof")
    if _contains_any(text, ("background missing equals zero", "background_model_missing = background_zero")):
        reason_codes.append("chapter9_background_missing_as_zero")
    if _contains_any(text, ("source stack proves", "source_physical + source_mathematical = proof")):
        reason_codes.append("chapter9_source_stack_as_proof")

    if reason_codes:
        return reason_codes, None
    return [], {
        "profile_version": profile.get("profile_version"),
        "chapter9_status": profile.get("chapter9_status"),
        "source_visibility": dict(source_visibility),
        "source_families": dict(_nested_mapping(profile, "source_families")),
        "central_experiment": dict(central_experiment),
        "paths": dict(paths),
        "chapter8_dependency": dict(chapter8_dependency),
        "synthia_gate": dict(synthia_gate),
        "forbidden_upgrades": list(forbidden_set),
        "boundary": dict(_nested_mapping(profile, "boundary")),
    }


def _validate_chapter10_chamber_profile(packet: Mapping[str, Any]) -> tuple[list[str], Mapping[str, object] | None]:
    profile = packet.get("chapter10_chamber_profile")
    if profile is None:
        return [], None
    if not isinstance(profile, Mapping):
        return ["invalid_chapter10_chamber_profile"], None

    reason_codes: list[str] = []
    if profile.get("profile_version") != "chapter10.chamber_container_public_safe.v1":
        reason_codes.append("invalid_chapter10_chamber_profile")
    if _contains_fnp_computation_fields(profile):
        reason_codes.append("synthia_packet_contains_fnp_computation_fields")

    source_visibility = _nested_mapping(profile, "source_visibility")
    chamber = _nested_mapping(profile, "Chamber_10")
    container = _nested_mapping(profile, "EventContainer_10")
    event = _nested_mapping(profile, "SimulatedNeutrinoEvent_10")
    run_contract = _nested_mapping(profile, "RunContract_10")
    run_prepared = _nested_mapping(profile, "RunPrepared_10")
    synthia_gate = _nested_mapping(profile, "SynthiaGate_10")
    chapter9_dependency = _nested_mapping(profile, "chapter9_dependency")

    if not source_visibility or not chamber or not container or not event or not run_contract or not run_prepared:
        reason_codes.append("invalid_chapter10_chamber_profile")

    provided_sources = source_visibility.get("provided_source_ids")
    provided_source_ids = {str(item).strip() for item in provided_sources} if isinstance(provided_sources, list) else set()
    if source_visibility.get("registry_status") != "present" or not CHAPTER10_REQUIRED_SOURCE_IDS <= provided_source_ids:
        reason_codes.append("chapter10_missing_source_registry")

    if chamber.get("not_detector") is not True:
        reason_codes.append("chapter10_chamber_as_detector")

    if container.get("required_fields_present") is not True:
        reason_codes.append("chapter10_missing_container_contract")
    if str(container.get("container_boundary", "")).strip() != "container_valid != physical_proof":
        reason_codes.append("chapter10_container_as_proof")

    if str(event.get("event_status", "")).strip() != "educational_simulation":
        reason_codes.append("chapter10_missing_simulated_event")
    if str(event.get("detection_status", "")).strip() != "no_real_detection_claim":
        reason_codes.append("chapter10_event_as_detection")
    if str(event.get("reproduction_status", "")).strip() != "not_T2K_reproduction":
        reason_codes.append("chapter10_t2k_reproduction_claim")
    if str(event.get("measurement_status", "")).strip() != "no_CP_measurement_claim":
        reason_codes.append("chapter10_cp_measurement_claim")

    if str(run_contract.get("run_contract_status", "")).strip() != "declared":
        reason_codes.append("chapter10_missing_run_contract")
    if str(run_contract.get("contract_boundary", "")).strip() != "prepared_tension_slot != dF":
        reason_codes.append("chapter10_prepared_tension_as_df")

    if run_prepared.get("chapter11_execution_ready") is not True:
        reason_codes.append("chapter10_not_ready_after_synthia")
    if run_prepared.get("physical_claim_allowed") is not False:
        reason_codes.append("chapter10_unbounded_manipulation")
    if run_prepared.get("FNP_after_Synthia_only") is not True:
        reason_codes.append("chapter10_fnp_before_synthia")

    if (
        synthia_gate.get("approved_for_container_validation") is not True
        or synthia_gate.get("ready_for_FNP") != "true_after_Synthia_for_run_contract_validation"
    ):
        reason_codes.append("chapter10_not_ready_after_synthia")
    if chapter9_dependency and chapter9_dependency.get("ready_for_container") is not True:
        reason_codes.append("chapter10_not_ready_after_synthia")

    forbidden = profile.get("forbidden_upgrades")
    forbidden_set = set(forbidden) if isinstance(forbidden, list) else set()
    required_forbidden = {
        "chamber_as_detector",
        "container_valid_as_physical_proof",
        "simulated_event_as_detection",
        "T2K_like_as_T2K_reproduction",
        "path_comparison_as_CP_measurement",
        "background_missing_as_zero",
        "prepared_tension_slot_as_dF",
        "FNP_before_Synthia",
    }
    if not required_forbidden <= forbidden_set:
        reason_codes.append("invalid_chapter10_chamber_profile")

    text = _json_text(profile)
    if _contains_any(text, ("chamber = detector", "chamber is detector", "chambre = detecteur")):
        reason_codes.append("chapter10_chamber_as_detector")
    if _contains_any(text, ("container valid is proof", "container_valid = physical_proof")):
        reason_codes.append("chapter10_container_as_proof")
    if _contains_any(text, ("simulated event is detection", "simulatedneutrinoevent_10 = real_neutrino_event")):
        reason_codes.append("chapter10_event_as_detection")
    if _contains_any(text, ("t2k reproduced", "t2k reproduction claim", "t2k_like = t2k")):
        reason_codes.append("chapter10_t2k_reproduction_claim")
    if _contains_any(text, ("cp measurement claim", "path_comparison = cp_measurement", "cp violation measured")):
        reason_codes.append("chapter10_cp_measurement_claim")
    if _contains_any(text, ("background missing equals zero", "background_missing = background_zero")):
        reason_codes.append("chapter10_background_missing_as_zero")
    if _contains_any(text, ("prepared_tension_slot = df", "prepared tension is df")):
        reason_codes.append("chapter10_prepared_tension_as_df")

    if reason_codes:
        return reason_codes, None
    return [], {
        "profile_version": profile.get("profile_version"),
        "chapter10_status": profile.get("chapter10_status"),
        "source_visibility": dict(source_visibility),
        "Chamber_10": dict(chamber),
        "EventContainer_10": dict(container),
        "SimulatedNeutrinoEvent_10": dict(event),
        "RunContract_10": dict(run_contract),
        "chapter9_dependency": dict(chapter9_dependency),
        "SynthiaGate_10": dict(synthia_gate),
        "RunPrepared_10": dict(run_prepared),
        "forbidden_upgrades": list(forbidden_set),
        "boundary": dict(_nested_mapping(profile, "boundary")),
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
