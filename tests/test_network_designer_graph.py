"""Focused tests for Network Designer graph and validation contract."""

from __future__ import annotations

import unittest

from core.network_designer.graph import NetworkEdge, NetworkFamily, NetworkGraph, NetworkNode, NetworkPort, NetworkPortDirection
from core.network_designer.presets import build_graph
from core.network_designer.validator import validate_graph


class NetworkDesignerGraphTests(unittest.TestCase):
    def test_duplicate_node_ids_are_rejected(self):
        graph = NetworkGraph(family=NetworkFamily.NEURAL_NETWORK.value)
        node = NetworkNode(
            node_id="node_1",
            family=NetworkFamily.NEURAL_NETWORK.value,
            node_type="input",
            label="Input",
            ports=(NetworkPort("out", NetworkPortDirection.OUTPUT),),
        )
        graph.add_node(node)
        with self.assertRaises(ValueError):
            graph.add_node(node)

    def test_invalid_edge_source_port_is_rejected(self):
        graph = NetworkGraph(family=NetworkFamily.NEURAL_NETWORK.value)
        input_node = NetworkNode(
            node_id="input",
            family=NetworkFamily.NEURAL_NETWORK.value,
            node_type="input",
            label="Input",
            ports=(NetworkPort("out", NetworkPortDirection.OUTPUT),),
        )
        output_node = NetworkNode(
            node_id="output",
            family=NetworkFamily.NEURAL_NETWORK.value,
            node_type="output",
            label="Output",
            ports=(NetworkPort("in", NetworkPortDirection.INPUT),),
        )
        graph.add_node(input_node)
        graph.add_node(output_node)
        with self.assertRaises(ValueError):
            graph.add_edge(
                NetworkEdge("input", "in", "output", "in", 1.0),
            )

    def test_cycle_validation_blocks_neural_family(self):
        graph = NetworkGraph(family=NetworkFamily.NEURAL_NETWORK.value)
        node_a = NetworkNode(
            node_id="a",
            family=NetworkFamily.NEURAL_NETWORK.value,
            node_type="n",
            label="A",
            ports=(
                NetworkPort("in", NetworkPortDirection.INPUT),
                NetworkPort("out", NetworkPortDirection.OUTPUT),
            ),
        )
        node_b = NetworkNode(
            node_id="b",
            family=NetworkFamily.NEURAL_NETWORK.value,
            node_type="n",
            label="B",
            ports=(
                NetworkPort("in", NetworkPortDirection.INPUT),
                NetworkPort("out", NetworkPortDirection.OUTPUT),
            ),
        )
        graph.add_node(node_a)
        graph.add_node(node_b)
        graph.add_edge(NetworkEdge("a", "out", "b", "in", 1.0))
        graph.add_edge(NetworkEdge("b", "out", "a", "in", 1.0))
        report = validate_graph(graph)
        self.assertFalse(report.is_valid)
        self.assertTrue(any(issue.code == "graph.cycle" for issue in report.errors))

    def test_cycle_is_allowed_for_spiderweb_family(self):
        graph = build_graph(NetworkFamily.SPIDERWEB_NETWORK)
        report = validate_graph(graph)
        self.assertTrue(report.is_valid)


if __name__ == "__main__":
    unittest.main()
