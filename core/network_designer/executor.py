"""Execution engines for Network Designer backend contracts."""

from __future__ import annotations

import importlib.util
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Sequence, Tuple

from .graph import NetworkFamily, NetworkGraph
from .registry import all_families
from .spiderweb import run_spiderweb_network
from .validator import validate_graph


@dataclass(frozen=True)
class NetworkExecutionResult:
    """Execution contract for deterministic graph runs."""

    status: str
    family: str
    backend: str
    outputs: Dict[str, float]
    trace: Tuple[Dict[str, Any], ...]
    warnings: Tuple[str, ...]
    errors: Tuple[str, ...]


def is_qiskit_available() -> bool:
    """Return True when optional Qiskit dependency is installed."""
    return importlib.util.find_spec("qiskit") is not None


def list_available_backends(family: str) -> Tuple[Dict[str, Any], ...]:
    """Return deterministic backend availability for a family."""
    if family not in all_families():
        raise ValueError(f"unsupported network family: {family}")
    backends: List[Dict[str, Any]] = [
        {"name": "torch_surrogate", "available": True, "label": "Deterministic Torch fallback"},
    ]
    if family == NetworkFamily.SPIDERWEB_NETWORK.value:
        backends.append({"name": "spiderweb", "available": True, "label": "Spiderweb local propagation"})
    if family in {
        NetworkFamily.QUANTUM_QNN.value,
        NetworkFamily.GRAVITY_NULL_TEST.value,
        NetworkFamily.MULTIVERSE_EXPERIMENTS.value,
        NetworkFamily.TIME_PHYSICS_EXPERIMENTS.value,
    }:
        backends.append(
            {
                "name": "qiskit",
                "available": is_qiskit_available(),
                "label": "Quantum lane (placeholder)",
            }
        )
    return tuple(backends)


def execute_network(
    graph: NetworkGraph,
    input_features: Mapping[str, float] | Sequence[float] | None = None,
    *,
    backend: str = "torch_surrogate",
) -> NetworkExecutionResult:
    """Execute a network graph using a deterministic local backend."""
    validation = validate_graph(graph)
    if not validation.is_valid:
        return NetworkExecutionResult(
            status="invalid",
            family=graph.family,
            backend=backend,
            outputs={},
            trace=(),
            warnings=(),
            errors=tuple(issue.message for issue in validation.errors),
        )

    normalized_backend = str(backend or "torch_surrogate").strip().lower()
    if normalized_backend == "torch_surrogate":
        return _execute_torch_surrogate(graph, input_features)
    if normalized_backend == "spiderweb":
        return _execute_spiderweb(graph, input_features)
    if normalized_backend == "qiskit":
        return _execute_qiskit_placeholder(graph, input_features)
    return NetworkExecutionResult(
        status="invalid",
        family=graph.family,
        backend=normalized_backend,
        outputs={},
        trace=(),
        warnings=(),
        errors=(f"unsupported backend '{normalized_backend}'",),
    )


def _execute_torch_surrogate(
    graph: NetworkGraph,
    input_features: Mapping[str, float] | Sequence[float] | None,
) -> NetworkExecutionResult:
    order = _execution_order(graph)
    input_nodes = _input_nodes(graph)
    ordered_input = sorted(input_nodes)
    feature_values = _coerce_features(input_features, ordered_input)
    outputs: Dict[str, float] = {}
    trace: List[Dict[str, Any]] = []

    node_values: Dict[str, float] = {}
    for node_id in order:
        incoming = [edge for edge in graph.edges if edge.target_node_id == node_id]
        if node_id in feature_values:
            base = feature_values[node_id]
            source = "feature"
        else:
            source = "incoming"
            base = 0.0
            for edge in incoming:
                if edge.source_node_id not in node_values:
                    continue
                weight = float(edge.weight)
                base += node_values[edge.source_node_id] * weight
        value = _deterministic_activation(base)
        node_values[node_id] = value
        trace.append({"node_id": node_id, "source": source, "value": round(value, 6)})

    output_nodes = [node_id for node_id in graph.node_ids if not graph.outgoing_edges(node_id)]
    if not output_nodes:
        output_nodes = order
    outputs = {node_id: round(node_values[node_id], 6) for node_id in output_nodes}
    return NetworkExecutionResult(
        status="ok",
        family=graph.family,
        backend="torch_surrogate",
        outputs=outputs,
        trace=tuple(trace),
        warnings=("torch_surrogate is deterministic placeholder",),
        errors=(),
    )


def _execute_spiderweb(
    graph: NetworkGraph,
    input_features: Mapping[str, float] | Sequence[float] | None,
) -> NetworkExecutionResult:
    if graph.family != NetworkFamily.SPIDERWEB_NETWORK.value:
        return NetworkExecutionResult(
            status="invalid",
            family=graph.family,
            backend="spiderweb",
            outputs={},
            trace=(),
            warnings=(),
            errors=("spiderweb backend is only available for spiderweb_network family",),
        )
    outputs = run_spiderweb_network(graph, input_values=input_features)
    trace = tuple({"node_id": node_id, "value": round(value, 6)} for node_id, value in sorted(outputs.items()))
    return NetworkExecutionResult(
        status="ok",
        family=graph.family,
        backend="spiderweb",
        outputs=outputs,
        trace=trace,
        warnings=("spiderweb is local propagation placeholder",),
        errors=(),
    )


def _execute_qiskit_placeholder(
    graph: NetworkGraph,
    input_features: Mapping[str, float] | Sequence[float] | None,
) -> NetworkExecutionResult:
    if graph.family not in {
        NetworkFamily.QUANTUM_QNN.value,
        NetworkFamily.GRAVITY_NULL_TEST.value,
        NetworkFamily.MULTIVERSE_EXPERIMENTS.value,
        NetworkFamily.TIME_PHYSICS_EXPERIMENTS.value,
    }:
        return NetworkExecutionResult(
            status="invalid",
            family=graph.family,
            backend="qiskit",
            outputs={},
            trace=(),
            warnings=(),
            errors=(
                "qiskit backend is only available for quantum_qnn, gravity_null_test, "
                "multiverse_experiments, or time_physics_experiments family",
            ),
        )

    if not is_qiskit_available():
        return NetworkExecutionResult(
            status="unavailable",
            family=graph.family,
            backend="qiskit",
            outputs={},
            trace=(),
            warnings=(),
            errors=("qiskit dependency is not installed",),
        )

    # Keep this placeholder deterministic and dependency-light. It emits a
    # clear status signal that the backend is only a contract preview.
    result = _execute_torch_surrogate(graph, input_features)
    return NetworkExecutionResult(
        status="placeholder",
        family=graph.family,
        backend="qiskit",
        outputs=result.outputs,
        trace=result.trace,
        warnings=result.warnings + ("qiskit backend output is placeholder-only",),
        errors=(),
    )


def _coerce_features(
    input_features: Mapping[str, float] | Sequence[float] | None,
    ordered_nodes: Sequence[str],
) -> Dict[str, float]:
    values: Dict[str, float] = {}
    if input_features is None:
        return values

    if isinstance(input_features, Mapping):
        for node_id in ordered_nodes:
            if node_id in input_features:
                value = input_features[node_id]
                if isinstance(value, (int, float)):
                    values[node_id] = float(value)
        return values

    for node_id, value in zip(ordered_nodes, input_features):
        if isinstance(value, (int, float)):
            values[node_id] = float(value)
    return values


def _execution_order(graph: NetworkGraph) -> Tuple[str, ...]:
    try:
        return graph.topological_order()
    except ValueError:
        return graph.node_ids


def _input_nodes(graph: NetworkGraph) -> List[str]:
    return [node_id for node_id in graph.node_ids if not graph.incoming_edges(node_id)]


def _deterministic_activation(value: float) -> float:
    return float(math.tanh(float(value)))
