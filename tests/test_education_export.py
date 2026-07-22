import json
import unittest

from core.education_export import (
    REDACTION_MARKER,
    build_redacted_review_export,
    export_review_json,
    render_review_markdown,
)
from core.education_run_contract import build_education_run_contract


class EducationExportTests(unittest.TestCase):
    def _run(self):
        return build_education_run_contract(
            "memory-to-evidence",
            7,
            "completed",
            5,
            5,
            ("feature vector", "review boundary"),
            "ready",
        )

    def test_sensitive_keys_and_private_values_are_redacted_recursively(self):
        export = build_redacted_review_export(
            self._run(),
            ({"subject": "safe", "api_key": "secret", "nested": {"token": "hidden", "path": "C:\\Users\\private"}},),
        )
        record = export["evidence"][0]
        self.assertEqual(record["api_key"], REDACTION_MARKER)
        self.assertEqual(record["nested"]["token"], REDACTION_MARKER)
        self.assertEqual(record["nested"]["path"], REDACTION_MARKER)

    def test_json_export_is_serializable_and_has_export_metadata(self):
        export = build_redacted_review_export(self._run(), ())
        payload = json.loads(export_review_json(export))
        self.assertEqual(payload["version"], 1)
        self.assertEqual(payload["schema"], "fnp-qnn.education.review-export")

    def test_markdown_review_contains_review_fields_without_secret_values(self):
        export = build_redacted_review_export(
            self._run(),
            ({"claim": "safe claim", "password": "do-not-export"},),
        )
        markdown = render_review_markdown(export)
        self.assertIn("# FNP-QNN Education Review", markdown)
        self.assertIn("feature vector", markdown)
        self.assertIn(REDACTION_MARKER, export["evidence"][0]["password"])
        self.assertNotIn("do-not-export", markdown)

    def test_export_does_not_mutate_source_records(self):
        records = [{"token": "secret", "subject": "safe"}]
        build_redacted_review_export(self._run(), records)
        self.assertEqual(records[0]["token"], "secret")

    def test_invalid_run_type_is_rejected(self):
        with self.assertRaisesRegex(TypeError, "EducationRunContract"):
            build_redacted_review_export({}, ())


if __name__ == "__main__":
    unittest.main()
