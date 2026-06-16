import unittest

import numpy as np

from core.neurobit_gates import (
    NeutrosophicGateProfile,
    build_neutrosophic_gate_sequence,
    gate_matrix,
    to_torchquantum_ops,
)


class NeuroBitGatesContractTests(unittest.TestCase):
    def test_agents_contract_names_are_available(self):
        profile = NeutrosophicGateProfile(0.6, 0.2, 0.2, delta_falsity=0.05)
        self.assertEqual(profile.normalized().metadata["delta_falsity"], 0.05)
        self.assertEqual(build_neutrosophic_gate_sequence(profile), ["hadamard", "w", "x", "y", "z"])

    def test_public_gate_matrices_are_unitary(self):
        for name in ("hadamard", "w", "x", "y", "z"):
            matrix = gate_matrix(name)
            np.testing.assert_allclose(matrix @ np.conjugate(matrix.T), np.eye(2), atol=1e-12)

    def test_torchquantum_ops_are_plain_descriptors(self):
        ops = to_torchquantum_ops(NeutrosophicGateProfile(0.6, 0.2, 0.2), [0, 1, 2])
        self.assertEqual(ops[0], ("h", 0, ()))
        self.assertTrue(all(isinstance(item, tuple) and len(item) == 3 for item in ops))


if __name__ == "__main__":
    unittest.main()
