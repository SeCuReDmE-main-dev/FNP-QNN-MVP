import unittest

from core.plithogenic_logic import plithogenic_runtime_fusion_profile
from core.plithogenic_probability_statistics import (
    plithogenic_multi_to_uni_decision,
    plithogenic_probability_family_profile,
    plithogenic_topology_wiring_profile,
    plithogenic_variate_sample_profile,
    refined_plithogenic_statistical_components,
)
from core.revolutionary_topologies import revolutionary_topology_runtime_profile


class PlithogenicProbabilityStatisticsTests(unittest.TestCase):
    def setUp(self):
        self.events = [
            {"modality": "audio", "value": 0.2, "timestamp": 0.0, "ending_time": 1.0, "weight": 1.0},
            {"modality": "video", "value": 0.8, "timestamp": 0.2, "ending_time": 1.2, "weight": 2.0},
            {"modality": "text", "value": 0.5, "timestamp": 0.4, "ending_time": 1.4, "weight": 0.5},
        ]
        self.pairs = [
            {
                "direction": "H2V",
                "source_modality": "audio",
                "target_modality": "video",
                "timestamp1": 0.0,
                "timestamp2": 0.2,
                "overlap_score": 0.8,
            }
        ]

    def test_sample_profile_keeps_probabilities_and_statistics_bounded(self):
        profile = plithogenic_variate_sample_profile(self.events)

        self.assertEqual(profile["sample_size"], 3)
        self.assertGreater(profile["partial_membership_load"], 0.0)
        for key in ("known_size_score", "modality_coverage", "value_mean", "value_variance"):
            self.assertGreaterEqual(profile[key], 0.0)
            self.assertLessEqual(profile[key], 1.0)

    def test_probability_family_profile_is_bounded(self):
        plithogenic = plithogenic_runtime_fusion_profile(self.events, self.pairs)
        profile = plithogenic_probability_family_profile(plithogenic)

        self.assertEqual(profile["attribute_count"], 3)
        self.assertIn("probability", profile["dominant_family"])
        for key in (
            "empirical_truth_probability",
            "empirical_indeterminate_probability",
            "empirical_false_probability",
        ):
            self.assertGreaterEqual(profile[key], 0.0)
            self.assertLessEqual(profile[key], 1.0)

    def test_refined_statistics_preserve_tif_subcomponents(self):
        plithogenic = plithogenic_runtime_fusion_profile(self.events, self.pairs)
        topology = revolutionary_topology_runtime_profile(self.events, self.pairs)
        refined = refined_plithogenic_statistical_components(plithogenic, topology)

        self.assertGreaterEqual(len(refined["T_components"]), 3)
        self.assertGreaterEqual(len(refined["I_components"]), 5)
        self.assertGreaterEqual(len(refined["F_components"]), 3)
        self.assertIn("D_f", refined["I_components"])
        self.assertIn("dF", refined["I_components"])
        self.assertIn("i_fractal", refined["I_components"])

    def test_statistical_confidence_increases_with_coherent_sample(self):
        coherent_events = [
            {"modality": "audio", "value": 0.5, "timestamp": 0.0, "ending_time": 1.0},
            {"modality": "video", "value": 0.52, "timestamp": 0.2, "ending_time": 1.2},
            {"modality": "text", "value": 0.51, "timestamp": 0.4, "ending_time": 1.4},
        ]
        divergent_events = [
            {"modality": "audio", "value": 0.0, "timestamp": 0.0, "ending_time": 1.0},
            {"modality": "video", "value": 1.0, "timestamp": 0.2, "ending_time": 1.2},
            {"modality": "text", "value": 0.0, "timestamp": 0.4, "ending_time": 1.4},
        ]
        coherent = plithogenic_topology_wiring_profile(
            coherent_events,
            self.pairs,
            plithogenic_runtime_fusion_profile(coherent_events, self.pairs),
            revolutionary_topology_runtime_profile(coherent_events, self.pairs),
        )
        divergent = plithogenic_topology_wiring_profile(
            divergent_events,
            self.pairs,
            plithogenic_runtime_fusion_profile(divergent_events, self.pairs),
            revolutionary_topology_runtime_profile(divergent_events, self.pairs),
        )

        self.assertGreater(coherent["statistical_confidence"], divergent["statistical_confidence"])
        self.assertGreater(
            divergent["refined_statistical_components"]["I_components"]["I2_truth_variance_load"],
            coherent["refined_statistical_components"]["I_components"]["I2_truth_variance_load"],
        )

    def test_multi_to_uni_conjunction_uses_min_max_max(self):
        decision = plithogenic_multi_to_uni_decision(
            [
                {"truth": 0.8, "indeterminacy": 0.2, "falsity": 0.1},
                {"truth": 0.3, "indeterminacy": 0.5, "falsity": 0.6},
                {"truth": 0.7, "indeterminacy": 0.1, "falsity": 0.4},
            ]
        )

        self.assertEqual(decision["T"], 0.3)
        self.assertEqual(decision["I"], 0.5)
        self.assertEqual(decision["F"], 0.6)

    def test_wiring_profile_returns_bounded_topology_completion(self):
        profile = plithogenic_topology_wiring_profile(
            self.events,
            self.pairs,
            plithogenic_runtime_fusion_profile(self.events, self.pairs),
            revolutionary_topology_runtime_profile(self.events, self.pairs),
        )

        self.assertEqual(profile["feature_dimension"], len(profile["feature_vector"]))
        self.assertTrue(all(0.0 <= item <= 1.0 for item in profile["feature_vector"]))
        self.assertIn("topology_class_probability", profile["topology_variable_completion"])
        self.assertIn("deformation_equivalence_probability", profile["topology_variable_completion"])


if __name__ == "__main__":
    unittest.main()
