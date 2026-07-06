import contextlib
import io
import json
from pathlib import Path
import unittest

from core.neutrino_chapter5_carrier import neutrino_chapter5_carrier
from fnp_qnn_cli.main import main


def _chapter5_packet():
    return json.loads(Path("tests/fixtures/neutrino_chapter5_valid_admission.json").read_text(encoding="utf-8"))


def _assert_no_key(payload, forbidden_key):
    if isinstance(payload, dict):
        testcase = unittest.TestCase()
        testcase.assertNotIn(forbidden_key, payload)
        for value in payload.values():
            _assert_no_key(value, forbidden_key)
    elif isinstance(payload, list):
        for value in payload:
            _assert_no_key(value, forbidden_key)


class NeutrinoChapter5CarrierTests(unittest.TestCase):
    def test_valid_packet_builds_d_f_hat_packet(self):
        payload = neutrino_chapter5_carrier(_chapter5_packet())

        self.assertTrue(payload["can_compute_chapter5_carrier"])
        self.assertFalse(payload["can_compute_dF"])
        self.assertEqual(payload["schema_version"], "fnp.neutrino_chapter5_carrier.v1")
        self.assertEqual(payload["CarrierAdm"]["carrier_family"], "phase_carrier")
        self.assertTrue(payload["NormAdm"]["admitted"])
        self.assertAlmostEqual(payload["D_f_hat_packet"]["D_f_hat"], 0.5)
        self.assertAlmostEqual(payload["D_f_hat_packet"]["D_f"], 1.5)
        _assert_no_key(payload, "dF")
        _assert_no_key(payload, "i_fractal")
        _assert_no_key(payload, "i_fractal_candidate")

    def test_invalid_normalization_bounds_are_blocked(self):
        packet = _chapter5_packet()
        packet["carrier_request"]["D_min"] = 1.0
        packet["carrier_request"]["D_max"] = 1.0

        payload = neutrino_chapter5_carrier(packet)

        self.assertFalse(payload["can_compute_chapter5_carrier"])
        self.assertIn("normalization_bounds_invalid", payload["decision"]["reason_codes"])
        self.assertIsNone(payload["D_f_hat_packet"])

    def test_missing_carrier_request_is_blocked(self):
        packet = _chapter5_packet()
        packet.pop("carrier_request")

        payload = neutrino_chapter5_carrier(packet)

        self.assertFalse(payload["can_compute_chapter5_carrier"])
        self.assertIn("missing_carrier_request", payload["decision"]["reason_codes"])

    def test_non_admitted_synthia_packet_blocks_before_carrier(self):
        packet = _chapter5_packet()
        packet["LexPacket_neutrino"]["Adm_lex"] = False
        packet["LexPacket_neutrino"]["decision"]["status"] = "rejected"

        payload = neutrino_chapter5_carrier(packet)

        self.assertFalse(payload["can_compute_chapter5_carrier"])
        self.assertIn("synthia_decision_not_admitted", payload["decision"]["reason_codes"])

    def test_excluded_payload_cannot_feed_carrier(self):
        packet = _chapter5_packet()
        packet["carrier_request"]["source"] = "excluded_payload"

        payload = neutrino_chapter5_carrier(packet)

        self.assertFalse(payload["can_compute_chapter5_carrier"])
        self.assertIn("blocked_payload_used_for_carrier", payload["decision"]["reason_codes"])

    def test_cli_chapter5_carrier_returns_contract(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "--json",
                    "neutrino",
                    "chapter5-carrier",
                    "--input",
                    "tests/fixtures/neutrino_chapter5_valid_admission.json",
                ]
            )

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["can_compute_chapter5_carrier"])
        self.assertEqual(payload["D_f_hat_packet"]["D_f_hat"], 0.5)
        _assert_no_key(payload, "dF")
        _assert_no_key(payload, "i_fractal")
        _assert_no_key(payload, "i_fractal_candidate")


if __name__ == "__main__":
    unittest.main()
