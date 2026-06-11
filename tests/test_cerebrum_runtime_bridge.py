import unittest
from pathlib import Path
import tempfile

import numpy as np
from fastapi.testclient import TestClient

from api.main import app
from core import CerebrumRuntimeBridge, LifeScienceObservationPort, QNNNucleus


class CerebrumRuntimeBridgeTests(unittest.TestCase):
    def setUp(self):
        self.bridge = CerebrumRuntimeBridge()

    def test_interval_events_normalize_consistently(self):
        events, pairs, warnings = self.bridge.ingest(
            {
                "memories": [
                    {"modality": "hearing", "starting_time": 10.0, "ending_time": 11.0, "value": 0.4},
                    {"modality": "vision", "starting_time": 10.5, "ending_time": 12.0, "value": 0.8},
                ]
            }
        )
        self.assertEqual(warnings, [])
        self.assertEqual(events[0].starting_time, 0.0)
        self.assertEqual(events[0].ending_time, 1.0)
        self.assertEqual(events[1].starting_time, 0.5)
        self.assertTrue(any(pair.direction == "H2V" for pair in pairs))
        self.assertTrue(any(pair.direction == "V2H" for pair in pairs))

    def test_invalid_modality_maps_to_stimuli_with_warning(self):
        events, _, warnings = self.bridge.ingest(
            {"memories": [{"modality": "unknown-sense", "starting_time": 0.0, "ending_time": 1.0, "value": 0.1}]}
        )
        self.assertEqual(events[0].modality, "stimuli")
        self.assertTrue(any("Unknown modality" in warning for warning in warnings))

    def test_overlap_pair_generation_matches_cerebrum_directions(self):
        events, pairs, _ = self.bridge.ingest(
            {
                "memories": [
                    {"modality": "hearing", "starting_time": 0.0, "ending_time": 2.0, "value": 0.1},
                    {"modality": "vision", "starting_time": 1.0, "ending_time": 3.0, "value": 0.2},
                    {"modality": "language", "starting_time": 1.5, "ending_time": 2.5, "value": 0.3},
                ]
            }
        )
        directions = {pair.direction for pair in pairs}
        self.assertEqual(len(events), 3)
        self.assertIn("H2V", directions)
        self.assertIn("V2H", directions)
        self.assertIn("H2L", directions)
        self.assertIn("L2H", directions)
        self.assertIn("V2L", directions)
        self.assertIn("L2V", directions)

    def test_legacy_pairs_are_accepted_when_provided(self):
        events, pairs, warnings = self.bridge.ingest(
            {
                "memories": [
                    {"modality": "hearing", "starting_time": 0.0, "ending_time": 1.0, "value": 0.3},
                    {"modality": "vision", "starting_time": 0.2, "ending_time": 1.2, "value": 0.6},
                ],
                "pairs": [
                    {"timestamp1": 0.0, "timestamp2": 0.2, "direction": "H2V", "overlap_score": 0.75},
                ],
            }
        )
        self.assertEqual(len(events), 2)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0].direction, "H2V")
        self.assertEqual(warnings, [])

    def test_legacy_snapshot_path_is_loaded(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot = Path(tmpdir) / "snapshot.json"
            snapshot.write_text(
                """
                {
                  "memories": [
                    {"modality": "hearing", "starting_time": 0.0, "ending_time": 1.0, "value": 0.2},
                    {"modality": "language", "starting_time": 0.3, "ending_time": 1.3, "value": 0.7}
                  ]
                }
                """.strip(),
                encoding="utf-8",
            )
            events, pairs, warnings = CerebrumRuntimeBridge(legacy_cerebrum_path=str(snapshot.parent)).ingest(
                {"legacy_snapshot": str(snapshot)}
            )
        self.assertEqual(len(events), 2)
        self.assertGreaterEqual(len(pairs), 2)
        self.assertEqual(warnings, [])

    def test_legacy_path_is_used_when_payload_is_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot = Path(tmpdir) / "legacy.json"
            snapshot.write_text(
                """
                {
                  "hearing_timestamps": [
                    {"starting_time": "0.0", "ending_time": "1.0", "data": 0.2, "label": "rhythm"}
                  ],
                  "vision_timestamps": [
                    {"starting_time": "0.2", "ending_time": "1.2", "data": 0.6, "label": "motion"}
                  ]
                }
                """.strip(),
                encoding="utf-8",
            )
            bridge = CerebrumRuntimeBridge(legacy_cerebrum_path=tmpdir)
            events, pairs, warnings = bridge.ingest(None)
        self.assertEqual(len(events), 2)
        self.assertGreaterEqual(len(pairs), 2)
        self.assertEqual(warnings, [])

    def test_legacy_table_payload_is_loaded(self):
        events, pairs, warnings = self.bridge.ingest(
            {
                "hearing_timestamps": [
                    {"starting_time": "0.0", "ending_time": "1.0", "data": 0.2, "label": "rhythm"},
                ],
                "vision_timestamps": [
                    {"starting_time": "0.2", "ending_time": "1.2", "data": 0.6, "label": "motion"},
                ],
                "crossmodal_mappings": [
                    {"timestamp1": 0.0, "timestamp2": 0.2, "direction": "H2V", "overlap_score": 0.8}
                ],
            }
        )
        self.assertEqual(len(events), 2)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0].direction, "H2V")
        self.assertEqual(warnings, [])

    def test_empty_stream_returns_safe_runtime_state(self):
        state = self.bridge.build_state({"memories": []})
        self.assertEqual(state.events, [])
        self.assertEqual(state.pairs, [])
        self.assertEqual(state.feature_bundle.sequence_length, 0)
        self.assertTrue(np.isfinite(state.feature_vector).all())
        self.assertTrue(state.warnings)

    def test_full_runtime_run_produces_qnn_result(self):
        nucleus = QNNNucleus(adapter=self.bridge.adapter)
        state = self.bridge.build_state(self.bridge.default_payload(), qnn_nucleus=nucleus, max_epochs=4)
        self.assertGreaterEqual(len(state.events), 4)
        self.assertGreaterEqual(len(state.pairs), 4)
        self.assertTrue(np.isfinite(state.feature_vector).all())
        self.assertIsNotNone(state.qnn_result)
        self.assertIn("backend", state.qnn_result)

    def test_life_science_statefield_port_is_opt_in(self):
        port = LifeScienceObservationPort()
        observations = port.statefield_to_observations({"mu": [0.2, 0.7], "nu": [0.1, 0.2], "pi": [0.7, 0.1]})
        self.assertEqual(len(observations), 2)
        self.assertEqual(observations[0]["modality"], "stimuli")
        self.assertTrue(0.0 <= observations[0]["value"] <= 1.0)


class CerebrumRuntimeApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_runtime_status_endpoint(self):
        response = self.client.get("/cerebrum/runtime/status")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["bridge"], "operational")

    def test_runtime_ingest_endpoint(self):
        response = self.client.post("/cerebrum/runtime/ingest", json={})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertGreaterEqual(len(payload["events"]), 4)
        self.assertGreaterEqual(len(payload["pairs"]), 4)

    def test_runtime_run_endpoint(self):
        response = self.client.post("/cerebrum/runtime/run", json={"epochs": 4})
        self.assertEqual(response.status_code, 200)
        runtime = response.json()["runtime"]
        self.assertIn("bundle", runtime)
        self.assertIn("qnn_result", runtime)
        self.assertIn("benchmark", runtime)
        self.assertGreater(runtime["feature_dimension"], 0)

    def test_execute_command_runtime_routes(self):
        response = self.client.post(
            "/execute-command",
            json={"command": "cerebrum-runtime-status"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["type"], "cerebrum-runtime")
        self.assertEqual(payload["data"]["status"], "ok")


if __name__ == "__main__":
    unittest.main()
