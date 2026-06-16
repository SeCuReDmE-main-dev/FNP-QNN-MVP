import unittest

import numpy as np

from core.quantum_feature_transforms import (
    complex_wavefunction_to_amplitude_phase_features,
    structure_vector_to_phi_scaled_state,
)


class QuantumFeatureTransformTests(unittest.TestCase):
    def test_complex_wavefunction_to_amplitude_phase_features(self):
        features = complex_wavefunction_to_amplitude_phase_features([1 + 0j, 0 + 1j])
        self.assertEqual(features.shape, (4,))
        np.testing.assert_allclose(features[:2], np.array([1.0, 1.0]), atol=1e-6)

    def test_structure_vector_to_phi_scaled_state_is_normalized(self):
        state = structure_vector_to_phi_scaled_state([0.2, 0.4, 0.8])
        self.assertEqual(state.shape, (3,))
        self.assertAlmostEqual(float(np.linalg.norm(state)), 1.0, places=6)

    def test_empty_inputs_are_safe(self):
        self.assertEqual(complex_wavefunction_to_amplitude_phase_features([]).size, 0)
        self.assertEqual(structure_vector_to_phi_scaled_state([]).size, 0)


if __name__ == "__main__":
    unittest.main()
