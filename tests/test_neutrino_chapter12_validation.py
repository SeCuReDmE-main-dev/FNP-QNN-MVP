import copy
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import unittest

from core.neutrino_admission_gate import neutrino_guardrail_check
from core.neutrino_chapter12_validation import neutrino_chapter12_validation
from fnp_qnn_cli.main import main


def _packet():
    return json.loads(Path("tests/fixtures/neutrino_chapter12_valid_admission.json").read_text(encoding="utf-8"))


class NeutrinoChapter12ValidationTests(unittest.TestCase):
    def test_admission_preserves_chapter12_contract(self):
        payload = neutrino_guardrail_check(_packet())

        self.assertTrue(payload["can_compute_fnp"])
        self.assertEqual(
            payload["admitted_chapter12_validation"]["chapter12_status"],
            "ready_for_fnp_validation",
        )

    def test_valid_packet_proves_internal_repeatability(self):
        payload = neutrino_chapter12_validation(_packet())

        self.assertEqual(payload["schema_version"], "fnp.neutrino_chapter12_validation.v1")
        self.assertEqual(payload["proof_state"], "P2_internal_repeatability")
        self.assertEqual(payload["ten_carrier_report"]["carrier_count"], 10)
        self.assertAlmostEqual(payload["ten_carrier_report"]["composite_tension"], 0.39)
        self.assertAlmostEqual(payload["D_f"], 1.39)
        self.assertAlmostEqual(payload["D_f_hat"], 0.39)
        self.assertAlmostEqual(payload["dF"], 0.39)
        self.assertAlmostEqual(payload["i_fractal_candidate"], 0.39)
        self.assertEqual(payload["stability_report"]["deterministic"]["run_count"], 100)
        self.assertEqual(payload["stability_report"]["stochastic"]["run_count"], 100)
        self.assertEqual(payload["stability_report"]["deterministic"]["delta_max"], 0.0)
        self.assertEqual(payload["stability_report"]["deterministic"]["rmse"], 0.0)
        self.assertTrue(payload["stability_report"]["same_seed_exact_replay"])
        self.assertTrue(payload["stability_report"]["stochastic_values_finite"])
        self.assertTrue(payload["capability_evidence"]["handles_ten_carrier_vector"])
        self.assertTrue(payload["capability_evidence"]["computes_weighted_ten_carrier_tension"])
        self.assertFalse(payload["capability_evidence"]["physical_model_validated"])
        self.assertEqual(payload["chapter12_6_entry_status"], "ready_for_variable_separation")

    def test_missing_chapter11_or_chapter12_profile_blocks(self):
        for profile, code in (
            ("chapter11_passage_profile", "missing_chapter11_passage_profile"),
            ("chapter12_validation_profile", "missing_chapter12_validation_profile"),
        ):
            with self.subTest(profile=profile):
                packet = _packet()
                packet["LexPacket_neutrino"].pop(profile)
                payload = neutrino_chapter12_validation(packet)
                self.assertIn(code, payload["decision"]["reason_codes"])

    def test_context_only_medium_suspends_without_numeric_shortcut(self):
        packet = _packet()
        packet["chapter12_validation_request"]["medium_request"] = {"level": "context_only"}

        payload = neutrino_chapter12_validation(packet)

        self.assertEqual(payload["decision"]["status"], "suspended")
        self.assertEqual(payload["proof_state"], "suspended")
        self.assertNotIn("dF", payload)
        self.assertIn("matter_context_without_model", payload["decision"]["reason_codes"])

    def test_claim_upgrades_are_blocked(self):
        for field, code in (
            ("physical_model_validated", "chapter12_physical_validation_claim"),
            ("repetition_is_experimental_evidence", "chapter12_repetition_as_experimental_evidence"),
            ("real_detection_claim", "chapter12_result_claim_as_detection"),
            ("candidate_as_proof", "chapter12_candidate_as_proof"),
            ("trace_is_neutrino", "chapter12_trace_as_neutrino"),
            ("secondary_as_primary_interaction", "chapter12_secondary_as_primary_interaction"),
            ("msw_measurement_claim", "chapter12_msw_as_measurement"),
            ("hidden_randomness", "chapter12_hidden_randomness"),
        ):
            with self.subTest(field=field):
                packet = _packet()
                packet["chapter12_validation_request"][field] = True
                payload = neutrino_chapter12_validation(packet)
                self.assertIn(code, payload["decision"]["reason_codes"])

    def test_missing_carrier_invalid_bounds_and_detector_errors_block(self):
        cases = []
        missing_carrier = _packet()
        missing_carrier["chapter12_validation_request"]["carriers"].pop()
        cases.append((missing_carrier, "missing_or_unknown_carrier"))
        invalid_bounds = _packet()
        invalid_bounds["chapter12_validation_request"]["D_max"] = 1.0
        cases.append((invalid_bounds, "normalization_bounds_invalid"))
        missing_background = _packet()
        missing_background["chapter12_validation_request"]["detector_request"].pop("background_status")
        cases.append((missing_background, "missing_detector_background"))

        for packet, code in cases:
            with self.subTest(code=code):
                payload = neutrino_chapter12_validation(copy.deepcopy(packet))
                self.assertIn(code, payload["decision"]["reason_codes"])

    def test_cli_returns_same_validation_contract(self):
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(
                [
                    "--json",
                    "neutrino",
                    "chapter12-validate",
                    "--input",
                    "tests/fixtures/neutrino_chapter12_valid_admission.json",
                ]
            )

        self.assertEqual(exit_code, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["proof_state"], "P2_internal_repeatability")
        self.assertEqual(payload["chapter12_6_entry_status"], "ready_for_variable_separation")


if __name__ == "__main__":
    unittest.main()
