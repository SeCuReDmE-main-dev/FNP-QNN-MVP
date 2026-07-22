import unittest

from core.education_review import build_teacher_review


class EducationReviewTests(unittest.TestCase):
    def test_complete_review_exposes_only_bounded_summary_fields(self):
        review = build_teacher_review(
            "memory-to-evidence",
            42,
            ("feature vector", "run seed", "feature vector"),
            "ready",
        )
        payload = review.to_dict()
        self.assertEqual(payload["seed"], 42)
        self.assertEqual(payload["trace_labels"], ("feature vector", "run seed"))
        self.assertEqual(payload["review_status"], "ready_for_human_review")
        self.assertTrue(payload["human_review_required"])
        self.assertIn("non-clinical", payload["claim_boundary"])

    def test_incomplete_export_remains_incomplete(self):
        review = build_teacher_review("neurobit-gate-trace", 0, ("gate sequence",), "pending")
        self.assertEqual(review.review_status, "incomplete")

    def test_unknown_lab_fails_closed(self):
        with self.assertRaisesRegex(KeyError, "Unknown education lab manifest"):
            build_teacher_review("unapproved-lab", 1, ("trace",), "ready")

    def test_invalid_seed_fails_closed(self):
        for seed in (-1, True, 1.5):
            with self.subTest(seed=seed):
                with self.assertRaisesRegex(ValueError, "seed"):
                    build_teacher_review("memory-to-evidence", seed, ("trace",), "ready")

    def test_invalid_trace_or_export_status_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "trace labels"):
            build_teacher_review("memory-to-evidence", 1, ("",), "ready")
        with self.assertRaisesRegex(ValueError, "export status"):
            build_teacher_review("memory-to-evidence", 1, ("trace",), "published")


if __name__ == "__main__":
    unittest.main()
