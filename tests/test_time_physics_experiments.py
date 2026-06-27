"""Focused tests for the bounded time-physics experiment suite."""

from __future__ import annotations

import json
import math
import unittest

from core.time_physics_experiments import (
    TIME_PHYSICS_EXPERIMENT_IDS,
    TimePhysicsExperimentConfig,
    run_all_time_physics_experiments,
    run_time_physics_experiment,
    time_physics_experiments_status,
)


class TimePhysicsExperimentsTests(unittest.TestCase):
    def test_every_lane_returns_stable_model_source_ids_and_features(self):
        for experiment_id in TIME_PHYSICS_EXPERIMENT_IDS:
            profile = run_time_physics_experiment(TimePhysicsExperimentConfig(experiment_id=experiment_id))
            self.assertEqual(profile["model"], "fnp_qnn_time_physics_experiment_profile_v1")
            self.assertEqual(profile["experiment_id"], experiment_id)
            self.assertIn("BIG_THINK_TIME_VIDEO_2026", profile["source_ids"])
            self.assertEqual(profile["feature_dimension"], len(profile["feature_vector"]))
            self.assertEqual(profile["feature_dimension"], 8)
            self.assertTrue(all(math.isfinite(item) and 0.0 <= item <= 1.0 for item in profile["feature_vector"]))
            self.assertEqual(profile["hierarchy"], "I -> I_system^S -> D_f -> dF -> i_fractal")
            self.assertTrue(profile["hierarchy_integrity"]["dF_is_not_generic_I"])

    def test_run_all_is_deterministic_json_safe_and_cited(self):
        first = run_all_time_physics_experiments(TimePhysicsExperimentConfig(seed=42, shots=128))
        second = run_all_time_physics_experiments(TimePhysicsExperimentConfig(seed=42, shots=128))
        self.assertEqual(first, second)
        json.dumps(first)
        self.assertEqual(first["experiment_count"], 6)
        self.assertEqual(first["experiment_ids"], list(TIME_PHYSICS_EXPERIMENT_IDS))
        self.assertEqual(first["feature_dimension"], len(first["feature_vector"]))
        self.assertIn("ALKHALILI_CHEN_DECOHERENT_ARROW_2024", first["source_ids"])
        self.assertTrue(first["citation_integrity"]["source_sets_are_separate"])
        self.assertIn("RI_QUANTUM_PARADOXES_MULTIVERSE_2026", first["related_prior_work_source_ids"])

    def test_invalid_ids_and_bad_shots_reject(self):
        with self.assertRaises(ValueError):
            TimePhysicsExperimentConfig(experiment_id="time_travel_works")
        with self.assertRaises(ValueError):
            TimePhysicsExperimentConfig(shots=4)
        with self.assertRaises(ValueError):
            run_all_time_physics_experiments(experiment_ids=["bad_lane"])

    def test_manifest_lane_separates_experience_from_physical_ontology(self):
        profile = run_time_physics_experiment(
            TimePhysicsExperimentConfig(experiment_id="manifest_vs_physical_time_flow")
        )
        self.assertEqual(profile["classification"], "manifest_time_flow_separated_from_physical_ontology")
        self.assertIn("not proof", profile["simulator_mapping"]["manifest_time"])
        self.assertIn("the simulator proves eternalism", profile["forbidden_claims"])

    def test_relativity_lane_does_not_claim_fatalism(self):
        profile = run_time_physics_experiment(
            TimePhysicsExperimentConfig(experiment_id="relativistic_time_dilation_block_universe")
        )
        self.assertEqual(profile["classification"], "relativistic_clock_accounting_not_fatalism_proof")
        self.assertIn("the block universe proves fatalism", profile["forbidden_claims"])

    def test_simultaneity_lane_rejects_absolute_now(self):
        profile = run_time_physics_experiment(
            TimePhysicsExperimentConfig(experiment_id="relativity_of_simultaneity_now")
        )
        self.assertEqual(profile["classification"], "local_now_only_no_universal_now_claim")
        self.assertIn("physics has found an absolute universal now", profile["forbidden_claims"])

    def test_entropy_lane_keeps_gradient_bounded(self):
        profile = run_time_physics_experiment(
            TimePhysicsExperimentConfig(experiment_id="thermodynamic_entropy_arrow", entropy_gradient=0.9)
        )
        self.assertEqual(profile["classification"], "thermodynamic_arrow_boundary_condition_profile")
        self.assertGreater(profile["evidence_profile"]["thermodynamic_arrow"], 0.0)
        self.assertLessEqual(profile["evidence_profile"]["thermodynamic_arrow"], 1.0)

    def test_entanglement_lane_cites_decoherent_arrow_paper(self):
        profile = run_time_physics_experiment(
            TimePhysicsExperimentConfig(experiment_id="entanglement_decoherence_arrow")
        )
        self.assertEqual(profile["classification"], "decoherent_arrow_entanglement_past_hypothesis_profile")
        self.assertIn("ALKHALILI_CHEN_DECOHERENT_ARROW_2024", profile["source_ids"])
        self.assertIn("entanglement sends signals through time", profile["forbidden_claims"])

    def test_cosmological_lane_rejects_operational_time_travel(self):
        profile = run_time_physics_experiment(
            TimePhysicsExperimentConfig(experiment_id="cosmological_boundary_time_travel", paradox_pressure=0.5)
        )
        self.assertEqual(profile["classification"], "cosmological_boundary_profile_time_travel_rejected")
        self.assertIn("time travel works", profile["forbidden_claims"])

    def test_status_lists_sources_and_endpoints(self):
        status = time_physics_experiments_status()
        self.assertEqual(status["status"], "ok")
        self.assertEqual(status["experiment_ids"], list(TIME_PHYSICS_EXPERIMENT_IDS))
        self.assertIn("POST /fnp-qnn/time-physics-experiments/run-all", status["endpoints"])
        self.assertIn("BIG_THINK_BLOCK_UNIVERSE_TRANSCRIPT_2026", status["source_ids"])
        self.assertIn("VIOLARIS_INTERBRANCH_COMMUNICATION_2026", status["related_prior_work_source_ids"])


if __name__ == "__main__":
    unittest.main()
