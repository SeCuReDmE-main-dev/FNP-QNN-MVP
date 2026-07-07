import contextlib
import copy
import io
import json
from pathlib import Path
import unittest

from core.neutrino_admission_gate import neutrino_guardrail_check
from core.neutrino_chapter8_run_permission import neutrino_chapter8_run_permission
from fnp_qnn_cli.main import main


def _chapter8_packet():
    return json.loads(Path("tests/fixtures/neutrino_chapter8_valid_admission.json").read_text(encoding="utf-8"))


def _assert_no_key(payload, key):
    if isinstance(payload, dict):
        if key in payload:
            raise AssertionError(f"unexpected key present: {key}")
        for value in payload.values():
            _assert_no_key(value, key)
    elif isinstance(payload, list):
        for value in payload:
            _assert_no_key(value, key)


class NeutrinoChapter8RunPermissionTests(unittest.TestCase):
    def test_admission_preserves_chapter8_run_without_computation(self):
        payload = neutrino_guardrail_check(_chapter8_packet())

        self.assertTrue(payload["can_compute_fnp"])
        chapter8 = payload["admitted_chapter8_run"]
        self.assertEqual(chapter8["profile_version"], "chapter8.first_run_public_safe.v1")
        self.assertEqual(chapter8["run_input"]["ready_for_FNP"], "false_before_Synthia")
        self.assertEqual(chapter8["run_decision"]["run_status"], "admissible_under_guardrails")
        self.assertTrue(chapter8["run_permission"]["permission_to_continue"])
        _assert_no_key(payload, "D_f")
        _assert_no_key(payload, "D_f_hat")
        _assert_no_key(payload, "dF")
        _assert_no_key(payload, "i_fractal")
        _assert_no_key(payload, "i_fractal_candidate")

    def test_valid_packet_builds_chapter8_run_permission(self):
        payload = neutrino_chapter8_run_permission(_chapter8_packet())

        self.assertTrue(payload["can_continue_to_fnp_readout"])
        self.assertTrue(payload["can_continue_to_chapter9"])
        self.assertEqual(payload["schema_version"], "fnp.neutrino_chapter8_run_permission.v1")
        self.assertEqual(payload["run_status"], "admissible_under_guardrails")
        self.assertEqual(payload["allowed_next_step"], "FNP_QNN_readout")
        self.assertEqual(payload["decision"]["reason_codes"], ["chapter8_run_permission_valid"])
        self.assertIn("permission is not proof", payload["claim_boundary"])
        _assert_no_key(payload, "D_f")
        _assert_no_key(payload, "D_f_hat")
        _assert_no_key(payload, "dF")
        _assert_no_key(payload, "i_fractal")
        _assert_no_key(payload, "i_fractal_candidate")

    def test_missing_chapter8_run_profile_blocks_permission(self):
        packet = _chapter8_packet()
        packet["LexPacket_neutrino"].pop("chapter8_run_profile")

        payload = neutrino_chapter8_run_permission(packet)

        self.assertFalse(payload["can_continue_to_fnp_readout"])
        self.assertIn("missing_chapter8_run_profile", payload["decision"]["reason_codes"])

    def test_suspended_or_rejected_status_blocks_permission(self):
        for status in ("suspended", "rejected"):
            packet = copy.deepcopy(_chapter8_packet())
            profile = packet["LexPacket_neutrino"]["chapter8_run_profile"]
            profile["run_decision"]["run_status"] = status
            profile["run_permission"]["permission_to_continue"] = False
            profile["run_permission"]["allowed_next_step"] = "repair_payload"

            payload = neutrino_chapter8_run_permission(packet)

            self.assertFalse(payload["can_continue_to_fnp_readout"])
            self.assertIn("chapter8_not_admissible", payload["decision"]["reason_codes"])

    def test_forbidden_fnp_field_inside_chapter8_profile_blocks_admission(self):
        packet = _chapter8_packet()
        packet["LexPacket_neutrino"]["chapter8_run_profile"]["dF"] = 0.5

        payload = neutrino_chapter8_run_permission(packet)

        self.assertFalse(payload["can_continue_to_fnp_readout"])
        self.assertIn("synthia_packet_contains_fnp_computation_fields", payload["decision"]["reason_codes"])

    def test_permission_or_candidate_as_proof_claim_blocks_permission(self):
        packet = _chapter8_packet()
        packet["chapter8_run_request"] = {"claim": "candidate_as_proof"}

        payload = neutrino_chapter8_run_permission(packet)

        self.assertFalse(payload["can_continue_to_fnp_readout"])
        self.assertIn("chapter8_candidate_as_proof", payload["decision"]["reason_codes"])

    def test_cli_chapter8_run_returns_contract(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "--json",
                    "neutrino",
                    "chapter8-run",
                    "--input",
                    "tests/fixtures/neutrino_chapter8_valid_admission.json",
                ]
            )

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["can_continue_to_fnp_readout"])
        self.assertEqual(payload["run_status"], "admissible_under_guardrails")
        self.assertEqual(payload["allowed_next_step"], "FNP_QNN_readout")


if __name__ == "__main__":
    unittest.main()
