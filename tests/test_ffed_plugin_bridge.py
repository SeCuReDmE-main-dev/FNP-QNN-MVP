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
        )

        self.assertTrue(payload["impact_verification"]["all_expected_plugins_seen"])
        self.assertEqual(payload["impact_verification"]["observed_plugins"], list(MVP5_PLUGIN_IDS))
        self.assertIsNotNone(payload["plugin_fractal_carrier"])
        self.assertGreaterEqual(payload["plugin_fractal_carrier"]["D_f_hat_plugin"], 0.0)
        self.assertLessEqual(payload["plugin_fractal_carrier"]["D_f_hat_plugin"], 1.0)
        self.assertIn("I -> I_system^S -> D_f -> dF -> i_fractal", payload["plugin_fractal_carrier"]["hierarchy"])
        self.assertIn("I_system_component", payload["plugin_gate_profile"])

    def test_missing_pluginpack_is_non_blocking(self):
        bridge = FfeDPluginBridge(pluginpack_path=Path("__missing_pluginpack_for_test__"))
        payload = bridge.run_mvp5({"series": [0.1, 0.2]})

        self.assertFalse(payload["impact_verification"]["activated"])
        self.assertEqual(payload["plugin_fractal_signals"], [])
        self.assertTrue(payload["plugin_errors"])
        self.assertFalse(payload["plugin_hook_status"]["enabled"])


if __name__ == "__main__":
    unittest.main()
