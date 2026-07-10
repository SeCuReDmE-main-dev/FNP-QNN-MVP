from __future__ import annotations

import contextlib
import copy
import io
import json
from pathlib import Path
import unittest

from core.neutrino_chapter14_threshold import neutrino_chapter14_threshold
from fnp_qnn_cli.main import main

ROOT = Path(__file__).resolve().parents[1]


def packet(): return json.loads((ROOT / "tests/fixtures/neutrino_chapter14_threshold.json").read_text(encoding="utf-8"))


class Chapter14ThresholdTests(unittest.TestCase):
    def test_valid_packet_computes_matrices_after_admission(self):
        result = neutrino_chapter14_threshold(packet())
        self.assertTrue(result["success"])
        self.assertEqual(result["carrier_composition"]["count"], 10)
        self.assertEqual(result["proof_state"], "P2_internal_repeatability")
        self.assertFalse(result["physical_model_validated"])
        self.assertEqual(len(result["fingerprint_sha256"]), 64)
        self.assertIn("D_f", result); self.assertIn("dF", result)

    def test_replay_is_deterministic(self):
        first = neutrino_chapter14_threshold(packet()); second = neutrino_chapter14_threshold(packet())
        self.assertEqual(first["fingerprint_sha256"], second["fingerprint_sha256"])
        self.assertEqual(first["state_trace"], second["state_trace"])

    def test_missing_synthia_or_nine_carriers_blocks_before_compute(self):
        for mutate in ("synthia", "carrier"):
            data = packet()
            if mutate == "synthia": data.pop("LexPacket_neutrino")
            else: data["chapter14_matrix_request"]["carriers"].pop()
            result = neutrino_chapter14_threshold(data)
            self.assertFalse(result["success"])
            self.assertFalse(result["fnp_computation_performed"])
            self.assertNotIn("D_f", result)

    def test_dimensions_nonfinite_and_claim_upgrades_block(self):
        variants = []
        data = packet(); data["chapter14_matrix_request"]["A_adj"] = [[0,1],[1,0]]; variants.append(data)
        data = packet(); data["chapter14_matrix_request"]["q_t"][0] = float("nan"); variants.append(data)
        for key in ("physical_model_validated", "real_detection_claim", "substrate_validated"):
            data = packet(); data["chapter14_matrix_request"][key] = True; variants.append(data)
        for data in variants:
            result = neutrino_chapter14_threshold(data)
            self.assertFalse(result["success"])
            self.assertNotIn("D_f", result)

    def test_cli_contract(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(["--json", "neutrino", "chapter14-threshold", "--input", str(ROOT / "tests/fixtures/neutrino_chapter14_threshold.json")])
        result = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(result["schema_version"], "fnp.neutrino_chapter14_threshold.v1")
        self.assertEqual(result["decision"]["status"], "accepted")


if __name__ == "__main__": unittest.main()
