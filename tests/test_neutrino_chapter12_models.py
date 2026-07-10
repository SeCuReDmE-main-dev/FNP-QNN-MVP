import copy
import math
import unittest

from core.neutrino_chapter12_models import (
    Chapter12ValidationError,
    REQUIRED_CARRIERS,
    canonical_fingerprint,
    detector_projection_profile,
    summarize_numeric_runs,
    ten_carrier_profile,
    toy_medium_profile,
)


def _carriers():
    return [
        {
            "name": name,
            "tension": (index + 1) / 20.0,
            "weight": float(index + 1),
            "role": f"role_{index}",
            "source_fields": [f"field_{index}"],
        }
        for index, name in enumerate(REQUIRED_CARRIERS)
    ]


def _detector():
    return {
        "x_true": [1.0, 0.0],
        "response_matrix": [[0.8, 0.1], [0.2, 0.7]],
        "background_status": "explicit",
        "background": [0.02, 0.01],
        "noise": {"mode": "deterministic_zero"},
        "labels": ["muon_like", "electron_like"],
        "thresholds": [0.0, 0.0],
    }


class NeutrinoChapter12ModelsTests(unittest.TestCase):
    def test_ten_carrier_profile_exposes_every_contribution(self):
        payload = ten_carrier_profile(_carriers())

        expected = sum((index + 1) * ((index + 1) / 20.0) for index in range(10)) / sum(range(1, 11))
        self.assertEqual(payload["carrier_count"], 10)
        self.assertAlmostEqual(payload["composite_tension"], expected)
        self.assertEqual([item["name"] for item in payload["contributions"]], list(REQUIRED_CARRIERS))
        self.assertAlmostEqual(sum(item["normalized_contribution"] for item in payload["contributions"]), expected)

    def test_ten_ablations_are_blocked(self):
        for name in REQUIRED_CARRIERS:
            with self.subTest(name=name):
                carriers = [item for item in _carriers() if item["name"] != name]
                with self.assertRaisesRegex(Chapter12ValidationError, "missing_or_unknown_carrier"):
                    ten_carrier_profile(carriers)

    def test_twenty_low_high_perturbations_match_weighted_derivative(self):
        baseline_carriers = _carriers()
        baseline = ten_carrier_profile(baseline_carriers)
        total_weight = float(baseline["total_weight"])
        for index, name in enumerate(REQUIRED_CARRIERS):
            for delta in (-0.01, 0.01):
                with self.subTest(name=name, delta=delta):
                    carriers = copy.deepcopy(baseline_carriers)
                    carriers[index]["tension"] += delta
                    changed = ten_carrier_profile(carriers)
                    expected_delta = carriers[index]["weight"] / total_weight * delta
                    actual_delta = changed["composite_tension"] - baseline["composite_tension"]
                    self.assertAlmostEqual(actual_delta, expected_delta, places=14)

    def test_invalid_carrier_weight_tension_and_duplicates_block(self):
        for field, value, code in (
            ("weight", 0.0, "invalid_carrier_weight"),
            ("tension", 1.1, "invalid_carrier_tension"),
        ):
            carriers = _carriers()
            carriers[0][field] = value
            with self.assertRaisesRegex(Chapter12ValidationError, code):
                ten_carrier_profile(carriers)
        duplicate = _carriers()
        duplicate[-1]["name"] = duplicate[0]["name"]
        with self.assertRaisesRegex(Chapter12ValidationError, "duplicate_carrier"):
            ten_carrier_profile(duplicate)

    def test_medium_vacuum_context_matter_and_antineutrino(self):
        vacuum = toy_medium_profile({"level": "vacuum", "theta_rad": 0.6, "particle_kind": "neutrino"})
        self.assertEqual(vacuum["medium_tension"], 0.0)
        context = toy_medium_profile({"level": "context_only"})
        self.assertEqual(context["status"], "suspended")

        matter_request = {
            "level": "toy_matter_model",
            "energy_gev": 0.6,
            "delta_m2_ev2": 0.0025,
            "theta_rad": 0.6,
            "matter_potential_ev": 7.6e-14,
            "particle_kind": "neutrino",
        }
        neutrino = toy_medium_profile(matter_request)
        anti_request = dict(matter_request)
        anti_request["particle_kind"] = "antineutrino"
        antineutrino = toy_medium_profile(anti_request)
        self.assertAlmostEqual(neutrino["A"], -antineutrino["A"])
        self.assertGreaterEqual(neutrino["medium_tension"], 0.0)
        self.assertLessEqual(neutrino["medium_tension"], 1.0)

    def test_medium_requires_explicit_model_parameters(self):
        with self.assertRaisesRegex(Chapter12ValidationError, "missing_explicit_matter_potential"):
            toy_medium_profile(
                {
                    "level": "toy_matter_model",
                    "energy_gev": 0.6,
                    "delta_m2_ev2": 0.0025,
                    "theta_rad": 0.6,
                    "particle_kind": "neutrino",
                }
            )

    def test_detector_projection_and_seeded_replay(self):
        deterministic = detector_projection_profile(_detector())
        self.assertEqual(deterministic["classification"], "muon_like")
        self.assertTrue(0.0 <= deterministic["detector_tension"] <= 1.0)

        seeded = _detector()
        seeded["noise"] = {"mode": "gaussian_seeded", "seed": 734, "std": [0.01, 0.01]}
        self.assertEqual(detector_projection_profile(seeded), detector_projection_profile(seeded))

    def test_detector_rejects_missing_background_and_bad_matrix(self):
        missing = _detector()
        missing.pop("background_status")
        with self.assertRaisesRegex(Chapter12ValidationError, "missing_detector_background"):
            detector_projection_profile(missing)
        mismatch = _detector()
        mismatch["response_matrix"] = [[0.8], [0.2]]
        with self.assertRaisesRegex(Chapter12ValidationError, "detector_dimension_mismatch"):
            detector_projection_profile(mismatch)

    def test_fingerprint_and_run_summary_are_deterministic(self):
        self.assertEqual(canonical_fingerprint({"b": 2, "a": 1}), canonical_fingerprint({"a": 1, "b": 2}))
        summary = summarize_numeric_runs([[0.2, 0.4]] * 100)
        self.assertEqual(summary["delta_max"], 0.0)
        self.assertEqual(summary["rmse"], 0.0)
        self.assertTrue(all(math.isfinite(item["mean"]) for item in summary["columns"]))


if __name__ == "__main__":
    unittest.main()
