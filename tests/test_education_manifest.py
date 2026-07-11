import json
import unittest

from core.education_manifest import (
    LAB_MANIFEST_SCHEMA,
    LAB_MANIFEST_VERSION,
    get_lab_manifest,
    list_lab_manifests,
    manifest_catalog,
)


class EducationManifestTests(unittest.TestCase):
    def test_catalog_is_versioned_and_json_compatible(self):
        catalog = manifest_catalog()
        self.assertEqual(catalog["schema"], LAB_MANIFEST_SCHEMA)
        self.assertEqual(catalog["version"], LAB_MANIFEST_VERSION)
        json.dumps(catalog)
        self.assertEqual(len(catalog["labs"]), len(list_lab_manifests()))

    def test_catalog_ids_are_unique_and_stable(self):
        manifests = list_lab_manifests()
        ids = [manifest.lab_id for manifest in manifests]
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(len(ids), len(set(ids)))

    def test_each_manifest_has_supervised_learning_contract(self):
        for manifest in list_lab_manifests():
            with self.subTest(lab_id=manifest.lab_id):
                self.assertEqual(set(manifest.audience), {"student", "teacher"})
                self.assertTrue(manifest.objective)
                self.assertTrue(manifest.input_profile.startswith("fixture:education."))
                self.assertGreaterEqual(len(manifest.expected_evidence), 3)
                self.assertIn("alpha-local", manifest.claim_boundary.lower())

    def test_lookup_returns_the_catalogued_manifest(self):
        manifest = get_lab_manifest("memory-to-evidence")
        self.assertEqual(manifest.to_dict(), manifest_catalog()["labs"][0])

    def test_unknown_lab_is_rejected(self):
        with self.assertRaisesRegex(KeyError, "Unknown education lab manifest"):
            get_lab_manifest("not-approved")


if __name__ == "__main__":
    unittest.main()
