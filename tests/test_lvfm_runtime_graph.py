"""LVFM graph unit coverage for runtime boottrace snapshots."""

from __future__ import annotations

import unittest

import numpy as np

from core import LVFMRuntimeGraph, RegisterBit, RegisterKey


class LVFMRuntimeGraphTests(unittest.TestCase):
    def test_register_key_and_node_registration(self):
        graph = LVFMRuntimeGraph()
        key = graph.register_node(
            node_id="evt:audio:0",
            bit=RegisterBit(0.7, 0.2, 0.1),
            register_weight=1.25,
            metadata={"modality": "audio"},
        )
        self.assertIsInstance(key, RegisterKey)
        self.assertEqual(key.node_id, "evt:audio:0")

    def test_compact_snapshot_and_trace(self):
        graph = LVFMRuntimeGraph()
        graph.register_node("a", RegisterBit(0.6, 0.2, 0.2), register_weight=1.0)
        graph.register_node("b", RegisterBit(0.1, 0.2, 0.7), register_weight=1.0)
        graph.add_edge("a", "b", weight=0.8)
        snapshot = graph.to_snapshot()

        compact = snapshot["snapshot"]["compact"]
        self.assertIn("a", compact)
        self.assertIn("T", compact["a"])
        self.assertIn("I", compact["a"])
        self.assertIn("dF", compact["a"])
        self.assertIn("node_ids", snapshot)
        self.assertIn("trace", snapshot["snapshot"])
        self.assertIn("T=", snapshot["decision"]["trace_line"])

    def test_invalid_weighted_edge_is_rejected(self):
        graph = LVFMRuntimeGraph()
        graph.register_node("a", RegisterBit(0.5, 0.25, 0.25))
        graph.register_node("b", RegisterBit(0.5, 0.3, 0.2))
        with self.assertRaises(ValueError):
            graph.add_edge("a", "b", weight=0.0)

    def test_empty_graph_returns_hold(self):
        graph = LVFMRuntimeGraph()
        snapshot = graph.to_snapshot()
        decision = snapshot["decision"]
        self.assertEqual(decision["verdict"], "hold")
        self.assertEqual(decision["t_mass"], 0.0)
        self.assertEqual(snapshot["snapshot"]["compact"], {})


class LVFMBridgeIntegrationStubTests(unittest.TestCase):
    def test_snapshot_payload_roundtrip_shape(self):
        bit = RegisterBit(0.2, 0.4, 0.4)
        graph = LVFMRuntimeGraph()
        graph.register_node("n1", bit, metadata={"role": "input"})
        graph.register_node("n2", bit, metadata={"role": "output"})
        graph.add_edge("n1", "n2", 0.9)
        payload = graph.to_snapshot()

        self.assertIn("node_weights", payload)
        self.assertIn("edge_weights", payload)
        self.assertIsInstance(payload["node_weights"]["n1"]["metadata"], dict)
        self.assertGreaterEqual(payload["snapshot"]["compact"]["n1"]["T"], 0.0)
        self.assertLessEqual(payload["snapshot"]["compact"]["n1"]["F"], 1.0)
        self.assertGreaterEqual(payload["decision"]["confidence"], -1.0)
        self.assertIsInstance(np.array(payload["adjacency_matrix"]).shape[0], int)


if __name__ == "__main__":
    unittest.main()
