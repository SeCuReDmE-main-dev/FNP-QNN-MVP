import unittest
from pathlib import Path

from core.hydra_em_gpcn_math import (
    VERDICTS,
    anesthesia_sweep_profile,
    gpcn_set_phi_profile,
    hydra_em_gpcn_orch_profile,
    quasicrystal_gpcn_projection_profile,
)


class HydraEMGPCNMathTests(unittest.TestCase):
    def test_gpcn_set_phi_admits_only_fractal_local_source(self):
        admitted = gpcn_set_phi_profile(
            local_point_count=8,
            d_f=1.5,
            d_min=1.0,
            d_max=2.0,
            i_system_source="fractal_projection",
        )
        suspended = gpcn_set_phi_profile(
            local_point_count=8,
            d_f=1.5,
            d_min=1.0,
            d_max=2.0,
            i_system_source="semantic_ambiguity",
        )

        self.assertEqual(admitted["Adm"], "admitted")
        self.assertAlmostEqual(admitted["D_f_hat"], 0.5)
        self.assertEqual(admitted["i_fractal_candidate"], admitted["D_f_hat"])
        self.assertEqual(suspended["Adm"], "suspended")
        self.assertIsNone(suspended["i_fractal_candidate"])
        self.assertIn("GPCN-Set_phi", admitted["axiom"])

    def test_quasicrystal_projection_is_seed_deterministic(self):
        left = quasicrystal_gpcn_projection_profile(seed=7, proxy_count=5, coupling_strength=0.8)
        right = quasicrystal_gpcn_projection_profile(seed=7, proxy_count=5, coupling_strength=0.8)

        self.assertEqual(left["points"], right["points"])
        self.assertEqual(left["feature_dimension"], len(left["feature_vector"]))
        self.assertTrue(all(0.0 <= item <= 1.0 for item in left["feature_vector"]))

    def test_orch_profile_returns_bounded_verdict_and_gpcn_container(self):
        profile = hydra_em_gpcn_orch_profile(
            [],
            [],
            microtubule_proxy_count=6,
            microtubule_coupling_strength=0.85,
            anesthetic_damping=0.05,
            coherence_time_s=1.0,
            objective_reduction_energy_joule=1.054571817e-34,
            microtubule_frequency_hz=100000000.0,
            quasicrystal_projection_enabled=True,
        )

        self.assertIn(profile["verdict"], VERDICTS)
        self.assertEqual(profile["axiomatic_container"]["model"], "gpcn_set_phi_chamber_v1")
        self.assertEqual(profile["feature_dimension"], len(profile["feature_vector"]))
        self.assertTrue(all(0.0 <= item <= 1.0 for item in profile["feature_vector"]))
        self.assertIn("not biological", profile["research_boundary"])

    def test_anesthesia_sweep_reduces_simulated_communication(self):
        sweep = anesthesia_sweep_profile(
            [],
            [],
            damping_values=[0.0, 0.25, 0.5, 0.75],
            microtubule_proxy_count=6,
            microtubule_coupling_strength=0.85,
            coherence_time_s=1.0,
            objective_reduction_energy_joule=1.054571817e-34,
            microtubule_frequency_hz=100000000.0,
        )

        self.assertTrue(sweep["monotonic_nonincreasing_communication"])
        self.assertGreaterEqual(sweep["communication_scores"][0], sweep["communication_scores"][-1])
        self.assertEqual(sweep["feature_dimension"], len(sweep["feature_vector"]))

    def test_source_guardrail_contains_hydra_em_rows(self):
        guardrail = Path(__file__).resolve().parent.parent / "docs" / "source_ledger" / "math_function_source_guardrail.md"
        text = guardrail.read_text(encoding="utf-8")

        self.assertIn("hydra_em_gpcn_orch_profile()", text)
        self.assertIn("GPCN-Set_phi", text)


if __name__ == "__main__":
    unittest.main()
