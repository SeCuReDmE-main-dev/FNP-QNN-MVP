"""Local spiderweb propagation placeholder."""

from __future__ import annotations

import math
from typing import Dict, Mapping, Sequence, Tuple

from .graph import NetworkGraph


def run_spiderweb_network(
    graph: NetworkGraph,
    input_values: Mapping[str, float] | Sequence[float] | None = None,
    iterations: int = 4,
) -> Dict[str, float]:
    """Run a deterministic local propagation pass over a spiderweb graph."""
    state: Dict[str, float] = _seed_values(graph, input_values)
    iterations = max(1, int(iterations))

    for _ in range(iterations):
        next_state = dict(state)
        for edge in graph.edges:
            source_value = state.get(edge.source_node_id, 0.0)
            next_state[edge.target_node_id] = _clamp_tanh(next_state.get(edge.target_node_id, 0.0) + source_value * edge.weight)
        if next_state == state:
            break
        state = next_state

    return state


def _seed_values(
    graph: NetworkGraph,
    input_values: Mapping[str, float] | Sequence[float] | None,
) -> Dict[str, float]:
    source_nodes = [node_id for node_id in graph.node_ids if not graph.incoming_edges(node_id)]
    state: Dict[str, float] = {}
    if input_values is None:
        for idx, node_id in enumerate(source_nodes):
            if idx == 0:
                state[node_id] = 1.0
        return state

    if isinstance(input_values, Mapping):
        normalized = [(str(key), float(value)) for key, value in input_values.items() if isinstance(value, (int, float)) or hasattr(value, "__float__")]
    else:
        normalized = [(str(idx), float(value)) for idx, value in enumerate(input_values)]

    if not normalized:
        for idx, node_id in enumerate(source_nodes):
            if idx == 0:
                state[node_id] = 1.0
        return state

    for source_index, node_id in enumerate(source_nodes):
        if source_index >= len(normalized):
            break
        state[node_id] = normalized[source_index][1]
    return state


def _clamp_tanh(value: float) -> float:
    return float(math.tanh(float(value)))

