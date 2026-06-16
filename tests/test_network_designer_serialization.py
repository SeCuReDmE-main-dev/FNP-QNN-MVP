"""Focused tests for Network Designer JSON serialization."""

from __future__ import annotations

import tempfile
import unittest

from core.network_designer.graph import NetworkFamily
from core.network_designer.presets import build_graph
from core.network_designer.serialization import deserialize_graph, read_json_file, serialize_graph, write_json_file


class NetworkDesignerSerializationTests(unittest.TestCase):
    def test_round_trip_for_all_presets(self):
        for family in NetworkFamily:
            original = build_graph(family)
            payload = serialize_graph(original)
            restored = deserialize_graph(payload)
            self.assertEqual(restored.family, original.family)
            self.assertEqual(len(restored.nodes), len(original.nodes))
            self.assertEqual(len(restored.edges), len(original.edges))
            self.assertEqual(restored.to_dict()["nodes"], original.to_dict()["nodes"])
            self.assertEqual(restored.to_dict()["edges"], original.to_dict()["edges"])

    def test_file_round_trip(self):
        graph = build_graph(NetworkFamily.CROSSMODAL_GRAPH)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = temp_dir + "\\crossmodal.json"
            write_json_file(graph, path)
            restored = read_json_file(path)
        self.assertEqual(restored.family, graph.family)
        self.assertEqual(len(restored.nodes), len(graph.nodes))


if __name__ == "__main__":
    unittest.main()
