import unittest

import numpy as np

from core.neurobit_gate_tunnel import (
    NeuroBitProfile,
    build_gate_parameters,
    build_neurobit_gate_sequence,
    counts_to_expectation_vector,
    gate_matrix,
    run_neurobit_gates,
    run_neurobit_tunnel_demo,
)


class NeuroBitGateTunnelTests(unittest.TestCase):
    def test_gate_matrices_are_unitary(self):
        for gate_name in ("hadamard", "w", "x", "y", "z"):
            with self.subTest(gate=gate_name):
                matrix = gate_matrix(gate_name)
                product = matrix @ np.conjugate(matrix.T)
                np.testing.assert_allclose(product, np.eye(2, dtype=complex), atol=1e-12)

    def test_profile_normalizes_and_preserves_delta_falsity(self):
        profile = NeuroBitProfile(truth=2.0, indeterminacy=1.0, falsity=1.0, delta_falsity=0.42).normalized()
        self.assertAlmostEqual(profile.truth + profile.indeterminacy + profile.falsity, 1.0)
        self.assertAlmostEqual(profile.delta_falsity, 0.42)
        self.assertEqual(profile.metadata["delta_falsity"], 0.42)

    def test_gate_sequence_is_deterministic(self):
        profile = NeuroBitProfile(truth=0.6, indeterminacy=0.2, falsity=0.2)
        self.assertEqual(build_neurobit_gate_sequence(profile), ["hadamard", "w", "x", "y", "z"])
        self.assertEqual(build_neurobit_gate_sequence(profile), build_neurobit_gate_sequence(profile))

    def test_parameters_and_expectation_vector_are_bounded(self):
        profile = NeuroBitProfile(truth=0.55, indeterminacy=0.30, falsity=0.15)
        params = build_gate_parameters(profile)
        self.assertIn("theta_x", params)
        self.assertIn("delta_falsity", params)

        values = counts_to_expectation_vector({"00": 5, "11": 5}, n_qubits=2, shots=10)
        np.testing.assert_allclose(values, np.array([0.0, 0.0], dtype=float))

    def test_gate_run_returns_fallback_safe_payload(self):
        result = run_neurobit_gates(NeuroBitProfile())
        self.assertEqual(result["status"], "ok")
        self.assertIn(result["backend"], {"deterministic_fallback", "qiskit_qasm_simulator"})
        self.assertEqual(result["hierarchy"], "I -> I_system^S -> D_f -> dF -> i_fractal")
        self.assertIn("w", result["gate_matrices"])
        self.assertEqual(len(result["expectation_vector"]), 4)
        self.assertEqual(result["neutrobit_measurement"]["measurement"], "non_projective_triplet")
        self.assertIn("partial_entanglement", result)
        self.assertIn("gate_semantics", result)
        self.assertIn("reversibility_profile", result)
        self.assertIn("gate_algebra_preview", result)

    def test_neutrobit_basis_can_emit_punctured_wave_metadata(self):
        profile = NeuroBitProfile(
            truth=0.55,
            indeterminacy=0.30,
            falsity=0.15,
            state_basis="neutrobit",
            puncture_delta=0.25,
            observer_strength=0.5,
            surface_width=0.5,
            surface_height=0.5,
        )
        result = run_neurobit_gates(profile, n_qubits=4)
        self.assertEqual(result["state_basis"], "neutrobit")
        self.assertIsNotNone(result["punctured_wave"])
        self.assertEqual(result["punctured_wave"]["delta"], 0.25)
        self.assertIsNotNone(result["punctured_surface"])
        self.assertEqual(result["punctured_surface"]["count"], 9)
        self.assertIsNotNone(result["observer_effect"])
        self.assertGreater(result["observer_effect"]["I"], result["neutrobit_measurement"]["I"])

    def test_tunnel_demo_is_research_bounded(self):
        result = run_neurobit_tunnel_demo(NeuroBitProfile(), data="abc")
        self.assertEqual(result["status"], "ok")
        self.assertIn("not encryption", result["research_boundary"])
        self.assertGreater(result["sequence_id"], 0)
        self.assertGreaterEqual(len(result["noise_preview"]), 3)


if __name__ == "__main__":
    unittest.main()
