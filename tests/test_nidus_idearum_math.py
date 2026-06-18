import unittest

from core.nidus_idearum_math import (
    partial_membership_mean,
    source_weighted_triplet_fusion,
    triplet_quality_profile,
)


class NidusIdearumMathTests(unittest.TestCase):
    def test_triplet_quality_profile_is_bounded(self):
        profile = triplet_quality_profile(0.6, 0.3, 0.2)

        self.assertEqual(profile["model"], "nidus_idearum_triplet_quality")
        self.assertGreaterEqual(profile["score"], -1.0)
        self.assertLessEqual(profile["score"], 1.0)
        for key in ("accuracy", "certainty", "positiveness", "negativeness"):
            self.assertGreaterEqual(profile[key], 0.0)
            self.assertLessEqual(profile[key], 1.0)
        self.assertGreater(profile["overdefined_load"], 0.0)
        self.assertIn("dynamic triplet", profile["interpretation"])

    def test_source_fusion_preserves_incomplete_indeterminacy(self):
        fusion = source_weighted_triplet_fusion(
            [
                {"T": 0.5, "I": 0.1, "F": 0.1, "beta": 2.0},
                {"T": 0.1, "I": 0.2, "F": 0.6, "intersection_indeterminacy": 0.3},
            ]
        )

        components = fusion["components"]
        self.assertEqual(fusion["model"], "nidus_idearum_source_weighted_triplet_fusion")
        self.assertGreater(components["incomplete_model_component"], 0.0)
        self.assertGreater(components["indeterminate_intersection_component"], 0.0)
        self.assertGreater(
            components["I_system_component"],
            components["base_indeterminacy"],
        )
        self.assertEqual(fusion["hierarchy"], "I -> I_system^S -> D_f -> dF -> i_fractal")

    def test_partial_membership_mean_supports_under_equal_and_over_membership(self):
        result = partial_membership_mean(
            values=[2.0, 8.0, 5.0, 11.0],
            memberships=[1.1, 0.4, 1.0, 0.3],
        )

        self.assertEqual(result["model"], "nidus_idearum_partial_membership_mean")
        self.assertTrue(result["has_overset_membership"])
        self.assertTrue(result["has_underset_membership"])
        self.assertGreater(result["over_membership_load"], 0.0)
        self.assertGreater(result["under_membership_load"], 0.0)
        self.assertNotEqual(result["classical_mean"], result["partial_membership_mean"])

    def test_partial_membership_mean_rejects_invalid_lengths(self):
        with self.assertRaises(ValueError):
            partial_membership_mean([1.0, 2.0], [1.0])


if __name__ == "__main__":
    unittest.main()
