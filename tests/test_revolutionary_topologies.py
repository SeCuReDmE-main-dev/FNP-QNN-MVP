import unittest

from core.revolutionary_topologies import (
    deformation_invariant_signature,
    nonstandard_neighborhood_profile,
    refined_topology_components,
    revolutionary_topology_runtime_profile,
    topological_axiom_profile,
)


class RevolutionaryTopologiesTests(unittest.TestCase):
    def test_axiom_profile_distinguishes_classical_neutro_and_anti_cases(self):
        classical = topological_axiom_profile(["a", "b"], [[], ["a"], ["b"], ["a", "b"]])
        neutro = topological_axiom_profile(["a", "b"], [[], ["a"], ["b"]])
        anti = topological_axiom_profile(["a", "b"], [["a"]])

        self.assertEqual(classical["classification"], "CT")
        self.assertEqual(classical["CT"], 1.0)
        self.assertEqual(neutro["classification"], "NCT")
        self.assertEqual(anti["classification"], "ACT")
        self.assertGreater(anti["ACT"], neutro["ACT"])

    def test_refined_components_preserve_multiple_tif_subcomponents(self):
        profile = refined_topology_components(
            [
                {"modality": "audio", "value": 0.2, "timestamp": 0.0, "ending_time": 1.0, "source": "s1"},
                {"modality": "video", "value": 1.2, "timestamp": 0.1, "ending_time": 1.1, "source": "s2"},
                {"modality": "text", "value": -0.2, "timestamp": 0.2, "ending_time": 1.2, "label": "repeat"},
                {"modality": "stimuli", "value": 0.5, "timestamp": 0.3, "ending_time": 1.3, "label": "repeat"},
            ],
            [{"overlap_score": 0.8}],
        )

        self.assertGreaterEqual(len(profile["T_components"]), 3)
        self.assertGreaterEqual(len(profile["I_components"]), 5)
        self.assertGreaterEqual(len(profile["F_components"]), 2)
        self.assertIn("D_f", profile["I_components"])
        self.assertIn("dF", profile["I_components"])
        self.assertIn("i_fractal", profile["I_components"])

    def test_nonstandard_binad_neighborhood_accepts_left_and_right_near_values(self):
        left = nonstandard_neighborhood_profile(0.95, 1.0, epsilon=0.1, mode="binad")
        right = nonstandard_neighborhood_profile(1.05, 1.0, epsilon=0.1, mode="binad")
        far = nonstandard_neighborhood_profile(1.3, 1.0, epsilon=0.1, mode="binad")

        self.assertTrue(left["in_neighborhood"])
        self.assertTrue(right["in_neighborhood"])
        self.assertFalse(far["in_neighborhood"])
        self.assertGreater(left["membership"], far["membership"])

    def test_deformation_signature_changes_when_cycle_rank_changes(self):
        events = [
            {"modality": "audio", "timestamp": 0.0, "value": 0.1},
            {"modality": "video", "timestamp": 0.1, "value": 0.2},
            {"modality": "text", "timestamp": 0.2, "value": 0.3},
        ]
        chain = [
            {"source_modality": "audio", "target_modality": "video", "timestamp1": 0.0, "timestamp2": 0.1},
            {"source_modality": "video", "target_modality": "text", "timestamp1": 0.1, "timestamp2": 0.2},
        ]
        triangle = chain + [
            {"source_modality": "text", "target_modality": "audio", "timestamp1": 0.2, "timestamp2": 0.0},
        ]

        chain_signature = deformation_invariant_signature(events, chain)
        triangle_signature = deformation_invariant_signature(events, triangle)

        self.assertEqual(chain_signature["node_count"], triangle_signature["node_count"])
        self.assertEqual(chain_signature["connected_components"], triangle_signature["connected_components"])
        self.assertLess(chain_signature["cycle_rank"], triangle_signature["cycle_rank"])
        self.assertGreater(chain_signature["deformation_stability"], triangle_signature["deformation_stability"])

    def test_runtime_profile_keeps_multiset_and_over_under_off_metadata_bounded(self):
        profile = revolutionary_topology_runtime_profile(
            [
                {"modality": "audio", "value": 1.4, "timestamp": 0.0, "ending_time": 1.0, "label": "same"},
                {"modality": "video", "value": 0.4, "timestamp": 0.2, "ending_time": 1.2, "label": "same"},
                {"modality": "text", "value": -0.2, "timestamp": 0.4, "ending_time": 1.4},
            ],
            [
                {
                    "direction": "H2V",
                    "source_modality": "audio",
                    "target_modality": "video",
                    "timestamp1": 0.0,
                    "timestamp2": 0.2,
                    "overlap_score": 0.9,
                }
            ],
        )

        refined = profile["refined_components"]
        self.assertEqual(profile["feature_dimension"], len(profile["feature_vector"]))
        self.assertTrue(all(0.0 <= item <= 1.0 for item in profile["feature_vector"]))
        self.assertEqual(refined["over_under_off"]["over_count"], 1)
        self.assertEqual(refined["over_under_off"]["off_count"], 1)
        self.assertGreater(refined["multiset_recurrence"]["recurrence_load"], 0.0)


if __name__ == "__main__":
    unittest.main()
