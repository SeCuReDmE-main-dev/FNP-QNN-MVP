import unittest

from core.axiomatic_chamber import ChamberBounds, dmin_dmax_chamber_bounds
from core.gravity_null_test import (
    GravityNullTestConfig,
    graviton_constraint_profile,
    run_gravity_null_test,
)


class GravityNullTestTests(unittest.TestCase):
    def test_null_case_classifies_no_remote_influence(self):
        profile = run_gravity_null_test(
            GravityNullTestConfig(
                seed=11,
                shots=512,
                local_noise=0.0,
                leakage=0.0,
                mass_dispersion=0.0,
                delta_ns_threshold=0.12,
            )
        )

        self.assertEqual(profile["classification"], "no_detected_remote_influence")
        self.assertLessEqual(profile["no_signalling"]["Delta_NS"], 0.12)
        self.assertIsNone(profile["fractal_carrier"]["i_fractal_candidate"])
        self.assertIn("not physical quantum-gravity proof", profile["research_boundary"])

    def test_leakage_case_classifies_local_contamination(self):
        profile = run_gravity_null_test(
            GravityNullTestConfig(
                seed=13,
                shots=512,
                local_noise=0.02,
                leakage=0.35,
                mass_dispersion=0.15,
            )
        )

        self.assertEqual(profile["classification"], "local_coupling_or_shared_noise")
        self.assertEqual(profile["admissibility"]["Adm"], "rejected")
        self.assertGreater(profile["e2b_datadog_review"]["datadog_telemetry"]["metrics"]["fnp_qnn.gravity_null_test.local_contamination"], 0.0)

    def test_frustrated_state_is_visible_without_physics_claim(self):
        profile = run_gravity_null_test(
            GravityNullTestConfig(
                seed=17,
                shots=512,
                local_noise=0.1,
                leakage=0.0,
                mass_dispersion=0.0,
                chamber_contradiction=1.0,
                alpha_wave_frequency=1.0,
                beta_wave_frequency=4.0,
                omega_wave_frequency=9.0,
                delta_ns_threshold=0.001,
                frustration_threshold=0.25,
            )
        )

        self.assertIn(profile["classification"], {"frustrated_state_requires_external_validation", "anomaly_requires_external_validation"})
        self.assertGreaterEqual(profile["frustrated_state"]["F_chamber"], 0.25)
        self.assertIn("not a physical law", profile["gq_super_equation"]["interpretation"])

    def test_invalid_bounds_are_rejected(self):
        with self.assertRaises(ValueError):
            ChamberBounds(d_min=1.0, d_max=1.0)
        with self.assertRaises(ValueError):
            dmin_dmax_chamber_bounds(D_min=2.0, D_max=1.0)
        with self.assertRaises(ValueError):
            GravityNullTestConfig(D_min=2.0, D_max=1.0)

    def test_graviton_constraint_never_returns_exact_mass(self):
        pending = graviton_constraint_profile()
        sourced = graviton_constraint_profile(1e-23, "external-bound-example")

        self.assertEqual(pending["status"], "constraint_profile_pending_external_data")
        self.assertIsNone(pending["exact_graviton_mass_ev"])
        self.assertIsNone(sourced["exact_graviton_mass_ev"])
        self.assertIn("do not claim exact graviton mass", sourced["forbidden_claim"])

    def test_sequence_qiskit_and_review_metadata_are_optional_outputs(self):
        profile = run_gravity_null_test(
            GravityNullTestConfig(
                include_sequence_export=True,
                include_qiskit_preview=True,
                include_e2b_datadog_review=True,
            )
        )

        self.assertIn("sequence_event_spec", profile)
        self.assertIn("qiskit_circuit_preview", profile)
        self.assertIn("e2b_datadog_review", profile)
        self.assertEqual(profile["e2b_datadog_review"]["model"], "e2b_datadog_gravity_review_v1")
        self.assertIn("fnp_qnn.gravity_null_test.entangled_pair_resistance", profile["e2b_datadog_review"]["datadog_telemetry"]["metrics"])


if __name__ == "__main__":
    unittest.main()
