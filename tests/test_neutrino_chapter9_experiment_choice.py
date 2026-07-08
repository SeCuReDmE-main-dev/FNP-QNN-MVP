import contextlib
import io
import json
from pathlib import Path
import unittest

from core.neutrino_admission_gate import neutrino_guardrail_check
from core.neutrino_chapter9_experiment_choice import neutrino_chapter9_experiment_choice
from fnp_qnn_cli.main import main


def _chapter9_packet():
    return json.loads(Path("tests/fixtures/neutrino_chapter9_valid_admission.json").read_text(encoding="utf-8"))


def _assert_no_key(payload, key):
    if isinstance(payload, dict):
        if key in payload:
            raise AssertionError(f"unexpected key present: {key}")
        for value in payload.values():
            _assert_no_key(value, key)
    elif isinstance(payload, list):
        for value in payload:
            _assert_no_key(value, key)


class NeutrinoChapter9ExperimentChoiceTests(unittest.TestCase):
    def test_admission_preserves_chapter9_source_choice_without_computation(self):
        payload = neutrino_guardrail_check(_chapter9_packet())

        self.assertTrue(payload["can_compute_fnp"])
        chapter9 = payload["admitted_chapter9_source_choice"]
        self.assertEqual(chapter9["profile_version"], "chapter9.source_choice_public_safe.v1")
        self.assertEqual(chapter9["chapter9_status"], "selected_for_container")
        self.assertEqual(chapter9["central_experiment"]["experiment_id"], "chapter11_t2k_like_flavor_antiflavor_phase_projection")
        self.assertEqual(chapter9["synthia_gate"]["ready_for_FNP"], "true_after_Synthia_for_container_validation")
        _assert_no_key(payload, "D_f")
        _assert_no_key(payload, "D_f_hat")
        _assert_no_key(payload, "dF")
        _assert_no_key(payload, "i_fractal")
        _assert_no_key(payload, "i_fractal_candidate")

    def test_valid_packet_builds_chapter9_experiment_choice_contract(self):
        payload = neutrino_chapter9_experiment_choice(_chapter9_packet())

        self.assertTrue(payload["can_prepare_chapter10_container"])
        self.assertEqual(payload["schema_version"], "fnp.neutrino_chapter9_experiment_choice.v1")
        self.assertEqual(payload["central_experiment_id"], "chapter11_t2k_like_flavor_antiflavor_phase_projection")
        self.assertEqual(payload["chapter10_entry_status"], "ready_for_experimental_container_design")
        self.assertEqual(payload["decision"]["reason_codes"], ["chapter9_experiment_choice_valid"])
        self.assertIn("not T2K reproduction", payload["claim_boundary"])
        self.assertIn("SB60-002", payload["source_ids"])
        self.assertIn("CH9-T2K-OSC-001", payload["source_ids"])
        self.assertIn("SB60-052", payload["source_ids"])
        _assert_no_key(payload, "D_f")
        _assert_no_key(payload, "D_f_hat")
        _assert_no_key(payload, "dF")
        _assert_no_key(payload, "i_fractal")
        _assert_no_key(payload, "i_fractal_candidate")

    def test_missing_chapter9_source_choice_profile_blocks_choice_contract(self):
        packet = _chapter9_packet()
        packet["LexPacket_neutrino"].pop("chapter9_source_choice_profile")

        payload = neutrino_chapter9_experiment_choice(packet)

        self.assertFalse(payload["can_prepare_chapter10_container"])
        self.assertIn("missing_chapter9_source_choice_profile", payload["decision"]["reason_codes"])

    def test_missing_source_registry_blocks_admission(self):
        packet = _chapter9_packet()
        profile = packet["LexPacket_neutrino"]["chapter9_source_choice_profile"]
        profile["source_visibility"]["provided_source_ids"] = ["SB60-002", "SB60-052"]

        payload = neutrino_chapter9_experiment_choice(packet)

        self.assertFalse(payload["can_prepare_chapter10_container"])
        self.assertIn("chapter9_missing_source_registry", payload["decision"]["reason_codes"])

    def test_unbounded_or_detection_choice_blocks_admission(self):
        packet = _chapter9_packet()
        profile = packet["LexPacket_neutrino"]["chapter9_source_choice_profile"]
        profile["central_experiment"]["experiment_id"] = "all_neutrino_physics"
        profile["central_experiment"]["detection_status"] = "real_detection_claim"

        payload = neutrino_chapter9_experiment_choice(packet)

        self.assertFalse(payload["can_prepare_chapter10_container"])
        self.assertIn("chapter9_unbounded_experiment_choice", payload["decision"]["reason_codes"])
        self.assertIn("chapter9_experiment_choice_as_detection", payload["decision"]["reason_codes"])

    def test_overclaim_request_blocks_choice_contract(self):
        packet = _chapter9_packet()
        packet["chapter9_experiment_request"] = {
            "claim": "T2K reproduced and CP violation measured and selected experiment is real detection"
        }

        payload = neutrino_chapter9_experiment_choice(packet)

        self.assertFalse(payload["can_prepare_chapter10_container"])
        self.assertIn("chapter9_t2k_reproduction_claim", payload["decision"]["reason_codes"])

    def test_forbidden_fnp_field_inside_profile_blocks_admission(self):
        packet = _chapter9_packet()
        packet["LexPacket_neutrino"]["chapter9_source_choice_profile"]["dF"] = 0.5

        payload = neutrino_chapter9_experiment_choice(packet)

        self.assertFalse(payload["can_prepare_chapter10_container"])
        self.assertIn("synthia_packet_contains_fnp_computation_fields", payload["decision"]["reason_codes"])

    def test_cli_chapter9_choice_returns_contract(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "--json",
                    "neutrino",
                    "chapter9-choice",
                    "--input",
                    "tests/fixtures/neutrino_chapter9_valid_admission.json",
                ]
            )

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["can_prepare_chapter10_container"])
        self.assertEqual(payload["chapter10_entry_status"], "ready_for_experimental_container_design")


if __name__ == "__main__":
    unittest.main()
