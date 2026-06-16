"""Network Designer backend contract primitives."""

from .executor import (
    NetworkExecutionResult,
    execute_network,
    is_qiskit_available,
    list_available_backends,
)
from .graph import (
    NetworkEdge,
    NetworkFamily,
    NetworkGraph,
    NetworkNode,
    NetworkPort,
    NetworkPortDirection,
)
from .presets import NetworkPreset, get_preset, get_supported_families, list_presets
from .serialization import deserialize_graph, serialize_graph
from .serialization import write_json_file, read_json_file
from .validator import NetworkValidationReport, ValidationIssue, validate_graph

__all__ = [
    "execute_network",
    "is_qiskit_available",
    "list_available_backends",
    "NetworkEdge",
    "NetworkExecutionResult",
    "NetworkFamily",
    "NetworkGraph",
    "NetworkNode",
    "NetworkPort",
    "NetworkPortDirection",
    "NetworkPreset",
    "get_preset",
    "get_supported_families",
    "list_presets",
    "deserialize_graph",
    "serialize_graph",
    "read_json_file",
    "write_json_file",
    "NetworkValidationReport",
    "ValidationIssue",
    "validate_graph",
]
