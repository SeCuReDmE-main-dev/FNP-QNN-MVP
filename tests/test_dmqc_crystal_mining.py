import unittest

from core.dmqc_crystal_mining import (
    DMQC_DEFINITION,
    convex_hull_proxy,
    load_dmqc_library,
    pca_correlation_profile,
    pls_energy_profile,
    run_dmqc_prediction,
)


class DMQCCrystalMiningTests(unittest.TestCase):
    def test_fixture_bridge_returns_bounded_feature_profile(self):
        profile = run_dmqc_prediction()

        self.assertEqual(profile["dmqc_definition"], DMQC_DEFINITION)
        self.assertEqual(profile["feature_dimension"], len(profile["feature_vector"]))
        self.assertTrue(all(0.0 <= item <= 1.0 for item in profile["feature_vector"]))
        self.assertIn("not DFT", profile["forbidden_claims"])
        self.assertIn("not validated material discovery", profile["research_boundary"])

    def test_pca_pls_and_hull_profiles_are_consistent(self):
        records = load_dmqc_library()
        pca = pca_correlation_profile(records)
        pls = pls_energy_profile(records)
        hull = convex_hull_proxy(records, records[-1])

        self.assertEqual(pca["feature_dimension"], len(pca["feature_vector"]))
        self.assertEqual(pls["feature_dimension"], len(pls["feature_vector"]))
        self.assertEqual(hull["feature_dimension"], len(hull["feature_vector"]))
        self.assertIn(hull["classification"], {
            "stable_or_low_proxy_distance",
            "metastable_proxy_window",
            "high_proxy_distance_suspended",
        })


if __name__ == "__main__":
    unittest.main()
