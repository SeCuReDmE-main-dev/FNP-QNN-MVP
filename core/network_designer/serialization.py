"""JSON serialization helpers for Network Designer graphs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .graph import NetworkGraph
from .validator import assert_valid_graph


SCHEMA_VERSION = "1.0.0"


def serialize_graph(graph: NetworkGraph) -> str:
    """Serialize a network graph into deterministic JSON."""
    payload = graph.to_dict()
    payload["schema_version"] = SCHEMA_VERSION
    return json.dumps(payload, sort_keys=True, indent=2, separators=(",", ": "))

 

def deserialize_graph(payload: str | bytes | bytearray | Mapping[str, Any], *, validate: bool = True) -> NetworkGraph:
    """Deserialize a network graph from JSON string/bytes or mapping."""
    if isinstance(payload, (str, bytes, bytearray)):
        data = json.loads(payload)
    else:
        if not isinstance(payload, Mapping):
            raise TypeError("payload must be JSON string, bytes, or mapping")
        data = payload
    graph = NetworkGraph.from_dict(data)
    if validate:
        assert_valid_graph(graph)
    return graph


def write_json_file(graph: NetworkGraph, path: str) -> None:
    Path(path).write_text(serialize_graph(graph), encoding="utf-8")


def read_json_file(path: str, *, validate: bool = True) -> NetworkGraph:
    payload = Path(path).read_text(encoding="utf-8")
    return deserialize_graph(payload, validate=validate)
