"""FastAPI surface for the local FNP-QNN research simulator."""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional, Sequence
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_ROOT = os.path.join(PROJECT_ROOT, "web")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(1, PROJECT_ROOT)

from api.schemas import (
    ChamberSceneRequest,
    CloudRAGAdmissionRequest,
    CommandRequest,
    CommandResponse,
    EncodeRequest,
    EncryptedRAGEnvelopeRequest,
    GravityNullTestRequest,
    HydraEMGPCNAnesthesiaSweepRequest,
    MultiverseExperimentRequest,
    MultiverseExperimentRunAllRequest,
    NidusFusionProfileRequest,
    NidusPartialMembershipMeanRequest,
    NidusTripletProfileRequest,
    NeuroBitProfileRequest,
    NeuroBitTunnelRequest,
    NovakAndersonConvergenceRequest,
    PenroseHameroffObjectiveReductionRequest,
    QNNSmokeRequest,
    RuntimeRunRequest,
    TimePhysicsExperimentRequest,
    TimePhysicsExperimentRunAllRequest,
)
from core.chamber_lab import ChamberLabError, build_chamber_scene, chamber_lab_status, list_chamber_presets
from core import (
    CerebrumAdapter,
    CerebrumRuntimeBridge,
    FfeDPluginBridge,
    LifeScienceObservationPort,
    LVFMGateLedger,
    LVFMGateRecord,
    NeuroBitProfile,
    PhiFramework,
    QNNNucleus,
    RuntimeStateStore,
    admission_to_runtime_payload,
    build_admission,
    cloud_kit_status,
    decrypt_admission,
    e2b_ingest_plan,
    encrypt_admission,
    envelope_to_runtime_payload,
    generate_rag_key,
    GravityNullTestConfig,
    MultiverseExperimentConfig,
    TimePhysicsExperimentConfig,
    anesthesia_sweep_profile,
    gravity_null_test_status,
    hydra_em_gpcn_orch_profile,
    convergence_profile,
    multiverse_experiments_status,
    novak_anderson_status,
    objective_reduction_profile,
    partial_membership_mean,
    penrose_hameroff_runtime_profile,
    plithogenic_runtime_fusion_profile,
    publish_gate_state,
    revolutionary_topology_runtime_profile,
    run_all_multiverse_experiments,
    run_all_time_physics_experiments,
    run_gravity_null_test,
    run_multiverse_experiment,
    run_neurobit_gates,
    run_neurobit_tunnel_demo,
    run_time_physics_experiment,
    source_weighted_triplet_fusion,
    time_physics_experiments_status,
    triplet_quality_profile,
)
from core.cerebrum_adapter import MODALITIES
from core.qlc_runtime_normalizer import normalize_qlc_runtime_payload

app = FastAPI(
    title="FNP-QNN Local Research Simulator API",
    description="Typed, non-clinical local research surface for Cerebrum-style runtime events and QNN candidates.",
    version="1.3.0-alpha-local",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9002", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-FNP-QNN-Auth"],
)


class DashboardSecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/dashboard"):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
                "script-src 'self'; connect-src 'self'; frame-ancestors 'none'; "
                "base-uri 'none'; form-action 'self'"
            )
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["Referrer-Policy"] = "no-referrer"
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=()"
            response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
            response.headers["X-Frame-Options"] = "DENY"
        return response


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path.startswith("/dashboard") or request.url.path in {"/health", "/", "/docs", "/openapi.json"}:
            return await call_next(request)

        api_key = os.environ.get("FNP_QNN_API_KEY")
        if api_key:
            auth_header = request.headers.get("Authorization")
            if not auth_header or auth_header != f"Bearer {api_key}":
                return JSONResponse(status_code=401, content={"detail": "Unauthorized: Invalid or missing API key"})

        return await call_next(request)

app.add_middleware(DashboardSecurityHeadersMiddleware)
app.add_middleware(APIKeyMiddleware)

if os.path.isdir(WEB_ROOT):
    app.mount("/dashboard/static", StaticFiles(directory=WEB_ROOT), name="dashboard-static")

phi_engine = PhiFramework()
cerebrum_adapter = CerebrumAdapter()
qnn_nucleus = QNNNucleus(adapter=cerebrum_adapter)
cerebrum_runtime_bridge = CerebrumRuntimeBridge(adapter=cerebrum_adapter)
life_science_port = LifeScienceObservationPort()
lvfm_gate_ledger = LVFMGateLedger()
runtime_state_store = RuntimeStateStore()

STATE_KEYS = {
    "health": "/api/health/latest",
    "runtime_status": "/runtime/status/latest",
    "runtime_ingest": "/runtime/ingest/latest",
    "runtime_pairs": "/runtime/pairs/latest",
    "runtime_run": "/runtime/run/latest",
    "cloud_rag": "/cloud-rag/latest",
}


def _persist_runtime_state(key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return runtime_state_store.put_json(key, payload)


def _state_store_status() -> Dict[str, Any]:
    return runtime_state_store.status()


def _neurobit_profile_from_request(payload: NeuroBitProfileRequest | None = None) -> NeuroBitProfile:
    if payload is None:
        return NeuroBitProfile()
    return NeuroBitProfile(
        truth=payload.truth,
        indeterminacy=payload.indeterminacy,
        falsity=payload.falsity,
        delta_falsity=payload.delta_falsity,
        state_basis=payload.state_basis,
        puncture_delta=payload.puncture_delta,
        observer_strength=payload.observer_strength,
        surface_width=payload.surface_width,
        surface_height=payload.surface_height,
        fractal_dimension=payload.fractal_dimension,
        fractal_dimension_min=payload.fractal_dimension_min,
        fractal_dimension_max=payload.fractal_dimension_max,
        fractal_admissible=payload.fractal_admissible,
        fractal_measurement_method=payload.fractal_measurement_method,
        fractal_scale=payload.fractal_scale,
        plugin_hook_enabled=payload.plugin_hook_enabled,
        plugin_set=payload.plugin_set,
        plugin_context=payload.plugin_context,
        cpai_context=payload.cpai_context,
        include_plugin_trace=payload.include_plugin_trace,
    )


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


def _gravity_config_from_request(payload: GravityNullTestRequest) -> GravityNullTestConfig:
    return GravityNullTestConfig(
        seed=payload.seed,
        shots=payload.shots,
        entanglement_correlation=payload.entanglement_correlation,
        probe_bias=payload.probe_bias,
        local_noise=payload.local_noise,
        leakage=payload.leakage,
        chamber_contradiction=payload.chamber_contradiction,
        mass_dispersion=payload.mass_dispersion,
        alpha_wave_frequency=payload.alpha_wave_frequency,
        beta_wave_frequency=payload.beta_wave_frequency,
        omega_wave_frequency=payload.omega_wave_frequency,
        d_min=payload.d_min,
        d_max=payload.d_max,
        D_min=payload.D_min,
        D_max=payload.D_max,
        delta_ns_threshold=payload.delta_ns_threshold,
        frustration_threshold=payload.frustration_threshold,
        include_sequence_export=payload.include_sequence_export,
        include_qiskit_preview=payload.include_qiskit_preview,
        include_e2b_datadog_review=payload.include_e2b_datadog_review,
        source_i=payload.source_i,
        graviton_external_bound_ev=payload.graviton_external_bound_ev,
        graviton_bound_source=payload.graviton_bound_source,
    )


def _gravity_config_from_qnn_payload(payload: QNNSmokeRequest | CommandRequest) -> GravityNullTestConfig:
    return GravityNullTestConfig(
        seed=payload.gravity_null_test_seed,
        shots=payload.gravity_null_test_shots,
        local_noise=payload.gravity_null_test_local_noise,
        leakage=payload.gravity_null_test_leakage,
        mass_dispersion=payload.gravity_null_test_mass_dispersion,
        chamber_contradiction=payload.gravity_null_test_chamber_contradiction,
        include_sequence_export=False,
        include_qiskit_preview=False,
        include_e2b_datadog_review=True,
    )


def _multiverse_config_from_request(payload: MultiverseExperimentRequest) -> MultiverseExperimentConfig:
    return MultiverseExperimentConfig(
        experiment_id=payload.experiment_id,
        seed=payload.seed,
        shots=payload.shots,
        branch_coherence=payload.branch_coherence,
        measurement_strength=payload.measurement_strength,
        interference_visibility=payload.interference_visibility,
        entanglement_fidelity=payload.entanglement_fidelity,
        classical_leakage=payload.classical_leakage,
        memory_erasure=payload.memory_erasure,
        scale_claim_strength=payload.scale_claim_strength,
        include_qiskit_preview=payload.include_qiskit_preview,
        source_i=payload.source_i,
    )


def _multiverse_config_from_run_all_request(
    payload: MultiverseExperimentRunAllRequest,
) -> MultiverseExperimentConfig:
    experiment_id = payload.experiment_ids[0] if payload.experiment_ids else "deutsch_quantum_computation_origin"
    return MultiverseExperimentConfig(
        experiment_id=experiment_id,
        seed=payload.seed,
        shots=payload.shots,
        branch_coherence=payload.branch_coherence,
        measurement_strength=payload.measurement_strength,
        interference_visibility=payload.interference_visibility,
        entanglement_fidelity=payload.entanglement_fidelity,
        classical_leakage=payload.classical_leakage,
        memory_erasure=payload.memory_erasure,
        scale_claim_strength=payload.scale_claim_strength,
        include_qiskit_preview=payload.include_qiskit_preview,
        source_i=payload.source_i,
    )


def _multiverse_config_from_qnn_payload(payload: QNNSmokeRequest | CommandRequest) -> MultiverseExperimentConfig:
    experiment_ids = list(payload.multiverse_experiment_ids)
    return MultiverseExperimentConfig(
        experiment_id=experiment_ids[0] if experiment_ids else "deutsch_quantum_computation_origin",
        seed=payload.multiverse_experiment_seed,
        shots=payload.multiverse_experiment_shots,
        branch_coherence=payload.multiverse_branch_coherence,
        measurement_strength=payload.multiverse_measurement_strength,
        interference_visibility=payload.multiverse_interference_visibility,
        entanglement_fidelity=payload.multiverse_entanglement_fidelity,
        classical_leakage=payload.multiverse_classical_leakage,
        memory_erasure=payload.multiverse_memory_erasure,
        scale_claim_strength=payload.multiverse_scale_claim_strength,
    )


def _time_physics_config_from_request(payload: TimePhysicsExperimentRequest) -> TimePhysicsExperimentConfig:
    return TimePhysicsExperimentConfig(
        experiment_id=payload.experiment_id,
        seed=payload.seed,
        shots=payload.shots,
        temporal_flow_strength=payload.temporal_flow_strength,
        relative_velocity_fraction=payload.relative_velocity_fraction,
        simultaneity_offset=payload.simultaneity_offset,
        entropy_gradient=payload.entropy_gradient,
        entanglement_growth=payload.entanglement_growth,
        decoherence_strength=payload.decoherence_strength,
        cosmological_boundary_pressure=payload.cosmological_boundary_pressure,
        paradox_pressure=payload.paradox_pressure,
        include_qiskit_preview=payload.include_qiskit_preview,
        source_i=payload.source_i,
    )


def _time_physics_config_from_run_all_request(
    payload: TimePhysicsExperimentRunAllRequest,
) -> TimePhysicsExperimentConfig:
    experiment_id = payload.experiment_ids[0] if payload.experiment_ids else "manifest_vs_physical_time_flow"
    return TimePhysicsExperimentConfig(
        experiment_id=experiment_id,
        seed=payload.seed,
        shots=payload.shots,
        temporal_flow_strength=payload.temporal_flow_strength,
        relative_velocity_fraction=payload.relative_velocity_fraction,
        simultaneity_offset=payload.simultaneity_offset,
        entropy_gradient=payload.entropy_gradient,
        entanglement_growth=payload.entanglement_growth,
        decoherence_strength=payload.decoherence_strength,
        cosmological_boundary_pressure=payload.cosmological_boundary_pressure,
        paradox_pressure=payload.paradox_pressure,
        include_qiskit_preview=payload.include_qiskit_preview,
        source_i=payload.source_i,
    )


def _time_physics_config_from_qnn_payload(payload: QNNSmokeRequest | CommandRequest) -> TimePhysicsExperimentConfig:
    experiment_ids = list(payload.time_physics_experiment_ids)
    return TimePhysicsExperimentConfig(
        experiment_id=experiment_ids[0] if experiment_ids else "manifest_vs_physical_time_flow",
        seed=payload.time_physics_experiment_seed,
        shots=payload.time_physics_experiment_shots,
        temporal_flow_strength=payload.time_physics_temporal_flow_strength,
        relative_velocity_fraction=payload.time_physics_relative_velocity_fraction,
        simultaneity_offset=payload.time_physics_simultaneity_offset,
        entropy_gradient=payload.time_physics_entropy_gradient,
        entanglement_growth=payload.time_physics_entanglement_growth,
        decoherence_strength=payload.time_physics_decoherence_strength,
        cosmological_boundary_pressure=payload.time_physics_cosmological_boundary_pressure,
        paradox_pressure=payload.time_physics_paradox_pressure,
    )


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
    runtime_payload = normalize_qlc_runtime_payload(_runtime_payload(payload))
    state = cerebrum_runtime_bridge.build_state(
        runtime_payload,
        qnn_nucleus=qnn_nucleus if run_qnn else None,
        label=float((payload or {}).get("label", 1.0)),
        max_epochs=int((payload or {}).get("epochs", 12)),
        state_basis=str((payload or {}).get("state_basis", "binary")),
        puncture_delta=(payload or {}).get("puncture_delta"),
        observer_strength=(payload or {}).get("observer_strength"),
        fractal_dimension=(payload or {}).get("fractal_dimension"),
        fractal_dimension_min=(payload or {}).get("fractal_dimension_min"),
        fractal_dimension_max=(payload or {}).get("fractal_dimension_max"),
        fractal_admissible=bool((payload or {}).get("fractal_admissible", True)),
        fractal_measurement_method=(payload or {}).get("fractal_measurement_method"),
        fractal_scale=(payload or {}).get("fractal_scale"),
        plugin_hook_enabled=bool((payload or {}).get("plugin_hook_enabled", False)),
        plugin_set=str((payload or {}).get("plugin_set", "mvp5")),
        plugin_context=(payload or {}).get("plugin_context") or {},
        cpai_context=(payload or {}).get("cpai_context") or {},
        include_plugin_trace=bool((payload or {}).get("include_plugin_trace", True)),
        plithogenic_enabled=bool((payload or {}).get("plithogenic_enabled", False)),
        revolutionary_topology_enabled=bool((payload or {}).get("revolutionary_topology_enabled", False)),
        neutro_algebra_enabled=bool((payload or {}).get("neutro_algebra_enabled", False)),
        penrose_hameroff_enabled=bool((payload or {}).get("penrose_hameroff_enabled", False)),
        objective_reduction_energy_joule=(payload or {}).get("objective_reduction_energy_joule"),
        coherence_time_s=(payload or {}).get("coherence_time_s"),
        anesthetic_damping=(payload or {}).get("anesthetic_damping"),
        microtubule_frequency_hz=(payload or {}).get("microtubule_frequency_hz"),
        spin_network_vertices=(payload or {}).get("spin_network_vertices"),
        hydra_em_enabled=bool((payload or {}).get("hydra_em_enabled", False)),
        gpcn_set_phi_enabled=bool((payload or {}).get("gpcn_set_phi_enabled", False)),
        orch_or_simulation_enabled=bool((payload or {}).get("orch_or_simulation_enabled", False)),
        microtubule_proxy_count=int((payload or {}).get("microtubule_proxy_count", 8)),
        microtubule_coupling_strength=float((payload or {}).get("microtubule_coupling_strength", 0.5)),
        quasicrystal_projection_enabled=bool((payload or {}).get("quasicrystal_projection_enabled", True)),
        plithogenic_contradiction_threshold=float((payload or {}).get("plithogenic_contradiction_threshold", 0.35)),
        lattice_seed=int((payload or {}).get("lattice_seed", 0)),
        observation_scale_min=float((payload or {}).get("observation_scale_min", 0.01)),
        observation_scale_max=float((payload or {}).get("observation_scale_max", 1.0)),
        multiverse_experiments_enabled=bool((payload or {}).get("multiverse_experiments_enabled", False)),
        multiverse_experiment_ids=(payload or {}).get("multiverse_experiment_ids") or None,
        multiverse_experiment_seed=int((payload or {}).get("multiverse_experiment_seed", 2026)),
        multiverse_experiment_shots=int((payload or {}).get("multiverse_experiment_shots", 512)),
        multiverse_branch_coherence=float((payload or {}).get("multiverse_branch_coherence", 0.82)),
        multiverse_measurement_strength=float((payload or {}).get("multiverse_measurement_strength", 0.35)),
        multiverse_interference_visibility=float((payload or {}).get("multiverse_interference_visibility", 0.72)),
        multiverse_entanglement_fidelity=float((payload or {}).get("multiverse_entanglement_fidelity", 0.84)),
        multiverse_classical_leakage=float((payload or {}).get("multiverse_classical_leakage", 0.0)),
        multiverse_memory_erasure=float((payload or {}).get("multiverse_memory_erasure", 1.0)),
        multiverse_scale_claim_strength=float((payload or {}).get("multiverse_scale_claim_strength", 0.65)),
        time_physics_experiments_enabled=bool((payload or {}).get("time_physics_experiments_enabled", False)),
        time_physics_experiment_ids=(payload or {}).get("time_physics_experiment_ids") or None,
        time_physics_experiment_seed=int((payload or {}).get("time_physics_experiment_seed", 2026)),
        time_physics_experiment_shots=int((payload or {}).get("time_physics_experiment_shots", 512)),
        time_physics_temporal_flow_strength=float((payload or {}).get("time_physics_temporal_flow_strength", 0.74)),
        time_physics_relative_velocity_fraction=float((payload or {}).get("time_physics_relative_velocity_fraction", 0.35)),
        time_physics_simultaneity_offset=float((payload or {}).get("time_physics_simultaneity_offset", 0.40)),
        time_physics_entropy_gradient=float((payload or {}).get("time_physics_entropy_gradient", 0.78)),
        time_physics_entanglement_growth=float((payload or {}).get("time_physics_entanglement_growth", 0.62)),
        time_physics_decoherence_strength=float((payload or {}).get("time_physics_decoherence_strength", 0.66)),
        time_physics_cosmological_boundary_pressure=float(
            (payload or {}).get("time_physics_cosmological_boundary_pressure", 0.55)
        ),
        time_physics_paradox_pressure=float((payload or {}).get("time_physics_paradox_pressure", 0.15)),
    )
    result = state.to_dict()
    if runtime_payload.get("qlc_runtime_normalized_context", {}).get("detected"):
        result["qlc_runtime"] = runtime_payload["qlc_runtime_normalized_context"]
    if run_qnn:
        samples, labels = build_demo_samples()
        runtime_label = 1 if float((payload or {}).get("label", 1)) >= 0.5 else 0
        benchmark_samples = [state.observations, *samples, state.observations, *samples]
        benchmark_labels = [runtime_label, 0, 1, 0, 1 - runtime_label, 1, 0, 1]
        if result.get("qnn_result"):
            result["qnn_result"] = _json_safe_qnn_result(result["qnn_result"])
        result["benchmark"] = _serialize_benchmark(qnn_nucleus.benchmark(benchmark_samples, benchmark_labels))
    return result


def _runtime_gate_run(
    payload: Dict[str, Any] | None,
    run_qnn: bool = False,
    publish_to_registry: bool = False,
    registry_threshold: float = -0.1,
) -> Dict[str, Any]:
    runtime_payload = _runtime_payload(payload)
    result = _runtime_result(runtime_payload, run_qnn=run_qnn)
    gate_record = LVFMGateRecord.from_snapshot(result.get("lvfm", {}), runtime_payload)
    gate_record = lvfm_gate_ledger.append(gate_record)
    response: Dict[str, Any] = {"runtime": result, "gate": gate_record.to_dict()}
    if publish_to_registry:
        response["registry"] = publish_gate_state(
            gate_record.to_dict(),
            threshold=registry_threshold,
        ).__dict__
    return response


def _legacy_runtime_result() -> Dict[str, Any]:
    legacy_root = os.path.join(PROJECT_ROOT, "examples")
    bridge = CerebrumRuntimeBridge(adapter=cerebrum_adapter, legacy_cerebrum_path=legacy_root)
    nucleus = QNNNucleus(adapter=bridge.adapter)
    state = bridge.build_state(None, qnn_nucleus=nucleus, max_epochs=6)
    result = state.to_dict()
    result["legacy_cerebrum_path"] = legacy_root
    result["legacy_cerebrum_path_exists"] = bridge.status(qnn_nucleus=nucleus)["legacy_cerebrum_path_exists"]
    return result


def _runtime_gate_run(
    payload: Dict[str, Any] | None,
    run_qnn: bool = False,
    publish_to_registry: bool = False,
    registry_threshold: float = -0.1,
) -> Dict[str, Any]:
    runtime_payload = _runtime_payload(payload)
    result = _runtime_result(runtime_payload, run_qnn=run_qnn)
    gate_record = LVFMGateRecord.from_snapshot(result.get("lvfm", {}), runtime_payload)
    gate_record = lvfm_gate_ledger.append(gate_record)
    response: Dict[str, Any] = {"runtime": result, "gate": gate_record.to_dict()}
    if publish_to_registry:
        response["registry"] = publish_gate_state(
            gate_record.to_dict(),
            threshold=registry_threshold,
        ).__dict__
    return response


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
    response = {
        "status": "healthy",
        "mode": "alpha-local-research",
        "clinical_use": False,
        "phi_framework": "synthetic-research",
        "cerebrum_adapter": "operational",
        "qnn_backend": backend,
        "golden_ratio": phi_engine.phi,
        "quantum_particles": len(phi_engine.quantum_states),
        "state_store": _state_store_status(),
    }
    response["persistence"] = _persist_runtime_state(STATE_KEYS["health"], response)
    return response


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
    response = cerebrum_runtime_bridge.status(qnn_nucleus=qnn_nucleus)
    response["state_store"] = _state_store_status()
    response["persistence"] = _persist_runtime_state(STATE_KEYS["runtime_status"], response)
    return response


@app.post("/cerebrum/runtime/ingest")
async def cerebrum_runtime_ingest(payload: RuntimeRunRequest) -> Dict[str, Any]:
    events, pairs, warnings = cerebrum_runtime_bridge.ingest(_runtime_payload(payload.to_runtime_payload()))
    response = {
        "status": "ok",
        "events": [event.to_dict() for event in events],
        "pairs": [pair.to_dict() for pair in pairs],
        "warnings": warnings,
        "state_store": _state_store_status(),
    }
    response["persistence"] = _persist_runtime_state(STATE_KEYS["runtime_ingest"], response)
    return response


@app.post("/cerebrum/runtime/pairs")
async def cerebrum_runtime_pairs(payload: RuntimeRunRequest) -> Dict[str, Any]:
    events, pairs, warnings = cerebrum_runtime_bridge.ingest(_runtime_payload(payload.to_runtime_payload()))
    response = {
        "status": "ok",
        "event_count": len(events),
        "pairs": [pair.to_dict() for pair in pairs],
        "warnings": warnings,
        "state_store": _state_store_status(),
    }
    response["persistence"] = _persist_runtime_state(STATE_KEYS["runtime_pairs"], response)
    return response


@app.post("/cerebrum/runtime/run")
async def cerebrum_runtime_run(payload: RuntimeRunRequest) -> Dict[str, Any]:
    response = {
        "status": "ok",
        "runtime": _runtime_result(payload.to_runtime_payload(), run_qnn=payload.run_qnn),
        "state_store": _state_store_status(),
    }
    response["persistence"] = _persist_runtime_state(STATE_KEYS["runtime_run"], response)
    return response


@app.get("/cerebrum/runtime/state/latest")
async def cerebrum_runtime_state_latest() -> Dict[str, Any]:
    record = runtime_state_store.get_json(STATE_KEYS["runtime_run"])
    return {
        "status": "ok",
        "record": record,
        "state_store": _state_store_status(),
    }


@app.post("/cerebrum/runtime/gate-run")
async def cerebrum_runtime_gate_run(
    payload: RuntimeRunRequest,
    publish_to_registry: bool = False,
    registry_threshold: float = -0.1,
) -> Dict[str, Any]:
    return {
        "status": "ok",
        **_runtime_gate_run(
            payload.to_runtime_payload(),
            run_qnn=payload.run_qnn,
            publish_to_registry=publish_to_registry,
            registry_threshold=registry_threshold,
        ),
    }


@app.get("/cerebrum/runtime/gate-history")
async def cerebrum_runtime_gate_history(limit: int = 25) -> Dict[str, Any]:
    return {
        "status": "ok",
        "count": min(limit, 1000),
        "records": lvfm_gate_ledger.recent(limit=min(limit, 1000)),
    }


@app.get("/cerebrum/runtime/legacy-demo")
async def cerebrum_runtime_legacy_demo() -> Dict[str, Any]:
    return {"status": "ok", "runtime": _legacy_runtime_result()}


@app.get("/cloud-kit/status")
async def cloud_kit_status_endpoint() -> Dict[str, Any]:
    return cloud_kit_status()


@app.post("/cloud-kit/e2b/ingest-plan")
async def cloud_kit_e2b_ingest_plan(payload: CloudRAGAdmissionRequest) -> Dict[str, Any]:
    return e2b_ingest_plan(payload.source, payload.title, payload.tool_route)


@app.get("/cloud-kit/rag/keygen")
async def cloud_kit_rag_keygen() -> Dict[str, Any]:
    try:
        return generate_rag_key()
    except RuntimeError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc


@app.post("/cloud-kit/rag/encrypt")
async def cloud_kit_rag_encrypt(payload: CloudRAGAdmissionRequest) -> Dict[str, Any]:
    admission = build_admission(
        payload.title,
        payload.content,
        payload.source,
        tool_route=payload.tool_route,
        tags=payload.tags,
    )
    try:
        envelope = encrypt_admission(admission)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    response = {"status": "ok", "admission": admission, "envelope": envelope}
    response["persistence"] = _persist_runtime_state(STATE_KEYS["cloud_rag"], response)
    return response


@app.post("/cloud-kit/rag/decrypt-runtime")
async def cloud_kit_rag_decrypt_runtime(payload: EncryptedRAGEnvelopeRequest) -> Dict[str, Any]:
    try:
        admission = decrypt_admission(payload.to_envelope())
        runtime_payload = admission_to_runtime_payload(admission)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    runtime = _runtime_result(runtime_payload, run_qnn=True)
    response = {
        "status": "ok",
        "admission": {
            "title": admission.get("title"),
            "source": admission.get("source"),
            "tool_route": admission.get("tool_route"),
            "content_sha256": admission.get("content_sha256"),
        },
        "runtime_payload": runtime_payload,
        "runtime": runtime,
    }
    response["persistence"] = _persist_runtime_state(STATE_KEYS["cloud_rag"], response)
    return response


@app.post("/cloud-kit/rag/runtime")
async def cloud_kit_rag_runtime(payload: CloudRAGAdmissionRequest) -> Dict[str, Any]:
    admission = build_admission(
        payload.title,
        payload.content,
        payload.source,
        tool_route=payload.tool_route,
        tags=payload.tags,
    )
    runtime_payload = admission_to_runtime_payload(admission)
    runtime = _runtime_result(runtime_payload, run_qnn=True)
    response = {
        "status": "ok",
        "admission": {
            "title": admission.get("title"),
            "source": admission.get("source"),
            "tool_route": admission.get("tool_route"),
            "content_sha256": admission.get("content_sha256"),
        },
        "runtime_payload": runtime_payload,
        "runtime": runtime,
    }
    response["persistence"] = _persist_runtime_state(STATE_KEYS["cloud_rag"], response)
    return response


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


@app.get("/fnp-qnn/chamber-lab/status")
async def chamber_lab_status_endpoint() -> Dict[str, Any]:
    """Report the local renderer and Synthia-gated admission contract."""

    return chamber_lab_status()


@app.get("/fnp-qnn/chamber-lab/presets")
async def chamber_lab_presets_endpoint() -> Dict[str, Any]:
    """List selectable display presets without issuing a chamber."""

    return {"status": "ok", "presets": list_chamber_presets(), **chamber_lab_status()}


@app.post("/fnp-qnn/chamber-lab/scene")
async def chamber_lab_scene_endpoint(payload: ChamberSceneRequest) -> Dict[str, Any]:
    """Create one visual chamber only after Synthia admits its ten carriers."""

    try:
        return build_chamber_scene(
            admission_packet=payload.admission_packet,
            carriers=payload.carriers,
            preset_id=payload.preset_id,
            style=payload.style,
        )
    except ChamberLabError as exc:
        raise HTTPException(status_code=422, detail=exc.code) from exc


@app.get("/fnp-qnn/novak-anderson/status")
async def novak_anderson_status_endpoint() -> Dict[str, Any]:
    return novak_anderson_status()


@app.post("/fnp-qnn/novak-anderson/convergence")
async def novak_anderson_convergence(payload: NovakAndersonConvergenceRequest) -> Dict[str, Any]:
    return {
        "status": "ok",
        "profile": convergence_profile(max_n=payload.max_n, sample_ns=payload.sample_ns or None),
    }


@app.get("/fnp-qnn/gravity-null-test/status")
async def gravity_null_test_status_endpoint() -> Dict[str, Any]:
    return gravity_null_test_status()


@app.post("/fnp-qnn/gravity-null-test/run")
async def gravity_null_test_run(payload: GravityNullTestRequest) -> Dict[str, Any]:
    return {
        "status": "ok",
        "profile": run_gravity_null_test(_gravity_config_from_request(payload)),
    }


@app.get("/fnp-qnn/multiverse-experiments/status")
async def multiverse_experiments_status_endpoint() -> Dict[str, Any]:
    return multiverse_experiments_status()


@app.post("/fnp-qnn/multiverse-experiments/run")
async def multiverse_experiment_run(payload: MultiverseExperimentRequest) -> Dict[str, Any]:
    return {
        "status": "ok",
        "profile": run_multiverse_experiment(_multiverse_config_from_request(payload)),
    }


@app.post("/fnp-qnn/multiverse-experiments/run-all")
async def multiverse_experiment_run_all(payload: MultiverseExperimentRunAllRequest) -> Dict[str, Any]:
    return {
        "status": "ok",
        "profile": run_all_multiverse_experiments(
            _multiverse_config_from_run_all_request(payload),
            experiment_ids=payload.experiment_ids or None,
        ),
    }


@app.get("/fnp-qnn/time-physics-experiments/status")
async def time_physics_experiments_status_endpoint() -> Dict[str, Any]:
    return time_physics_experiments_status()


@app.post("/fnp-qnn/time-physics-experiments/run")
async def time_physics_experiment_run(payload: TimePhysicsExperimentRequest) -> Dict[str, Any]:
    return {
        "status": "ok",
        "profile": run_time_physics_experiment(_time_physics_config_from_request(payload)),
    }


@app.post("/fnp-qnn/time-physics-experiments/run-all")
async def time_physics_experiment_run_all(payload: TimePhysicsExperimentRunAllRequest) -> Dict[str, Any]:
    return {
        "status": "ok",
        "profile": run_all_time_physics_experiments(
            _time_physics_config_from_run_all_request(payload),
            experiment_ids=payload.experiment_ids or None,
        ),
    }


@app.post("/qnn/smoke")
async def qnn_smoke(payload: QNNSmokeRequest) -> Dict[str, Any]:
    samples = payload.dump_samples()
    labels = payload.labels
    if not samples or not labels:
        samples, labels = build_demo_samples()
    penrose_hameroff_profile = None
    if payload.penrose_hameroff_enabled:
        events, pairs, _warnings = cerebrum_runtime_bridge.ingest({"memories": samples[0]})
        penrose_hameroff_profile = penrose_hameroff_runtime_profile(
            events,
            pairs,
            objective_reduction_energy_joule=payload.objective_reduction_energy_joule,
            coherence_time_s=payload.coherence_time_s,
            anesthetic_damping=payload.anesthetic_damping,
            microtubule_frequency_hz=payload.microtubule_frequency_hz,
            spin_network_vertices=payload.spin_network_vertices,
        )
    hydra_em_gpcn_profile = None
    if payload.hydra_em_enabled and payload.gpcn_set_phi_enabled and payload.orch_or_simulation_enabled:
        events, pairs, _warnings = cerebrum_runtime_bridge.ingest({"memories": samples[0]})
        hydra_em_gpcn_profile = hydra_em_gpcn_orch_profile(
            events,
            pairs,
            microtubule_proxy_count=payload.microtubule_proxy_count,
            microtubule_coupling_strength=payload.microtubule_coupling_strength,
            anesthetic_damping=payload.anesthetic_damping,
            coherence_time_s=payload.coherence_time_s,
            objective_reduction_energy_joule=payload.objective_reduction_energy_joule,
            microtubule_frequency_hz=payload.microtubule_frequency_hz,
            quasicrystal_projection_enabled=payload.quasicrystal_projection_enabled,
            plithogenic_contradiction_threshold=payload.plithogenic_contradiction_threshold,
            lattice_seed=payload.lattice_seed,
            observation_scale_min=payload.observation_scale_min,
            observation_scale_max=payload.observation_scale_max,
        )
    gravity_null_test_profile = None
    if payload.gravity_null_test_enabled:
        gravity_null_test_profile = run_gravity_null_test(_gravity_config_from_qnn_payload(payload))
    multiverse_experiments_profile = None
    if payload.multiverse_experiments_enabled:
        multiverse_experiments_profile = run_all_multiverse_experiments(
            _multiverse_config_from_qnn_payload(payload),
            experiment_ids=payload.multiverse_experiment_ids or None,
        )
    time_physics_experiments_profile = None
    if payload.time_physics_experiments_enabled:
        time_physics_experiments_profile = run_all_time_physics_experiments(
            _time_physics_config_from_qnn_payload(payload),
            experiment_ids=payload.time_physics_experiment_ids or None,
        )
    result = _json_safe_qnn_result(qnn_nucleus.smoke_run(
        samples[0],
        label=float(labels[0]) if labels else 1.0,
        max_epochs=payload.epochs,
        test_size=payload.test_size,
        state_basis=payload.state_basis,
        puncture_delta=payload.puncture_delta,
        observer_strength=payload.observer_strength,
        fractal_dimension=payload.fractal_dimension,
        fractal_dimension_min=payload.fractal_dimension_min,
        fractal_dimension_max=payload.fractal_dimension_max,
        fractal_admissible=payload.fractal_admissible,
        fractal_measurement_method=payload.fractal_measurement_method,
        fractal_scale=payload.fractal_scale,
        plugin_hook_enabled=payload.plugin_hook_enabled,
        plugin_set=payload.plugin_set,
        plugin_context=payload.plugin_context,
        cpai_context=payload.cpai_context,
        include_plugin_trace=payload.include_plugin_trace,
        penrose_hameroff_features=None if penrose_hameroff_profile is None else penrose_hameroff_profile["feature_vector"],
        penrose_hameroff_payload=penrose_hameroff_profile,
        hydra_em_gpcn_features=None if hydra_em_gpcn_profile is None else hydra_em_gpcn_profile["feature_vector"],
        hydra_em_gpcn_payload=hydra_em_gpcn_profile,
        gravity_null_test_features=None
        if gravity_null_test_profile is None
        else gravity_null_test_profile["feature_vector"],
        gravity_null_test_payload=gravity_null_test_profile,
        multiverse_experiment_features=None
        if multiverse_experiments_profile is None
        else multiverse_experiments_profile["feature_vector"],
        multiverse_experiment_payload=multiverse_experiments_profile,
        time_physics_experiment_features=None
        if time_physics_experiments_profile is None
        else time_physics_experiments_profile["feature_vector"],
        time_physics_experiment_payload=time_physics_experiments_profile,
    ))
    return {
        "status": "ok",
        "result": result,
        "benchmark": _serialize_benchmark(qnn_nucleus.benchmark(samples, labels)),
    }


@app.get("/fnp-qnn/neurobit/status")
async def neurobit_status() -> Dict[str, Any]:
    result = run_neurobit_gates(NeuroBitProfile())
    plugin_status = FfeDPluginBridge().status()
    return {
        "status": "ok",
        "mode": "alpha-local-research",
        "feature": "neurobit-gates-and-tunnel-demo",
        "backend": result["backend"],
        "qiskit_available": result["qiskit_available"],
        "available_gates": ["hadamard", "w", "x", "y", "z"],
        "research_boundary": result["research_boundary"],
        "hierarchy": result["hierarchy"],
        "state_basis": result["state_basis"],
        "fractal_carrier_supported": True,
        "plugin_hook_supported": True,
        "plugin_hook_default_enabled": False,
        "plugin_mvp5": plugin_status["mvp5_plugins"],
        "plugin_engine": plugin_status,
    }


@app.post("/fnp-qnn/neurobit/gates/run")
async def neurobit_gates_run(payload: NeuroBitProfileRequest) -> Dict[str, Any]:
    profile = _neurobit_profile_from_request(payload)
    return run_neurobit_gates(profile, n_qubits=payload.n_qubits)


@app.post("/fnp-qnn/neurobit/tunnel/demo")
async def neurobit_tunnel_demo(payload: NeuroBitTunnelRequest) -> Dict[str, Any]:
    profile = _neurobit_profile_from_request(payload)
    return run_neurobit_tunnel_demo(profile, data=payload.data)


@app.get("/fnp-qnn/nidus/status")
async def nidus_status() -> Dict[str, Any]:
    return {
        "status": "ok",
        "mode": "alpha-local-research",
        "feature": "nidus-idearum-ii-math-layer",
        "source": "Nidus Idearum II, 2nd ed.",
        "available_primitives": [
            "triplet_quality_profile",
            "source_weighted_triplet_fusion",
            "partial_membership_mean",
        ],
        "endpoints": [
            "POST /fnp-qnn/nidus/triplet/profile",
            "POST /fnp-qnn/nidus/fusion/profile",
            "POST /fnp-qnn/nidus/partial-membership/mean",
        ],
        "hierarchy": "I -> I_system^S -> D_f -> dF -> i_fractal",
        "research_boundary": (
            "alpha-local educational simulation only; not clinical, diagnostic, "
            "therapeutic, security, production-public, or validated physical behavior"
        ),
    }


@app.get("/fnp-qnn/penrose-hameroff/status")
async def penrose_hameroff_status() -> Dict[str, Any]:
    return {
        "status": "ok",
        "mode": "alpha-local-research",
        "feature": "penrose-hameroff-study-layer",
        "available_primitives": [
            "objective_reduction_profile",
            "orchestration_profile",
            "spin_network_admissibility_profile",
            "twistor_nonlocality_profile",
            "microtubule_signal_profile",
            "penrose_hameroff_runtime_profile",
        ],
        "endpoints": [
            "POST /fnp-qnn/penrose-hameroff/objective-reduction/profile",
            "POST /fnp-qnn/penrose-hameroff/runtime/profile",
        ],
        "hierarchy": "I -> I_system^S -> D_f -> dF -> i_fractal",
        "research_boundary": (
            "alpha-local educational simulation only; not a consciousness proof, clinical system, "
            "physical quantum-gravity engine, security system, or production-public claim"
        ),
    }


@app.post("/fnp-qnn/penrose-hameroff/objective-reduction/profile")
async def penrose_hameroff_objective_reduction_profile(
    payload: PenroseHameroffObjectiveReductionRequest,
) -> Dict[str, Any]:
    return {
        "status": "ok",
        "profile": objective_reduction_profile(
            payload.objective_reduction_energy_joule,
            reference_time_s=payload.reference_time_s,
        ),
    }


@app.post("/fnp-qnn/penrose-hameroff/runtime/profile")
async def penrose_hameroff_runtime_profile_endpoint(payload: RuntimeRunRequest) -> Dict[str, Any]:
    events, pairs, warnings = cerebrum_runtime_bridge.ingest(_runtime_payload(payload.to_runtime_payload()))
    return {
        "status": "ok",
        "profile": penrose_hameroff_runtime_profile(
            events,
            pairs,
            objective_reduction_energy_joule=payload.objective_reduction_energy_joule,
            coherence_time_s=payload.coherence_time_s,
            anesthetic_damping=payload.anesthetic_damping,
            microtubule_frequency_hz=payload.microtubule_frequency_hz,
            spin_network_vertices=payload.spin_network_vertices,
        ),
        "warnings": warnings,
    }


@app.get("/fnp-qnn/hydra-em-gpcn/status")
async def hydra_em_gpcn_status() -> Dict[str, Any]:
    return {
        "status": "ok",
        "mode": "alpha-local-research",
        "feature": "hydra-em-gpcn-orch-or-hypothesis-simulator",
        "axiomatic_container": "GPCN-Set_phi",
        "available_primitives": [
            "gpcn_set_phi_profile",
            "quasicrystal_gpcn_projection_profile",
            "microtubule_proxy_phi_profile",
            "hydra_em_gpcn_orch_profile",
            "anesthesia_sweep_profile",
        ],
        "endpoints": [
            "POST /fnp-qnn/hydra-em-gpcn/orch-profile",
            "POST /fnp-qnn/hydra-em-gpcn/anesthesia-sweep",
            "POST /fnp-qnn/hydra-em-gpcn/runtime/profile",
        ],
        "verdicts": ["communicates", "decoheres", "suspended", "rejected"],
        "hierarchy": "I -> I_system^S -> D_f -> dF -> i_fractal",
        "research_boundary": (
            "alpha-local educational simulation only; not clinical, biological validation, "
            "consciousness proof, physical quantum-gravity engine, or production-public claim"
        ),
    }


@app.post("/fnp-qnn/hydra-em-gpcn/orch-profile")
async def hydra_em_gpcn_orch_profile_endpoint(payload: RuntimeRunRequest) -> Dict[str, Any]:
    events, pairs, warnings = cerebrum_runtime_bridge.ingest(_runtime_payload(payload.to_runtime_payload()))
    return {
        "status": "ok",
        "profile": hydra_em_gpcn_orch_profile(
            events,
            pairs,
            microtubule_proxy_count=payload.microtubule_proxy_count,
            microtubule_coupling_strength=payload.microtubule_coupling_strength,
            anesthetic_damping=payload.anesthetic_damping,
            coherence_time_s=payload.coherence_time_s,
            objective_reduction_energy_joule=payload.objective_reduction_energy_joule,
            microtubule_frequency_hz=payload.microtubule_frequency_hz,
            quasicrystal_projection_enabled=payload.quasicrystal_projection_enabled,
            plithogenic_contradiction_threshold=payload.plithogenic_contradiction_threshold,
            lattice_seed=payload.lattice_seed,
            observation_scale_min=payload.observation_scale_min,
            observation_scale_max=payload.observation_scale_max,
        ),
        "warnings": warnings,
    }


@app.post("/fnp-qnn/hydra-em-gpcn/anesthesia-sweep")
async def hydra_em_gpcn_anesthesia_sweep(payload: HydraEMGPCNAnesthesiaSweepRequest) -> Dict[str, Any]:
    events, pairs, warnings = cerebrum_runtime_bridge.ingest(_runtime_payload(payload.to_runtime_payload()))
    return {
        "status": "ok",
        "profile": anesthesia_sweep_profile(
            events,
            pairs,
            damping_values=payload.damping_values,
            microtubule_proxy_count=payload.microtubule_proxy_count,
            microtubule_coupling_strength=payload.microtubule_coupling_strength,
            coherence_time_s=payload.coherence_time_s,
            objective_reduction_energy_joule=payload.objective_reduction_energy_joule,
            microtubule_frequency_hz=payload.microtubule_frequency_hz,
            quasicrystal_projection_enabled=payload.quasicrystal_projection_enabled,
            plithogenic_contradiction_threshold=payload.plithogenic_contradiction_threshold,
            lattice_seed=payload.lattice_seed,
            observation_scale_min=payload.observation_scale_min,
            observation_scale_max=payload.observation_scale_max,
        ),
        "warnings": warnings,
    }


@app.post("/fnp-qnn/hydra-em-gpcn/runtime/profile")
async def hydra_em_gpcn_runtime_profile_endpoint(payload: RuntimeRunRequest) -> Dict[str, Any]:
    runtime_payload = payload.to_runtime_payload()
    runtime_payload["hydra_em_enabled"] = True
    runtime_payload["gpcn_set_phi_enabled"] = True
    runtime_payload["orch_or_simulation_enabled"] = True
    state = cerebrum_runtime_bridge.build_state(
        _runtime_payload(runtime_payload),
        hydra_em_enabled=True,
        gpcn_set_phi_enabled=True,
        orch_or_simulation_enabled=True,
        objective_reduction_energy_joule=payload.objective_reduction_energy_joule,
        coherence_time_s=payload.coherence_time_s,
        anesthetic_damping=payload.anesthetic_damping,
        microtubule_frequency_hz=payload.microtubule_frequency_hz,
        microtubule_proxy_count=payload.microtubule_proxy_count,
        microtubule_coupling_strength=payload.microtubule_coupling_strength,
        quasicrystal_projection_enabled=payload.quasicrystal_projection_enabled,
        plithogenic_contradiction_threshold=payload.plithogenic_contradiction_threshold,
        lattice_seed=payload.lattice_seed,
        observation_scale_min=payload.observation_scale_min,
        observation_scale_max=payload.observation_scale_max,
    )
    return {
        "status": "ok",
        "profile": state.hydra_em_gpcn,
        "warnings": state.warnings,
    }


@app.post("/fnp-qnn/nidus/triplet/profile")
async def nidus_triplet_profile(payload: NidusTripletProfileRequest) -> Dict[str, Any]:
    return {
        "status": "ok",
        "profile": triplet_quality_profile(
            payload.truth,
            payload.indeterminacy,
            payload.falsity,
        ),
    }


@app.post("/fnp-qnn/nidus/fusion/profile")
async def nidus_fusion_profile(payload: NidusFusionProfileRequest) -> Dict[str, Any]:
    return {
        "status": "ok",
        "fusion": source_weighted_triplet_fusion(payload.dump_sources()),
    }


@app.post("/fnp-qnn/nidus/partial-membership/mean")
async def nidus_partial_membership_mean(payload: NidusPartialMembershipMeanRequest) -> Dict[str, Any]:
    return {
        "status": "ok",
        "mean": partial_membership_mean(payload.values, payload.memberships),
    }


@app.post("/fnp-qnn/plithogenic/runtime/profile")
async def plithogenic_runtime_profile(payload: RuntimeRunRequest) -> Dict[str, Any]:
    events, pairs, warnings = cerebrum_runtime_bridge.ingest(_runtime_payload(payload.to_runtime_payload()))
    return {
        "status": "ok",
        "profile": plithogenic_runtime_fusion_profile(events, pairs),
        "warnings": warnings,
    }


@app.post("/fnp-qnn/revolutionary-topology/runtime/profile")
async def revolutionary_topology_runtime_profile_endpoint(payload: RuntimeRunRequest) -> Dict[str, Any]:
    events, pairs, warnings = cerebrum_runtime_bridge.ingest(_runtime_payload(payload.to_runtime_payload()))
    return {
        "status": "ok",
        "profile": revolutionary_topology_runtime_profile(events, pairs),
        "warnings": warnings,
    }


@app.post("/fnp-qnn/plithogenic-topology/runtime/profile")
async def plithogenic_topology_runtime_profile_endpoint(payload: RuntimeRunRequest) -> Dict[str, Any]:
    runtime_payload = _runtime_payload(payload.to_runtime_payload())
    state = cerebrum_runtime_bridge.build_state(
        runtime_payload,
        plithogenic_enabled=True,
        revolutionary_topology_enabled=True,
        plugin_hook_enabled=payload.plugin_hook_enabled,
        plugin_set=payload.plugin_set,
        plugin_context=payload.plugin_context,
        cpai_context=payload.cpai_context,
        include_plugin_trace=payload.include_plugin_trace,
    )
    return {
        "status": "ok",
        "profile": state.plithogenic_topology,
        "warnings": state.warnings,
    }


@app.post("/fnp-qnn/neutro-algebra/profile")
async def neutro_algebra_profile_endpoint(payload: RuntimeRunRequest) -> Dict[str, Any]:
    runtime_payload = _runtime_payload(payload.to_runtime_payload())
    state = cerebrum_runtime_bridge.build_state(
        runtime_payload,
        plithogenic_enabled=payload.plithogenic_enabled,
        revolutionary_topology_enabled=payload.revolutionary_topology_enabled,
        plugin_hook_enabled=payload.plugin_hook_enabled,
        plugin_set=payload.plugin_set,
        plugin_context=payload.plugin_context,
        cpai_context=payload.cpai_context,
        include_plugin_trace=payload.include_plugin_trace,
        neutro_algebra_enabled=True,
    )
    return {
        "status": "ok",
        "profile": state.neutro_algebra,
        "warnings": state.warnings,
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
    if command_name == "novak-anderson-phi-pi":
        result = novak_anderson_status(max_n=request.novak_anderson_max_n)
        final_row = result["convergence"]["rows"][-1]
        return CommandResponse(
            success=True,
            output=(
                "Novak-Anderson phi/pi convergence complete:\n"
                f"max_n={result['convergence']['max_n']}\n"
                f"pseudopi={final_row['pseudopi']:.12f}\n"
                f"pi_error={final_row['pseudopi_error_to_pi']:.6g}\n"
                f"stim_available={result['stim_available']}"
            ),
            type="novak-anderson-phi-pi",
            data=result,
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
    if command_name == "cerebrum-runtime-gate-run":
        payload = request.payload.to_runtime_payload() if request.payload is not None else {}
        run_qnn = bool(request.payload.run_qnn) if request.payload is not None else True
        result = _runtime_gate_run(
            payload,
            run_qnn=run_qnn,
            publish_to_registry=request.publish_to_registry,
            registry_threshold=request.registry_threshold,
        )
        return CommandResponse(
            success=True,
            output=(
                "Cerebrum LVFM gate run complete:\n"
                f"gate_id={result['gate']['gate_id']}\n"
                f"verdict={result['gate']['decision'].get('verdict')}\n"
                f"trace={result['gate']['decision'].get('trace_line')}\n"
                f"log={result['gate']['source_path']}"
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
            state_basis=request.state_basis,
            puncture_delta=request.puncture_delta,
            observer_strength=request.observer_strength,
            fractal_dimension=request.fractal_dimension,
            fractal_dimension_min=request.fractal_dimension_min,
            fractal_dimension_max=request.fractal_dimension_max,
            fractal_admissible=request.fractal_admissible,
            fractal_measurement_method=request.fractal_measurement_method,
            fractal_scale=request.fractal_scale,
            plugin_hook_enabled=request.plugin_hook_enabled,
            plugin_set=request.plugin_set,
            plugin_context=request.plugin_context,
            cpai_context=request.cpai_context,
            include_plugin_trace=request.include_plugin_trace,
            penrose_hameroff_enabled=request.penrose_hameroff_enabled,
            objective_reduction_energy_joule=request.objective_reduction_energy_joule,
            coherence_time_s=request.coherence_time_s,
            anesthetic_damping=request.anesthetic_damping,
            microtubule_frequency_hz=request.microtubule_frequency_hz,
            spin_network_vertices=request.spin_network_vertices,
            hydra_em_enabled=request.hydra_em_enabled,
            gpcn_set_phi_enabled=request.gpcn_set_phi_enabled,
            orch_or_simulation_enabled=request.orch_or_simulation_enabled,
            microtubule_proxy_count=request.microtubule_proxy_count,
            microtubule_coupling_strength=request.microtubule_coupling_strength,
            quasicrystal_projection_enabled=request.quasicrystal_projection_enabled,
            plithogenic_contradiction_threshold=request.plithogenic_contradiction_threshold,
            lattice_seed=request.lattice_seed,
            observation_scale_min=request.observation_scale_min,
            observation_scale_max=request.observation_scale_max,
            gravity_null_test_enabled=request.gravity_null_test_enabled,
            gravity_null_test_seed=request.gravity_null_test_seed,
            gravity_null_test_shots=request.gravity_null_test_shots,
            gravity_null_test_local_noise=request.gravity_null_test_local_noise,
            gravity_null_test_leakage=request.gravity_null_test_leakage,
            gravity_null_test_mass_dispersion=request.gravity_null_test_mass_dispersion,
            gravity_null_test_chamber_contradiction=request.gravity_null_test_chamber_contradiction,
            multiverse_experiments_enabled=request.multiverse_experiments_enabled,
            multiverse_experiment_ids=request.multiverse_experiment_ids,
            multiverse_experiment_seed=request.multiverse_experiment_seed,
            multiverse_experiment_shots=request.multiverse_experiment_shots,
            multiverse_branch_coherence=request.multiverse_branch_coherence,
            multiverse_measurement_strength=request.multiverse_measurement_strength,
            multiverse_interference_visibility=request.multiverse_interference_visibility,
            multiverse_entanglement_fidelity=request.multiverse_entanglement_fidelity,
            multiverse_classical_leakage=request.multiverse_classical_leakage,
            multiverse_memory_erasure=request.multiverse_memory_erasure,
            multiverse_scale_claim_strength=request.multiverse_scale_claim_strength,
            time_physics_experiments_enabled=request.time_physics_experiments_enabled,
            time_physics_experiment_ids=request.time_physics_experiment_ids,
            time_physics_experiment_seed=request.time_physics_experiment_seed,
            time_physics_experiment_shots=request.time_physics_experiment_shots,
            time_physics_temporal_flow_strength=request.time_physics_temporal_flow_strength,
            time_physics_relative_velocity_fraction=request.time_physics_relative_velocity_fraction,
            time_physics_simultaneity_offset=request.time_physics_simultaneity_offset,
            time_physics_entropy_gradient=request.time_physics_entropy_gradient,
            time_physics_entanglement_growth=request.time_physics_entanglement_growth,
            time_physics_decoherence_strength=request.time_physics_decoherence_strength,
            time_physics_cosmological_boundary_pressure=request.time_physics_cosmological_boundary_pressure,
            time_physics_paradox_pressure=request.time_physics_paradox_pressure,
        )
        samples = qnn_request.dump_samples()
        labels = qnn_request.labels
        if not samples or not labels:
            samples, labels = build_demo_samples()
        penrose_hameroff_profile = None
        if qnn_request.penrose_hameroff_enabled:
            events, pairs, _warnings = cerebrum_runtime_bridge.ingest({"memories": samples[0]})
            penrose_hameroff_profile = penrose_hameroff_runtime_profile(
                events,
                pairs,
                objective_reduction_energy_joule=qnn_request.objective_reduction_energy_joule,
                coherence_time_s=qnn_request.coherence_time_s,
                anesthetic_damping=qnn_request.anesthetic_damping,
                microtubule_frequency_hz=qnn_request.microtubule_frequency_hz,
                spin_network_vertices=qnn_request.spin_network_vertices,
            )
        hydra_em_gpcn_profile = None
        if qnn_request.hydra_em_enabled and qnn_request.gpcn_set_phi_enabled and qnn_request.orch_or_simulation_enabled:
            events, pairs, _warnings = cerebrum_runtime_bridge.ingest({"memories": samples[0]})
            hydra_em_gpcn_profile = hydra_em_gpcn_orch_profile(
                events,
                pairs,
                microtubule_proxy_count=qnn_request.microtubule_proxy_count,
                microtubule_coupling_strength=qnn_request.microtubule_coupling_strength,
                anesthetic_damping=qnn_request.anesthetic_damping,
                coherence_time_s=qnn_request.coherence_time_s,
                objective_reduction_energy_joule=qnn_request.objective_reduction_energy_joule,
                microtubule_frequency_hz=qnn_request.microtubule_frequency_hz,
                quasicrystal_projection_enabled=qnn_request.quasicrystal_projection_enabled,
                plithogenic_contradiction_threshold=qnn_request.plithogenic_contradiction_threshold,
                lattice_seed=qnn_request.lattice_seed,
                observation_scale_min=qnn_request.observation_scale_min,
                observation_scale_max=qnn_request.observation_scale_max,
            )
        gravity_null_test_profile = None
        if qnn_request.gravity_null_test_enabled:
            gravity_null_test_profile = run_gravity_null_test(_gravity_config_from_qnn_payload(qnn_request))
        multiverse_experiments_profile = None
        if qnn_request.multiverse_experiments_enabled:
            multiverse_experiments_profile = run_all_multiverse_experiments(
                _multiverse_config_from_qnn_payload(qnn_request),
                experiment_ids=qnn_request.multiverse_experiment_ids or None,
            )
        time_physics_experiments_profile = None
        if qnn_request.time_physics_experiments_enabled:
            time_physics_experiments_profile = run_all_time_physics_experiments(
                _time_physics_config_from_qnn_payload(qnn_request),
                experiment_ids=qnn_request.time_physics_experiment_ids or None,
            )
        result = _json_safe_qnn_result(qnn_nucleus.smoke_run(
            samples[0],
            label=float(labels[0]),
            max_epochs=qnn_request.epochs,
            test_size=qnn_request.test_size,
            state_basis=qnn_request.state_basis,
            puncture_delta=qnn_request.puncture_delta,
            observer_strength=qnn_request.observer_strength,
            fractal_dimension=qnn_request.fractal_dimension,
            fractal_dimension_min=qnn_request.fractal_dimension_min,
            fractal_dimension_max=qnn_request.fractal_dimension_max,
            fractal_admissible=qnn_request.fractal_admissible,
            fractal_measurement_method=qnn_request.fractal_measurement_method,
            fractal_scale=qnn_request.fractal_scale,
            plugin_hook_enabled=qnn_request.plugin_hook_enabled,
            plugin_set=qnn_request.plugin_set,
            plugin_context=qnn_request.plugin_context,
            cpai_context=qnn_request.cpai_context,
            include_plugin_trace=qnn_request.include_plugin_trace,
            penrose_hameroff_features=None if penrose_hameroff_profile is None else penrose_hameroff_profile["feature_vector"],
            penrose_hameroff_payload=penrose_hameroff_profile,
            hydra_em_gpcn_features=None if hydra_em_gpcn_profile is None else hydra_em_gpcn_profile["feature_vector"],
            hydra_em_gpcn_payload=hydra_em_gpcn_profile,
            gravity_null_test_features=None
            if gravity_null_test_profile is None
            else gravity_null_test_profile["feature_vector"],
            gravity_null_test_payload=gravity_null_test_profile,
            multiverse_experiment_features=None
            if multiverse_experiments_profile is None
            else multiverse_experiments_profile["feature_vector"],
            multiverse_experiment_payload=multiverse_experiments_profile,
            time_physics_experiment_features=None
            if time_physics_experiments_profile is None
            else time_physics_experiments_profile["feature_vector"],
            time_physics_experiment_payload=time_physics_experiments_profile,
        ))
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
    if command_name == "neurobit-gates":
        neurobit_request = request.neurobit if request and request.neurobit is not None else NeuroBitTunnelRequest()
        result = run_neurobit_gates(
            _neurobit_profile_from_request(neurobit_request),
            n_qubits=neurobit_request.n_qubits,
        )
        return CommandResponse(
            success=True,
            output=(
                "NeuroBit gates complete:\n"
                f"Backend: {result['backend']}\n"
                f"Sequence: {', '.join(result['sequence'])}\n"
                f"Expectation: {result['expectation_vector']}"
            ),
            type="neurobit-system",
            data=result,
        )
    if command_name == "neurobit-tunnel-demo":
        neurobit_request = request.neurobit if request and request.neurobit is not None else NeuroBitTunnelRequest()
        result = run_neurobit_tunnel_demo(
            _neurobit_profile_from_request(neurobit_request),
            data=neurobit_request.data,
        )
        return CommandResponse(
            success=True,
            output=(
                "NeuroBit tunnel demo complete:\n"
                f"Backend: {result['backend']}\n"
                f"Sequence id: {result['sequence_id']}\n"
                "Boundary: deterministic noise simulation, not security."
            ),
            type="neurobit-system",
            data=result,
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
    api_key = os.environ.get("FNP_QNN_API_KEY")
    try:
        if api_key:
            auth_data = await websocket.receive_text()
            try:
                auth_payload = json.loads(auth_data)
                if auth_payload.get("api_key") != api_key:
                    await websocket.send_text(json.dumps({"success": False, "error": "Unauthorized", "type": "error"}))
                    await websocket.close()
                    return
            except Exception:
                await websocket.send_text(json.dumps({"success": False, "error": "Invalid auth format", "type": "error"}))
                await websocket.close()
                return

        while True:
            data = await websocket.receive_text()
            command_data = json.loads(data)
            result = await execute_command(command_data)
            await websocket.send_text(json.dumps(result))
    except WebSocketDisconnect:
        return
    except Exception:
        await websocket.send_text(json.dumps({"success": False, "error": "Internal server error", "type": "error"}))
    finally:
        await websocket.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
