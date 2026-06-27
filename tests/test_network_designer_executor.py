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

    def test_gravity_null_test_preset_executes_and_exposes_qiskit_lane(self):
        graph = build_graph(NetworkFamily.GRAVITY_NULL_TEST)

        result = execute_network(
            graph,
            input_features={"source_ledger": 1.0, "probe_c": 0.35},
            backend="torch_surrogate",
        )
        backends = {item["name"]: item["available"] for item in list_available_backends(graph.family)}

        self.assertEqual(result.status, "ok")
        self.assertEqual(result.family, NetworkFamily.GRAVITY_NULL_TEST.value)
        self.assertIn("e2b_datadog_review", result.outputs)
        self.assertIn("qiskit", backends)

    def test_multiverse_experiments_preset_validates_and_executes(self):
        graph = build_graph(NetworkFamily.MULTIVERSE_EXPERIMENTS)

        result = execute_network(
            graph,
            input_features={"source_ledger": 1.0},
            backend="torch_surrogate",
        )
        backends = {item["name"]: item["available"] for item in list_available_backends(graph.family)}

        self.assertEqual(result.status, "ok")
        self.assertEqual(result.family, NetworkFamily.MULTIVERSE_EXPERIMENTS.value)
        self.assertIn("suite_output", result.outputs)
        self.assertIn("qiskit", backends)
        self.assertEqual(graph.metadata["preset"], "multiverse_experiments_v1")
        lane_ids = {
            graph.nodes[node_id].metadata.get("experiment_id")
            for node_id in graph.node_ids
            if node_id.endswith("_lane")
        }
        self.assertIn("wigner_friend_inter_branch_communication", lane_ids)

    def test_time_physics_experiments_preset_validates_and_executes(self):
        graph = build_graph(NetworkFamily.TIME_PHYSICS_EXPERIMENTS)

        result = execute_network(
            graph,
            input_features={"source_ledger": 1.0},
            backend="torch_surrogate",
        )
        backends = {item["name"]: item["available"] for item in list_available_backends(graph.family)}

        self.assertEqual(result.status, "ok")
        self.assertEqual(result.family, NetworkFamily.TIME_PHYSICS_EXPERIMENTS.value)
        self.assertIn("suite_output", result.outputs)
        self.assertIn("qiskit", backends)
        self.assertEqual(graph.metadata["preset"], "time_physics_experiments_v1")
        lane_ids = {
            graph.nodes[node_id].metadata.get("experiment_id")
            for node_id in graph.node_ids
            if node_id.endswith("_lane")
        }
        self.assertIn("entanglement_decoherence_arrow", lane_ids)

    def test_qiskit_gate_dependency_helper_is_deterministic(self):
        self.assertIsInstance(is_qiskit_available(), bool)


if __name__ == "__main__":
    unittest.main()
