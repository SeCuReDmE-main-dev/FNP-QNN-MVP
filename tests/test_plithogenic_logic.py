import unittest

from core.plithogenic_logic import (
    plithogenic_attribute_profile,
    plithogenic_contradiction_degree,
    plithogenic_neutrosophic_conjunction,
    plithogenic_runtime_fusion_profile,
    plithogenic_weighted_cumulative_truth,
)


class PlithogenicLogicTests(unittest.TestCase):
    def test_multi_attribute_profile_preserves_one_profile_per_event(self):
        profile = plithogenic_attribute_profile(
            [
                {"modality": "audio", "value": 0.2, "timestamp": 0.0, "weight": 1.0},
                {"modality": "video", "value": 0.8, "timestamp": 0.2, "weight": 3.0},
            ]
        )

        self.assertEqual(profile["attribute_count"], 2)
        self.assertEqual([item["variable"] for item in profile["attributes"]], ["V1", "V2"])
        self.assertAlmostEqual(sum(item["normalized_weight"] for item in profile["attributes"]), 1.0)

    def test_triplet_values_remain_bounded(self):
        profile = plithogenic_attribute_profile(
            [{"modality": "audio", "value": 4.0, "timestamp": 0.0, "duration": 12.0}]
        )
        attribute = profile["attributes"][0]

        for key in ("truth", "indeterminacy", "falsity"):
            self.assertGreaterEqual(attribute[key], 0.0)
            self.assertLessEqual(attribute[key], 1.0)
        self.assertEqual(attribute["hierarchy_components"]["i_fractal"], None)

    def test_contradiction_increases_when_truth_values_diverge(self):
        left = {"attribute_id": "V1", "modality": "audio", "truth": 0.45, "indeterminacy": 0.1, "falsity": 0.55}
        close = {"attribute_id": "V2", "modality": "video", "truth": 0.50, "indeterminacy": 0.1, "falsity": 0.50}
        far = {"attribute_id": "V3", "modality": "video", "truth": 0.95, "indeterminacy": 0.1, "falsity": 0.05}

        close_profile = plithogenic_contradiction_degree(left, close, overlap_score=1.0)
        far_profile = plithogenic_contradiction_degree(left, far, overlap_score=1.0)

        self.assertGreater(far_profile["contradiction_degree"], close_profile["contradiction_degree"])
        self.assertLessEqual(far_profile["contradiction_degree"], 1.0)

    def test_neutrosophic_conjunction_uses_min_max_max(self):
        result = plithogenic_neutrosophic_conjunction(
            [
                {"truth": 0.8, "indeterminacy": 0.2, "falsity": 0.1},
                {"truth": 0.3, "indeterminacy": 0.5, "falsity": 0.6},
                {"truth": 0.7, "indeterminacy": 0.1, "falsity": 0.4},
            ]
        )

        self.assertEqual(result["T"], 0.3)
        self.assertEqual(result["I"], 0.5)
        self.assertEqual(result["F"], 0.6)

    def test_weighted_cumulative_truth_changes_when_weights_change(self):
        low_truth_heavy = plithogenic_weighted_cumulative_truth(
            [
                {"truth": 0.2, "indeterminacy": 0.1, "falsity": 0.8, "weight": 5.0},
                {"truth": 0.9, "indeterminacy": 0.1, "falsity": 0.1, "weight": 1.0},
            ]
        )
        high_truth_heavy = plithogenic_weighted_cumulative_truth(
            [
                {"truth": 0.2, "indeterminacy": 0.1, "falsity": 0.8, "weight": 1.0},
                {"truth": 0.9, "indeterminacy": 0.1, "falsity": 0.1, "weight": 5.0},
            ]
        )

        self.assertGreater(high_truth_heavy["T"], low_truth_heavy["T"])

    def test_runtime_fusion_profile_returns_bounded_feature_vector_and_trace(self):
        profile = plithogenic_runtime_fusion_profile(
            [
                {"modality": "audio", "value": 0.1, "timestamp": 0.0, "ending_time": 1.0},
                {"modality": "video", "value": 0.9, "timestamp": 0.1, "ending_time": 1.1},
            ],
            [
                {
                    "direction": "H2V",
                    "source_modality": "audio",
                    "target_modality": "video",
                    "timestamp1": 0.0,
                    "timestamp2": 0.1,
                    "overlap_score": 0.8,
                }
            ],
        )

        self.assertEqual(profile["feature_dimension"], len(profile["feature_vector"]))
        self.assertTrue(profile["pairwise_contradictions"])
        self.assertTrue(all(0.0 <= item <= 1.0 for item in profile["feature_vector"]))


if __name__ == "__main__":
    unittest.main()
