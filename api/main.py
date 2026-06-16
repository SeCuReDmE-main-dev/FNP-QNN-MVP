"""FastAPI surface for the local FNP-QNN research simulator."""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional, Sequence

import numpy as np
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_ROOT = os.path.join(PROJECT_ROOT, "web")

sys.path.append(PROJECT_ROOT)

from api.schemas import CommandRequest, CommandResponse, EncodeRequest, QNNSmokeRequest, RuntimeRunRequest
from core import CerebrumAdapter, CerebrumRuntimeBridge, LifeScienceObservationPort, PhiFramework, QNNNucleus
from core.cerebrum_adapter import MODALITIES

app = FastAPI(
    title="FNP-QNN Local Research Simulator API",
    description="Typed, non-clinical local research surface for Cerebrum-style runtime events and QNN candidates.",
    version="1.3.0-alpha-local",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9002", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.isdir(WEB_ROOT):
    app.mount("/dashboard/static", StaticFiles(directory=WEB_ROOT), name="dashboard-static")

phi_engine = PhiFramework()
cerebrum_adapter = CerebrumAdapter()
qnn_nucleus = QNNNucleus(adapter=cerebrum_adapter)
cerebrum_runtime_bridge = CerebrumRuntimeBridge(adapter=cerebrum_adapter)
life_science_port = LifeScienceObservationPort()


def build_demo_observations() -> List[Dict[str, Any]]:
    return cerebrum_adapter.default_observations()


def build_demo_samples() -> tuple[list[list[dict[str, Any]]], list[int]]:
    sample_a = build_demo_observations()
    sample_b = [
        {"modality": "audio", "value": 0.28, "timestamp": 0.0, "label": "voice", "source": "demo"},
        {"modality": "video", "value": 0.72, "timestamp": 0.7, "label": "motion", "source": "demo"},
        {"modality": "text", "value": 0.84, "timestamp": 1.4, "label": "caption", "source": "demo"},
        {"modality": "stimuli", "value": 0.40, "timestamp": 2.1, "label": "prompt", "source": "demo"},
    ]
    sample_c = [
        {"modality": "audio", "value": 0.89, "timestamp": 0.0, "label": "rhythm", "source": "demo"},
        {"modality": "video", "value": 0.33, "timestamp": 0.6, "label": "flash", "source": "demo"},
        {"modality": "text", "value": 0.52, "timestamp": 1.3, "label": "token", "source": "demo"},
        {"modality": "stimuli", "value": 0.91, "timestamp": 2.5, "label": "trigger", "source": "demo"},
    ]
    return [sample_a, sample_b, sample_c], [0, 1, 1]


def _encode_observations(observations: Sequence[Any]) -> Dict[str, Any]:
    bundle = cerebrum_adapter.build_bundle(observations)
    vector = cerebrum_adapter.bundle_to_vector(bundle)
    return {
        "sequence_length": bundle.sequence_length,
        "summary": bundle.summary,
        "feature_vector": vector.tolist(),
        "feature_dimension": int(vector.shape[0]),
        "transition_matrix": bundle.transition_matrix.tolist(),
    }


def _runtime_payload(payload: Dict[str, Any] | None) -> Dict[str, Any]:
    if not payload:
        return cerebrum_runtime_bridge.default_payload()
    runtime_keys = {"memories", "events", "observations", "statefield"}
    if not any(key in payload for key in runtime_keys):
        return cerebrum_runtime_bridge.default_payload()
    if "statefield" in payload:
        observations = life_science_port.statefield_to_observations(payload["statefield"])
        return {"memories": observations}
    return payload


def _serialize_benchmark(benchmark: Sequence[Any]) -> List[Dict[str, Any]]:
    return [
        {
            "candidate": item.candidate,
            "available": item.available,
            "backend": item.backend,
            "notes": item.notes,
            "train_accuracy": item.train_accuracy,
            "test_accuracy": item.test_accuracy,
            "predicted_probability": item.predicted_probability,
            "feature_dimension": item.feature_dimension,
        }
        for item in benchmark
    ]


def _json_safe_qnn_result(result: Dict[str, Any]) -> Dict[str, Any]:
    safe = dict(result)
    bundle = safe.pop("bundle", None)
    if bundle is not None:
        safe["bundle"] = {
            "sequence_length": bundle.sequence_length,
            "summary": bundle.summary,
            "modality_counts": bundle.modality_counts,
            "modality_means": bundle.modality_means,
            "modality_stds": bundle.modality_stds,
            "transition_matrix": bundle.transition_matrix.tolist(),
        }
    return safe


def _runtime_result(payload: Dict[str, Any] | None, run_qnn: bool = False) -> Dict[str, Any]:
    runtime_payload = _runtime_payload(payload)
    state = cerebrum_runtime_bridge.build_state(
        runtime_payload,
        qnn_nucleus=qnn_nucleus if run_qnn else None,
        label=float((payload or {}).get("label", 1.0)),
        max_epochs=int((payload or {}).get("epochs", 12)),
    )
    result = state.to_dict()
    if run_qnn:
        samples, labels = build_demo_samples()
        runtime_label = 1 if float((payload or {}).get("label", 1)) >= 0.5 else 0
        benchmark_samples = [state.observations, *samples, state.observations, *samples]
        benchmark_labels = [runtime_label, 0, 1, 0, 1 - runtime_label, 1, 0, 1]
        if result.get("qnn_result"):
            result["qnn_result"] = _json_safe_qnn_result(result["qnn_result"])
        result["benchmark"] = _serialize_benchmark(qnn_nucleus.benchmark(benchmark_samples, benchmark_labels))
    return result


def _legacy_runtime_result() -> Dict[str, Any]:
    legacy_root = os.path.join(PROJECT_ROOT, "examples")
    bridge = CerebrumRuntimeBridge(adapter=cerebrum_adapter, legacy_cerebrum_path=legacy_root)
    nucleus = QNNNucleus(adapter=bridge.adapter)
    state = bridge.build_state(None, qnn_nucleus=nucleus, max_epochs=6)
    result = state.to_dict()
    result["legacy_cerebrum_path"] = legacy_root
    result["legacy_cerebrum_path_exists"] = bridge.status(qnn_nucleus=nucleus)["legacy_cerebrum_path_exists"]
    return result


@app.get("/dashboard", include_in_schema=False)
async def dashboard() -> FileResponse:
    index_path = os.path.join(WEB_ROOT, "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Dashboard assets not found")
    return FileResponse(index_path)


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "message": "FNP-QNN local research simulator API active",
        "mode": "alpha-local-non-clinical",
        "phi": phi_engine.phi,
        "qnn_candidates": [candidate.name for candidate in qnn_nucleus.candidate_matrix()],
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    backend = cerebrum_runtime_bridge.status(qnn_nucleus=qnn_nucleus)["qnn_backend"]
    return {
        "status": "healthy",
        "mode": "alpha-local-research",
        "clinical_use": False,
        "phi_framework": "synthetic-research",
        "cerebrum_adapter": "operational",
        "qnn_backend": backend,
        "golden_ratio": phi_engine.phi,
        "quantum_particles": len(phi_engine.quantum_states),
    }


@app.get("/cerebrum/status")
async def cerebrum_status() -> Dict[str, Any]:
    observations = build_demo_observations()
    return {
        "status": "ok",
        "bundle": _encode_observations(observations),
        "modalities": list(MODALITIES),
    }


@app.post("/cerebrum/encode")
async def cerebrum_encode(payload: EncodeRequest) -> Dict[str, Any]:
    observations = [item.model_dump(exclude_none=True) for item in payload.observations] or build_demo_observations()
    return {"status": "ok", "encoded": _encode_observations(observations)}


@app.get("/cerebrum/runtime/status")
async def cerebrum_runtime_status() -> Dict[str, Any]:
    return cerebrum_runtime_bridge.status(qnn_nucleus=qnn_nucleus)


@app.post("/cerebrum/runtime/ingest")
async def cerebrum_runtime_ingest(payload: RuntimeRunRequest) -> Dict[str, Any]:
    events, pairs, warnings = cerebrum_runtime_bridge.ingest(_runtime_payload(payload.to_runtime_payload()))
    return {
        "status": "ok",
        "events": [event.to_dict() for event in events],
        "pairs": [pair.to_dict() for pair in pairs],
        "warnings": warnings,
    }


@app.post("/cerebrum/runtime/pairs")
async def cerebrum_runtime_pairs(payload: RuntimeRunRequest) -> Dict[str, Any]:
    events, pairs, warnings = cerebrum_runtime_bridge.ingest(_runtime_payload(payload.to_runtime_payload()))
    return {
        "status": "ok",
        "event_count": len(events),
        "pairs": [pair.to_dict() for pair in pairs],
        "warnings": warnings,
    }


@app.post("/cerebrum/runtime/run")
async def cerebrum_runtime_run(payload: RuntimeRunRequest) -> Dict[str, Any]:
    return {"status": "ok", "runtime": _runtime_result(payload.to_runtime_payload(), run_qnn=payload.run_qnn)}


@app.get("/cerebrum/runtime/legacy-demo")
async def cerebrum_runtime_legacy_demo() -> Dict[str, Any]:
    return {"status": "ok", "runtime": _legacy_runtime_result()}


@app.get("/qnn/candidates")
async def qnn_candidates() -> Dict[str, Any]:
    return {
        "status": "ok",
        "candidates": [
            {
                "name": candidate.name,
                "role": candidate.role,
                "available": candidate.available,
                "backend": candidate.backend,
                "notes": candidate.notes,
            }
            for candidate in qnn_nucleus.candidate_matrix()
        ],
    }


@app.post("/qnn/smoke")
async def qnn_smoke(payload: QNNSmokeRequest) -> Dict[str, Any]:
    samples = payload.dump_samples()
    labels = payload.labels
    if not samples or not labels:
        samples, labels = build_demo_samples()
    result = _json_safe_qnn_result(qnn_nucleus.smoke_run(
        samples[0],
        label=float(labels[0]) if labels else 1.0,
        max_epochs=payload.epochs,
        test_size=payload.test_size,
    ))
    return {
        "status": "ok",
        "result": result,
        "benchmark": _serialize_benchmark(qnn_nucleus.benchmark(samples, labels)),
    }


def _command_response(command_name: str, request: Optional[CommandRequest] = None) -> CommandResponse:
    request = request or CommandRequest()
    if command_name == "phi-status":
        particles = phi_engine.generate_quantum_particles(100)
        return CommandResponse(
            success=True,
            output=f"Phi research status: golden_ratio={phi_engine.phi:.12f}; synthetic_particles={len(particles)}",
            type="phi-system",
            data={"phi": phi_engine.phi, "particles": len(particles)},
        )
    if command_name == "cerebrum-runtime-status":
        return CommandResponse(
            success=True,
            output="Cerebrum runtime bridge operational.",
            type="cerebrum-runtime",
            data=cerebrum_runtime_bridge.status(qnn_nucleus=qnn_nucleus),
        )
    if command_name == "cerebrum-runtime-run":
        payload = request.payload.to_runtime_payload() if request.payload is not None else {}
        result = _runtime_result(payload, run_qnn=True)
        qnn_backend = (result.get("qnn_result") or {}).get("backend", "not-run")
        return CommandResponse(
            success=True,
            output=(
                "Cerebrum runtime run complete:\n"
                f"Events: {len(result['events'])}\n"
                f"Pairs: {len(result['pairs'])}\n"
                f"Feature dimension: {result['feature_dimension']}\n"
                f"QNN backend: {qnn_backend}"
            ),
            type="cerebrum-runtime",
            data=result,
        )
    if command_name == "cerebrum-runtime-legacy-demo":
        result = _legacy_runtime_result()
        return CommandResponse(
            success=True,
            output=f"Legacy fixture replay complete: events={len(result['events'])}; pairs={len(result['pairs'])}",
            type="cerebrum-runtime",
            data=result,
        )
    if command_name == "qnn-smoke":
        qnn_request = QNNSmokeRequest(
            samples=request.samples,
            labels=request.labels,
            epochs=request.epochs,
            test_size=request.test_size,
        )
        samples = qnn_request.dump_samples()
        labels = qnn_request.labels
        if not samples or not labels:
            samples, labels = build_demo_samples()
        result = _json_safe_qnn_result(qnn_nucleus.smoke_run(samples[0], label=float(labels[0]), max_epochs=qnn_request.epochs, test_size=qnn_request.test_size))
        return CommandResponse(
            success=True,
            output=(
                "QNN smoke completed:\n"
                f"Backend: {result['backend']}\n"
                f"Feature dimension: {result['feature_dimension']}\n"
                f"Predicted probability: {result['predicted_probability']:.3f}"
            ),
            type="qnn-system",
            data={"result": result, "benchmark": _serialize_benchmark(qnn_nucleus.benchmark(samples, labels))},
        )
    raise HTTPException(status_code=404, detail=f"Command '{command_name}' is not available in alpha-local mode")


@app.post("/commands/{command_name}", response_model=CommandResponse)
async def run_command(command_name: str, request: CommandRequest | None = None) -> CommandResponse:
    return _command_response(command_name, request)


@app.post("/execute-command")
async def execute_command(command_data: Dict[str, Any]) -> Dict[str, Any]:
    command = str(command_data.get("command", "")).strip()
    if not command:
        raise HTTPException(status_code=400, detail="No command provided")
    try:
        request = CommandRequest(**{key: value for key, value in command_data.items() if key != "command"})
        return _command_response(command, request).model_dump()
    except HTTPException:
        return {
            "success": False,
            "error": f"Command '{command}' not allowed in alpha-local mode",
            "type": "error",
        }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            command_data = json.loads(data)
            result = await execute_command(command_data)
            await websocket.send_text(json.dumps(result))
    except WebSocketDisconnect:
        return
    except Exception as exc:
        await websocket.send_text(json.dumps({"success": False, "error": str(exc), "type": "error"}))
    finally:
        await websocket.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
