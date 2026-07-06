import contextlib
import io
import json
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


if __name__ == "__main__":
    unittest.main()
