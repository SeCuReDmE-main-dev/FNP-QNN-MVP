import json
import unittest
from pathlib import Path
import tempfile

import numpy as np
from fastapi.testclient import TestClient

from api.main import app
from core import (
    CerebrumRuntimeBridge,
    LifeScienceObservationPort,
    QNNNucleus,
    admission_to_runtime_payload,
    build_admission,
    cloud_kit_status,
    decrypt_admission,
    e2b_ingest_plan,
    e2b_smoke,
    encrypt_admission,
    generate_rag_key,
)


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

    def test_invalid_legacy_snapshot_is_reported(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot = Path(tmpdir) / "broken.json"
            snapshot.write_text("{not-json", encoding="utf-8")
            events, pairs, warnings = CerebrumRuntimeBridge(legacy_cerebrum_path=tmpdir).ingest(
                {"legacy_snapshot": str(snapshot)}
            )
        self.assertEqual(events, [])
        self.assertEqual(pairs, [])
        self.assertTrue(any("could not be read" in warning for warning in warnings))

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

    def test_plithogenic_runtime_fusion_is_opt_in(self):
        default_state = self.bridge.build_state(self.bridge.default_payload())
        enabled_state = self.bridge.build_state(self.bridge.default_payload(), plithogenic_enabled=True)

        self.assertIsNone(default_state.plithogenic)
        self.assertNotIn("plithogenic", default_state.to_dict())
        self.assertIsNotNone(enabled_state.plithogenic)
        self.assertIn("plithogenic", enabled_state.to_dict())
        self.assertIn("plithogenic_fusion_profile", enabled_state.lvfm)
        self.assertGreater(enabled_state.feature_vector.shape[0], default_state.feature_vector.shape[0])

    def test_plithogenic_runtime_features_reach_qnn_when_enabled(self):
        nucleus = QNNNucleus(adapter=self.bridge.adapter)
        state = self.bridge.build_state(
            self.bridge.default_payload(),
            qnn_nucleus=nucleus,
            max_epochs=2,
            plithogenic_enabled=True,
        )

        self.assertIsNotNone(state.qnn_result)
        self.assertIn("plithogenic_fusion_profile", state.qnn_result)
        self.assertEqual(
            state.qnn_result["plithogenic_fusion_profile"]["feature_dimension"],
            state.plithogenic["feature_dimension"],
        )

    def test_revolutionary_topology_runtime_layer_is_opt_in(self):
        default_state = self.bridge.build_state(self.bridge.default_payload())
        enabled_state = self.bridge.build_state(self.bridge.default_payload(), revolutionary_topology_enabled=True)

        self.assertIsNone(default_state.revolutionary_topology)
        self.assertNotIn("revolutionary_topology", default_state.to_dict())
        self.assertIsNotNone(enabled_state.revolutionary_topology)
        self.assertIn("revolutionary_topology", enabled_state.to_dict())
        self.assertIn("revolutionary_topology_profile", enabled_state.lvfm)
        self.assertGreater(enabled_state.feature_vector.shape[0], default_state.feature_vector.shape[0])

    def test_revolutionary_topology_features_reach_qnn_when_enabled(self):
        nucleus = QNNNucleus(adapter=self.bridge.adapter)
        state = self.bridge.build_state(
            self.bridge.default_payload(),
            qnn_nucleus=nucleus,
            max_epochs=2,
            revolutionary_topology_enabled=True,
        )

        self.assertIsNotNone(state.qnn_result)
        self.assertIn("revolutionary_topology_profile", state.qnn_result)
        self.assertEqual(
            state.qnn_result["revolutionary_topology_profile"]["feature_dimension"],
            state.revolutionary_topology["feature_dimension"],
        )

    def test_plithogenic_topology_bridge_requires_both_flags(self):
        default_state = self.bridge.build_state(self.bridge.default_payload())
        plithogenic_only = self.bridge.build_state(self.bridge.default_payload(), plithogenic_enabled=True)
        topology_only = self.bridge.build_state(self.bridge.default_payload(), revolutionary_topology_enabled=True)
        enabled_state = self.bridge.build_state(
            self.bridge.default_payload(),
            plithogenic_enabled=True,
            revolutionary_topology_enabled=True,
        )

        self.assertIsNone(default_state.plithogenic_topology)
        self.assertIsNone(plithogenic_only.plithogenic_topology)
        self.assertIsNone(topology_only.plithogenic_topology)
        self.assertIsNotNone(enabled_state.plithogenic_topology)
        self.assertIn("plithogenic_topology", enabled_state.to_dict())
        self.assertIn("plithogenic_topology_profile", enabled_state.lvfm)
        self.assertGreater(enabled_state.feature_vector.shape[0], plithogenic_only.feature_vector.shape[0])
        self.assertGreater(enabled_state.feature_vector.shape[0], topology_only.feature_vector.shape[0])
        self.assertNotIn("plugin_stabilization_profile", enabled_state.plithogenic_topology)

    def test_plithogenic_topology_features_reach_qnn_when_both_flags_enabled(self):
        nucleus = QNNNucleus(adapter=self.bridge.adapter)
        state = self.bridge.build_state(
            self.bridge.default_payload(),
            qnn_nucleus=nucleus,
            max_epochs=2,
            plithogenic_enabled=True,
            revolutionary_topology_enabled=True,
        )

        self.assertIsNotNone(state.qnn_result)
        self.assertIn("plithogenic_topology_profile", state.qnn_result)
        self.assertEqual(
            state.qnn_result["plithogenic_topology_profile"]["feature_dimension"],
            state.plithogenic_topology["feature_dimension"],
        )

    def test_plugin_stabilized_plithogenic_topology_reaches_runtime_lvfm_and_qnn(self):
        nucleus = QNNNucleus(adapter=self.bridge.adapter)
        state = self.bridge.build_state(
            self.bridge.default_payload(),
            qnn_nucleus=nucleus,
            max_epochs=2,
            plithogenic_enabled=True,
            revolutionary_topology_enabled=True,
            plugin_hook_enabled=True,
            plugin_context={
                "series": [0.1, 0.3, 0.2, 0.8, 0.4, 0.9],
                "steps": 120,
                "n_atoms": 8,
                "depth": 2,
                "max_terms": 8,
            },
            cpai_context={"local_load": 0.8, "nodes_active": 2, "nodes_visible": 2},
        )

        self.assertIsNotNone(state.plithogenic_topology)
        self.assertIn("plugin_stabilization_profile", state.plithogenic_topology)
        self.assertIn("plugin_stabilization_profile", state.lvfm["plithogenic_topology_profile"])
        self.assertIn("plugin_stabilization_profile", state.qnn_result["plithogenic_topology_profile"])
        self.assertIn("plugin_hook_status", state.qnn_result)
        self.assertTrue(
            all(0.0 <= item <= 1.0 for item in state.plithogenic_topology["stabilized_feature_vector"])
        )

    def test_neutro_algebra_runtime_layer_is_opt_in(self):
        default_state = self.bridge.build_state(self.bridge.default_payload())
        enabled_state = self.bridge.build_state(self.bridge.default_payload(), neutro_algebra_enabled=True)

        self.assertIsNone(default_state.neutro_algebra)
        self.assertNotIn("neutro_algebra", default_state.to_dict())
        self.assertIsNotNone(enabled_state.neutro_algebra)
        self.assertIn("neutro_algebra", enabled_state.to_dict())
        self.assertIn("structure_system_profile", enabled_state.neutro_algebra)
        self.assertIn("neutro_algebra_profile", enabled_state.lvfm)
        self.assertIn("neutro_structure_profile", enabled_state.lvfm)
        self.assertGreater(enabled_state.feature_vector.shape[0], default_state.feature_vector.shape[0])
        self.assertTrue(all(0.0 <= item <= 1.0 for item in enabled_state.neutro_algebra["feature_vector"]))
        self.assertTrue(
            all(0.0 <= item <= 1.0 for item in enabled_state.neutro_algebra["structure_system_profile"]["feature_vector"])
        )

    def test_neutro_algebra_features_reach_qnn_when_enabled(self):
        nucleus = QNNNucleus(adapter=self.bridge.adapter)
        state = self.bridge.build_state(
            self.bridge.default_payload(),
            qnn_nucleus=nucleus,
            max_epochs=2,
            plithogenic_enabled=True,
            revolutionary_topology_enabled=True,
            neutro_algebra_enabled=True,
        )

        self.assertIsNotNone(state.qnn_result)
        self.assertIn("neutro_algebra_profile", state.qnn_result)
        self.assertIn("neutro_structure_profile", state.qnn_result)
        self.assertIn("plithogenic_topology_profile", state.qnn_result)
        self.assertEqual(
            state.qnn_result["neutro_algebra_profile"]["feature_dimension"],
            state.neutro_algebra["feature_dimension"],
        )
        self.assertEqual(
            state.qnn_result["neutro_structure_profile"]["feature_dimension"],
            state.neutro_algebra["structure_system_profile"]["feature_dimension"],
        )

    def test_penrose_hameroff_runtime_layer_is_opt_in(self):
        default_state = self.bridge.build_state(self.bridge.default_payload())
        enabled_state = self.bridge.build_state(
            self.bridge.default_payload(),
            penrose_hameroff_enabled=True,
            objective_reduction_energy_joule=1.054571817e-34,
            coherence_time_s=1.0,
            anesthetic_damping=0.1,
            microtubule_frequency_hz=1e8,
            spin_network_vertices=[[1.0, 1.0, 1.0]],
        )

        self.assertIsNone(default_state.penrose_hameroff)
        self.assertNotIn("penrose_hameroff", default_state.to_dict())
        self.assertIsNotNone(enabled_state.penrose_hameroff)
        self.assertIn("penrose_hameroff", enabled_state.to_dict())
        self.assertIn("penrose_hameroff_profile", enabled_state.lvfm)
        self.assertGreater(enabled_state.feature_vector.shape[0], default_state.feature_vector.shape[0])
        self.assertTrue(all(0.0 <= item <= 1.0 for item in enabled_state.penrose_hameroff["feature_vector"]))

    def test_penrose_hameroff_features_reach_qnn_when_enabled(self):
        nucleus = QNNNucleus(adapter=self.bridge.adapter)
        state = self.bridge.build_state(
            self.bridge.default_payload(),
            qnn_nucleus=nucleus,
            max_epochs=2,
            penrose_hameroff_enabled=True,
            objective_reduction_energy_joule=1.054571817e-34,
            coherence_time_s=1.0,
            anesthetic_damping=0.1,
            microtubule_frequency_hz=1e8,
            spin_network_vertices=[[1.0, 1.0, 1.0]],
        )

        self.assertIsNotNone(state.qnn_result)
        self.assertIn("penrose_hameroff_profile", state.qnn_result)
        self.assertEqual(
            state.qnn_result["penrose_hameroff_profile"]["feature_dimension"],
            state.penrose_hameroff["feature_dimension"],
        )

    def test_hydra_em_gpcn_runtime_layer_is_opt_in(self):
        default_state = self.bridge.build_state(self.bridge.default_payload())
        enabled_state = self.bridge.build_state(
            self.bridge.default_payload(),
            hydra_em_enabled=True,
            gpcn_set_phi_enabled=True,
            orch_or_simulation_enabled=True,
            objective_reduction_energy_joule=1.054571817e-34,
            coherence_time_s=1.0,
            anesthetic_damping=0.1,
            microtubule_frequency_hz=100000000.0,
            microtubule_proxy_count=6,
            microtubule_coupling_strength=0.8,
        )

        self.assertIsNone(default_state.hydra_em_gpcn)
        self.assertNotIn("hydra_em_gpcn", default_state.to_dict())
        self.assertIsNotNone(enabled_state.hydra_em_gpcn)
        self.assertIn("hydra_em_gpcn", enabled_state.to_dict())
        self.assertIn("hydra_em_gpcn_profile", enabled_state.lvfm)
        self.assertGreater(enabled_state.feature_vector.shape[0], default_state.feature_vector.shape[0])
        self.assertTrue(all(0.0 <= item <= 1.0 for item in enabled_state.hydra_em_gpcn["feature_vector"]))

    def test_hydra_em_gpcn_features_reach_qnn_when_enabled(self):
        nucleus = QNNNucleus(adapter=self.bridge.adapter)
        state = self.bridge.build_state(
            self.bridge.default_payload(),
            qnn_nucleus=nucleus,
            max_epochs=2,
            hydra_em_enabled=True,
            gpcn_set_phi_enabled=True,
            orch_or_simulation_enabled=True,
            objective_reduction_energy_joule=1.054571817e-34,
            coherence_time_s=1.0,
            anesthetic_damping=0.1,
            microtubule_frequency_hz=100000000.0,
            microtubule_proxy_count=6,
            microtubule_coupling_strength=0.8,
        )

        self.assertIsNotNone(state.qnn_result)
        self.assertIn("hydra_em_gpcn_profile", state.qnn_result)
        self.assertEqual(
            state.qnn_result["hydra_em_gpcn_profile"]["feature_dimension"],
            state.hydra_em_gpcn["feature_dimension"],
        )

    def test_life_science_statefield_port_is_opt_in(self):
        port = LifeScienceObservationPort()
        observations = port.statefield_to_observations({"mu": [0.2, 0.7], "nu": [0.1, 0.2], "pi": [0.7, 0.1]})
        self.assertEqual(len(observations), 2)
        self.assertEqual(observations[0]["modality"], "stimuli")
        self.assertTrue(0.0 <= observations[0]["value"] <= 1.0)

    def test_life_science_statefield_defaults_when_only_mu_provided(self):
        port = LifeScienceObservationPort()
        # Previously raised a numpy broadcast ValueError because the nu/pi defaults
        # were dropped by _as_vector and eagerly broadcast against mu.
        observations = port.statefield_to_observations({"mu": [0.2, 0.7, 0.4]})
        self.assertEqual(len(observations), 3)
        self.assertTrue(all(0.0 <= obs["value"] <= 1.0 for obs in observations))

    def test_life_science_statefield_handles_mismatched_lengths(self):
        port = LifeScienceObservationPort()
        observations = port.statefield_to_observations({"mu": [0.2, 0.7, 0.4], "nu": [0.1, 0.2]})
        self.assertEqual(len(observations), 3)
        self.assertTrue(all(np.isfinite(obs["value"]) for obs in observations))

    def test_life_science_statefield_computes_residual_pi(self):
        port = LifeScienceObservationPort()
        observations = port.statefield_to_observations({"mu": [0.0], "nu": [0.0]})
        # pi defaults to the residual 1 - mu - nu = 1.0, so value = 0 * 1 + 0.5 * 1 = 0.5.
        self.assertAlmostEqual(observations[0]["value"], 0.5)

    def test_cloud_kit_status_is_secret_safe(self):
        payload = cloud_kit_status()
        self.assertEqual(payload["status"], "ok")
        self.assertIn("e2b", payload)
        self.assertFalse(payload["e2b"]["api_key_value_printed"])
        self.assertFalse(payload["rag_encryption"]["raw_key_value_printed"])

    def test_e2b_ingest_plan_keeps_external_data_outside_core(self):
        payload = e2b_ingest_plan("https://example.com/data.csv", "External data", "codex")
        self.assertTrue(payload["success"])
        self.assertEqual(payload["provider"], "e2b")
        self.assertFalse(payload["writes_files"])
        self.assertFalse(payload["raw_secret_stored"])
        self.assertIn("sanitized summary", " ".join(payload["plan"]).lower())

    def test_e2b_real_smoke_when_openclaw_key_is_available(self):
        env_file = Path.home() / ".openclaw" / "workspace" / ".env"
        if not env_file.exists():
            self.skipTest("OpenClaw .env is not available")
        has_key = any(
            line.strip().startswith("E2B_API_KEY=") and bool(line.split("=", 1)[1].strip())
            for line in env_file.read_text(encoding="utf-8").splitlines()
        )
        if not has_key:
            self.skipTest("E2B_API_KEY is not present in OpenClaw .env")
        payload = e2b_smoke(env_file)
        self.assertTrue(payload["success"], payload)
        self.assertTrue(payload["stdout_contains_expected_marker"])
        self.assertFalse(payload["raw_token_stored"])

    def test_cloud_rag_admission_encrypts_and_converts_to_lvfm_payload(self):
        key = generate_rag_key()["key"]
        admission = build_admission(
            "E2B normalized data",
            "Rows inspected in E2B. Admit only the stable feature summary.",
            "e2b://sandbox/result",
            tool_route="codex",
            tags=["e2b", "lvfm"],
        )
        envelope = encrypt_admission(admission, key=key)
        self.assertEqual(envelope["algorithm"], "fernet")
        self.assertNotIn("Rows inspected", envelope["ciphertext"])
        restored = decrypt_admission(envelope, key=key)
        self.assertEqual(restored["content_sha256"], admission["content_sha256"])
        runtime_payload = admission_to_runtime_payload(restored)
        self.assertEqual(runtime_payload["memories"][0]["modality"], "text")
        self.assertEqual(runtime_payload["memories"][0]["provenance"]["bridge"], "cloud-rag-to-lvfm")


class CerebrumRuntimeApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_dashboard_route_serves_local_panel(self):
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn("FNP-QNN Control Panel", response.text)
        self.assertIn("/dashboard/static/app.js", response.text)

    def test_runtime_status_endpoint(self):
        response = self.client.get("/cerebrum/runtime/status")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["bridge"], "operational")
        self.assertIn("state_store", payload)
        self.assertIn("persistence", payload)

    def test_runtime_ingest_endpoint(self):
        response = self.client.post("/cerebrum/runtime/ingest", json={})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertGreaterEqual(len(payload["events"]), 4)
        self.assertGreaterEqual(len(payload["pairs"]), 4)
        self.assertIn("persistence", payload)

    def test_runtime_run_endpoint(self):
        response = self.client.post("/cerebrum/runtime/run", json={"epochs": 4})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        runtime = body["runtime"]
        self.assertIn("bundle", runtime)
        self.assertIn("qnn_result", runtime)
        self.assertIn("benchmark", runtime)
        self.assertGreater(runtime["feature_dimension"], 0)
        self.assertIn("lvfm", runtime)
        self.assertIn("snapshot", runtime["lvfm"])
        self.assertIn("decision", runtime["lvfm"])
        self.assertIn("persistence", body)

    def test_runtime_run_accepts_qlc_gateway_mesh_payload(self):
        qlc_mesh_payload = {
            "memories": [
                {
                    "modality": "stimuli",
                    "starting_time": 0.0,
                    "ending_time": 1.0,
                    "value": 0.7,
                    "label": "qlc-container",
                    "source": "ffed-qlc-mvp",
                    "payload_ref": "asset-001",
                    "provenance": {
                        "bridge": "qlc-to-fnpqnn-gateway",
                        "qlc": {"container_sha256": "abc123", "raw_payload_exposed": False},
                    },
                }
            ],
            "label": 1.0,
            "epochs": 2,
            "run_qnn": True,
            "fractal_dimension": 1.4,
            "fractal_dimension_min": 1.0,
            "fractal_dimension_max": 2.0,
            "fractal_admissible": True,
            "plugin_hook_enabled": True,
            "plugin_set": "mvp5",
            "plugin_context": {
                "orchestrator": "CeLeBrUm",
                "runtime_memory_surface": "Cerebrum",
                "sensitivity_weighted_obfuscation_policy": {
                    "schema": "ffed.qlc.sensitivity_weighted_obfuscation_policy.v1",
                    "media_type": "image",
                    "sensitivity_level": "high",
                },
            },
            "cpai_context": {"route": "qlc-gateway-codeproject-fnpqnn", "mesh_enabled": True, "can_connect": True},
            "hydra_em_enabled": True,
            "gpcn_set_phi_enabled": True,
            "orch_or_simulation_enabled": True,
            "quasicrystal_projection_enabled": True,
            "microtubule_proxy_count": 4,
            "microtubule_coupling_strength": 0.5,
        }

        response = self.client.post("/cerebrum/runtime/run", json=qlc_mesh_payload)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        runtime = body["runtime"]
        self.assertIn("qnn_result", runtime)
        self.assertIn("hydra_em_gpcn", runtime)
        self.assertEqual(runtime["qlc_runtime"]["schema"], "ffed.qlc.runtime_normalized_context.v1")
        self.assertEqual(runtime["qlc_runtime"]["contract_version"], "qlc-wiring-contract.v2")
        self.assertEqual(runtime["qlc_runtime"]["swop_level"], "high")
        self.assertEqual(runtime["qlc_runtime"]["lvfm_metadata"]["bridge"], "qlc-gateway-to-cerebrum-runtime")
        self.assertFalse(runtime["qlc_runtime"]["raw_payload_embedded"])
        self.assertIn("plugin_hook_status", runtime["qnn_result"])
        self.assertIn("persistence", body)

    def test_runtime_run_accepts_shared_qlc_contract_fixture(self):
        fixture = Path(__file__).parent / "fixtures" / "qlc_contract" / "qlc_workflow_image.json"
        bundle = json.loads(fixture.read_text(encoding="utf-8"))
        mesh_payload = bundle["gateway_submission"]["mesh_payload"]

        response = self.client.post("/cerebrum/runtime/run", json=mesh_payload)

        self.assertEqual(response.status_code, 200)
        runtime = response.json()["runtime"]
        self.assertEqual(bundle["contract_version"], "qlc-wiring-contract.v2")
        self.assertEqual(bundle["gateway_submission"]["contract_version"], "qlc-wiring-contract.v2")
        self.assertEqual(runtime["qlc_runtime"]["media_type"], "image")
        self.assertEqual(runtime["qlc_runtime"]["contract_version"], "qlc-wiring-contract.v2")
        self.assertEqual(runtime["qlc_runtime"]["swop_level"], "high")
        self.assertIn("mesh_payload_fingerprint", runtime["qlc_runtime"])
        self.assertEqual(
            sorted(runtime["qlc_runtime"].keys()),
            [
                "contract_version",
                "detected",
                "lvfm_metadata",
                "media_type",
                "mesh_enabled",
                "mesh_payload_fingerprint",
                "orchestrator",
                "raw_payload_embedded",
                "recommended_chunk_mode",
                "runtime_memory_surface",
                "schema",
                "swop_level",
            ],
        )

    def test_runtime_run_rejects_raw_qlc_fields(self):
        response = self.client.post(
            "/cerebrum/runtime/run",
            json={
                "memories": [{"modality": "stimuli", "value": 0.5}],
                "plugin_context": {"raw_image": "not-allowed"},
            },
        )

        self.assertEqual(response.status_code, 422)

    def test_runtime_run_endpoint_accepts_plithogenic_opt_in(self):
        response = self.client.post(
            "/cerebrum/runtime/run",
            json={"epochs": 2, "plithogenic_enabled": True},
        )
        self.assertEqual(response.status_code, 200)
        runtime = response.json()["runtime"]
        self.assertIn("plithogenic", runtime)
        self.assertIn("plithogenic_fusion_profile", runtime["lvfm"])
        self.assertIn("plithogenic_fusion_profile", runtime["qnn_result"])
        self.assertTrue(all(0.0 <= item <= 1.0 for item in runtime["plithogenic"]["feature_vector"]))

    def test_plithogenic_runtime_profile_endpoint(self):
        response = self.client.post(
            "/fnp-qnn/plithogenic/runtime/profile",
            json={
                "memories": [
                    {"modality": "audio", "starting_time": 0.0, "ending_time": 1.0, "value": 0.2},
                    {"modality": "video", "starting_time": 0.2, "ending_time": 1.2, "value": 0.8},
                ]
            },
        )
        self.assertEqual(response.status_code, 200)
        profile = response.json()["profile"]
        self.assertEqual(profile["model"], "plithogenic_runtime_fusion_v1")
        self.assertEqual(profile["attribute_profile"]["attribute_count"], 2)
        self.assertTrue(all(0.0 <= item <= 1.0 for item in profile["feature_vector"]))

    def test_runtime_run_endpoint_accepts_revolutionary_topology_opt_in(self):
        response = self.client.post(
            "/cerebrum/runtime/run",
            json={"epochs": 2, "revolutionary_topology_enabled": True},
        )
        self.assertEqual(response.status_code, 200)
        runtime = response.json()["runtime"]
        self.assertIn("revolutionary_topology", runtime)
        self.assertIn("revolutionary_topology_profile", runtime["lvfm"])
        self.assertIn("revolutionary_topology_profile", runtime["qnn_result"])
        self.assertTrue(all(0.0 <= item <= 1.0 for item in runtime["revolutionary_topology"]["feature_vector"]))

    def test_revolutionary_topology_runtime_profile_endpoint(self):
        response = self.client.post(
            "/fnp-qnn/revolutionary-topology/runtime/profile",
            json={
                "memories": [
                    {"modality": "audio", "starting_time": 0.0, "ending_time": 1.0, "value": 0.2},
                    {"modality": "video", "starting_time": 0.2, "ending_time": 1.2, "value": 0.8},
                ]
            },
        )
        self.assertEqual(response.status_code, 200)
        profile = response.json()["profile"]
        self.assertEqual(profile["model"], "revolutionary_topology_runtime_v1")
        self.assertIn("deformation_signature", profile)
        self.assertTrue(all(0.0 <= item <= 1.0 for item in profile["feature_vector"]))

    def test_runtime_run_endpoint_accepts_plithogenic_topology_bridge(self):
        response = self.client.post(
            "/cerebrum/runtime/run",
            json={
                "epochs": 2,
                "plithogenic_enabled": True,
                "revolutionary_topology_enabled": True,
            },
        )
        self.assertEqual(response.status_code, 200)
        runtime = response.json()["runtime"]
        self.assertIn("plithogenic_topology", runtime)
        self.assertIn("plithogenic_topology_profile", runtime["lvfm"])
        self.assertIn("plithogenic_topology_profile", runtime["qnn_result"])
        self.assertTrue(all(0.0 <= item <= 1.0 for item in runtime["plithogenic_topology"]["feature_vector"]))

    def test_runtime_run_endpoint_accepts_plugin_stabilized_plithogenic_topology(self):
        response = self.client.post(
            "/cerebrum/runtime/run",
            json={
                "epochs": 2,
                "plithogenic_enabled": True,
                "revolutionary_topology_enabled": True,
                "plugin_hook_enabled": True,
                "plugin_context": {"series": [0.2, 0.4, 0.8], "steps": 120, "n_atoms": 8},
                "cpai_context": {"local_load": 0.9, "nodes_active": 2, "nodes_visible": 2},
            },
        )
        self.assertEqual(response.status_code, 200)
        runtime = response.json()["runtime"]
        self.assertIn("plugin_stabilization_profile", runtime["plithogenic_topology"])
        self.assertIn("plugin_stabilization_profile", runtime["lvfm"]["plithogenic_topology_profile"])
        self.assertIn("plugin_stabilization_profile", runtime["qnn_result"]["plithogenic_topology_profile"])

    def test_plithogenic_topology_runtime_profile_endpoint(self):
        response = self.client.post(
            "/fnp-qnn/plithogenic-topology/runtime/profile",
            json={
                "memories": [
                    {"modality": "audio", "starting_time": 0.0, "ending_time": 1.0, "value": 0.2},
                    {"modality": "video", "starting_time": 0.2, "ending_time": 1.2, "value": 0.8},
                ]
            },
        )
        self.assertEqual(response.status_code, 200)
        profile = response.json()["profile"]
        self.assertEqual(profile["model"], "plithogenic_probability_statistics_topology_wiring_v1")
        self.assertIn("topology_variable_completion", profile)
        self.assertTrue(all(0.0 <= item <= 1.0 for item in profile["feature_vector"]))

    def test_plithogenic_topology_runtime_profile_endpoint_accepts_plugin_hook(self):
        response = self.client.post(
            "/fnp-qnn/plithogenic-topology/runtime/profile",
            json={
                "plugin_hook_enabled": True,
                "plugin_context": {"series": [0.2, 0.4, 0.8], "steps": 120, "n_atoms": 8},
                "cpai_context": {"local_load": 0.9, "nodes_active": 2, "nodes_visible": 2},
                "memories": [
                    {"modality": "audio", "starting_time": 0.0, "ending_time": 1.0, "value": 0.2},
                    {"modality": "video", "starting_time": 0.2, "ending_time": 1.2, "value": 0.8},
                ],
            },
        )
        self.assertEqual(response.status_code, 200)
        profile = response.json()["profile"]
        self.assertIn("plugin_stabilization_profile", profile)
        self.assertIn("plithogenic_topology_load_profile", profile)
        self.assertFalse(profile["plithogenic_topology_load_profile"]["offload_performed"])

    def test_runtime_run_endpoint_accepts_neutro_algebra_opt_in(self):
        response = self.client.post(
            "/cerebrum/runtime/run",
            json={
                "epochs": 2,
                "plithogenic_enabled": True,
                "revolutionary_topology_enabled": True,
                "neutro_algebra_enabled": True,
            },
        )
        self.assertEqual(response.status_code, 200)
        runtime = response.json()["runtime"]
        self.assertIn("neutro_algebra", runtime)
        self.assertIn("structure_system_profile", runtime["neutro_algebra"])
        self.assertIn("neutro_algebra_profile", runtime["lvfm"])
        self.assertIn("neutro_structure_profile", runtime["lvfm"])
        self.assertIn("neutro_algebra_profile", runtime["qnn_result"])
        self.assertIn("neutro_structure_profile", runtime["qnn_result"])
        self.assertTrue(all(0.0 <= item <= 1.0 for item in runtime["neutro_algebra"]["feature_vector"]))

    def test_neutro_algebra_profile_endpoint(self):
        response = self.client.post(
            "/fnp-qnn/neutro-algebra/profile",
            json={
                "plithogenic_enabled": True,
                "revolutionary_topology_enabled": True,
                "memories": [
                    {"modality": "audio", "starting_time": 0.0, "ending_time": 1.0, "value": 0.2},
                    {"modality": "video", "starting_time": 0.2, "ending_time": 1.2, "value": 0.8},
                ],
            },
        )
        self.assertEqual(response.status_code, 200)
        profile = response.json()["profile"]
        self.assertEqual(profile["model"], "neutroalgebra_structure_profile_v1")
        self.assertIn("operation_profiles", profile)
        self.assertIn("structure_system_profile", profile)
        self.assertIn("T_system", profile["structure_system_profile"])
        self.assertIn("I_system", profile["structure_system_profile"])
        self.assertIn("F_system", profile["structure_system_profile"])
        self.assertTrue(all(0.0 <= item <= 1.0 for item in profile["feature_vector"]))

    def test_runtime_latest_state_endpoint(self):
        run_response = self.client.post("/cerebrum/runtime/run", json={"epochs": 3})
        self.assertEqual(run_response.status_code, 200)

        latest_response = self.client.get("/cerebrum/runtime/state/latest")
        self.assertEqual(latest_response.status_code, 200)
        payload = latest_response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertIsNotNone(payload["record"])
        self.assertEqual(payload["record"]["key"], "/runtime/run/latest")
        self.assertEqual(payload["record"]["payload"]["status"], "ok")

    def test_legacy_runtime_demo_endpoint(self):
        response = self.client.get("/cerebrum/runtime/legacy-demo")
        self.assertEqual(response.status_code, 200)
        runtime = response.json()["runtime"]
        self.assertTrue(runtime["legacy_cerebrum_path_exists"])
        self.assertGreaterEqual(len(runtime["events"]), 1)
        self.assertGreaterEqual(len(runtime["pairs"]), 1)

    def test_cloud_kit_status_endpoint(self):
        response = self.client.get("/cloud-kit/status")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertIn("rag_encryption", payload)

    def test_cloud_rag_runtime_endpoint_feeds_lvfm(self):
        response = self.client.post(
            "/cloud-kit/rag/runtime",
            json={
                "title": "Gateway RAG summary",
                "content": "External source was normalized in the cloud kit and admitted as a small RAG note.",
                "source": "e2b://sandbox/result",
                "tool_route": "openclaw",
                "tags": ["e2b", "rag", "lvfm"],
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["runtime_payload"]["memories"][0]["provenance"]["bridge"], "cloud-rag-to-lvfm")
        self.assertIn("lvfm", payload["runtime"])
        self.assertIn("persistence", payload)

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

    def test_execute_command_legacy_demo_route(self):
        response = self.client.post(
            "/execute-command",
            json={"command": "cerebrum-runtime-legacy-demo"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["type"], "cerebrum-runtime")
        self.assertTrue(payload["data"]["legacy_cerebrum_path_exists"])

    def test_execute_command_rejects_shell_commands(self):
        response = self.client.post(
            "/execute-command",
            json={"command": "python --version"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["type"], "error")

    def test_runtime_rejects_non_finite_payload(self):
        response = self.client.post(
            "/cerebrum/runtime/run",
            content='{"memories": [{"modality": "audio", "starting_time": "NaN", "ending_time": 1.0, "value": 0.2}]}',
            headers={"content-type": "application/json"},
        )
        self.assertEqual(response.status_code, 422)

    def test_runtime_rejects_inverted_time_payload(self):
        response = self.client.post(
            "/cerebrum/runtime/run",
            json={"memories": [{"modality": "audio", "starting_time": 2.0, "ending_time": 1.0, "value": 0.2}]},
        )
        self.assertEqual(response.status_code, 422)

    def test_legacy_fixture_exists(self):
        fixture = Path(__file__).resolve().parent.parent / "examples" / "legacy_cerebrum_snapshot.json"
        self.assertTrue(fixture.exists())

    def test_multiverse_experiments_runtime_layer_is_opt_in(self):
        bridge = CerebrumRuntimeBridge()
        default_state = bridge.build_state(None)
        enabled_state = bridge.build_state(
            None,
            multiverse_experiments_enabled=True,
            multiverse_experiment_ids=["deutsch_quantum_computation_origin"],
            multiverse_experiment_shots=128,
        )

        self.assertIsNone(default_state.multiverse_experiments)
        self.assertNotIn("multiverse_experiments", default_state.to_dict())
        self.assertIsNotNone(enabled_state.multiverse_experiments)
        self.assertIn("multiverse_experiments", enabled_state.to_dict())
        self.assertIn("multiverse_experiments_profile", enabled_state.lvfm)
        self.assertEqual(enabled_state.multiverse_experiments["experiment_count"], 1)
        self.assertTrue(all(0.0 <= item <= 1.0 for item in enabled_state.multiverse_experiments["feature_vector"]))

    def test_multiverse_experiments_features_reach_qnn_when_enabled(self):
        bridge = CerebrumRuntimeBridge()
        nucleus = QNNNucleus(adapter=bridge.adapter)
        state = bridge.build_state(
            None,
            qnn_nucleus=nucleus,
            max_epochs=2,
            multiverse_experiments_enabled=True,
            multiverse_experiment_ids=["deutsch_quantum_computation_origin"],
            multiverse_experiment_shots=128,
        )

        self.assertIsNotNone(state.qnn_result)
        self.assertIn("multiverse_experiments_profile", state.qnn_result)
        self.assertEqual(
            state.qnn_result["multiverse_experiments_profile"]["feature_dimension"],
            state.multiverse_experiments["feature_dimension"],
        )

    def test_runtime_endpoint_accepts_multiverse_opt_in(self):
        response = self.client.post(
            "/cerebrum/runtime/run",
            json={
                "epochs": 2,
                "multiverse_experiments_enabled": True,
                "multiverse_experiment_ids": ["deutsch_quantum_computation_origin"],
                "multiverse_experiment_shots": 128,
            },
        )
        self.assertEqual(response.status_code, 200)
        runtime = response.json()["runtime"]
        self.assertIn("multiverse_experiments", runtime)
        self.assertIn("multiverse_experiments_profile", runtime["lvfm"])
        self.assertIn("multiverse_experiments_profile", runtime["qnn_result"])

    def test_time_physics_experiments_runtime_layer_is_opt_in(self):
        bridge = CerebrumRuntimeBridge()
        default_state = bridge.build_state(None)
        enabled_state = bridge.build_state(
            None,
            time_physics_experiments_enabled=True,
            time_physics_experiment_ids=["manifest_vs_physical_time_flow"],
            time_physics_experiment_shots=128,
        )

        self.assertIsNone(default_state.time_physics_experiments)
        self.assertNotIn("time_physics_experiments", default_state.to_dict())
        self.assertIsNotNone(enabled_state.time_physics_experiments)
        self.assertIn("time_physics_experiments", enabled_state.to_dict())
        self.assertIn("time_physics_experiments_profile", enabled_state.lvfm)
        self.assertEqual(enabled_state.time_physics_experiments["experiment_count"], 1)
        self.assertTrue(all(0.0 <= item <= 1.0 for item in enabled_state.time_physics_experiments["feature_vector"]))

    def test_time_physics_experiments_features_reach_qnn_when_enabled(self):
        bridge = CerebrumRuntimeBridge()
        nucleus = QNNNucleus(adapter=bridge.adapter)
        state = bridge.build_state(
            None,
            qnn_nucleus=nucleus,
            max_epochs=2,
            time_physics_experiments_enabled=True,
            time_physics_experiment_ids=["entanglement_decoherence_arrow"],
            time_physics_experiment_shots=128,
        )

        self.assertIsNotNone(state.qnn_result)
        self.assertIn("time_physics_experiments_profile", state.qnn_result)
        self.assertEqual(
            state.qnn_result["time_physics_experiments_profile"]["feature_dimension"],
            state.time_physics_experiments["feature_dimension"],
        )
        self.assertIn(
            "ALKHALILI_CHEN_DECOHERENT_ARROW_2024",
            state.qnn_result["time_physics_experiments_profile"]["source_ids"],
        )

    def test_runtime_endpoint_accepts_time_physics_opt_in(self):
        response = self.client.post(
            "/cerebrum/runtime/run",
            json={
                "epochs": 2,
                "time_physics_experiments_enabled": True,
                "time_physics_experiment_ids": ["manifest_vs_physical_time_flow"],
                "time_physics_experiment_shots": 128,
            },
        )
        self.assertEqual(response.status_code, 200)
        runtime = response.json()["runtime"]
        self.assertIn("time_physics_experiments", runtime)
        self.assertIn("time_physics_experiments_profile", runtime["lvfm"])
        self.assertIn("time_physics_experiments_profile", runtime["qnn_result"])


if __name__ == "__main__":
    unittest.main()
