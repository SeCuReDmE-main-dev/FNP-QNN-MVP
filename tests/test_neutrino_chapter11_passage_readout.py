import copy
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import unittest

from core.neutrino_admission_gate import neutrino_guardrail_check
from core.neutrino_chapter11_passage_readout import neutrino_chapter11_passage_readout
from fnp_qnn_cli.main import main


def _packet():
    return json.loads(Path("tests/fixtures/neutrino_chapter11_valid_admission.json").read_text(encoding="utf-8"))


class NeutrinoChapter11PassageReadoutTests(unittest.TestCase):
    def test_admission_preserves_chapter11_passage(self):
        payload = neutrino_guardrail_check(_packet())

        self.assertTrue(payload["can_compute_fnp"])
        self.assertEqual(payload["admitted_chapter11_passage"]["chapter11_status"], "ready_for_fnp_passage")

    def test_valid_packet_builds_expected_conditional_readout(self):
        payload = neutrino_chapter11_passage_readout(_packet())

        self.assertEqual(payload["schema_version"], "fnp.neutrino_chapter11_passage.v1")
        self.assertEqual(payload["FNPReadout_11"]["status"], "conditional_readout_constructed")
        self.assertAlmostEqual(payload["D_f_11"], 1.7669502631272902)
        self.assertAlmostEqual(payload["D_f_hat_11"], 0.7669502631272902)
        self.assertAlmostEqual(payload["dF_11"], 0.7669502631272902)
        self.assertAlmostEqual(payload["i_fractal_candidate_11"], 0.7669502631272902)
        self.assertEqual(payload["PathComparison_11"], "chamber_comparison")
        self.assertEqual(payload["chapter12_entry_status"], "ready_for_variation_tests")
        self.assertFalse(payload["physical_model_validated"])

    def test_missing_synthia_admission_or_profile_blocks(self):
        self.assertEqual(
            neutrino_chapter11_passage_readout({})["decision"]["status"],
            "blocked",
        )
        packet = _packet()
        packet["LexPacket_neutrino"].pop("chapter11_passage_profile")
        payload = neutrino_chapter11_passage_readout(packet)
        self.assertIn("missing_chapter11_passage_profile", payload["decision"]["reason_codes"])

    def test_path_container_or_route_mismatch_blocks_before_readout(self):
        for field, value, code in (
            ("container_id", "other", "chapter11_path_container_mismatch"),
            ("admission_route", "direct_to_fnp", "chapter11_path_admission_route_mismatch"),
        ):
            with self.subTest(field=field):
                packet = _packet()
                packet["LexPacket_neutrino"]["chapter11_passage_profile"]["Path_B_event"][field] = value
                payload = neutrino_chapter11_passage_readout(packet)
                self.assertIn(code, payload["decision"]["reason_codes"])

    def test_claim_upgrades_block(self):
        for field, code in (
            ("t2k_reproduction_claim", "chapter11_t2k_reproduction_claim"),
            ("cp_measurement_claim", "chapter11_cp_measurement_claim"),
            ("real_detection_claim", "chapter11_result_claim_as_detection"),
            ("candidate_as_proof", "chapter11_candidate_as_proof"),
        ):
            with self.subTest(field=field):
                packet = _packet()
                packet["chapter11_readout_request"][field] = True
                payload = neutrino_chapter11_passage_readout(packet)
                self.assertIn(code, payload["decision"]["reason_codes"])

    def test_background_bounds_and_caller_output_are_rejected(self):
        cases = []
        missing_background = _packet()
        missing_background["chapter11_readout_request"]["background_model_status"] = "missing"
        cases.append((missing_background, "chapter11_background_missing_as_zero"))
        invalid_bounds = _packet()
        invalid_bounds["chapter11_readout_request"]["D_max_11"] = 1.0
        cases.append((invalid_bounds, "normalization_bounds_invalid"))
        supplied_output = _packet()
        supplied_output["chapter11_readout_request"]["D_f_11"] = 1.5
        cases.append((supplied_output, "chapter11_caller_supplied_fnp_output"))

        for packet, code in cases:
            with self.subTest(code=code):
                payload = neutrino_chapter11_passage_readout(copy.deepcopy(packet))
                self.assertIn(code, payload["decision"]["reason_codes"])

    def test_cli_returns_same_contract(self):
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(
                [
                    "--json",
                    "neutrino",
                    "chapter11-passage",
                    "--input",
                    "tests/fixtures/neutrino_chapter11_valid_admission.json",
                ]
            )

        self.assertEqual(exit_code, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["FNPReadout_11"]["status"], "conditional_readout_constructed")


if __name__ == "__main__":
    unittest.main()
