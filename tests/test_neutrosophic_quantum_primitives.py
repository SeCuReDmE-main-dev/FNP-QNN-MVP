import unittest

import numpy as np

from core.neutrosophic_quantum_primitives import (
    CoherentNeutroState,
    DecoherentNeutroState,
    NeutrobitState,
    fractal_carrier_profile,
    neutrobit_features_from_vector,
    neutrosophic_gate_algebra,
    neutrosophic_measurement,
    normalize_fractal_dimension,
    observer_effect_profile,
    partial_entanglement_profile,
    punctured_surface_state,
    punctured_wave_state,
)


class NeutrosophicQuantumPrimitiveTests(unittest.TestCase):
    def test_neutrobit_state_normalizes_probabilities(self):
        state = NeutrobitState.from_tif(truth=2.0, indeterminacy=1.0, falsity=1.0)
        probabilities = state.probabilities()
        self.assertAlmostEqual(sum(probabilities.values()), 1.0)
        self.assertAlmostEqual(probabilities["one"], 0.5)
        self.assertAlmostEqual(probabilities["indeterminate"], 0.25)
        self.assertAlmostEqual(probabilities["zero"], 0.25)

    def test_coherent_state_decoheres_to_triplet_measurement(self):
        coherent = CoherentNeutroState(NeutrobitState.from_tif(0.5, 0.25, 0.25))
        decoherent = coherent.decohere()
        self.assertIsInstance(decoherent, DecoherentNeutroState)

        measurement = neutrosophic_measurement(coherent)
        self.assertEqual(measurement["measurement"], "non_projective_triplet")
        self.assertAlmostEqual(measurement["T"], 0.5)
        self.assertAlmostEqual(measurement["I"], 0.25)
        self.assertAlmostEqual(measurement["F"], 0.25)

    def test_invalid_neutrobit_inputs_raise(self):
        with self.assertRaises(ValueError):
            NeutrobitState.from_probabilities(zero=-0.1, one=1.0, indeterminate=0.0)
        with self.assertRaises(ValueError):
            NeutrobitState(zero=complex(float("nan"), 0.0))

    def test_punctured_wave_state_is_deterministic_and_bounded(self):
        wave_a = punctured_wave_state(delta=0.25, length=1.0)
        wave_b = punctured_wave_state(delta=0.25, length=1.0)
        self.assertEqual(wave_a, wave_b)
        self.assertEqual(wave_a["count"], 5)
        self.assertEqual(wave_a["positions"][0], 0.0)
        self.assertLessEqual(wave_a["positions"][-1], 1.0)
        self.assertAlmostEqual(float(np.linalg.norm(wave_a["amplitudes"])), 1.0)

    def test_punctured_wave_zero_length_and_invalid_delta(self):
        empty = punctured_wave_state(delta=0.1, length=0.0)
        self.assertEqual(empty["count"], 0)
        self.assertEqual(empty["positions"], [])
        with self.assertRaises(ValueError):
            punctured_wave_state(delta=0.0, length=1.0)

    def test_partial_entanglement_profile_maps_to_tif(self):
        profile = partial_entanglement_profile(correlation=0.8, decoherence=0.1, delta_falsity=0.1)
        self.assertEqual(profile["model"], "partial_entanglement_tif_profile")
        self.assertAlmostEqual(profile["T"] + profile["I"] + profile["F"], 1.0)
        self.assertGreater(profile["T"], profile["F"])
        self.assertGreater(profile["I"], 0.0)

    def test_neutrobit_feature_expansion_is_finite(self):
        features = neutrobit_features_from_vector([0.1, 0.5, 0.9], puncture_delta=0.1)
        self.assertGreaterEqual(features.shape[0], 11)
        self.assertTrue(np.isfinite(features).all())

    def test_normalize_fractal_dimension_is_bounded(self):
        self.assertAlmostEqual(normalize_fractal_dimension(1.5, 1.0, 2.0), 0.5)
        self.assertAlmostEqual(normalize_fractal_dimension(1.0, 1.0, 2.0), 0.0)
        self.assertAlmostEqual(normalize_fractal_dimension(2.0, 1.0, 2.0), 1.0)
        self.assertAlmostEqual(normalize_fractal_dimension(0.5, 1.0, 2.0), 0.0)
        self.assertAlmostEqual(normalize_fractal_dimension(2.5, 1.0, 2.0), 1.0)

    def test_normalize_fractal_dimension_rejects_invalid_bounds(self):
        with self.assertRaises(ValueError):
            normalize_fractal_dimension(1.5, 1.0, 1.0)
        with self.assertRaises(ValueError):
            normalize_fractal_dimension(float("nan"), 1.0, 2.0)

    def test_fractal_carrier_profile_preserves_hierarchy(self):
        profile = fractal_carrier_profile(
            1.5,
            1.0,
            2.0,
            system="S",
            measurement_method="box-counting-provided",
            scale="alpha-local",
            domain="unit-test",
        )
        self.assertAlmostEqual(profile["D_f_hat"], 0.5)
        self.assertAlmostEqual(profile["i_fractal_candidate"], 0.5)
        self.assertEqual(profile["hierarchy"], "I -> I_system^S -> D_f -> dF -> i_fractal")
        self.assertIn("not identical to I", profile["interpretation"])

    def test_fractal_carrier_profile_can_mark_context_inadmissible(self):
        profile = fractal_carrier_profile(1.5, 1.0, 2.0, admissible=False)
        self.assertFalse(profile["admissible"])
        self.assertIsNone(profile["D_f_hat"])
        self.assertIsNone(profile["i_fractal_candidate"])

    def test_neutrobit_features_accept_fractal_carrier_without_replacing_legacy(self):
        baseline = neutrobit_features_from_vector([0.1, 0.5, 0.9])
        enriched = neutrobit_features_from_vector(
            [0.1, 0.5, 0.9],
            fractal_dimension=1.5,
            fractal_dimension_min=1.0,
            fractal_dimension_max=2.0,
        )
        self.assertEqual(enriched.shape[0], baseline.shape[0] + 3)
        self.assertTrue(np.isfinite(enriched).all())

    def test_neutrosophic_gate_not_swaps_truth_and_falsity(self):
        result = neutrosophic_gate_algebra("not", {"T": 0.7, "I": 0.2, "F": 0.1})
        self.assertAlmostEqual(result["T"], 0.1)
        self.assertAlmostEqual(result["I"], 0.2)
        self.assertAlmostEqual(result["F"], 0.7)

    def test_neutrosophic_gate_binary_ops_are_bounded(self):
        left = {"T": 0.8, "I": 0.1, "F": 0.1}
        right = {"T": 0.2, "I": 0.3, "F": 0.5}
        for operation in ("and", "or", "if_then"):
            with self.subTest(operation=operation):
                result = neutrosophic_gate_algebra(operation, left, right)
                self.assertAlmostEqual(result["T"] + result["I"] + result["F"], 1.0)
                self.assertTrue(0.0 <= result["T"] <= 1.0)
                self.assertTrue(0.0 <= result["I"] <= 1.0)
                self.assertTrue(0.0 <= result["F"] <= 1.0)

    def test_neutrosophic_gate_if_then_keeps_indeterminacy(self):
        result = neutrosophic_gate_algebra(
            "if_then",
            {"T": 0.1, "I": 0.3, "F": 0.6},
            {"T": 0.4, "I": 0.4, "F": 0.2},
        )
        self.assertGreater(result["I"], 0.0)
        self.assertAlmostEqual(result["T"] + result["I"] + result["F"], 1.0)

    def test_neutrosophic_gate_invalid_inputs_raise(self):
        with self.assertRaises(ValueError):
            neutrosophic_gate_algebra("xor", {"T": 1.0, "I": 0.0, "F": 0.0})
        with self.assertRaises(ValueError):
            neutrosophic_gate_algebra("and", {"T": float("nan"), "I": 0.0, "F": 0.0}, {"T": 1.0})

    def test_punctured_surface_state_is_deterministic_and_bounded(self):
        surface_a = punctured_surface_state(delta=0.5, width=1.0, height=1.0)
        surface_b = punctured_surface_state(delta=0.5, width=1.0, height=1.0)
        self.assertEqual(surface_a, surface_b)
        self.assertEqual(surface_a["count"], 9)
        self.assertEqual(surface_a["points"][0], {"x": 0.0, "y": 0.0})
        self.assertLessEqual(surface_a["points"][-1]["x"], 1.0)
        self.assertLessEqual(surface_a["points"][-1]["y"], 1.0)
        self.assertAlmostEqual(float(np.linalg.norm(surface_a["amplitudes"])), 1.0)

    def test_punctured_surface_empty_and_invalid_inputs(self):
        empty = punctured_surface_state(delta=0.25, width=0.0, height=1.0)
        self.assertEqual(empty["count"], 0)
        self.assertEqual(empty["points"], [])
        with self.assertRaises(ValueError):
            punctured_surface_state(delta=0.0, width=1.0, height=1.0)
        with self.assertRaises(ValueError):
            punctured_surface_state(
                delta=0.5,
                width=1.0,
                height=1.0,
                density_fn=lambda _x, _y: float("nan"),
            )

    def test_observer_effect_preserves_and_then_increases_indeterminacy(self):
        state = {"T": 0.6, "I": 0.2, "F": 0.2}
        baseline = observer_effect_profile(state, observer_strength=0.0)
        observed = observer_effect_profile(state, observer_strength=1.0)
        self.assertAlmostEqual(baseline["T"], 0.6)
        self.assertAlmostEqual(baseline["I"], 0.2)
        self.assertAlmostEqual(baseline["F"], 0.2)
        self.assertGreater(observed["I"], baseline["I"])
        self.assertAlmostEqual(observed["T"] + observed["I"] + observed["F"], 1.0)


if __name__ == "__main__":
    unittest.main()
