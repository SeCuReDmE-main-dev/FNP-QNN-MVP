import json
import unittest

from core.education_run_contract import (
    RUN_CONTRACT_SCHEMA,
    RUN_CONTRACT_VERSION,
    build_education_run_contract,
)


class EducationRunContractTests(unittest.TestCase):
    def test_contract_has_one_versioned_cross_surface_envelope(self):
        contract = build_education_run_contract(
            "memory-to-evidence",
            7,
            "awaiting_review",
            4,
            5,
            ("input summary", "feature vector"),
            "pending",
        )
        payload = contract.to_dict()
        self.assertEqual(payload["schema"], RUN_CONTRACT_SCHEMA)
        self.assertEqual(payload["version"], RUN_CONTRACT_VERSION)
        self.assertEqual(payload["lab_id"], "memory-to-evidence")
        self.assertEqual(payload["progress"]["state"], "awaiting_review")
        self.assertEqual(payload["review"]["seed"], 7)

    def test_contract_json_is_deterministic_and_serializable(self):
        args = (
            "neurobit-gate-trace",
            11,
            "completed",
            5,
            5,
            ("T/I/F profile", "gate sequence"),
            "ready",
        )
        first = build_education_run_contract(*args).to_json()
        second = build_education_run_contract(*args).to_json()
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["progress"]["percent_complete"], 100)

    def test_shared_contract_rejects_invalid_nested_state(self):
        with self.assertRaisesRegex(ValueError, "completed runs"):
            build_education_run_contract(
                "memory-to-evidence",
                1,
                "completed",
                2,
                5,
                ("trace",),
                "ready",
            )

    def test_shared_contract_rejects_unknown_lab(self):
        with self.assertRaisesRegex(KeyError, "Unknown education lab manifest"):
            build_education_run_contract("unapproved-lab", 1, "not_started", 0, 1, (), "not_started")


if __name__ == "__main__":
    unittest.main()
