import json
import unittest

from core.evidence_schema import (
    CURRENT_EVIDENCE_VERSION,
    EVIDENCE_SCHEMA,
    migrate_evidence_payload,
)


class EvidenceSchemaTests(unittest.TestCase):
    def test_v1_record_is_normalized_and_json_compatible(self):
        record = migrate_evidence_payload(
            {
                "schema": EVIDENCE_SCHEMA,
                "version": CURRENT_EVIDENCE_VERSION,
                "record_id": "ev-1",
                "run_id": "run-1",
                "subject": "feature encoding",
                "claim": "The vector was produced deterministically.",
                "text": "Local replay evidence.",
                "provenance": "fixture:education.basic-memory-event.v1",
                "approval_state": "pending",
            }
        )
        self.assertEqual(record.to_dict()["version"], CURRENT_EVIDENCE_VERSION)
        json.dumps(record.to_dict())

    def test_v0_aliases_migrate_to_v1(self):
        record = migrate_evidence_payload(
            {
                "id": "legacy-1",
                "experiment_id": "run-legacy",
                "subject": "legacy lab",
                "claim": "A bounded claim.",
                "evidence": "Legacy local evidence.",
                "source": "fixture:legacy.v0",
                "status": "approved",
            }
        )
        self.assertEqual(record.record_id, "legacy-1")
        self.assertEqual(record.text, "Legacy local evidence.")
        self.assertEqual(record.approval_state, "approved")
        self.assertEqual(record.to_dict()["schema"], EVIDENCE_SCHEMA)

    def test_missing_critical_fields_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Evidence field is required: claim"):
            migrate_evidence_payload(
                {"id": "ev", "run_id": "run", "subject": "x", "text": "y", "source": "z", "status": "pending"}
            )

    def test_unknown_future_and_approval_versions_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "future evidence version"):
            migrate_evidence_payload({"version": CURRENT_EVIDENCE_VERSION + 1})
        with self.assertRaisesRegex(ValueError, "approval state"):
            migrate_evidence_payload(
                {
                    "id": "ev",
                    "run_id": "run",
                    "subject": "x",
                    "claim": "y",
                    "text": "z",
                    "source": "s",
                    "status": "published",
                }
            )

    def test_current_version_requires_current_schema_identifier(self):
        with self.assertRaisesRegex(ValueError, "schema identifier"):
            migrate_evidence_payload({"version": CURRENT_EVIDENCE_VERSION, "schema": "other"})


if __name__ == "__main__":
    unittest.main()
