import json

from fastapi.testclient import TestClient

from api import main as api_main
from core.cpai_http import CodeProjectMeshClient


class _Response:
    def __init__(self, payload: dict[str, object]):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _limit: int) -> bytes:
        return self.payload


def test_live_client_normalizes_health_and_mesh_without_raw_payloads() -> None:
    def opener(request, **_kwargs):
        if request.full_url.endswith("/summary"):
            return _Response(
                {
                    "localServer": {"isActive": True},
                    "serverInfos": [
                        {"isLocalServer": False, "isActive": True}
                        for _ in range(11)
                    ],
                    "private": "must-not-cross",
                }
            )
        return _Response(
            {
                "success": True,
                "hostname": "cpai-fnp-qnn",
                "platform": "Docker",
                "enabledRoutes": ["vision/detection"],
                "private": "must-not-cross",
            }
        )

    client = CodeProjectMeshClient(opener=opener)
    health = client.health()
    mesh = client.mesh_status()

    assert health["status"] == "success"
    assert health["node_id"] == "cpai-fnp-qnn"
    assert mesh["status"] == "success"
    assert mesh["active_peer_count"] == 11
    assert "must-not-cross" not in json.dumps((health, mesh))
    assert health["secret_values_exposed"] is False


def test_api_routes_call_real_connector_boundary(monkeypatch) -> None:
    class StubClient:
        def health(self):
            return {"status": "success", "operation": "health", "secret_values_exposed": False}

        def mesh_status(self):
            return {"status": "degraded", "operation": "mesh_status", "secret_values_exposed": False}

    monkeypatch.setattr(api_main, "cpai_client", StubClient())
    client = TestClient(api_main.app)

    assert client.get("/cpai/status").json()["operation"] == "health"
    assert client.get("/cpai/mesh").json()["operation"] == "mesh_status"


def test_unavailable_node_is_fail_closed_and_redacted() -> None:
    def unavailable(*_args, **_kwargs):
        raise OSError("offline")

    payload = CodeProjectMeshClient(opener=unavailable).health()

    assert payload["status"] == "error"
    assert payload["error_code"] == "NODE_UNAVAILABLE"
    assert payload["secret_values_exposed"] is False
