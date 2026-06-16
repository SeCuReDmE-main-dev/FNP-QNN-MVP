"""Validation helpers for Network Designer graph contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .graph import NetworkEdge, NetworkFamily, NetworkGraph, NetworkNode, NetworkPortDirection
from .registry import all_families, supports_cycles


@dataclass(frozen=True)
class ValidationIssue:
    """Single deterministic validation issue."""

    code: str
    message: str
    subject: str = ""


@dataclass(frozen=True)
class NetworkValidationReport:
    """Structured validation result for graph contracts."""

    is_valid: bool
    errors: tuple[ValidationIssue, ...]
    warnings: tuple[ValidationIssue, ...]


def validate_graph(graph: NetworkGraph) -> NetworkValidationReport:
    """Validate topology and identifiers and return a deterministic report."""
    errors: List[ValidationIssue] = []
    warnings: List[ValidationIssue] = []

    if graph.family not in all_families():
        errors.append(ValidationIssue("family.unsupported", f"unsupported family: {graph.family}", "graph.family"))
        return NetworkValidationReport(False, tuple(errors), tuple(warnings))

    node_ids = list(graph.node_ids)
    for node in graph.nodes.values():
        _validate_node(graph.family, node, errors)

    edge_keys: Dict[tuple[str, str, str, str], int] = {}
    for edge in graph.edges:
        _validate_edge(graph, edge, edge_keys, errors, warnings)

    if not supports_cycles(graph.family) and graph.has_cycle():
        errors.append(ValidationIssue("graph.cycle", "cycles are not supported for this family", "edges"))

    if len(graph.nodes) == 0:
        warnings.append(ValidationIssue("graph.empty", "graph has no nodes", "graph"))

    return NetworkValidationReport(len(errors) == 0, tuple(errors), tuple(warnings))


def _validate_node(family: str, node: NetworkNode, errors: List[ValidationIssue]) -> None:
    if node.family != family:
        errors.append(
            ValidationIssue(
                "node.family_mismatch",
                f"node '{node.node_id}' family '{node.family}' does not match graph family '{family}'",
                f"node.{node.node_id}.family",
            )
        )
    if not node.ports:
        errors.append(
            ValidationIssue(
                "node.empty_ports",
                f"node '{node.node_id}' has no ports",
                f"node.{node.node_id}.ports",
            )
        )


def _validate_edge(
    graph: NetworkGraph,
    edge: NetworkEdge,
    edge_keys: Dict[tuple[str, str, str, str], int],
    errors: List[ValidationIssue],
    warnings: List[ValidationIssue],
) -> None:
    if edge.source_node_id not in graph.nodes:
        errors.append(
            ValidationIssue(
                "edge.invalid_source",
                f"edge source node '{edge.source_node_id}' not found",
                "edge.source_node_id",
            )
        )
        return
    if edge.target_node_id not in graph.nodes:
        errors.append(
            ValidationIssue(
                "edge.invalid_target",
                f"edge target node '{edge.target_node_id}' not found",
                "edge.target_node_id",
            )
        )
        return

    if edge.key() in edge_keys:
        errors.append(
            ValidationIssue(
                "edge.duplicate",
                f"duplicate edge with key '{edge.key()}'",
                f"edge[{edge_keys[edge.key()]}]",
            )
        )
    else:
        edge_keys[edge.key()] = len(edge_keys)

    try:
        source_port = graph.get_port(edge.source_node_id, edge.source_port_id)
    except KeyError:
        errors.append(
            ValidationIssue(
                "edge.missing_source_port",
                f"source port '{edge.source_port_id}' not found on node '{edge.source_node_id}'",
                f"edge.source_port_id",
            )
        )
        source_port = None
    try:
        target_port = graph.get_port(edge.target_node_id, edge.target_port_id)
    except KeyError:
        errors.append(
            ValidationIssue(
                "edge.missing_target_port",
                f"target port '{edge.target_port_id}' not found on node '{edge.target_node_id}'",
                f"edge.target_port_id",
            )
        )
        target_port = None

    if source_port is not None and source_port.direction != NetworkPortDirection.OUTPUT:
        errors.append(
            ValidationIssue(
                "edge.invalid_source_direction",
                f"source port '{edge.source_port_id}' on '{edge.source_node_id}' must be output",
                f"edge.{edge.source_node_id}.source_port_id",
            )
        )
    if target_port is not None and target_port.direction != NetworkPortDirection.INPUT:
        errors.append(
            ValidationIssue(
                "edge.invalid_target_direction",
                f"target port '{edge.target_port_id}' on '{edge.target_node_id}' must be input",
                f"edge.{edge.target_node_id}.target_port_id",
            )
        )

    if source_port is not None and source_port == target_port:
        warnings.append(
            ValidationIssue(
                "edge.port_linking_redundant",
                "edge reuses same port object for source and target (unlikely in strict graph designs)",
                "edge",
            )
        )


def assert_valid_graph(graph: NetworkGraph) -> NetworkValidationReport:
    """Raise ValueError if a graph is invalid, else return its report."""
    report = validate_graph(graph)
    if not report.is_valid:
        messages = [issue.message for issue in report.errors]
        raise ValueError("invalid network graph: " + "; ".join(messages))
    return report

