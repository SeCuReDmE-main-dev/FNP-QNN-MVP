import contextlib
import io
import json
from pathlib import Path
import unittest

from core.neutrino_admission_gate import neutrino_guardrail_check, validate_synthia_admission
from fnp_qnn_cli.main import main


def _accepted_packet():
    return {
        "LexPacket_neutrino": {
            "schema_version": "synthia.lex_neutrino.v1",
            "event_id": "public-safe-neutrino-001",
            "Adm_lex": True,
            "dL_lex": 0.12,
            "decision": {
                "status": "accepted",
                "next_action": "admit_to_fnp",
                "reason_codes": [],
            },
            "refusal_packet": {
                "blocked": False,
                "reason_codes": [],
                "next_action": "admit_to_fnp",
                "source_layer": "lexical",
            },
            "source_layer": "lexical",
            "boundary": "simulation_not_detection",
        }
    }


def _chapter3_packet():
    return json.loads(Path("tests/fixtures/neutrino_chapter3_valid_admission.json").read_text(encoding="utf-8"))


def _chapter4_packet():
    return json.loads(Path("tests/fixtures/neutrino_chapter4_valid_admission.json").read_text(encoding="utf-8"))


def _chapter5_packet():
    return json.loads(Path("tests/fixtures/neutrino_chapter5_valid_admission.json").read_text(encoding="utf-8"))


def _chapter6_packet():
    return json.loads(Path("tests/fixtures/neutrino_chapter6_valid_admission.json").read_text(encoding="utf-8"))


def _assert_no_key(payload, forbidden_key):
    if isinstance(payload, dict):
        testcase = unittest.TestCase()
        testcase.assertNotIn(forbidden_key, payload)
        for value in payload.values():
            _assert_no_key(value, forbidden_key)
    elif isinstance(payload, list):
        for value in payload:
            _assert_no_key(value, forbidden_key)


class NeutrinoAdmissionGateTests(unittest.TestCase):
    def test_accepted_lex_packet_allows_fnp_compute(self):
        payload = neutrino_guardrail_check(_accepted_packet())

        self.assertTrue(payload["can_compute_fnp"])
        self.assertEqual(payload["decision"]["status"], "accepted")
        self.assertIn("synthia_admission_valid", payload["decision"]["reason_codes"])
        _assert_no_key(payload, "dF")
        _assert_no_key(payload, "D_f")
        _assert_no_key(payload, "i_fractal")

    def test_blocking_synthia_statuses_are_rejected(self):
        for status in ("rejected", "suspended", "corrected"):
            packet = _accepted_packet()
            packet["LexPacket_neutrino"]["Adm_lex"] = False
            packet["LexPacket_neutrino"]["decision"]["status"] = status
            decision = validate_synthia_admission(packet)

            self.assertFalse(decision.can_compute_fnp)
            self.assertIn("synthia_decision_not_admitted", decision.reason_codes)

    def test_missing_packet_is_blocked(self):
        decision = validate_synthia_admission({"event_id": "missing-packet"})

        self.assertFalse(decision.can_compute_fnp)
        self.assertEqual(decision.reason_codes, ("missing_synthia_lex_packet",))

    def test_missing_schema_version_is_blocked(self):
        packet = _accepted_packet()
        packet["LexPacket_neutrino"].pop("schema_version")
        decision = validate_synthia_admission(packet)

        self.assertFalse(decision.can_compute_fnp)
        self.assertIn("invalid_synthia_schema_version", decision.reason_codes)

    def test_collapse_codes_are_blocked(self):
        packet = _accepted_packet()
        packet["LexPacket_neutrino"]["dF"] = 0.12
        packet["LexPacket_neutrino"]["I_lexicon"] = 0.4
        packet["LexPacket_neutrino"]["i_fractal"] = 0.4
        decision = validate_synthia_admission(packet)

        self.assertFalse(decision.can_compute_fnp)
        self.assertIn("synthia_packet_contains_fnp_computation_fields", decision.reason_codes)
        self.assertIn("dL_lex_equals_dF", decision.reason_codes)
        self.assertIn("I_lexicon_equals_i_fractal", decision.reason_codes)

    def test_cli_guardrail_check_returns_contract(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["--json", "neutrino", "guardrail-check", "--input", "tests/fixtures/neutrino_valid_admission.json"])

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["schema_version"], "fnp.neutrino_admission.v1")
        self.assertTrue(payload["can_compute_fnp"])
        _assert_no_key(payload, "dF")

    def test_chapter3_profile_is_admitted_as_carriers_without_computation(self):
        payload = neutrino_guardrail_check(_chapter3_packet())

        self.assertTrue(payload["can_compute_fnp"])
        carriers = payload["admitted_chapter3_carriers"]
        self.assertEqual(carriers["profile_version"], "chapter3.neutrino_public_safe.v1")
        self.assertEqual(carriers["I_flavor"]["created_flavor"], "nu_mu")
        self.assertEqual(carriers["I_interaction"]["channel"], "weak_CC")
        _assert_no_key(payload, "dF")
        _assert_no_key(payload, "D_f")
        _assert_no_key(payload, "i_fractal")

    def test_chapter3_equal_flavor_and_mass_basis_is_blocked(self):
        packet = _chapter3_packet()
        packet["LexPacket_neutrino"]["chapter3_profile"]["mass_profile"]["I_mass"]["mass_basis"] = {
            "nu_1": 0.0,
            "nu_2": 1.0,
            "nu_3": 0.0,
        }

        decision = validate_synthia_admission(packet)

        self.assertFalse(decision.can_compute_fnp)
        self.assertIn("mass_basis_equals_flavor_basis", decision.reason_codes)

    def test_chapter3_direct_detector_projection_is_blocked(self):
        packet = _chapter3_packet()
        detector = packet["LexPacket_neutrino"]["chapter3_profile"]["detector_profile"]["I_detector"]
        detector["detector_projection_status"] = "direct"

        decision = validate_synthia_admission(packet)

        self.assertFalse(decision.can_compute_fnp)
        self.assertIn("visible_neutrino_claim", decision.reason_codes)

    def test_chapter3_secondary_primary_force_collapse_is_blocked(self):
        packet = _chapter3_packet()
        secondary = packet["LexPacket_neutrino"]["chapter3_profile"]["secondary_profile"]["I_secondary"]
        secondary["primary_force"] = "strong_primary"

        decision = validate_synthia_admission(packet)

        self.assertFalse(decision.can_compute_fnp)
        self.assertIn("secondary_response_as_primary_force", decision.reason_codes)

    def test_chapter3_nested_fnp_computation_field_is_blocked(self):
        packet = _chapter3_packet()
        packet["LexPacket_neutrino"]["chapter3_profile"]["phase_profile"]["I_phase"]["dF"] = 0.3

        decision = validate_synthia_admission(packet)

        self.assertFalse(decision.can_compute_fnp)
        self.assertIn("synthia_packet_contains_fnp_computation_fields", decision.reason_codes)

    def test_cli_guardrail_check_accepts_chapter3_fixture(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["--json", "neutrino", "guardrail-check", "--input", "tests/fixtures/neutrino_chapter3_valid_admission.json"])

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["can_compute_fnp"])
        self.assertEqual(payload["admitted_chapter3_carriers"]["I_detector"]["detector_projection_status"], "indirect")

    def test_chapter4_profile_is_admitted_as_guard_without_computation(self):
        payload = neutrino_guardrail_check(_chapter4_packet())

        self.assertTrue(payload["can_compute_fnp"])
        guard = payload["admitted_chapter4_guard"]
        self.assertEqual(guard["profile_version"], "chapter4.lex_neutrino_public_safe.v1")
        self.assertEqual(guard["approval_scope"], "full_lexical_payload")
        self.assertTrue(payload["allowed_payload"])
        _assert_no_key(payload, "dF")
        _assert_no_key(payload, "D_f")
        _assert_no_key(payload, "i_fractal")

    def test_chapter4_partitioned_packet_requires_allowed_payload(self):
        packet = _chapter4_packet()
        lex_packet = packet["LexPacket_neutrino"]
        lex_packet["decision"]["status"] = "accepted_with_partition"
        guard = lex_packet["chapter4_profile"]["protection_profile"]["SynthiaGuard_neutrino"]
        guard["approval_scope"] = "allowed_payload_only"
        guard["excluded_payload"] = {"metaphor_payload": "conceptual_language_only"}

        decision = validate_synthia_admission(packet)

        self.assertTrue(decision.can_compute_fnp)
        self.assertEqual(decision.allowed_payload["event_id"], "chapter4-public-safe-neutrino-001")
        self.assertEqual(decision.excluded_payload_summary["metaphor_payload"], "conceptual_language_only")

    def test_chapter4_partitioned_packet_without_allowed_payload_is_blocked(self):
        packet = _chapter4_packet()
        lex_packet = packet["LexPacket_neutrino"]
        lex_packet["decision"]["status"] = "accepted_with_partition"
        guard = lex_packet["chapter4_profile"]["protection_profile"]["SynthiaGuard_neutrino"]
        guard["allowed_payload"] = {}

        decision = validate_synthia_admission(packet)

        self.assertFalse(decision.can_compute_fnp)
        self.assertIn("missing_chapter4_allowed_payload", decision.reason_codes)

    def test_chapter4_blocked_guard_blocks_fnp(self):
        packet = _chapter4_packet()
        guard_packet = packet["LexPacket_neutrino"]["chapter4_profile"]["protection_profile"]["ProtectionPacket_neutrino"]
        guard_packet["simulation_detection_guard"]["action"] = "block"
        guard_packet["simulation_detection_guard"]["reason_codes"] = ["simulation_trace_as_detection"]

        decision = validate_synthia_admission(packet)

        self.assertFalse(decision.can_compute_fnp)
        self.assertIn("chapter4_guard_blocked", decision.reason_codes)

    def test_chapter4_forbidden_fnp_field_is_blocked(self):
        packet = _chapter4_packet()
        packet["LexPacket_neutrino"]["chapter4_profile"]["lex_metrics"]["dF"] = 0.4

        decision = validate_synthia_admission(packet)

        self.assertFalse(decision.can_compute_fnp)
        self.assertIn("synthia_packet_contains_fnp_computation_fields", decision.reason_codes)

    def test_cli_guardrail_check_accepts_chapter4_fixture(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["--json", "neutrino", "guardrail-check", "--input", "tests/fixtures/neutrino_chapter4_valid_admission.json"])

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["can_compute_fnp"])
        self.assertEqual(payload["admitted_chapter4_guard"]["profile_version"], "chapter4.lex_neutrino_public_safe.v1")

    def test_chapter5_intake_profile_is_admitted_without_carrier_computation(self):
        payload = neutrino_guardrail_check(_chapter5_packet())

        self.assertTrue(payload["can_compute_fnp"])
        intake = payload["admitted_chapter5_intake"]
        self.assertEqual(intake["profile_version"], "chapter5.fnp_intake_public_safe.v1")
        self.assertEqual(intake["carrier_request_policy"]["requested_family"], "phase_carrier")
        _assert_no_key(payload, "D_f")
        _assert_no_key(payload, "D_f_hat")
        _assert_no_key(payload, "dF")
        _assert_no_key(payload, "i_fractal")
        _assert_no_key(payload, "i_fractal_candidate")

    def test_chapter5_intake_without_approval_is_blocked(self):
        packet = _chapter5_packet()
        packet["LexPacket_neutrino"]["chapter5_intake_profile"]["guard_state"]["approved_for_fnp_intake"] = False

        decision = validate_synthia_admission(packet)

        self.assertFalse(decision.can_compute_fnp)
        self.assertIn("chapter5_not_approved_for_fnp_intake", decision.reason_codes)

    def test_chapter5_synthia_carrier_field_is_blocked(self):
        packet = _chapter5_packet()
        packet["LexPacket_neutrino"]["chapter5_intake_profile"]["D_f_hat"] = 0.5

        decision = validate_synthia_admission(packet)

        self.assertFalse(decision.can_compute_fnp)
        self.assertIn("synthia_packet_contains_fnp_computation_fields", decision.reason_codes)

    def test_chapter6_vector_profile_is_admitted_without_computation(self):
        payload = neutrino_guardrail_check(_chapter6_packet())

        self.assertTrue(payload["can_compute_fnp"])
        vector = payload["admitted_chapter6_vector"]["I_neutrino_vec"]
        self.assertEqual(len(vector["carrier_order"]), 10)
        self.assertIn("I_uncertainty", vector["carriers"])
        self.assertTrue(payload["chapter6_guardrail_check"]["ready_for_Synthia"])
        self.assertEqual(payload["chapter6_guardrail_check"]["ready_for_FNP"], "false_before_Synthia")
        _assert_no_key(payload, "D_f")
        _assert_no_key(payload, "D_f_hat")
        _assert_no_key(payload, "dF")
        _assert_no_key(payload, "i_fractal")
        _assert_no_key(payload, "i_fractal_candidate")

    def test_chapter6_missing_carrier_is_blocked(self):
        packet = _chapter6_packet()
        carriers = packet["LexPacket_neutrino"]["chapter6_vector_profile"]["I_neutrino_vec"]["carriers"]
        carriers.pop("I_medium")

        decision = validate_synthia_admission(packet)

        self.assertFalse(decision.can_compute_fnp)
        self.assertIn("missing_i_neutrino_vector_carrier", decision.reason_codes)

    def test_chapter6_missing_uncertainty_is_blocked(self):
        packet = _chapter6_packet()
        carriers = packet["LexPacket_neutrino"]["chapter6_vector_profile"]["I_neutrino_vec"]["carriers"]
        carriers.pop("I_uncertainty")

        decision = validate_synthia_admission(packet)

        self.assertFalse(decision.can_compute_fnp)
        self.assertIn("i_uncertainty_missing", decision.reason_codes)

    def test_chapter6_forbidden_fnp_field_is_blocked(self):
        packet = _chapter6_packet()
        profile = packet["LexPacket_neutrino"]["chapter6_vector_profile"]
        profile["I_neutrino_vec"]["carriers"]["I_phase"]["dF"] = 0.4

        decision = validate_synthia_admission(packet)

        self.assertFalse(decision.can_compute_fnp)
        self.assertIn("synthia_packet_contains_fnp_computation_fields", decision.reason_codes)

    def test_chapter6_ready_for_fnp_before_synthia_is_blocked(self):
        packet = _chapter6_packet()
        guard = packet["LexPacket_neutrino"]["chapter6_vector_profile"]["GuardrailCheck"]
        guard["ready_for_FNP"] = True

        decision = validate_synthia_admission(packet)

        self.assertFalse(decision.can_compute_fnp)
        self.assertIn("ready_for_fnp_before_synthia", decision.reason_codes)


if __name__ == "__main__":
    unittest.main()
