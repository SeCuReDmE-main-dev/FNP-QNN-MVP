import unittest


class PanelAppTests(unittest.TestCase):
    def test_panel_app_builds_without_serving(self):
        import panel_app

        app = panel_app.create_app()
        self.assertEqual(app.title, "FNP-QNN Control Room")
        self.assertGreaterEqual(len(app.main), 2)
        self.assertGreaterEqual(len(app.sidebar), 2)

    def test_panel_actions_execute_runtime_paths(self):
        import panel_app

        payload = dict(panel_app.DEFAULT_PAYLOAD)
        payload["epochs"] = 2
        runtime = panel_app.run_panel_simulation(payload)
        self.assertGreaterEqual(len(runtime["events"]), 4)
        self.assertGreaterEqual(len(runtime["pairs"]), 4)
        self.assertIn("benchmark", runtime)

        encoded = panel_app.encode_panel_payload(payload)
        self.assertGreater(encoded["feature_dimension"], 0)

        neurobit_gates = panel_app.run_panel_neurobit_gates(
            {"truth": 0.55, "indeterminacy": 0.3, "falsity": 0.15, "delta_falsity": 0.05}
        )
        self.assertEqual(neurobit_gates["status"], "ok")
        self.assertEqual(neurobit_gates["profile"]["delta_falsity"], 0.05)

        neurobit_tunnel = panel_app.run_panel_neurobit_tunnel(
            {"truth": 0.55, "indeterminacy": 0.3, "falsity": 0.15},
            data="panel",
        )
        self.assertEqual(neurobit_tunnel["status"], "ok")
        self.assertIn("noise_preview", neurobit_tunnel)

        legacy = panel_app.legacy_panel_replay()
        self.assertTrue(legacy["legacy_cerebrum_path_exists"])


if __name__ == "__main__":
    unittest.main()
