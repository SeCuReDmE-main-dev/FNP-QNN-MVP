"""
FNP-QNN API server.

This surface now exposes:
- legacy phi commands for compatibility
- Cerebrum crossmodal encoding
- QNN candidate inspection and smoke benchmarking
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Any, Dict, List, Sequence

import numpy as np
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import CerebrumAdapter, PhiFramework, QNNNucleus
from core.cerebrum_adapter import MODALITIES

app = FastAPI(
    title="FNP-QNN API",
    description="Crossmodal Cerebrum adapter plus testable QNN nucleus",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9002", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

phi_engine = PhiFramework()
cerebrum_adapter = CerebrumAdapter()
qnn_nucleus = QNNNucleus(adapter=cerebrum_adapter)


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


@app.get("/")
async def root():
    return {
        "message": "FNP-QNN API Active",
        "mode": "cerebrum-plus-qnn-research",
        "phi": phi_engine.phi,
        "qnn_candidates": [candidate.name for candidate in qnn_nucleus.candidate_matrix()],
    }


@app.get("/cerebrum/status")
async def cerebrum_status():
    observations = build_demo_observations()
    return {
        "status": "ok",
        "bundle": _encode_observations(observations),
        "modalities": list(MODALITIES),
    }


@app.post("/cerebrum/encode")
async def cerebrum_encode(payload: Dict[str, Any]):
    observations = payload.get("observations") or build_demo_observations()
    return {"status": "ok", "encoded": _encode_observations(observations)}


@app.get("/qnn/candidates")
async def qnn_candidates():
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
async def qnn_smoke(payload: Dict[str, Any]):
    samples = payload.get("samples")
    labels = payload.get("labels")
    if not samples or not labels:
        samples, labels = build_demo_samples()
    result = qnn_nucleus.smoke_run(
        samples[0],
        label=float(labels[0]) if labels else 1.0,
        max_epochs=int(payload.get("epochs", 24)),
        test_size=float(payload.get("test_size", 0.25)),
    )
    benchmark = qnn_nucleus.benchmark(samples, labels)
    return {
        "status": "ok",
        "result": result,
        "benchmark": [
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
        ],
    }


@app.post("/execute-command")
async def execute_command(command_data: dict):
    command = command_data.get("command", "")

    if not command:
        raise HTTPException(status_code=400, detail="No command provided")

    try:
        if command.startswith("phi-"):
            return await handle_phi_command(command)
        if command.startswith("cerebrum-"):
            return await handle_cerebrum_command(command, command_data)
        if command.startswith("qnn-"):
            return await handle_qnn_command(command, command_data)
        if command.startswith("quantum-"):
            return await handle_quantum_command(command)
        if command.startswith("neural-"):
            return await handle_neural_command(command)

        safe_commands = ["ls", "pwd", "whoami", "date", "echo", "ps", "node -v", "python --version"]
        if any(command.startswith(safe) for safe in safe_commands):
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return {
                "success": True,
                "output": result.stdout if result.stdout else result.stderr,
                "type": "system",
            }

        return {
            "success": False,
            "error": f"Command '{command}' not allowed",
            "type": "error",
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out",
            "type": "error",
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "type": "error",
        }


async def handle_phi_command(command: str):
    try:
        if command == "phi-status":
            particles = phi_engine.generate_quantum_particles(100)
            return {
                "success": True,
                "output": (
                    f"φ-Framework Status:\n"
                    f"Golden Ratio: {phi_engine.phi}\n"
                    f"Quantum Particles: {len(particles)} generated\n"
                    f"Resonance: {phi_engine.phi * 40:.2f} Hz"
                ),
                "type": "phi-system",
                "data": {"phi": phi_engine.phi, "particles": len(particles)},
            }

        if command == "phi-calc":
            c3_result = phi_engine.calculate_c3_formula(2.5, 1.2, 0.8, 1.5)
            return {
                "success": True,
                "output": (
                    f"C³ Formula Result: {c3_result:.6f}\n"
                    f"φ = {phi_engine.phi}\n"
                    f"Quantum Field Strength: {c3_result * phi_engine.phi:.6f}"
                ),
                "type": "phi-system",
                "data": {"c3": c3_result, "phi": phi_engine.phi},
            }

        if command == "phi-map":
            hippocampus = phi_engine.map_brain_region("hippocampus", (20, 15, 10))
            return {
                "success": True,
                "output": (
                    f"Brain Region Mapped:\n"
                    f"Hippocampus: {hippocampus.shape}\n"
                    f"Complex quantum field generated\n"
                    f"Mean field strength: {np.mean(np.abs(hippocampus)):.6f}"
                ),
                "type": "phi-system",
                "data": {"region": "hippocampus", "shape": hippocampus.shape},
            }

        return {
            "success": False,
            "error": f"Unknown phi command: {command}",
            "type": "error",
        }

    except Exception as exc:
        return {
            "success": False,
            "error": f"Phi command error: {str(exc)}",
            "type": "error",
        }


async def handle_cerebrum_command(command: str, command_data: Dict[str, Any]):
    try:
        if command == "cerebrum-status":
            observations = build_demo_observations()
            payload = _encode_observations(observations)
            return {
                "success": True,
                "output": (
                    "Cerebrum crossmodal status:\n"
                    f"Sequence length: {payload['sequence_length']}\n"
                    f"Feature dimension: {payload['feature_dimension']}\n"
                    f"Diversity: {payload['summary']['diversity']:.3f}\n"
                    f"Stability: {payload['summary']['stability']:.3f}"
                ),
                "type": "cerebrum-system",
                "data": payload,
            }

        if command == "cerebrum-encode":
            observations = command_data.get("observations") or build_demo_observations()
            payload = _encode_observations(observations)
            return {
                "success": True,
                "output": (
                    "Cerebrum encoding complete:\n"
                    f"Sequence length: {payload['sequence_length']}\n"
                    f"Feature dimension: {payload['feature_dimension']}\n"
                    f"Recency-weighted intensity: {payload['summary']['recency_weighted_intensity']:.4f}"
                ),
                "type": "cerebrum-system",
                "data": payload,
            }

        return {
            "success": False,
            "error": f"Unknown cerebrum command: {command}",
            "type": "error",
        }

    except Exception as exc:
        return {
            "success": False,
            "error": f"Cerebrum command error: {str(exc)}",
            "type": "error",
        }


async def handle_qnn_command(command: str, command_data: Dict[str, Any]):
    try:
        samples = command_data.get("samples")
        labels = command_data.get("labels")
        if not samples or not labels:
            samples, labels = build_demo_samples()

        if command == "qnn-candidates":
            return {
                "success": True,
                "output": "QNN candidate matrix ready.",
                "type": "qnn-system",
                "data": qnn_nucleus.candidate_matrix(),
            }

        if command == "qnn-smoke":
            result = qnn_nucleus.smoke_run(
                samples[0],
                label=float(labels[0]) if labels else 1.0,
                max_epochs=int(command_data.get("epochs", 24)),
                test_size=float(command_data.get("test_size", 0.25)),
            )
            benchmark = qnn_nucleus.benchmark(samples, labels)
            return {
                "success": True,
                "output": (
                    "QNN smoke completed:\n"
                    f"Backend: {result['backend']}\n"
                    f"Train accuracy: {result['train_accuracy']:.3f}\n"
                    f"Test accuracy: {result['test_accuracy']:.3f}\n"
                    f"Predicted probability: {result['predicted_probability']:.3f}"
                ),
                "type": "qnn-system",
                "data": {"result": result, "benchmark": [item.__dict__ for item in benchmark]},
            }

        if command == "qnn-fit":
            if qnn_nucleus.candidate_matrix()[0].available:
                try:
                    result = qnn_nucleus.fit_qiskit_hybrid(
                        samples,
                        labels,
                        max_epochs=int(command_data.get("epochs", 24)),
                        test_size=float(command_data.get("test_size", 0.25)),
                    )
                except Exception:
                    result = qnn_nucleus.fit_surrogate(
                        samples,
                        labels,
                        max_epochs=int(command_data.get("epochs", 24)),
                        test_size=float(command_data.get("test_size", 0.25)),
                    )
            else:
                result = qnn_nucleus.fit_surrogate(
                    samples,
                    labels,
                    max_epochs=int(command_data.get("epochs", 24)),
                    test_size=float(command_data.get("test_size", 0.25)),
                )
            return {
                "success": True,
                "output": (
                    "QNN fit completed:\n"
                    f"Backend: {result['backend']}\n"
                    f"Train accuracy: {result['train_accuracy']:.3f}\n"
                    f"Test accuracy: {result['test_accuracy']:.3f}"
                ),
                "type": "qnn-system",
                "data": result,
            }

        return {
            "success": False,
            "error": f"Unknown qnn command: {command}",
            "type": "error",
        }

    except Exception as exc:
        return {
            "success": False,
            "error": f"QNN command error: {str(exc)}",
            "type": "error",
        }


async def handle_quantum_command(command: str):
    try:
        if command == "quantum-test":
            particles = phi_engine.generate_quantum_particles(50)
            coherence = np.mean([abs(p.amplitude) for p in particles])
            return {
                "success": True,
                "output": (
                    f"Quantum Test Results:\n"
                    f"Particles: {len(particles)}\n"
                    f"Coherence: {coherence:.4f}\n"
                    f"Entanglement: Active\n"
                    f"Phase Correlation: {np.mean([p.phase for p in particles]):.4f}"
                ),
                "type": "quantum-system",
                "data": {"particles": len(particles), "coherence": coherence},
            }

        if command == "quantum-state":
            state = phi_engine.quantum_states[0] if phi_engine.quantum_states else None
            if not state:
                particles = phi_engine.generate_quantum_particles(1)
                state = particles[0]
            return {
                "success": True,
                "output": (
                    f"Quantum State:\n|ψ⟩ = {state.amplitude}\n"
                    f"Phase: {state.phase:.4f}\n"
                    f"Frequency: {state.frequency:.4f} Hz\n"
                    f"Resonance: {state.quantum_resonance:.4f}"
                ),
                "type": "quantum-system",
                "data": {"amplitude": str(state.amplitude), "phase": state.phase},
            }

        return {
            "success": False,
            "error": f"Unknown quantum command: {command}",
            "type": "error",
        }

    except Exception as exc:
        return {
            "success": False,
            "error": f"Quantum command error: {str(exc)}",
            "type": "error",
        }


async def handle_neural_command(command: str):
    try:
        if command == "neural-map":
            regions = ["hippocampus", "frontal_cortex", "cerebellum"]
            mapped_regions = {}
            for region in regions:
                mapping = phi_engine.map_brain_region(region, (10, 10, 8))
                mapped_regions[region] = {
                    "shape": mapping.shape,
                    "mean_strength": float(np.mean(np.abs(mapping))),
                }

            output = "Neural Mapping Complete:\n"
            for region, data in mapped_regions.items():
                output += f"{region}: {data['shape']}, strength: {data['mean_strength']:.4f}\n"

            return {
                "success": True,
                "output": output,
                "type": "neural-system",
                "data": mapped_regions,
            }

        if command == "neural-cure":
            deficit_pos = (10, 8, 5)
            cure_algo = phi_engine.generate_cure_algorithm(deficit_pos, "test_deficit")
            return {
                "success": True,
                "output": (
                    "Cure Algorithm Generated:\n"
                    f"Frequency: {cure_algo['therapeutic_frequency']:.2f} Hz\n"
                    f"Recovery Time: {cure_algo['estimated_recovery_time']:.1f}\n"
                    f"Plasticity Factor: {cure_algo['neural_plasticity_factor']:.4f}"
                ),
                "type": "neural-system",
                "data": cure_algo,
            }

        return {
            "success": False,
            "error": f"Unknown neural command: {command}",
            "type": "error",
        }

    except Exception as exc:
        return {
            "success": False,
            "error": f"Neural command error: {str(exc)}",
            "type": "error",
        }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            command_data = json.loads(data)
            result = await execute_command(command_data)
            await websocket.send_text(json.dumps(result))
    except Exception as exc:
        print(f"WebSocket error: {exc}")
    finally:
        await websocket.close()


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "phi_framework": "operational",
        "cerebrum_adapter": "operational",
        "qnn_backend": "torch_surrogate" if "torch_surrogate" in [candidate.name for candidate in qnn_nucleus.candidate_matrix()] else "unknown",
        "golden_ratio": phi_engine.phi,
        "quantum_particles": len(phi_engine.quantum_states),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
