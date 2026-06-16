"""Typed graph model for the Network Designer backend contract."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Mapping, Sequence, Tuple


_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]+$")
GRAPH_SCHEMA_VERSION = "1.0.0"


class NetworkFamily(str, Enum):
    """Supported network families for deterministic backend execution."""

    NEURAL_NETWORK = "neural_network"
    QUANTUM_QNN = "quantum_qnn"
    SPIDERWEB_NETWORK = "spiderweb_network"
    MEMORY_GRAPH = "memory_graph"
    CROSSMODAL_GRAPH = "crossmodal_graph"
    LOGIC_DECISION_NETWORK = "logic_decision_network"
    CUSTOM_NETWORK = "custom_network"


class NetworkPortDirection(str, Enum):
    """Allowed port direction values."""

    INPUT = "input"
    OUTPUT = "output"


@dataclass(frozen=True)
class NetworkPort:
    """Typed port definition attached to a network node."""

    port_id: str
    direction: NetworkPortDirection
    label: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._validate_port_id(self.port_id, "port_id")
        self._validate_direction(self.direction)

    @staticmethod
    def _validate_port_id(port_id: str, label: str) -> None:
        if not isinstance(port_id, str) or not port_id:
            raise ValueError(f"{label} must be a non-empty string")
        if not _ID_PATTERN.match(port_id):
            raise ValueError(f"{label} '{port_id}' contains invalid characters")

    @staticmethod
    def _validate_direction(direction: NetworkPortDirection) -> None:
        if direction not in {NetworkPortDirection.INPUT, NetworkPortDirection.OUTPUT}:
            raise ValueError("direction must be 'input' or 'output'")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "port_id": self.port_id,
            "direction": self.direction.value,
            "label": self.label,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "NetworkPort":
        return cls(
            port_id=str(payload["port_id"]),
            direction=NetworkPortDirection(str(payload["direction"])),
            label=str(payload.get("label", "")),
            metadata=dict(payload.get("metadata", {})),
        )


@dataclass(frozen=True)
class NetworkNode:
    """Typed node definition for the graph contract."""

    node_id: str
    family: str
    node_type: str
    label: str
    ports: Tuple[NetworkPort, ...] = field(default_factory=tuple)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._validate_node_id(self.node_id)
        if not self.label:
            raise ValueError("label must be a non-empty string")
        if not self.node_type:
            raise ValueError("node_type must be a non-empty string")
        port_ids = [port.port_id for port in self.ports]
        if len(port_ids) != len(set(port_ids)):
            raise ValueError(f"duplicate port ids for node '{self.node_id}'")
        object.__setattr__(self, "ports", tuple(self.ports))

    @staticmethod
    def _validate_node_id(node_id: str) -> None:
        if not isinstance(node_id, str) or not node_id:
            raise ValueError("node_id must be a non-empty string")
        if not _ID_PATTERN.match(node_id):
            raise ValueError(f"node_id '{node_id}' contains invalid characters")

    def get_port(self, port_id: str) -> NetworkPort:
        for port in self.ports:
            if port.port_id == port_id:
                return port
        raise KeyError(f"port '{port_id}' not found on node '{self.node_id}'")

    @property
    def port_ids(self) -> Tuple[str, ...]:
        return tuple(port.port_id for port in self.ports)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "family": self.family,
            "node_type": self.node_type,
            "label": self.label,
            "ports": [port.to_dict() for port in sorted(self.ports, key=lambda p: p.port_id)],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "NetworkNode":
        return cls(
            node_id=str(payload["node_id"]),
            family=str(payload["family"]),
            node_type=str(payload["node_type"]),
            label=str(payload["label"]),
            ports=tuple(
                NetworkPort.from_dict(port_payload) for port_payload in payload.get("ports", ())
            ),
            metadata=dict(payload.get("metadata", {})),
        )


@dataclass(frozen=True)
class NetworkEdge:
    """Directed typed edge for network execution."""

    source_node_id: str
    source_port_id: str
    target_node_id: str
    target_port_id: str
    weight: float = 1.0

    def __post_init__(self) -> None:
        if self.source_node_id == self.target_node_id and self.source_port_id == self.target_port_id:
            raise ValueError("source and target ports on same edge cannot be identical")
        if not isinstance(self.weight, (int, float)):
            raise ValueError("weight must be numeric")
        if self.weight <= 0.0:
            raise ValueError("edge weight must be strictly positive")
        NetworkNode._validate_node_id(self.source_node_id)
        NetworkNode._validate_node_id(self.target_node_id)
        NetworkPort._validate_port_id(self.source_port_id, "source_port_id")
        NetworkPort._validate_port_id(self.target_port_id, "target_port_id")

    def key(self) -> Tuple[str, str, str, str]:
        return (
            self.source_node_id,
            self.source_port_id,
            self.target_node_id,
            self.target_port_id,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_node_id": self.source_node_id,
            "source_port_id": self.source_port_id,
            "target_node_id": self.target_node_id,
            "target_port_id": self.target_port_id,
            "weight": float(self.weight),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "NetworkEdge":
        return cls(
            source_node_id=str(payload["source_node_id"]),
            source_port_id=str(payload["source_port_id"]),
            target_node_id=str(payload["target_node_id"]),
            target_port_id=str(payload["target_port_id"]),
            weight=float(payload["weight"]),
        )


class NetworkGraph:
    """Dependency-light directed graph model for Network Designer backend contracts."""

    def __init__(self, family: str, metadata: Mapping[str, Any] | None = None) -> None:
        self.family = family
        self.metadata: Dict[str, Any] = dict(metadata or {})
        self.nodes: Dict[str, NetworkNode] = {}
        self.edges: List[NetworkEdge] = []

    @property
    def node_ids(self) -> Tuple[str, ...]:
        return tuple(sorted(self.nodes))

    def add_node(self, node: NetworkNode) -> NetworkNode:
        node_id = node.node_id
        if node_id in self.nodes:
            raise ValueError(f"duplicate node id: {node_id}")
        self.nodes[node_id] = node
        return node

    def add_edge(self, edge: NetworkEdge) -> NetworkEdge:
        if edge.source_node_id not in self.nodes:
            raise ValueError(f"source node '{edge.source_node_id}' not found")
        if edge.target_node_id not in self.nodes:
            raise ValueError(f"target node '{edge.target_node_id}' not found")
        source_node = self.get_node(edge.source_node_id)
        target_node = self.get_node(edge.target_node_id)
        try:
            source_port = source_node.get_port(edge.source_port_id)
        except KeyError as exc:
            raise ValueError(f"source port '{edge.source_port_id}' not found on node '{edge.source_node_id}'") from exc
        try:
            target_port = target_node.get_port(edge.target_port_id)
        except KeyError as exc:
            raise ValueError(f"target port '{edge.target_port_id}' not found on node '{edge.target_node_id}'") from exc
        if source_port.direction != NetworkPortDirection.OUTPUT:
            raise ValueError("source port must be an output port")
        if target_port.direction != NetworkPortDirection.INPUT:
            raise ValueError("target port must be an input port")
        if edge.key() in {existing.key() for existing in self.edges}:
            raise ValueError(f"duplicate edge: {edge.key()}")
        self.edges.append(edge)
        return edge

    def get_node(self, node_id: str) -> NetworkNode:
        try:
            return self.nodes[node_id]
        except KeyError as exc:
            raise KeyError(f"node '{node_id}' does not exist") from exc

    def get_port(self, node_id: str, port_id: str) -> NetworkPort:
        return self.get_node(node_id).get_port(port_id)

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    def incoming_edges(self, node_id: str) -> Tuple[NetworkEdge, ...]:
        return tuple(edge for edge in self.edges if edge.target_node_id == node_id)

    def outgoing_edges(self, node_id: str) -> Tuple[NetworkEdge, ...]:
        return tuple(edge for edge in self.edges if edge.source_node_id == node_id)

    def topological_order(self) -> Tuple[str, ...]:
        order: List[str] = []
        in_degree = {node_id: 0 for node_id in self.nodes}
        outgoing: Dict[str, List[str]] = {node_id: [] for node_id in self.nodes}
        for edge in self.edges:
            in_degree[edge.target_node_id] += 1
            outgoing[edge.source_node_id].append(edge.target_node_id)

        available = sorted(node_id for node_id, degree in in_degree.items() if degree == 0)
        while available:
            current = available.pop(0)
            order.append(current)
            for target in outgoing.get(current, []):
                in_degree[target] -= 1
                if in_degree[target] == 0:
                    available.append(target)
                    available.sort()
        if len(order) != len(self.nodes):
            raise ValueError("graph has at least one cycle; topological order is undefined")
        return tuple(order)

    def has_cycle(self) -> bool:
        try:
            self.topological_order()
            return False
        except ValueError:
            return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": GRAPH_SCHEMA_VERSION,
            "family": self.family,
            "metadata": dict(self.metadata),
            "nodes": [self.nodes[node_id].to_dict() for node_id in self.node_ids],
            "edges": [edge.to_dict() for edge in sorted(self.edges, key=lambda edge: edge.key())],
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "NetworkGraph":
        if not isinstance(payload, Mapping):
            raise TypeError("payload must be a mapping")
        family = str(payload.get("family", ""))
        graph = cls(family=family, metadata=dict(payload.get("metadata", {})))
        nodes = payload.get("nodes", ())
        if not isinstance(nodes, Sequence):
            raise TypeError("nodes must be a sequence")
        for node_payload in nodes:
            graph.add_node(NetworkNode.from_dict(node_payload))
        edges = payload.get("edges", ())
        if not isinstance(edges, Sequence):
            raise TypeError("edges must be a sequence")
        for edge_payload in edges:
            graph.add_edge(NetworkEdge.from_dict(edge_payload))
        return graph
