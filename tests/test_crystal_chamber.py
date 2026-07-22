import unittest

from core.crystal_chamber import (
    CRYSTAL_CHAIN,
    FRACTAL_CHAIN,
    crystal_chamber_admission_profile,
    crystal_chamber_status,
)
from core.crystal_growth_fractal_profile import (
    branch_drift_profile,
    crystal_growth_window_profile,
    fractal_dimension_proxy,
    growth_rate_profile,
)


class CrystalChamberTests(unittest.TestCase):
    def test_crystal_chain_is_separate_from_optional_fractal_chain(self):
        profile = crystal_chamber_admission_profile({
            "branch_drift": 0.2,
            "surface_roughness": 0.15,
            "defect_density": 0.1,
            "phase_stability_margin": 0.85,
        })

        self.assertEqual(profile["crystal_chain"], CRYSTAL_CHAIN)
        self.assertEqual(profile["fractal_chain"], FRACTAL_CHAIN)
        self.assertIsNone(profile["i_fractal"])
        self.assertIn("i_crystal is not automatically i_fractal", profile["forbidden_claims"])
        self.assertEqual(profile["feature_dimension"], len(profile["feature_vector"]))

    def test_fractal_line_is_admitted_only_when_payload_requests_it(self):
        profile = crystal_chamber_admission_profile({
            "fractal_dimension_Df": 1.5,
            "fractal_admissible": True,
        })

        self.assertIsNotNone(profile["fractal_carrier"])
        self.assertAlmostEqual(profile["fractal_carrier"]["D_f_hat"], 0.5)
        self.assertAlmostEqual(profile["i_fractal"], 0.5)
        self.assertNotEqual(profile["i_crystal"], profile["i_fractal"])

    def test_near_chaotic_growth_is_suspended_not_falsity(self):
        profile = crystal_chamber_admission_profile({
            "growth_rate": 0.95,
            "branch_drift": 0.82,
            "surface_roughness": 0.72,
            "defect_density": 0.68,
            "phase_stability_margin": 0.34,
        })

        self.assertEqual(profile["Adm"], "suspended")
        self.assertEqual(profile["classification"], "near-chaotic suspended crystal growth state")
        self.assertIn("suspended is not falsity", profile["forbidden_claims"])

    def test_growth_helpers_return_bounded_vectors(self):
        rate = growth_rate_profile([0, 1, 2, 3], [0.0, 0.4, 0.9, 1.1])
        drift = branch_drift_profile([[1, 0], [0.8, 0.2], [-0.2, 1.0]], [1, 0])
        fractal = fractal_dimension_proxy([[0, 0], [0.5, 0.5], [1.0, 1.0], [0.25, 0.75]])
        window = crystal_growth_window_profile(
            growth_rate=0.4,
            branch_drift=drift["branch_drift"],
            surface_roughness=0.2,
            defect_density=0.1,
            phase_stability_margin=0.9,
        )

        for profile in (rate, drift, fractal, window):
            self.assertEqual(profile["feature_dimension"], len(profile["feature_vector"]))
            self.assertTrue(all(0.0 <= item <= 1.0 for item in profile["feature_vector"]))

    def test_status_lists_nine_variables(self):
        status = crystal_chamber_status()

        self.assertEqual(status["feature"], "crystal-chamber")
        self.assertEqual(len(status["variables"]), 9)
        self.assertEqual(status["near_chaos_state"], "near-chaotic suspended crystal growth state")


if __name__ == "__main__":
    unittest.main()
