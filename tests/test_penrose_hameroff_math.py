import unittest
from pathlib import Path

from core.penrose_hameroff_math import (
    HBAR_JOULE_SECOND,
    microtubule_signal_profile,
    objective_reduction_profile,
    orchestration_profile,
    penrose_hameroff_runtime_profile,
    spin_network_admissibility_profile,
    twistor_nonlocality_profile,
)


class PenroseHameroffMathTests(unittest.TestCase):
    def test_objective_reduction_uses_hbar_over_energy(self):
        energy = HBAR_JOULE_SECOND * 10.0
        profile = objective_reduction_profile(energy, reference_time_s=0.2)

        self.assertEqual(profile["model"], "penrose_objective_reduction_v1")
        self.assertAlmostEqual(profile["tau_s"], 0.1)
        self.assertTrue(profile["finite_reduction_threshold"])
        self.assertTrue(profile["reference_meets_threshold"])
        self.assertAlmostEqual(profile["reduction_pressure"], 1.0)
        self.assertIn("hbar / E_delta", profile["interpretation"])

    def test_objective_reduction_marks_non_positive_energy_as_no_finite_threshold(self):
        profile = objective_reduction_profile(0.0, reference_time_s=1.0)

        self.assertIsNone(profile["tau_s"])
        self.assertFalse(profile["finite_reduction_threshold"])
        self.assertFalse(profile["reference_meets_threshold"])
        self.assertEqual(profile["feature_vector"][0], 0.0)

    def test_objective_reduction_rejects_non_finite_input(self):
        with self.assertRaises(ValueError):
            objective_reduction_profile(float("nan"))

    def test_orchestration_profile_is_bounded_and_not_a_consciousness_claim(self):
        profile = orchestration_profile(coherence_time_s=2.0, reduction_time_s=1.0, damping=0.25)

        self.assertEqual(profile["classification"], "coherence_meets_or_threshold")
        self.assertTrue(profile["coherence_meets_threshold"])
        self.assertTrue(all(0.0 <= item <= 1.0 for item in profile["feature_vector"]))
        self.assertIn("not a consciousness claim", profile["interpretation"])

    def test_spin_network_admissibility_checks_parity_and_triangle_rules(self):
        profile = spin_network_admissibility_profile(
            [
                [1.0, 1.0, 1.0],
                [1.0, 1.0, 3.0],
                [0.5, 0.5, 0.5],
            ]
        )

        self.assertEqual(profile["vertex_count"], 3)
        self.assertEqual(profile["admissible_count"], 1)
        self.assertAlmostEqual(profile["admissible_fraction"], 1.0 / 3.0)
        self.assertFalse(profile["vertices"][1]["triangle_admissible"])
        self.assertFalse(profile["vertices"][2]["parity_admissible"])

    def test_spin_network_rejects_non_half_integer_labels(self):
        with self.assertRaises(ValueError):
            spin_network_admissibility_profile([[0.2, 0.5, 0.5]])

    def test_twistor_and_microtubule_profiles_are_bounded_metadata(self):
        twistor = twistor_nonlocality_profile(0.8, 0.6, {"curvature": 0.4})
        microtubule = microtubule_signal_profile(
            frequency_hz=1e8,
            diffusion_nm=250.0,
            anesthetic_damping=0.5,
        )

        self.assertTrue(all(0.0 <= item <= 1.0 for item in twistor["feature_vector"]))
        self.assertTrue(all(0.0 <= item <= 1.0 for item in microtubule["feature_vector"]))
        self.assertIn("not biological validation", microtubule["interpretation"])

    def test_runtime_profile_combines_bounded_feature_vector(self):
        profile = penrose_hameroff_runtime_profile(
            [],
            [],
            objective_reduction_energy_joule=HBAR_JOULE_SECOND,
            coherence_time_s=1.0,
            anesthetic_damping=0.1,
            microtubule_frequency_hz=1e8,
            spin_network_vertices=[[1.0, 1.0, 1.0]],
        )

        self.assertEqual(profile["model"], "penrose_hameroff_runtime_profile_v1")
        self.assertEqual(profile["feature_dimension"], len(profile["feature_vector"]))
        self.assertTrue(all(0.0 <= item <= 1.0 for item in profile["feature_vector"]))
        self.assertEqual(profile["hierarchy"], "I -> I_system^S -> D_f -> dF -> i_fractal")
        self.assertIn("not a consciousness proof", profile["research_boundary"])

    def test_source_guardrail_contains_penrose_hameroff_rows(self):
        guardrail = Path(__file__).resolve().parent.parent / "docs" / "source_ledger" / "math_function_source_guardrail.md"
        text = guardrail.read_text(encoding="utf-8")

        self.assertIn("PENROSE_GRAVITY_REDUCTION_1996", text)
        self.assertIn("HAMEROFF_PENROSE_ORCH_OR_2014", text)
        self.assertIn("penrose_hameroff_runtime_profile()", text)


if __name__ == "__main__":
    unittest.main()
