"""Bounded HTTP connector to FNP-QNN's embedded CodeProject.AI node."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


CONTRACT_VERSION = "securedme.codeproject.mesh.v1"
DEFAULT_CPAI_URL = "http://127.0.0.1:32172"
MAX_RESPONSE_BYTES = 4 * 1024 * 1024


@dataclass
class CodeProjectMeshClient:
    """Read-only operational connector; scientific execution stays independent."""

    base_url: str = DEFAULT_CPAI_URL
    timeout_seconds: float = 5.0
    opener: Any = urlopen

    def _error(self, operation: str, code: str) -> dict[str, Any]:
        return {
            "contract": CONTRACT_VERSION,
            "status": "error",
            "operation": operation,
            "error_code": code,
            "node_id": "cpai-fnp-qnn",
            "secret_values_exposed": False,
        }

    def _request(self, route: str, operation: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        request = Request(
            self.base_url.rstrip("/") + route,
            method="GET",
            headers={"Accept": "application/json", "User-Agent": "fnp-qnn-mvp/1.3"},
        )
        try:
            with self.opener(request, timeout=max(0.1, float(self.timeout_seconds))) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
        except (HTTPError, URLError, OSError, TimeoutError):
            return None, self._error(operation, "NODE_UNAVAILABLE")
        if len(raw) > MAX_RESPONSE_BYTES:
            return None, self._error(operation, "INVALID_RESPONSE")
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None, self._error(operation, "INVALID_RESPONSE")
        if not isinstance(payload, dict):
            return None, self._error(operation, "INVALID_RESPONSE")
        return payload, None

    def health(self) -> dict[str, Any]:
        payload, error = self._request("/v1/server/mesh/status", "health")
        if error:
            return error
        assert payload is not None
        routes = payload.get("enabledRoutes")
        return {
            "contract": CONTRACT_VERSION,
            "status": "success" if payload.get("success") is True else "degraded",
            "operation": "health",
            "node_id": str(payload.get("hostname") or "cpai-fnp-qnn"),
            "reachable": True,
            "platform": str(payload.get("platform") or "unknown"),
            "route_count": len(routes) if isinstance(routes, list) else 0,
            "secret_values_exposed": False,
        }

    def mesh_status(self, expected_peer_count: int = 11) -> dict[str, Any]:
        payload, error = self._request("/v1/server/mesh/summary", "mesh_status")
        if error:
            return error
        assert payload is not None
        local = payload.get("localServer") if isinstance(payload.get("localServer"), dict) else {}
        peers = payload.get("serverInfos") if isinstance(payload.get("serverInfos"), list) else []
        active_peers = sum(
            item.get("isActive") is True
            for item in peers
            if isinstance(item, dict) and item.get("isLocalServer") is not True
        )
        ready = local.get("isActive") is True and active_peers >= expected_peer_count
        return {
            "contract": CONTRACT_VERSION,
            "status": "success" if ready else "degraded",
            "operation": "mesh_status",
            "node_id": "cpai-fnp-qnn",
            "active_peer_count": active_peers,
            "expected_peer_count": expected_peer_count,
            "error_code": None if ready else "MESH_DEGRADED",
            "secret_values_exposed": False,
        }


__all__ = [
    "CONTRACT_VERSION",
    "DEFAULT_CPAI_URL",
    "CodeProjectMeshClient",
]
