import unittest

from core.education_progress import build_education_progress


class EducationProgressTests(unittest.TestCase):
    def test_in_progress_has_resume_recovery(self):
        progress = build_education_progress("in_progress", 2, 5)
        self.assertEqual(progress.percent_complete, 40)
        self.assertEqual(progress.recovery_action, "resume_run")
        self.assertFalse(progress.human_review_required)

    def test_awaiting_review_requires_teacher_action(self):
        progress = build_education_progress("awaiting_review", 5, 5)
        self.assertEqual(progress.recovery_action, "open_teacher_review")
        self.assertTrue(progress.human_review_required)

    def test_rejected_run_preserves_recovery_reason(self):
        progress = build_education_progress("rejected", 1, 5, "  invalid payload  ")
        self.assertEqual(progress.rejection_reason, "invalid payload")
        self.assertEqual(progress.recovery_action, "review_rejection")
        self.assertTrue(progress.human_review_required)

    def test_completed_run_requires_all_steps(self):
        progress = build_education_progress("completed", 5, 5)
        self.assertEqual(progress.percent_complete, 100)
        self.assertEqual(progress.recovery_action, "export_evidence")
        with self.assertRaisesRegex(ValueError, "all steps"):
            build_education_progress("completed", 4, 5)

    def test_invalid_state_counts_and_reason_fail_closed(self):
        invalid_calls = (
            ("unknown", 0, 1, None),
            ("in_progress", 2, 1, None),
            ("rejected", 0, 1, None),
            ("in_progress", 0, 1, "not allowed"),
        )
        for args in invalid_calls:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    build_education_progress(*args)


if __name__ == "__main__":
    unittest.main()
