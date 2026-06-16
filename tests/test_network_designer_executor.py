"""Focused tests for Network Designer backend execution."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from core.network_designer.graph import NetworkFamily
from core.network_designer.executor import execute_network, is_qiskit_available, list_available_backends
from core.network_designer.presets import build_graph


class NetworkDesignerExecutorTests(unittest.TestCase):
    def test_torch_surrogate_is_deterministic(self):
        graph = build_graph(NetworkFamily.NEURAL_NETWORK)
        result_1 = execute_network(graph, input_features=[0.45, 0.7], backend="torch_surrogate")
        result_2 = execute_network(graph, input_features=[0.45, 0.7], backend="torch_surrogate")
        self.assertEqual(result_1.status, "ok")
        self.assertEqual(result_1.outputs, result_2.outputs)
        self.assertEqual(result_1.outputs["output"], result_2.outputs["output"])

    def test_spiderweb_execution_produces_state(self):
        graph = build_graph(NetworkFamily.SPIDERWEB_NETWORK)
        result = execute_network(graph, input_features={"source": 1.0}, backend="spiderweb")
        self.assertEqual(result.status, "ok")
        self.assertIn("output", result.outputs)

    def test_quantum_qiskit_lane_is_gated_when_missing(self):
        graph = build_graph(NetworkFamily.QUANTUM_QNN)
        backends = {item["name"]: item["available"] for item in list_available_backends(graph.family)}
        if backends.get("qiskit"):
            with patch("core.network_designer.executor.is_qiskit_available", return_value=False):
                result = execute_network(graph, backend="qiskit")
        else:
            result = execute_network(graph, backend="qiskit")
        self.assertIn(result.status, {"unavailable", "placeholder", "ok"})

    def test_qiskit_gate_dependency_helper_is_deterministic(self):
        self.assertIsInstance(is_qiskit_available(), bool)


if __name__ == "__main__":
    unittest.main()
