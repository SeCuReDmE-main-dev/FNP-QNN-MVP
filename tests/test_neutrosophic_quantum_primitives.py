import unittest

import numpy as np

from core.neutrosophic_quantum_primitives import (
    CoherentNeutroState,
    DecoherentNeutroState,
    NeutrobitState,
    neutrobit_features_from_vector,
    neutrosophic_measurement,
    partial_entanglement_profile,
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


if __name__ == "__main__":
    unittest.main()
