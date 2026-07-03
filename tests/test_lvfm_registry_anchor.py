"""LVFM registry anchoring behavior."""

from __future__ import annotations

import unittest
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

from core import compute_lock_state
from core.lvfm_registry_anchor import DEFAULT_LOCK_THRESHOLD, RegistryAnchoringResult, publish_gate_state


class LVFMRegistryAnchorTests(unittest.TestCase):
    def test_compute_lock_state_when_allowable(self):
        decision = {
            "verdict": "allow",
            "confidence": 0.45,
            "i_mass": 0.1,
            "f_mass": 0.05,
            "dF_mass": 0.22,
        }
        state = compute_lock_state(decision, threshold=DEFAULT_LOCK_THRESHOLD)
        self.assertFalse(state["locked"])
        self.assertEqual(state["lock_reason"], "none")

    def test_compute_lock_state_blocks_high_f_mass(self):
        decision = {
            "verdict": "allow",
            "confidence": 0.22,
            "i_mass": 0.96,
            "f_mass": 0.7,
            "dF_mass": 0.1,
        }
        state = compute_lock_state(decision, threshold=DEFAULT_LOCK_THRESHOLD)
        self.assertTrue(state["locked"])
        self.assertEqual(state["lock_reason"], "high_i_mass")

    def test_publish_gate_state_without_windows_registry_is_deterministic(self):
        gate = {
            "gate_id": "test-gate",
            "sequence_fingerprint": "abc",
            "created_at": "1970-01-01T00:00:00Z",
            "decision": {
                "verdict": "allow",
                "confidence": 0.2,
                "i_mass": 0.1,
                "f_mass": 0.2,
                "dF_mass": 0.3,
                "t_mass": 0.6,
                "lock_reason": "none",
                "trace_line": "T=0.600|I=0.100|dF=0.300|F=0.200|nodes=1|edges=0|verdict=allow",
            },
            "snapshot": {
                "compact": {"evt:0": {"T": 0.5, "I": 0.4, "dF": 0.1, "F": 0.0}},
                "exact_bits": {"evt:0": {"T": 0.5, "I": 0.4, "dF": 0.1, "F": 0.0}},
                "register_keys": {
                    "evt:0": {
                        "bit": {"T": 0.5, "I": 0.4, "dF": 0.1, "F": 0.0, "register_weight": 1.0},
                        "metadata": {"modality": "audio"},
                    }
                },
            },
            "payload_metrics": {},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            history_path = str(Path(tmpdir) / "lvfm_registry_history.jsonl")
            with patch("core.lvfm_registry_anchor.winreg", None):
                result: RegistryAnchoringResult = publish_gate_state(
                    gate,
                    registry_subkey=r"Software\\SeCuReDmE\\LVFM\\Test",
                    history_path=history_path,
                )
            self.assertFalse(result.published)
            self.assertIsNotNone(result.error)
            self.assertIn("winreg", result.error)
            self.assertEqual(result.schema_version, "lvfm.registry.history.v1")
            self.assertTrue(result.history_event_id)
            self.assertTrue(Path(result.history_path).exists())
            lines = Path(result.history_path).read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            history_event = json.loads(lines[0])
            self.assertEqual(history_event["gate_id"], "test-gate")
            self.assertEqual(history_event["schema_version"], "lvfm.registry.history.v1")
            self.assertIn("registry_payload", history_event)
            self.assertIn("lock_state", history_event)

    def test_publish_gate_state_includes_register_keys(self):
        storage = {}

        class FakeRegistryKey:
            def __init__(self) -> None:
                self._storage = storage

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        class FakeWinreg:
            HKEY_CURRENT_USER = object()
            REG_DWORD = 4
            REG_SZ = 1

            def CreateKey(self, _base, path):
                self._path = path
                return FakeRegistryKey()

            def SetValueEx(self, key, name, _reserved, _type, value):
                key._storage[name] = value

        fake_winreg = FakeWinreg()

        gate = {
            "gate_id": "test-gate",
            "sequence_fingerprint": "abc",
            "created_at": "1970-01-01T00:00:00Z",
            "decision": {
                "verdict": "allow",
                "confidence": 0.2,
                "i_mass": 0.1,
                "f_mass": 0.2,
                "dF_mass": 0.3,
                "t_mass": 0.6,
                "lock_reason": "none",
                "trace_line": "T=0.600|I=0.100|dF=0.300|F=0.200|nodes=1|edges=0|verdict=allow",
            },
            "snapshot": {
                "compact": {"evt:0": {"T": 0.5, "I": 0.4, "dF": 0.1, "F": 0.0}},
                "exact_bits": {"evt:0": {"T": 0.5, "I": 0.4, "dF": 0.1, "F": 0.0}},
                "register_keys": {
                    "evt:0": {
                        "bit": {"T": 0.5, "I": 0.4, "dF": 0.1, "F": 0.0, "register_weight": 1.2},
                        "metadata": {"modality": "audio"},
                    }
                },
            },
            "payload_metrics": {"input_events": 3},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            history_path = str(Path(tmpdir) / "lvfm_registry_history.jsonl")
            with patch("core.lvfm_registry_anchor.winreg", fake_winreg):
                result = publish_gate_state(
                    gate,
                    registry_subkey=r"Software\\SeCuReDmE\\LVFM\\Test",
                    history_path=history_path,
                )
            history_lines = Path(result.history_path).read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(history_lines), 1)
            history_event = json.loads(history_lines[0])
            self.assertEqual(history_event["event_id"], result.history_event_id)
            self.assertEqual(history_event["registry_payload"]["gate_id"], "test-gate")
            self.assertEqual(history_event["lock_state"]["lock_reason"], result.lock_reason)

        self.assertTrue(result.published)
        self.assertIn("RegisterKeysJson", storage)
        self.assertIn("DecisionJson", storage)
        self.assertIn("RegistryPayloadJson", storage)
        self.assertIn("BitTableJson", storage)
        self.assertIn("TiDfRaw", storage)
        self.assertIn("LockScore", storage)
        self.assertIn("RegistrySchemaVersion", storage)
        self.assertIn("HistoryEventId", storage)
        self.assertIn("HistoryPath", storage)
        self.assertIn("HistoryWrittenAt", storage)
        reg_keys = json.loads(storage["RegisterKeysJson"])
        decision = json.loads(storage["DecisionJson"])
        payload = json.loads(storage["RegistryPayloadJson"])
        bit_table = json.loads(storage["BitTableJson"])
        self.assertIn("evt:0", reg_keys)
        self.assertIn("metadata", reg_keys["evt:0"])
        self.assertEqual(reg_keys["evt:0"]["metadata"]["modality"], "audio")
        self.assertEqual(decision["verdict"], "allow")
        self.assertEqual(decision["dF_mass"], 0.3)
        self.assertIn("f_mass", decision)
        self.assertEqual(payload["gate_id"], "test-gate")
        self.assertEqual(payload["schema_version"], "lvfm.registry.history.v1")
        self.assertEqual(payload["bit_table"][0]["node_id"], "evt:0")
        self.assertEqual(payload["bit_table"][0]["metadata"]["modality"], "audio")
        self.assertEqual(payload["bit_table"][0]["register_weight"], 1.2)
        self.assertEqual(history_event["event_id"], storage["HistoryEventId"])


if __name__ == "__main__":
    unittest.main()
