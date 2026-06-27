"""Focused tests for the Quantum Paradoxes multiverse experiment suite."""

from __future__ import annotations

import json
import math
import unittest

from core.multiverse_experiments import (
    MULTIVERSE_EXPERIMENT_IDS,
    MultiverseExperimentConfig,
    multiverse_experiments_status,
    run_all_multiverse_experiments,
    run_multiverse_experiment,
)


class MultiverseExperimentsTests(unittest.TestCase):
    def test_every_lane_returns_stable_model_source_ids_and_features(self):
        for experiment_id in MULTIVERSE_EXPERIMENT_IDS:
            profile = run_multiverse_experiment(MultiverseExperimentConfig(experiment_id=experiment_id))
            self.assertEqual(profile["model"], "fnp_qnn_multiverse_experiment_profile_v1")
            self.assertEqual(profile["experiment_id"], experiment_id)
            self.assertIn("RI_QUANTUM_PARADOXES_MULTIVERSE_2026", profile["source_ids"])
            self.assertEqual(profile["feature_dimension"], len(profile["feature_vector"]))
            self.assertEqual(profile["feature_dimension"], 8)
            self.assertTrue(all(math.isfinite(item) and 0.0 <= item <= 1.0 for item in profile["feature_vector"]))
            self.assertEqual(profile["hierarchy"], "I -> I_system^S -> D_f -> dF -> i_fractal")
            self.assertTrue(profile["hierarchy_integrity"]["dF_is_not_generic_I"])

    def test_run_all_is_deterministic_and_json_safe(self):
        first = run_all_multiverse_experiments(MultiverseExperimentConfig(seed=42, shots=128))
        second = run_all_multiverse_experiments(MultiverseExperimentConfig(seed=42, shots=128))
        self.assertEqual(first, second)
        json.dumps(first)
        self.assertEqual(first["experiment_count"], 5)
        self.assertEqual(first["experiment_ids"], list(MULTIVERSE_EXPERIMENT_IDS))
        self.assertEqual(first["feature_dimension"], len(first["feature_vector"]))
        self.assertIn("VIOLARIS_INTERBRANCH_COMMUNICATION_2026", first["source_ids"])
        self.assertIn("RI_QUANTUM_PARADOXES_MULTIVERSE_2026", first["source_ids"])

    def test_invalid_ids_and_bad_shots_reject(self):
        with self.assertRaises(ValueError):
            MultiverseExperimentConfig(experiment_id="schrodinger_cat_context_only")
        with self.assertRaises(ValueError):
            MultiverseExperimentConfig(shots=4)
        with self.assertRaises(ValueError):
            run_all_multiverse_experiments(experiment_ids=["bad_lane"])

    def test_deutsch_lane_is_evidence_not_ontology_validation(self):
        profile = run_multiverse_experiment(
            MultiverseExperimentConfig(experiment_id="deutsch_quantum_computation_origin")
        )
        self.assertEqual(profile["classification"], "reversible_quantum_computation_evidence_not_ontology_claim")
        self.assertIn("not ontology validation", profile["evidence_profile"]["interpretation"])
        self.assertIn("many-worlds is physically true", profile["forbidden_claims"])

    def test_bomb_lane_detects_positive_and_negative_cases(self):
        profile = run_multiverse_experiment(
            MultiverseExperimentConfig(experiment_id="elitzur_vaidman_bomb_tester")
        )
        evidence = profile["evidence_profile"]
        self.assertGreater(evidence["interaction_free_positive_rate"], 0.0)
        self.assertGreater(evidence["negative_case_rate"], 0.0)
        self.assertEqual(profile["classification"], "interaction_free_detection_with_positive_negative_cases")

    def test_teleportation_lane_separates_entanglement_from_signalling(self):
        profile = run_multiverse_experiment(
            MultiverseExperimentConfig(experiment_id="entanglement_teleportation_branch_accounting")
        )
        self.assertEqual(profile["classification"], "entanglement_accounting_without_signalling")
        self.assertIn("classical_channel", profile["simulator_mapping"])
        self.assertGreater(profile["evidence_profile"]["no_signalling_guard"], 0.0)

    def test_google_lane_keeps_scale_review_bounded(self):
        profile = run_multiverse_experiment(
            MultiverseExperimentConfig(experiment_id="google_quantum_computer_scale_review")
        )
        self.assertEqual(profile["classification"], "scale_evidence_review_not_multiverse_validation")
        self.assertIn("evidence-review", profile["simulator_mapping"]["qnn_use"])
        self.assertIn("quantum supremacy validates a multiverse ontology", profile["forbidden_claims"])

    def test_wigner_lane_requires_memory_erasure_constraints(self):
        profile = run_multiverse_experiment(
            MultiverseExperimentConfig(
                experiment_id="wigner_friend_inter_branch_communication",
                memory_erasure=0.2,
                measurement_strength=0.8,
            )
        )
        self.assertEqual(profile["classification"], "inter_branch_protocol_suspended_by_memory_record_constraints")
        self.assertTrue(profile["evidence_profile"]["memory_erasure_required"])
        self.assertIn("VIOLARIS_INTERBRANCH_COMMUNICATION_2026", profile["source_ids"])

    def test_status_lists_source_ledger_and_endpoints(self):
        status = multiverse_experiments_status()
        self.assertEqual(status["status"], "ok")
        self.assertEqual(status["experiment_ids"], list(MULTIVERSE_EXPERIMENT_IDS))
        self.assertIn("POST /fnp-qnn/multiverse-experiments/run-all", status["endpoints"])
        self.assertIn("RI_QUANTUM_PARADOXES_MULTIVERSE_2026", status["source_ids"])
        self.assertIn("VIOLARIS_QUANTUM_PARADOXES_SERIES", status["source_ids"])
        self.assertIn("VIOLARIS_INTERBRANCH_COMMUNICATION_2026", status["source_ids"])


if __name__ == "__main__":
    unittest.main()
