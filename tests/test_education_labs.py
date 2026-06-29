import unittest

from core.education_labs import (
    MIN_LEARNER_AGE,
    build_learning_activities,
    build_learning_pack,
    validate_learner_age,
)


class EducationLabsTests(unittest.TestCase):
    def test_age_guardrail_blocks_underage(self):
        with self.assertRaises(ValueError):
            validate_learner_age(MIN_LEARNER_AGE - 1)

    def test_learning_activities_cover_age_threshold(self):
        activities = build_learning_activities()
        self.assertGreaterEqual(len(activities), 3)
        self.assertTrue(all(activity.age_min >= MIN_LEARNER_AGE for activity in activities))
        ids = [activity.activity_id for activity in activities]
        self.assertEqual(len(ids), len(set(ids)))

    def test_learning_pack_has_schema_and_expected_fields(self):
        pack = build_learning_pack(age_years=14, include_tunnel_demo=False)
        self.assertEqual(pack["learner_policy"]["status"], "age_ok")
        self.assertIn("activities", pack)
        self.assertEqual(pack["learner_policy"]["age_years"], 14)
        self.assertGreaterEqual(len(pack["activities"]), 3)
        sample = pack["activities"][0]
        self.assertIn("expected_to_observe", sample)
        self.assertIn("observation", sample["expected_to_observe"])
        self.assertIn("dominant_axis", sample["expected_to_observe"]["observation"])
        self.assertIn("dominant_magnitude", sample["expected_to_observe"]["observation"])

    def test_learning_pack_runs_tunnel_preview_when_requested(self):
        pack = build_learning_pack(age_years=16, include_tunnel_demo=True)
        with_tunnel = pack["activities"][0]
        self.assertIn("tunnel_preview", with_tunnel)
        tunnel = with_tunnel["tunnel_preview"]
        self.assertIn("sequence_id", tunnel)
        self.assertIn("research_boundary", tunnel)


if __name__ == "__main__":
    unittest.main()
