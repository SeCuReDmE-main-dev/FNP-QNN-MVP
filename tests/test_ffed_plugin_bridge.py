import unittest
from pathlib import Path

from core.ffed_plugin_bridge import FfeDPluginBridge, MVP5_PLUGIN_IDS, build_plugin_payload_from_results


class FfeDPluginBridgeTests(unittest.TestCase):
    def test_fixture_mapping_is_bounded_and_preserves_hierarchy(self):
        payload = build_plugin_payload_from_results(
            {
                "p011_fractales_atomiques": {
                    "status": "success",
                    "outputs": {"overload_risk": 0.7, "recomposition_score": 0.4},
                    "metrics": {"overload_risk": 0.7, "recomposition_score": 0.4},
                },
                "p046_rossler_beaulieu_cubic_framework": {
                    "status": "success",
                    "outputs": {"anti_entropy": {"balance": -0.2}},
                    "metrics": {"chaos_risk": 0.5, "divergence_index": 0.25, "anti_entropy_balance": -0.2},
                },
                "p097_fbm_tuner": {
                    "status": "success",
                    "outputs": {"classification": "watch"},
                    "metrics": {"instability_score": 0.62},
                },
                "p109_dual_triplex": {
                    "status": "success",
                    "outputs": {"summary": {"fractal_density": 0.9}},
                    "metrics": {"truth": 0.2, "falsehood": 1.6, "fractal_density": 0.9},
                },
                "p114_ffed_neutrosophic_consensus": {
                    "status": "success",
                    "outputs": {"consensus": {"truth": 0.55, "indeterminacy": 0.35, "falsity": 0.10}},
                    "metrics": {"truth": 0.55, "indeterminacy": 0.35, "falsity": 0.10},
                },
            },
            status={"effective_configs": {}},
            cpai_state=None,
        )

        self.assertTrue(payload["impact_verification"]["all_expected_plugins_seen"])
        self.assertEqual(payload["impact_verification"]["observed_plugins"], list(MVP5_PLUGIN_IDS))
        self.assertIsNotNone(payload["plugin_fractal_carrier"])
        self.assertGreaterEqual(payload["plugin_fractal_carrier"]["D_f_hat_plugin"], 0.0)
        self.assertLessEqual(payload["plugin_fractal_carrier"]["D_f_hat_plugin"], 1.0)
        self.assertIn("I -> I_system^S -> D_f -> dF -> i_fractal", payload["plugin_fractal_carrier"]["hierarchy"])
        self.assertIn("I_system_component", payload["plugin_gate_profile"])
        self.assertEqual(payload["cpai_mesh_profile"]["base"], "CPAI mesh")
        self.assertTrue(payload["cpai_mesh_profile"]["native"])
        self.assertIn("cpai.mesh.nodes_active", payload["cpai_mesh_profile"]["datadog_metrics"])

    def test_missing_pluginpack_is_non_blocking(self):
        bridge = FfeDPluginBridge(pluginpack_path=Path("__missing_pluginpack_for_test__"))
        payload = bridge.run_mvp5({"series": [0.1, 0.2]})

        self.assertFalse(payload["impact_verification"]["activated"])
        self.assertEqual(payload["plugin_fractal_signals"], [])
        self.assertTrue(payload["plugin_errors"])
        self.assertFalse(payload["plugin_hook_status"]["enabled"])
        self.assertEqual(payload["impact_verification"]["cpai_mesh_base"]["base"], "CPAI mesh")

    def test_status_reports_datadog_cpai_contract_without_secrets(self):
        status = FfeDPluginBridge().status()

        self.assertIn("cpai_mesh_profile", status)
        self.assertEqual(status["cpai_mesh_profile"]["datadog_dashboard_id"], "4i9-v3n-pe7")
        self.assertEqual(status["observability"]["datadog_mesh_notebook_id"], "293549")
        self.assertFalse(status["observability"]["secrets_exposed"])

    def test_p114_consensus_runs_as_cli_admission_gate(self):
        payload = FfeDPluginBridge().run_p114_consensus(
            [
                "verified evidence passed with implementation proof",
                "partial risk remains pending",
            ]
        )
        if payload["status"] == "disabled":
            self.skipTest(payload["metadata"].get("message", "p114 pluginpack disabled"))
        self.assertTrue(payload["success"], payload)
        self.assertEqual(payload["plugin_id"], "p114_ffed_neutrosophic_consensus")
        self.assertIn(payload["action"], {"ask_clarification", "escalate_or_reject", "respond_with_confidence", "respond_with_caveat"})
        self.assertIn("allow_lvfm_admission", payload["cli_gate"])
        self.assertFalse(payload["raw_token_stored"])


if __name__ == "__main__":
    unittest.main()
