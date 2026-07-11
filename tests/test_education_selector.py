import unittest

from core.education_selector import select_lab_manifests


class EducationSelectorTests(unittest.TestCase):
    def test_default_selection_is_complete_and_catalog_ordered(self):
        manifests = select_lab_manifests()
        self.assertEqual([manifest.lab_id for manifest in manifests], ["memory-to-evidence", "neurobit-gate-trace"])

    def test_audience_selection_is_explicit(self):
        self.assertEqual(len(select_lab_manifests(audience="student")), 2)
        self.assertEqual(len(select_lab_manifests(audience="teacher")), 2)

    def test_requested_ids_are_filtered_without_reordering(self):
        manifests = select_lab_manifests(lab_ids={"neurobit-gate-trace"})
        self.assertEqual([manifest.lab_id for manifest in manifests], ["neurobit-gate-trace"])

    def test_unknown_audience_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Unsupported education audience"):
            select_lab_manifests(audience="operator")

    def test_unknown_lab_id_fails_closed(self):
        with self.assertRaisesRegex(KeyError, "Unknown education lab manifest"):
            select_lab_manifests(lab_ids=["unapproved-lab"])


if __name__ == "__main__":
    unittest.main()
