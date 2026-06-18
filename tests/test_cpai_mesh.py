import unittest

from core.cpai_mesh import CPAIMeshState, cpai_mesh_profile


class CPAIMeshTests(unittest.TestCase):
    def test_default_state_is_native_local_mesh(self):
        state = CPAIMeshState()
        payload = state.as_dict()

        self.assertTrue(payload["native"])
        self.assertEqual(payload["base"], "CPAI mesh")
        self.assertEqual(payload["routing_decision"], "process_local")
        self.assertFalse(payload["secrets_exposed"])

    def test_high_local_load_with_active_nodes_marks_forward_candidate(self):
        state = CPAIMeshState.from_context(
            {
                "nodes_visible": 3,
                "nodes_active": 3,
                "local_load": 0.82,
                "can_connect": True,
            }
        )

        self.assertTrue(state.should_forward)
        self.assertEqual(state.routing_decision, "forward_candidate")

    def test_profile_exposes_datadog_metric_contract(self):
        profile = cpai_mesh_profile({"nodes_active": 2, "local_load": 0.2})

        self.assertEqual(profile["base"], "CPAI mesh")
        self.assertIn("cpai.mesh.nodes_active", profile["datadog_metrics"])
        self.assertEqual(profile["datadog_dashboard_id"], "4i9-v3n-pe7")
        self.assertEqual(profile["datadog_notebook_id"], "293549")


if __name__ == "__main__":
    unittest.main()
