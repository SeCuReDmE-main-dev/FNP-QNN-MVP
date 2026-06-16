import unittest

from core.experiment_seed import ExperimentSeedManager


class ExperimentSeedManagerTests(unittest.TestCase):
    def test_seed_sequence_is_deterministic(self):
        a = ExperimentSeedManager(base_seed=42, current_seed=42)
        b = ExperimentSeedManager(base_seed=42, current_seed=42)
        self.assertEqual([a.get_next_seed() for _ in range(3)], [b.get_next_seed() for _ in range(3)])

    def test_register_experiment_records_seed(self):
        manager = ExperimentSeedManager()
        seed = manager.register_experiment("neurobit-demo", seed=123)
        self.assertEqual(seed, 123)
        self.assertEqual(manager.get_experiment_seed("neurobit-demo"), 123)
        self.assertEqual(manager.get_state_summary()["experiment_count"], 1)

    def test_invalid_seed_and_name_are_rejected(self):
        with self.assertRaises(ValueError):
            ExperimentSeedManager(base_seed=-1)
        with self.assertRaises(ValueError):
            ExperimentSeedManager().register_experiment("")


if __name__ == "__main__":
    unittest.main()
