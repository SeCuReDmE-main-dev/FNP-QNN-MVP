import contextlib
import copy
import io
import json
from pathlib import Path
import unittest

from core.neutrino_admission_gate import neutrino_guardrail_check
from core.neutrino_chapter7_readout import neutrino_chapter7_readout
from fnp_qnn_cli.main import main


def _chapter7_packet():
    return json.loads(Path("tests/fixtures/neutrino_chapter7_valid_admission.json").read_text(encoding="utf-8"))


class NeutrinoChapter7ReadoutTests(unittest.TestCase):
    def test_admission_preserves_chapter7_transition_without_computation(self):
        payload = neutrino_guardrail_check(_chapter7_packet())

        self.assertTrue(payload["can_compute_fnp"])
        transition = payload["admitted_chapter7_transition"]
        self.assertEqual(transition["profile_version"], "chapter7.synthia_transition_public_safe.v1")
        self.assertEqual(transition["passage_test"]["ready_for_FNP"], "false_before_Synthia")
        self.assertEqual(transition["chapter7_gate"]["ready_for_FNP"], "true_after_Synthia")
        self.assertEqual(transition["synthia_reading"]["dL_lex"], 0.31927681)

    def test_valid_packet_builds_chapter7_readout(self):
        payload = neutrino_chapter7_readout(_chapter7_packet())

        self.assertTrue(payload["can_compute_chapter7_readout"])
        self.assertEqual(payload["schema_version"], "fnp.neutrino_chapter7_readout.v1")
        self.assertEqual(payload["ready_for_FNP"], "true_after_Synthia")
        self.assertAlmostEqual(payload["D_f"], 1.7669502631272902)
        self.assertAlmostEqual(payload["D_f_hat"], 0.7669502631272902)
        self.assertAlmostEqual(payload["dF"], 0.7669502631272902)
        self.assertAlmostEqual(payload["i_fractal_candidate"], 0.7669502631272902)
        self.assertAlmostEqual(payload["friction_tensions"]["composite_friction_tension"], 0.48290796)
        self.assertEqual(payload["chapter8_entry_status"], "ready_for_first_run_interpretation")
        self.assertIn("candidate is not proof", payload["claim_boundary"])

    def test_lexicon_gap_must_match_admitted_d_l_lex(self):
        packet = _chapter7_packet()
        packet["chapter7_readout_request"]["friction_tensions"]["lexicon_gap_tension"] = 0.12

        payload = neutrino_chapter7_readout(packet)

        self.assertFalse(payload["can_compute_chapter7_readout"])
        self.assertIn("chapter7_lexicon_gap_mismatch", payload["decision"]["reason_codes"])

    def test_non_admitted_synthia_packet_blocks_before_readout(self):
        packet = _chapter7_packet()
        packet["LexPacket_neutrino"]["Adm_lex"] = False
        packet["LexPacket_neutrino"]["decision"]["status"] = "rejected"

        payload = neutrino_chapter7_readout(packet)

        self.assertFalse(payload["can_compute_chapter7_readout"])
        self.assertIn("synthia_decision_not_admitted", payload["decision"]["reason_codes"])

    def test_missing_chapter7_transition_profile_blocks_readout(self):
        packet = _chapter7_packet()
        packet["LexPacket_neutrino"].pop("chapter7_transition_profile")

        payload = neutrino_chapter7_readout(packet)

        self.assertFalse(payload["can_compute_chapter7_readout"])
        self.assertIn("missing_chapter7_transition_profile", payload["decision"]["reason_codes"])

    def test_candidate_as_proof_or_real_detection_claim_blocks_readout(self):
        for key, value, reason in (
            ("claim", "candidate_as_proof", "candidate_confused_with_proof"),
            ("claim", "real_detection", "real_detection_claim"),
        ):
            packet = copy.deepcopy(_chapter7_packet())
            packet["chapter7_readout_request"][key] = value

            payload = neutrino_chapter7_readout(packet)

            self.assertFalse(payload["can_compute_chapter7_readout"])
            self.assertIn(reason, payload["decision"]["reason_codes"])

    def test_invalid_normalization_bounds_block_readout(self):
        packet = _chapter7_packet()
        packet["chapter7_readout_request"]["D_min"] = 2.0
        packet["chapter7_readout_request"]["D_max"] = 2.0

        payload = neutrino_chapter7_readout(packet)

        self.assertFalse(payload["can_compute_chapter7_readout"])
        self.assertIn("normalization_bounds_invalid", payload["decision"]["reason_codes"])

    def test_cli_chapter7_readout_returns_contract(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "--json",
                    "neutrino",
                    "chapter7-readout",
                    "--input",
                    "tests/fixtures/neutrino_chapter7_valid_admission.json",
                ]
            )

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["can_compute_chapter7_readout"])
        self.assertAlmostEqual(payload["dF"], 0.7669502631272902)
        self.assertEqual(payload["chapter8_entry_status"], "ready_for_first_run_interpretation")


if __name__ == "__main__":
    unittest.main()
