import ast
import json
import unittest
from pathlib import Path
from uuid import uuid4

from core.qcg_companion_adapter import (
    ADAPTER_SCHEMA,
    NAVIGATION_SCHEMA,
    PANEL_NAVIGATION_TARGETS,
    QCG_SNAPSHOT_SCHEMA,
    FnpQnnQcgCompanionAdapter,
)


class QcgCompanionAdapterTests(unittest.TestCase):
    def setUp(self):
        self.adapter = FnpQnnQcgCompanionAdapter(str(uuid4()))
        self.state = {
            "run_id": "fnp-qnn-run-7",
            "status": "completed",
            "events_count": 4,
            "pairs_count": 6,
            "feature_dimension": 31,
            "evidence_count": 1,
        }

    def test_snapshot_matches_read_only_qcg_v2_boundary(self):
        snapshot = self.adapter.get_snapshot(self.state)

        self.assertEqual(snapshot["schema_version"], QCG_SNAPSHOT_SCHEMA)
        self.assertEqual(snapshot["surface"], "web")
        self.assertEqual(snapshot["phase"], "active")
        self.assertEqual(snapshot["authority_state"], "unavailable")
        self.assertEqual(snapshot["available_commands"], [])
        self.assertEqual(snapshot["tools"], [])
        self.assertEqual(snapshot["effects"]["qpu_submissions"], 0)
        self.assertEqual(snapshot["effects"]["local_simulations"], 0)
        self.assertRegex(snapshot["artifact"]["digest"], r"^[0-9a-f]{64}$")

    def test_snapshot_digest_is_deterministic_and_changes_with_summary(self):
        first = self.adapter.get_snapshot(self.state)["artifact"]["digest"]
        second = self.adapter.get_snapshot(dict(reversed(tuple(self.state.items()))))["artifact"]["digest"]
        changed = self.adapter.get_snapshot({**self.state, "events_count": 5})["artifact"]["digest"]

        self.assertEqual(first, second)
        self.assertNotEqual(first, changed)

    def test_state_rejects_unknown_or_unbounded_fields(self):
        with self.assertRaisesRegex(ValueError, "non-allowlisted fields"):
            self.adapter.get_snapshot({**self.state, "api_key": "not-accepted"})
        with self.assertRaisesRegex(ValueError, "run_id"):
            self.adapter.get_snapshot({**self.state, "run_id": "C:/private/file"})
        with self.assertRaisesRegex(ValueError, "events_count"):
            self.adapter.get_snapshot({**self.state, "events_count": True})

    def test_navigation_manifest_matches_current_panel_tabs(self):
        targets = self.adapter.navigation_manifest()

        self.assertEqual([item["key"] for item in targets], list(PANEL_NAVIGATION_TARGETS))
        self.assertEqual(targets[1], {"key": "events", "label": "Events", "panel_tab_index": 0})
        self.assertEqual(targets[-1], {"key": "chamber_lab", "label": "Chamber Lab", "panel_tab_index": 7})

    def test_navigation_indices_match_panel_evidence_tab_order(self):
        panel_path = Path(__file__).resolve().parents[1] / "panel_app.py"
        tree = ast.parse(panel_path.read_text(encoding="utf-8"))
        evidence_tabs = next(
            node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_evidence_tabs"
        )
        return_node = next(node for node in evidence_tabs.body if isinstance(node, ast.Return))
        labels = [
            item.elts[0].value
            for item in return_node.value.args
            if isinstance(item, ast.Tuple) and isinstance(item.elts[0], ast.Constant)
        ]
        expected = [target.label for key, target in PANEL_NAVIGATION_TARGETS.items() if key != "overview"]

        self.assertEqual(labels, expected)

    def test_navigation_applies_only_allowlisted_panel_index(self):
        activated = []

        result = self.adapter.navigate("network_designer", activated.append)

        self.assertEqual(result["schema_version"], NAVIGATION_SCHEMA)
        self.assertEqual(result["activation"], "applied")
        self.assertEqual(activated, [5])

    def test_navigation_fails_closed_without_invoking_callback(self):
        activated = []

        with self.assertRaisesRegex(ValueError, "not allowlisted"):
            self.adapter.navigate("external-provider", activated.append)

        self.assertEqual(activated, [])

    def test_envelope_is_deterministic_bounded_and_public_safe(self):
        encoded = self.adapter.to_json(self.state, "events")
        envelope = json.loads(encoded)

        self.assertEqual(envelope["schema_version"], ADAPTER_SCHEMA)
        self.assertEqual(envelope["mode"], "read_only")
        self.assertEqual(envelope["navigation"]["current"]["target"], "events")
        self.assertLessEqual(len(encoded.encode("utf-8")), 8_192)
        for forbidden in ("api_key", "password", "access_token", "authorization", "provider"):
            self.assertNotIn(forbidden, encoded.lower())

    def test_invalid_session_binding_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "valid UUID"):
            FnpQnnQcgCompanionAdapter("not-a-session")
        with self.assertRaisesRegex(ValueError, "QCG-compatible UUID"):
            FnpQnnQcgCompanionAdapter("00000000-0000-0000-0000-000000000000")


if __name__ == "__main__":
    unittest.main()
