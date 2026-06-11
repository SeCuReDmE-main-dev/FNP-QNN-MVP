import unittest

import numpy as np

from core.cerebrum_adapter import CerebrumAdapter
from core.qnn_nucleus import QNNNucleus


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
