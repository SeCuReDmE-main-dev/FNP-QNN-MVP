import unittest

import numpy as np

from core.cerebrum_adapter import CerebrumAdapter
from core.qnn_nucleus import QISKIT_AVAILABLE, QNNNucleus


class CerebrumQNNTests(unittest.TestCase):
    def test_adapter_produces_fixed_vector(self):
        adapter = CerebrumAdapter()
        vector = adapter.to_feature_vector(adapter.default_observations())
        self.assertEqual(vector.ndim, 1)
        self.assertGreater(vector.size, 20)
        self.assertTrue(np.isfinite(vector).all())

    def test_candidate_matrix_contains_primary_qnn_and_fallback(self):
        nucleus = QNNNucleus()
        candidates = {candidate.name for candidate in nucleus.candidate_matrix()}
        self.assertIn("qiskit_estimator_qnn", candidates)
        self.assertIn("torch_surrogate", candidates)

    def test_surrogate_smoke_run_is_stable(self):
        nucleus = QNNNucleus()
        result = nucleus.fit_surrogate(
            [nucleus.adapter.default_observations(), nucleus.adapter.default_observations()],
            [0, 1],
            max_epochs=12,
            test_size=0.0,
        )
        self.assertEqual(result["backend"], "torch_surrogate")
        self.assertTrue(0.0 <= result["predicted_probability"] <= 1.0)
        self.assertGreaterEqual(result["train_accuracy"], 0.0)
        self.assertLessEqual(result["train_accuracy"], 1.0)

    def test_surrogate_smoke_run_is_reproducible(self):
        nucleus_a = QNNNucleus()
        nucleus_b = QNNNucleus()
        samples = [nucleus_a.adapter.default_observations(), nucleus_a.adapter.default_observations()]
        labels = [0, 1]
        result_a = nucleus_a.fit_surrogate(samples, labels, max_epochs=8, test_size=0.0)
        result_b = nucleus_b.fit_surrogate(samples, labels, max_epochs=8, test_size=0.0)
        self.assertEqual(result_a["backend"], result_b["backend"])
        self.assertEqual(result_a["feature_dimension"], result_b["feature_dimension"])
        self.assertAlmostEqual(result_a["predicted_probability"], result_b["predicted_probability"], places=6)

    def test_smoke_run_prefers_qiskit_or_fallback(self):
        nucleus = QNNNucleus()
        result = nucleus.smoke_run(nucleus.adapter.default_observations(), label=1.0, max_epochs=4, test_size=0.0)
        self.assertIn("backend", result)
        if QISKIT_AVAILABLE:
            self.assertIn(result["backend"], {"qiskit_torchconnector", "torch_surrogate_fallback_after_qiskit_error"})
        else:
            self.assertEqual(result["backend"], "torch_surrogate")

    def test_neutrobit_basis_expands_feature_vector_when_requested(self):
        nucleus = QNNNucleus()
        events = nucleus.adapter.default_observations()
        binary = nucleus.fit_surrogate([events], [1], max_epochs=2, test_size=0.0)
        neutrobit = nucleus.fit_surrogate(
            [events],
            [1],
            max_epochs=2,
            test_size=0.0,
            state_basis="neutrobit",
            puncture_delta=0.25,
            observer_strength=0.5,
        )
        self.assertEqual(binary["state_basis"], "binary")
        self.assertEqual(neutrobit["state_basis"], "neutrobit")
        self.assertGreater(neutrobit["feature_dimension"], binary["feature_dimension"])
        self.assertEqual(neutrobit["puncture_delta"], 0.25)
        self.assertEqual(neutrobit["observer_strength"], 0.5)

    def test_benchmark_returns_entries_for_all_candidates(self):
        nucleus = QNNNucleus()
        benchmark = nucleus.benchmark(
            [nucleus.adapter.default_observations(), nucleus.adapter.default_observations()],
            [0, 1],
        )
        self.assertGreaterEqual(len(benchmark), 4)
        self.assertTrue(any(item.candidate == "torch_surrogate" and item.available for item in benchmark))


if __name__ == "__main__":
    unittest.main()
