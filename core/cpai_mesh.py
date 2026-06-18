"""Native CPAI mesh primitives for the local simulator.

CPAI is the local routing substrate. MCP and Datadog can observe or extend it,
but the simulator must still carry a small native CPAI state so plugin routing
does not depend on an external control plane being live.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional

from .neutrosophic_quantum_primitives import RESEARCH_BOUNDARY, SOURCE_HIERARCHY


CPAI_MESH_NODES = (
    "cpai-mcp-server",
    "cpai-celebrum",
    "cpai-ffed",
)
CPAI_MESH_METRICS = (
    "cpai.mesh.local_response_time_ms",
    "cpai.mesh.effective_response_time_ms",
    "cpai.mesh.requests_processed_local",
    "cpai.mesh.requests_forwarded",
    "cpai.mesh.requests_received",
    "cpai.mesh.nodes_visible",
    "cpai.mesh.nodes_active",
)
CPAI_SERVICE_CHECK = "cpai.mesh.can_connect"
DATADOG_MESH_DASHBOARD_ID = "4i9-v3n-pe7"
DATADOG_MESH_NOTEBOOK_ID = "293549"


def _clamp01(value: Any) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        numeric = 0.0
    return float(min(1.0, max(0.0, numeric)))


@dataclass(frozen=True)
class CPAIMeshState:
    route: str = "local-qnn"
    nodes_visible: int = 1
    nodes_active: int = 1
    local_response_time_ms: float = 0.0
    effective_response_time_ms: float = 0.0
    local_load: float = 0.0
    forwarded_load: float = 0.0
    can_connect: bool = True
    mesh_enabled: bool = True
    privacy_class: str = "public_safe"

    @classmethod
    def from_context(cls, context: Optional[Mapping[str, Any]] = None) -> "CPAIMeshState":
        context = dict(context or {})
        return cls(
            route=str(context.get("route", "local-qnn")),
            nodes_visible=max(0, int(float(context.get("nodes_visible", 1)))),
            nodes_active=max(0, int(float(context.get("nodes_active", 1)))),
            local_response_time_ms=max(0.0, float(context.get("local_response_time_ms", 0.0))),
            effective_response_time_ms=max(0.0, float(context.get("effective_response_time_ms", 0.0))),
            local_load=_clamp01(context.get("local_load", 0.0)),
            forwarded_load=_clamp01(context.get("forwarded_load", 0.0)),
            can_connect=bool(context.get("can_connect", True)),
            mesh_enabled=bool(context.get("mesh_enabled", True)),
            privacy_class=str(context.get("privacy_class", "public_safe")),
        )

    @property
    def should_forward(self) -> bool:
        if not self.mesh_enabled or not self.can_connect:
            return False
        return bool(self.nodes_active > 1 and self.local_load > 0.65)

    @property
    def routing_decision(self) -> str:
        if not self.mesh_enabled:
            return "local_only_mesh_disabled"
        if not self.can_connect:
            return "local_only_mesh_unavailable"
        if self.should_forward:
            return "forward_candidate"
        return "process_local"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "base": "CPAI mesh",
            "native": True,
            "route": self.route,
            "nodes_visible": int(self.nodes_visible),
            "nodes_active": int(self.nodes_active),
            "local_response_time_ms": float(self.local_response_time_ms),
            "effective_response_time_ms": float(self.effective_response_time_ms),
            "local_load": float(self.local_load),
            "forwarded_load": float(self.forwarded_load),
            "can_connect": bool(self.can_connect),
            "mesh_enabled": bool(self.mesh_enabled),
            "privacy_class": self.privacy_class,
            "routing_decision": self.routing_decision,
            "should_forward": self.should_forward,
            "hierarchy": SOURCE_HIERARCHY,
            "research_boundary": RESEARCH_BOUNDARY,
            "secrets_exposed": False,
        }


def cpai_mesh_profile(state: Optional[CPAIMeshState | Mapping[str, Any]] = None) -> Dict[str, Any]:
    if isinstance(state, CPAIMeshState):
        mesh_state = state
    else:
        mesh_state = CPAIMeshState.from_context(state)
    return {
        **mesh_state.as_dict(),
        "role": "native routing substrate for FNP-QNN plugin blocks",
        "nodes": list(CPAI_MESH_NODES),
        "datadog_metrics": list(CPAI_MESH_METRICS),
        "datadog_service_check": CPAI_SERVICE_CHECK,
        "service_tags": [
            "service:fnp-qnn-mesh",
            "service:fnp-qnn-local-research-simulator",
            "team:fnp-qnn",
        ],
        "datadog_dashboard_id": DATADOG_MESH_DASHBOARD_ID,
        "datadog_notebook_id": DATADOG_MESH_NOTEBOOK_ID,
        "mesh_rule": "FFeD plugin signals attach to CPAI as local measurable features; CPAI remains the native mesh base.",
    }


__all__ = [
    "CPAI_MESH_METRICS",
    "CPAI_MESH_NODES",
    "CPAI_SERVICE_CHECK",
    "CPAIMeshState",
    "DATADOG_MESH_DASHBOARD_ID",
    "DATADOG_MESH_NOTEBOOK_ID",
    "cpai_mesh_profile",
]
