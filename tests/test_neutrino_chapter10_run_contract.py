import contextlib
import io
import json
from pathlib import Path
import unittest

from core.neutrino_admission_gate import neutrino_guardrail_check
from core.neutrino_chapter10_run_contract import neutrino_chapter10_run_contract
from fnp_qnn_cli.main import main


def _chapter10_packet():
    return json.loads(Path("tests/fixtures/neutrino_chapter10_valid_admission.json").read_text(encoding="utf-8"))


def _chapter10_profile(packet):
    return packet["LexPacket_neutrino"]["chapter10_chamber_profile"]


def _assert_no_key(payload, key):
    if isinstance(payload, dict):
        if key in payload:
            raise AssertionError(f"unexpected key present: {key}")
        for value in payload.values():
            _assert_no_key(value, key)
    elif isinstance(payload, list):
        for value in payload:
            _assert_no_key(value, key)


class NeutrinoChapter10RunContractTests(unittest.TestCase):
    def test_admission_preserves_chapter10_chamber_without_computation(self):
        payload = neutrino_guardrail_check(_chapter10_packet())

        self.assertTrue(payload["can_compute_fnp"])
        chapter10 = payload["admitted_chapter10_chamber"]
        self.assertEqual(chapter10["profile_version"], "chapter10.chamber_container_public_safe.v1")
        self.assertEqual(chapter10["chapter10_status"], "run_prepared_for_chapter11")
        self.assertTrue(chapter10["RunPrepared_10"]["chapter11_execution_ready"])
        self.assertFalse(chapter10["RunPrepared_10"]["physical_claim_allowed"])
        _assert_no_key(payload, "D_f")
        _assert_no_key(payload, "D_f_hat")
        _assert_no_key(payload, "dF")
        _assert_no_key(payload, "i_fractal")
        _assert_no_key(payload, "i_fractal_candidate")

    def test_valid_packet_builds_chapter10_run_contract(self):
        payload = neutrino_chapter10_run_contract(_chapter10_packet())

        self.assertTrue(payload["can_prepare_chapter11_run"])
        self.assertEqual(payload["schema_version"], "fnp.neutrino_chapter10_run_contract.v1")
        self.assertEqual(payload["chapter11_entry_status"], "ready_for_first_passage_under_declared_contract")
        self.assertEqual(payload["decision"]["reason_codes"], ["chapter10_run_contract_valid"])
        self.assertIn("simulated event is not detection", payload["claim_boundary"])
        _assert_no_key(payload, "D_f")
        _assert_no_key(payload, "D_f_hat")
        _assert_no_key(payload, "dF")
        _assert_no_key(payload, "i_fractal")
        _assert_no_key(payload, "i_fractal_candidate")

    def test_missing_chapter10_profile_blocks_contract(self):
        packet = _chapter10_packet()
        packet["LexPacket_neutrino"].pop("chapter10_chamber_profile")

        payload = neutrino_chapter10_run_contract(packet)

        self.assertFalse(payload["can_prepare_chapter11_run"])
        self.assertIn("missing_chapter10_chamber_profile", payload["decision"]["reason_codes"])

    def test_missing_source_registry_blocks_contract(self):
        packet = _chapter10_packet()
        profile = _chapter10_profile(packet)
        profile["source_visibility"]["provided_source_ids"] = ["CH10-GEANT4-001"]

        payload = neutrino_chapter10_run_contract(packet)

        self.assertFalse(payload["can_prepare_chapter11_run"])
        self.assertIn("chapter10_missing_source_registry", payload["decision"]["reason_codes"])

    def test_detection_t2k_cp_and_background_overclaims_block_contract(self):
        cases = [
            ("simulated event is detection", "chapter10_event_as_detection"),
            ("T2K reproduced", "chapter10_t2k_reproduction_claim"),
            ("path_comparison = CP_measurement", "chapter10_cp_measurement_claim"),
            ("background missing equals zero", "chapter10_background_missing_as_zero"),
            ("prepared_tension_slot = dF", "chapter10_prepared_tension_as_df"),
        ]
        for claim, reason_code in cases:
            with self.subTest(claim=claim):
                packet = _chapter10_packet()
                packet["chapter10_run_request"] = {"claim": claim}

                payload = neutrino_chapter10_run_contract(packet)

                self.assertFalse(payload["can_prepare_chapter11_run"])
                self.assertIn(reason_code, payload["decision"]["reason_codes"])

    def test_profile_overclaim_blocks_contract(self):
        packet = _chapter10_packet()
        profile = _chapter10_profile(packet)
        profile["EventContainer_10"]["container_boundary"] = "container_valid = physical_proof"

        payload = neutrino_chapter10_run_contract(packet)

        self.assertFalse(payload["can_prepare_chapter11_run"])
        self.assertIn("chapter10_container_as_proof", payload["decision"]["reason_codes"])

    def test_forbidden_fnp_field_inside_profile_blocks_contract(self):
        packet = _chapter10_packet()
        _chapter10_profile(packet)["dF"] = 0.5

        payload = neutrino_chapter10_run_contract(packet)

        self.assertFalse(payload["can_prepare_chapter11_run"])
        self.assertIn("synthia_packet_contains_fnp_computation_fields", payload["decision"]["reason_codes"])

    def test_cli_chapter10_contract_returns_contract(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "--json",
                    "neutrino",
                    "chapter10-contract",
                    "--input",
                    "tests/fixtures/neutrino_chapter10_valid_admission.json",
                ]
            )

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["can_prepare_chapter11_run"])
        self.assertEqual(payload["chapter11_entry_status"], "ready_for_first_passage_under_declared_contract")


if __name__ == "__main__":
    unittest.main()
