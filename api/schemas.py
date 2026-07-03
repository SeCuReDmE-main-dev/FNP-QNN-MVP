"""Pydantic contracts for the local alpha API surface."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from core.qlc_runtime_normalizer import reject_forbidden_qlc_fields

ALLOWED_MODALITIES = {"audio", "video", "text", "stimuli", "hearing", "vision", "language", "stimulus"}
MAX_EVENTS = 1000
MAX_LABEL_LENGTH = 120
PLUGIN_SET = Literal["mvp5"]
MULTIVERSE_EXPERIMENT_ID = Literal[
    "deutsch_quantum_computation_origin",
    "elitzur_vaidman_bomb_tester",
    "entanglement_teleportation_branch_accounting",
    "google_quantum_computer_scale_review",
    "wigner_friend_inter_branch_communication",
]
TIME_PHYSICS_EXPERIMENT_ID = Literal[
    "manifest_vs_physical_time_flow",
    "relativistic_time_dilation_block_universe",
    "relativity_of_simultaneity_now",
    "thermodynamic_entropy_arrow",
    "entanglement_decoherence_arrow",
    "cosmological_boundary_time_travel",
]


def _finite(value: float, field_name: str) -> float:
    if not math.isfinite(float(value)):
        raise ValueError(f"{field_name} must be finite")
    return float(value)


def _copy_fractal_aliases(values):
    if not isinstance(values, dict):
        return values
    updated = dict(values)
    aliases = {
        "D_f": "fractal_dimension",
        "D_min": "fractal_dimension_min",
        "D_max": "fractal_dimension_max",
    }
    for alias, field_name in aliases.items():
        if alias in updated and field_name not in updated:
            updated[field_name] = updated[alias]
    return updated


class Observation(BaseModel):
    modality: str = Field(default="stimuli", max_length=32)
    value: Any = 0.0
    timestamp: Optional[float] = None
    starting_time: Optional[float] = None
    ending_time: Optional[float] = None
    end_time: Optional[float] = None
    label: str = Field(default="", max_length=MAX_LABEL_LENGTH)
    source: str = Field(default="", max_length=MAX_LABEL_LENGTH)
    weight: float = 1.0
    payload_ref: str = Field(default="", max_length=MAX_LABEL_LENGTH)
    provenance: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("modality")
    @classmethod
    def validate_modality(cls, value: str) -> str:
        normalized = value.lower().strip()
        if normalized not in ALLOWED_MODALITIES:
            raise ValueError(f"Unsupported modality '{value}'")
        return normalized

    @field_validator("timestamp", "starting_time", "ending_time", "end_time", "weight")
    @classmethod
    def validate_finite_optional(cls, value: Optional[float], info):
        if value is None:
            return value
        return _finite(value, info.field_name)

    @model_validator(mode="after")
    def validate_time_order(self):
        start = self.starting_time if self.starting_time is not None else self.timestamp
        end = self.ending_time if self.ending_time is not None else self.end_time
        if start is not None and end is not None and end < start:
            raise ValueError("ending_time must be greater than or equal to starting_time")
        return self


class RuntimeRunRequest(BaseModel):
    memories: Optional[List[Observation]] = None
    events: Optional[List[Observation]] = None
    observations: Optional[List[Observation]] = None
    statefield: Optional[Dict[str, Any]] = None
    label: float = 1.0
    epochs: int = Field(default=12, ge=0, le=256)
    run_qnn: bool = True
    state_basis: Literal["binary", "neutrobit"] = "binary"
    puncture_delta: Optional[float] = Field(default=None, gt=0.0)
    observer_strength: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    fractal_dimension: Optional[float] = None
    fractal_dimension_min: Optional[float] = None
    fractal_dimension_max: Optional[float] = None
    fractal_admissible: bool = True
    fractal_measurement_method: Optional[str] = Field(default=None, max_length=120)
    fractal_scale: Optional[str] = Field(default=None, max_length=120)
    plugin_hook_enabled: bool = False
    plugin_set: PLUGIN_SET = "mvp5"
    plugin_context: Dict[str, Any] = Field(default_factory=dict)
    cpai_context: Dict[str, Any] = Field(default_factory=dict)
    include_plugin_trace: bool = True
    plithogenic_enabled: bool = False
    revolutionary_topology_enabled: bool = False
    neutro_algebra_enabled: bool = False
    penrose_hameroff_enabled: bool = False
    objective_reduction_energy_joule: Optional[float] = None
    coherence_time_s: Optional[float] = Field(default=None, ge=0.0)
    anesthetic_damping: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    microtubule_frequency_hz: Optional[float] = Field(default=None, ge=0.0)
    spin_network_vertices: Optional[List[List[float]]] = None
    hydra_em_enabled: bool = False
    gpcn_set_phi_enabled: bool = False
    orch_or_simulation_enabled: bool = False
    microtubule_proxy_count: int = Field(default=8, ge=0, le=256)
    microtubule_coupling_strength: float = Field(default=0.5, ge=0.0, le=1.0)
    quasicrystal_projection_enabled: bool = True
    plithogenic_contradiction_threshold: float = Field(default=0.35, ge=0.0, le=1.0)
    lattice_seed: int = Field(default=0, ge=0)
    observation_scale_min: float = Field(default=0.01, gt=0.0)
    observation_scale_max: float = Field(default=1.0, gt=0.0)
    multiverse_experiments_enabled: bool = False
    multiverse_experiment_ids: List[MULTIVERSE_EXPERIMENT_ID] = Field(default_factory=list)
    multiverse_experiment_seed: int = Field(default=2026, ge=0)
    multiverse_experiment_shots: int = Field(default=512, ge=16, le=100000)
    multiverse_branch_coherence: float = Field(default=0.82, ge=0.0, le=1.0)
    multiverse_measurement_strength: float = Field(default=0.35, ge=0.0, le=1.0)
    multiverse_interference_visibility: float = Field(default=0.72, ge=0.0, le=1.0)
    multiverse_entanglement_fidelity: float = Field(default=0.84, ge=0.0, le=1.0)
    multiverse_classical_leakage: float = Field(default=0.0, ge=0.0, le=1.0)
    multiverse_memory_erasure: float = Field(default=1.0, ge=0.0, le=1.0)
    multiverse_scale_claim_strength: float = Field(default=0.65, ge=0.0, le=1.0)
    time_physics_experiments_enabled: bool = False
    time_physics_experiment_ids: List[TIME_PHYSICS_EXPERIMENT_ID] = Field(default_factory=list)
    time_physics_experiment_seed: int = Field(default=2026, ge=0)
    time_physics_experiment_shots: int = Field(default=512, ge=16, le=100000)
    time_physics_temporal_flow_strength: float = Field(default=0.74, ge=0.0, le=1.0)
    time_physics_relative_velocity_fraction: float = Field(default=0.35, ge=0.0, le=1.0)
    time_physics_simultaneity_offset: float = Field(default=0.40, ge=0.0, le=1.0)
    time_physics_entropy_gradient: float = Field(default=0.78, ge=0.0, le=1.0)
    time_physics_entanglement_growth: float = Field(default=0.62, ge=0.0, le=1.0)
    time_physics_decoherence_strength: float = Field(default=0.66, ge=0.0, le=1.0)
    time_physics_cosmological_boundary_pressure: float = Field(default=0.55, ge=0.0, le=1.0)
    time_physics_paradox_pressure: float = Field(default=0.15, ge=0.0, le=1.0)

    @model_validator(mode="before")
    @classmethod
    def accept_fractal_aliases(cls, values):
        reject_forbidden_qlc_fields(values)
        return _copy_fractal_aliases(values)

    @field_validator("memories", "events", "observations")
    @classmethod
    def validate_event_count(cls, value: Optional[List[Observation]]):
        if value is not None and len(value) > MAX_EVENTS:
            raise ValueError(f"At most {MAX_EVENTS} events are accepted")
        return value

    @field_validator("label")
    @classmethod
    def validate_label(cls, value: float) -> float:
        return _finite(value, "label")

    @field_validator(
        "fractal_dimension",
        "fractal_dimension_min",
        "fractal_dimension_max",
        "objective_reduction_energy_joule",
        "coherence_time_s",
        "anesthetic_damping",
        "microtubule_frequency_hz",
    )
    @classmethod
    def validate_fractal_numbers(cls, value: Optional[float], info):
        if value is None:
            return value
        return _finite(value, info.field_name)

    @field_validator("spin_network_vertices")
    @classmethod
    def validate_spin_network_vertices(cls, value: Optional[List[List[float]]]):
        if value is None:
            return value
        if len(value) > MAX_EVENTS:
            raise ValueError(f"At most {MAX_EVENTS} spin vertices are accepted")
        for vertex in value:
            if len(vertex) != 3:
                raise ValueError("spin network vertices must contain exactly three labels")
            for label in vertex:
                _finite(label, "spin_network_vertices")
        return value

    def to_runtime_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "label": self.label,
            "epochs": self.epochs,
            "state_basis": self.state_basis,
        }
        if self.puncture_delta is not None:
            payload["puncture_delta"] = self.puncture_delta
        if self.observer_strength is not None:
            payload["observer_strength"] = self.observer_strength
        payload.update(self.fractal_payload())
        payload.update(self.plugin_payload())
        payload["plithogenic_enabled"] = self.plithogenic_enabled
        payload["revolutionary_topology_enabled"] = self.revolutionary_topology_enabled
        payload["neutro_algebra_enabled"] = self.neutro_algebra_enabled
        payload["penrose_hameroff_enabled"] = self.penrose_hameroff_enabled
        payload.update(self.penrose_hameroff_payload())
        payload.update(self.hydra_em_gpcn_payload())
        payload.update(self.multiverse_experiments_payload())
        payload.update(self.time_physics_experiments_payload())
        if self.memories is not None:
            payload["memories"] = [item.model_dump(exclude_none=True) for item in self.memories]
        if self.events is not None:
            payload["events"] = [item.model_dump(exclude_none=True) for item in self.events]
        if self.observations is not None:
            payload["observations"] = [item.model_dump(exclude_none=True) for item in self.observations]
        if self.statefield is not None:
            payload["statefield"] = self.statefield
        return payload

    def plugin_payload(self) -> Dict[str, Any]:
        return {
            "plugin_hook_enabled": self.plugin_hook_enabled,
            "plugin_set": self.plugin_set,
            "plugin_context": self.plugin_context,
            "cpai_context": self.cpai_context,
            "include_plugin_trace": self.include_plugin_trace,
        }

    def fractal_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"fractal_admissible": self.fractal_admissible}
        if self.fractal_dimension is not None:
            payload["fractal_dimension"] = self.fractal_dimension
        if self.fractal_dimension_min is not None:
            payload["fractal_dimension_min"] = self.fractal_dimension_min
        if self.fractal_dimension_max is not None:
            payload["fractal_dimension_max"] = self.fractal_dimension_max
        if self.fractal_measurement_method is not None:
            payload["fractal_measurement_method"] = self.fractal_measurement_method
        if self.fractal_scale is not None:
            payload["fractal_scale"] = self.fractal_scale
        return payload

    def penrose_hameroff_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if self.objective_reduction_energy_joule is not None:
            payload["objective_reduction_energy_joule"] = self.objective_reduction_energy_joule
        if self.coherence_time_s is not None:
            payload["coherence_time_s"] = self.coherence_time_s
        if self.anesthetic_damping is not None:
            payload["anesthetic_damping"] = self.anesthetic_damping
        if self.microtubule_frequency_hz is not None:
            payload["microtubule_frequency_hz"] = self.microtubule_frequency_hz
        if self.spin_network_vertices is not None:
            payload["spin_network_vertices"] = self.spin_network_vertices
        return payload

    def hydra_em_gpcn_payload(self) -> Dict[str, Any]:
        return {
            "hydra_em_enabled": self.hydra_em_enabled,
            "gpcn_set_phi_enabled": self.gpcn_set_phi_enabled,
            "orch_or_simulation_enabled": self.orch_or_simulation_enabled,
            "microtubule_proxy_count": self.microtubule_proxy_count,
            "microtubule_coupling_strength": self.microtubule_coupling_strength,
            "quasicrystal_projection_enabled": self.quasicrystal_projection_enabled,
            "plithogenic_contradiction_threshold": self.plithogenic_contradiction_threshold,
            "lattice_seed": self.lattice_seed,
            "observation_scale_min": self.observation_scale_min,
            "observation_scale_max": self.observation_scale_max,
        }

    def multiverse_experiments_payload(self) -> Dict[str, Any]:
        return {
            "multiverse_experiments_enabled": self.multiverse_experiments_enabled,
            "multiverse_experiment_ids": list(self.multiverse_experiment_ids),
            "multiverse_experiment_seed": self.multiverse_experiment_seed,
            "multiverse_experiment_shots": self.multiverse_experiment_shots,
            "multiverse_branch_coherence": self.multiverse_branch_coherence,
            "multiverse_measurement_strength": self.multiverse_measurement_strength,
            "multiverse_interference_visibility": self.multiverse_interference_visibility,
            "multiverse_entanglement_fidelity": self.multiverse_entanglement_fidelity,
            "multiverse_classical_leakage": self.multiverse_classical_leakage,
            "multiverse_memory_erasure": self.multiverse_memory_erasure,
            "multiverse_scale_claim_strength": self.multiverse_scale_claim_strength,
        }

    def time_physics_experiments_payload(self) -> Dict[str, Any]:
        return {
            "time_physics_experiments_enabled": self.time_physics_experiments_enabled,
            "time_physics_experiment_ids": list(self.time_physics_experiment_ids),
            "time_physics_experiment_seed": self.time_physics_experiment_seed,
            "time_physics_experiment_shots": self.time_physics_experiment_shots,
            "time_physics_temporal_flow_strength": self.time_physics_temporal_flow_strength,
            "time_physics_relative_velocity_fraction": self.time_physics_relative_velocity_fraction,
            "time_physics_simultaneity_offset": self.time_physics_simultaneity_offset,
            "time_physics_entropy_gradient": self.time_physics_entropy_gradient,
            "time_physics_entanglement_growth": self.time_physics_entanglement_growth,
            "time_physics_decoherence_strength": self.time_physics_decoherence_strength,
            "time_physics_cosmological_boundary_pressure": self.time_physics_cosmological_boundary_pressure,
            "time_physics_paradox_pressure": self.time_physics_paradox_pressure,
        }

    @model_validator(mode="after")
    def validate_hydra_scale(self):
        if self.observation_scale_max <= self.observation_scale_min:
            raise ValueError("observation_scale_max must be greater than observation_scale_min")
        return self


class CloudRAGAdmissionRequest(BaseModel):
    title: str = Field(max_length=120)
    content: str = Field(max_length=65536)
    source: str = Field(max_length=240)
    tool_route: str = Field(default="gateway", max_length=80)
    tags: List[str] = Field(default_factory=list)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: List[str]) -> List[str]:
        if len(value) > 24:
            raise ValueError("At most 24 tags are accepted")
        return [item[:64] for item in value]


class EncryptedRAGEnvelopeRequest(BaseModel):
    version: int = 1
    kind: str = Field(default="fnpqnn-encrypted-rag-envelope", max_length=80)
    algorithm: Literal["fernet"] = "fernet"
    key_env: str = Field(default="FNP_QNN_RAG_ENCRYPTION_KEY", max_length=120)
    ciphertext: str = Field(max_length=200000)
    plaintext_sha256: Optional[str] = Field(default=None, max_length=128)
    encrypted_at: Optional[str] = Field(default=None, max_length=64)
    raw_key_stored: bool = False

    def to_envelope(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)


class EncodeRequest(BaseModel):
    observations: List[Observation] = Field(default_factory=list)

    @field_validator("observations")
    @classmethod
    def validate_observation_count(cls, value: List[Observation]):
        if len(value) > MAX_EVENTS:
            raise ValueError(f"At most {MAX_EVENTS} observations are accepted")
        return value


class QNNSmokeRequest(BaseModel):
    samples: Optional[List[List[Observation]]] = None
    labels: Optional[List[int]] = None
    epochs: int = Field(default=24, ge=0, le=256)
    test_size: float = Field(default=0.25, ge=0.0, le=0.9)
    publish_to_registry: bool = False
    registry_threshold: float = Field(default=-0.1, ge=-1.0, le=1.0)
    state_basis: Literal["binary", "neutrobit"] = "binary"
    puncture_delta: Optional[float] = Field(default=None, gt=0.0)
    observer_strength: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    fractal_dimension: Optional[float] = None
    fractal_dimension_min: Optional[float] = None
    fractal_dimension_max: Optional[float] = None
    fractal_admissible: bool = True
    fractal_measurement_method: Optional[str] = Field(default=None, max_length=120)
    fractal_scale: Optional[str] = Field(default=None, max_length=120)
    plugin_hook_enabled: bool = False
    plugin_set: PLUGIN_SET = "mvp5"
    plugin_context: Dict[str, Any] = Field(default_factory=dict)
    cpai_context: Dict[str, Any] = Field(default_factory=dict)
    include_plugin_trace: bool = True
    penrose_hameroff_enabled: bool = False
    objective_reduction_energy_joule: Optional[float] = None
    coherence_time_s: Optional[float] = Field(default=None, ge=0.0)
    anesthetic_damping: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    microtubule_frequency_hz: Optional[float] = Field(default=None, ge=0.0)
    spin_network_vertices: Optional[List[List[float]]] = None
    hydra_em_enabled: bool = False
    gpcn_set_phi_enabled: bool = False
    orch_or_simulation_enabled: bool = False
    microtubule_proxy_count: int = Field(default=8, ge=0, le=256)
    microtubule_coupling_strength: float = Field(default=0.5, ge=0.0, le=1.0)
    quasicrystal_projection_enabled: bool = True
    plithogenic_contradiction_threshold: float = Field(default=0.35, ge=0.0, le=1.0)
    lattice_seed: int = Field(default=0, ge=0)
    observation_scale_min: float = Field(default=0.01, gt=0.0)
    observation_scale_max: float = Field(default=1.0, gt=0.0)
    gravity_null_test_enabled: bool = False
    gravity_null_test_seed: int = Field(default=734, ge=0)
    gravity_null_test_shots: int = Field(default=512, ge=16, le=100000)
    gravity_null_test_local_noise: float = Field(default=0.02, ge=0.0, le=1.0)
    gravity_null_test_leakage: float = Field(default=0.0, ge=0.0, le=1.0)
    gravity_null_test_mass_dispersion: float = Field(default=0.0, ge=0.0, le=1.0)
    gravity_null_test_chamber_contradiction: float = Field(default=0.25, ge=0.0, le=1.0)
    multiverse_experiments_enabled: bool = False
    multiverse_experiment_ids: List[MULTIVERSE_EXPERIMENT_ID] = Field(default_factory=list)
    multiverse_experiment_seed: int = Field(default=2026, ge=0)
    multiverse_experiment_shots: int = Field(default=512, ge=16, le=100000)
    multiverse_branch_coherence: float = Field(default=0.82, ge=0.0, le=1.0)
    multiverse_measurement_strength: float = Field(default=0.35, ge=0.0, le=1.0)
    multiverse_interference_visibility: float = Field(default=0.72, ge=0.0, le=1.0)
    multiverse_entanglement_fidelity: float = Field(default=0.84, ge=0.0, le=1.0)
    multiverse_classical_leakage: float = Field(default=0.0, ge=0.0, le=1.0)
    multiverse_memory_erasure: float = Field(default=1.0, ge=0.0, le=1.0)
    multiverse_scale_claim_strength: float = Field(default=0.65, ge=0.0, le=1.0)
    time_physics_experiments_enabled: bool = False
    time_physics_experiment_ids: List[TIME_PHYSICS_EXPERIMENT_ID] = Field(default_factory=list)
    time_physics_experiment_seed: int = Field(default=2026, ge=0)
    time_physics_experiment_shots: int = Field(default=512, ge=16, le=100000)
    time_physics_temporal_flow_strength: float = Field(default=0.74, ge=0.0, le=1.0)
    time_physics_relative_velocity_fraction: float = Field(default=0.35, ge=0.0, le=1.0)
    time_physics_simultaneity_offset: float = Field(default=0.40, ge=0.0, le=1.0)
    time_physics_entropy_gradient: float = Field(default=0.78, ge=0.0, le=1.0)
    time_physics_entanglement_growth: float = Field(default=0.62, ge=0.0, le=1.0)
    time_physics_decoherence_strength: float = Field(default=0.66, ge=0.0, le=1.0)
    time_physics_cosmological_boundary_pressure: float = Field(default=0.55, ge=0.0, le=1.0)
    time_physics_paradox_pressure: float = Field(default=0.15, ge=0.0, le=1.0)

    @model_validator(mode="before")
    @classmethod
    def accept_fractal_aliases(cls, values):
        return _copy_fractal_aliases(values)

    @model_validator(mode="after")
    def validate_samples_and_labels(self):
        if self.samples is None and self.labels is None:
            return self
        if not self.samples or not self.labels:
            raise ValueError("samples and labels must be provided together")
        if len(self.samples) != len(self.labels):
            raise ValueError("samples and labels must have the same length")
        if len(self.samples) > MAX_EVENTS:
            raise ValueError(f"At most {MAX_EVENTS} samples are accepted")
        return self

    @model_validator(mode="after")
    def validate_qnn_hydra_scale(self):
        if self.observation_scale_max <= self.observation_scale_min:
            raise ValueError("observation_scale_max must be greater than observation_scale_min")
        return self

    @field_validator(
        "fractal_dimension",
        "fractal_dimension_min",
        "fractal_dimension_max",
        "objective_reduction_energy_joule",
        "coherence_time_s",
        "anesthetic_damping",
        "microtubule_frequency_hz",
    )
    @classmethod
    def validate_fractal_numbers(cls, value: Optional[float], info):
        if value is None:
            return value
        return _finite(value, info.field_name)

    @field_validator("spin_network_vertices")
    @classmethod
    def validate_qnn_spin_network_vertices(cls, value: Optional[List[List[float]]]):
        if value is None:
            return value
        if len(value) > MAX_EVENTS:
            raise ValueError(f"At most {MAX_EVENTS} spin vertices are accepted")
        for vertex in value:
            if len(vertex) != 3:
                raise ValueError("spin network vertices must contain exactly three labels")
            for label in vertex:
                _finite(label, "spin_network_vertices")
        return value

    def dump_samples(self) -> Optional[List[List[Dict[str, Any]]]]:
        if self.samples is None:
            return None
        return [[event.model_dump(exclude_none=True) for event in sample] for sample in self.samples]


class PenroseHameroffObjectiveReductionRequest(BaseModel):
    objective_reduction_energy_joule: float
    reference_time_s: Optional[float] = Field(default=None, ge=0.0)

    @field_validator("objective_reduction_energy_joule", "reference_time_s")
    @classmethod
    def validate_objective_reduction_numbers(cls, value: Optional[float], info):
        if value is None:
            return value
        return _finite(value, info.field_name)


class GravityNullTestRequest(BaseModel):
    seed: int = Field(default=734, ge=0)
    shots: int = Field(default=512, ge=16, le=100000)
    entanglement_correlation: float = Field(default=0.92, ge=0.0, le=1.0)
    probe_bias: float = Field(default=0.5, ge=0.0, le=1.0)
    local_noise: float = Field(default=0.02, ge=0.0, le=1.0)
    leakage: float = Field(default=0.0, ge=0.0, le=1.0)
    mass_dispersion: float = Field(default=0.0, ge=0.0, le=1.0)
    chamber_contradiction: float = Field(default=0.25, ge=0.0, le=1.0)
    alpha_wave_frequency: float = Field(default=1.0, ge=0.0)
    beta_wave_frequency: float = Field(default=1.0, ge=0.0)
    omega_wave_frequency: float = Field(default=1.0, ge=0.0)
    d_min: float = Field(default=0.1, ge=0.0)
    d_max: float = Field(default=10.0, gt=0.0)
    D_min: float = 1.0
    D_max: float = 2.0
    delta_ns_threshold: float = Field(default=0.05, gt=0.0)
    frustration_threshold: float = Field(default=0.55, ge=0.0, le=1.0)
    include_sequence_export: bool = False
    include_qiskit_preview: bool = False
    include_e2b_datadog_review: bool = True
    source_i: str = Field(default="fractal_boundary", max_length=120)
    graviton_external_bound_ev: Optional[float] = Field(default=None, ge=0.0)
    graviton_bound_source: Optional[str] = Field(default=None, max_length=240)

    @field_validator(
        "entanglement_correlation",
        "probe_bias",
        "local_noise",
        "leakage",
        "mass_dispersion",
        "chamber_contradiction",
        "alpha_wave_frequency",
        "beta_wave_frequency",
        "omega_wave_frequency",
        "d_min",
        "d_max",
        "D_min",
        "D_max",
        "delta_ns_threshold",
        "frustration_threshold",
        "graviton_external_bound_ev",
    )
    @classmethod
    def validate_gravity_numbers(cls, value: Optional[float], info):
        if value is None:
            return value
        return _finite(value, info.field_name)

    @model_validator(mode="after")
    def validate_bounds(self):
        if self.d_max <= self.d_min:
            raise ValueError("d_max must be greater than d_min")
        if self.D_max <= self.D_min:
            raise ValueError("D_max must be greater than D_min")
        return self


class MultiverseExperimentBaseRequest(BaseModel):
    seed: int = Field(default=2026, ge=0)
    shots: int = Field(default=512, ge=16, le=100000)
    branch_coherence: float = Field(default=0.82, ge=0.0, le=1.0)
    measurement_strength: float = Field(default=0.35, ge=0.0, le=1.0)
    interference_visibility: float = Field(default=0.72, ge=0.0, le=1.0)
    entanglement_fidelity: float = Field(default=0.84, ge=0.0, le=1.0)
    classical_leakage: float = Field(default=0.0, ge=0.0, le=1.0)
    memory_erasure: float = Field(default=1.0, ge=0.0, le=1.0)
    scale_claim_strength: float = Field(default=0.65, ge=0.0, le=1.0)
    include_qiskit_preview: bool = False
    source_i: str = Field(default="fractal_boundary", max_length=120)

    @field_validator(
        "branch_coherence",
        "measurement_strength",
        "interference_visibility",
        "entanglement_fidelity",
        "classical_leakage",
        "memory_erasure",
        "scale_claim_strength",
    )
    @classmethod
    def validate_multiverse_numbers(cls, value: float, info):
        return _finite(value, info.field_name)


class MultiverseExperimentRequest(MultiverseExperimentBaseRequest):
    experiment_id: MULTIVERSE_EXPERIMENT_ID = "deutsch_quantum_computation_origin"


class MultiverseExperimentRunAllRequest(MultiverseExperimentBaseRequest):
    experiment_ids: List[MULTIVERSE_EXPERIMENT_ID] = Field(default_factory=list)


class TimePhysicsExperimentBaseRequest(BaseModel):
    seed: int = Field(default=2026, ge=0)
    shots: int = Field(default=512, ge=16, le=100000)
    temporal_flow_strength: float = Field(default=0.74, ge=0.0, le=1.0)
    relative_velocity_fraction: float = Field(default=0.35, ge=0.0, le=1.0)
    simultaneity_offset: float = Field(default=0.40, ge=0.0, le=1.0)
    entropy_gradient: float = Field(default=0.78, ge=0.0, le=1.0)
    entanglement_growth: float = Field(default=0.62, ge=0.0, le=1.0)
    decoherence_strength: float = Field(default=0.66, ge=0.0, le=1.0)
    cosmological_boundary_pressure: float = Field(default=0.55, ge=0.0, le=1.0)
    paradox_pressure: float = Field(default=0.15, ge=0.0, le=1.0)
    include_qiskit_preview: bool = False
    source_i: str = Field(default="fractal_boundary", max_length=120)

    @field_validator(
        "temporal_flow_strength",
        "relative_velocity_fraction",
        "simultaneity_offset",
        "entropy_gradient",
        "entanglement_growth",
        "decoherence_strength",
        "cosmological_boundary_pressure",
        "paradox_pressure",
    )
    @classmethod
    def validate_time_physics_numbers(cls, value: float, info):
        return _finite(value, info.field_name)


class TimePhysicsExperimentRequest(TimePhysicsExperimentBaseRequest):
    experiment_id: TIME_PHYSICS_EXPERIMENT_ID = "manifest_vs_physical_time_flow"


class TimePhysicsExperimentRunAllRequest(TimePhysicsExperimentBaseRequest):
    experiment_ids: List[TIME_PHYSICS_EXPERIMENT_ID] = Field(default_factory=list)


class HydraEMGPCNAnesthesiaSweepRequest(RuntimeRunRequest):
    damping_values: List[float] = Field(default_factory=lambda: [0.0, 0.25, 0.5, 0.75, 1.0])

    @field_validator("damping_values")
    @classmethod
    def validate_damping_values(cls, value: List[float]):
        if not value:
            raise ValueError("damping_values must contain at least one value")
        if len(value) > 16:
            raise ValueError("At most 16 damping values are accepted")
        for item in value:
            _finite(item, "damping_values")
            if item < 0.0 or item > 1.0:
                raise ValueError("damping_values must be between 0 and 1")
        return value


class NeuroBitProfileRequest(BaseModel):
    truth: float = Field(default=0.55, ge=0.0)
    indeterminacy: float = Field(default=0.30, ge=0.0)
    falsity: float = Field(default=0.15, ge=0.0)
    delta_falsity: float = 0.0
    n_qubits: int = Field(default=4, ge=1, le=12)
    state_basis: Literal["binary", "neutrobit"] = "binary"
    puncture_delta: Optional[float] = Field(default=None, gt=0.0)
    observer_strength: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    surface_width: Optional[float] = Field(default=None, gt=0.0, le=256.0)
    surface_height: Optional[float] = Field(default=None, gt=0.0, le=256.0)
    fractal_dimension: Optional[float] = None
    fractal_dimension_min: Optional[float] = None
    fractal_dimension_max: Optional[float] = None
    fractal_admissible: bool = True
    fractal_measurement_method: Optional[str] = Field(default=None, max_length=120)
    fractal_scale: Optional[str] = Field(default=None, max_length=120)
    plugin_hook_enabled: bool = False
    plugin_set: PLUGIN_SET = "mvp5"
    plugin_context: Dict[str, Any] = Field(default_factory=dict)
    cpai_context: Dict[str, Any] = Field(default_factory=dict)
    include_plugin_trace: bool = True

    @model_validator(mode="before")
    @classmethod
    def accept_df_alias(cls, values):
        if isinstance(values, dict) and "dF" in values and "delta_falsity" not in values:
            values = dict(values)
            values["delta_falsity"] = values.pop("dF")
        values = _copy_fractal_aliases(values)
        return values

    @field_validator(
        "truth",
        "indeterminacy",
        "falsity",
        "delta_falsity",
        "fractal_dimension",
        "fractal_dimension_min",
        "fractal_dimension_max",
    )
    @classmethod
    def validate_neurobit_numbers(cls, value: Optional[float], info):
        if value is None:
            return value
        return _finite(value, info.field_name)

    def to_profile_payload(self) -> Dict[str, Any]:
        return {
            "truth": self.truth,
            "indeterminacy": self.indeterminacy,
            "falsity": self.falsity,
            "delta_falsity": self.delta_falsity,
            "state_basis": self.state_basis,
            "puncture_delta": self.puncture_delta,
            "observer_strength": self.observer_strength,
            "surface_width": self.surface_width,
            "surface_height": self.surface_height,
            "fractal_dimension": self.fractal_dimension,
            "fractal_dimension_min": self.fractal_dimension_min,
            "fractal_dimension_max": self.fractal_dimension_max,
            "fractal_admissible": self.fractal_admissible,
            "fractal_measurement_method": self.fractal_measurement_method,
            "fractal_scale": self.fractal_scale,
            "plugin_hook_enabled": self.plugin_hook_enabled,
            "plugin_set": self.plugin_set,
            "plugin_context": self.plugin_context,
            "cpai_context": self.cpai_context,
            "include_plugin_trace": self.include_plugin_trace,
        }


class NeuroBitTunnelRequest(NeuroBitProfileRequest):
    data: str = Field(default="neurobit-demo", max_length=4096)


class NidusTripletProfileRequest(BaseModel):
    truth: float = Field(default=0.55, ge=0.0)
    indeterminacy: float = Field(default=0.30, ge=0.0)
    falsity: float = Field(default=0.15, ge=0.0)

    @model_validator(mode="before")
    @classmethod
    def accept_tif_aliases(cls, values):
        if not isinstance(values, dict):
            return values
        updated = dict(values)
        aliases = {
            "T": "truth",
            "I": "indeterminacy",
            "F": "falsity",
        }
        for alias, field_name in aliases.items():
            if alias in updated and field_name not in updated:
                updated[field_name] = updated[alias]
        return updated

    @field_validator("truth", "indeterminacy", "falsity")
    @classmethod
    def validate_triplet_numbers(cls, value: float, info):
        return _finite(value, info.field_name)


class NidusFusionSource(BaseModel):
    truth: float = Field(default=0.0, ge=0.0)
    indeterminacy: float = Field(default=0.0, ge=0.0)
    falsity: float = Field(default=0.0, ge=0.0)
    weight: float = Field(default=1.0, ge=0.0)
    intersection_indeterminacy: float = Field(default=0.0, ge=0.0)
    label: str = Field(default="", max_length=MAX_LABEL_LENGTH)

    @model_validator(mode="before")
    @classmethod
    def accept_source_aliases(cls, values):
        if not isinstance(values, dict):
            return values
        updated = dict(values)
        aliases = {
            "T": "truth",
            "I": "indeterminacy",
            "F": "falsity",
            "beta": "weight",
            "source_importance": "weight",
            "indeterminate_intersection": "intersection_indeterminacy",
            "intersection_unknown": "intersection_indeterminacy",
        }
        for alias, field_name in aliases.items():
            if alias in updated and field_name not in updated:
                updated[field_name] = updated[alias]
        return updated

    @field_validator("truth", "indeterminacy", "falsity", "weight", "intersection_indeterminacy")
    @classmethod
    def validate_source_numbers(cls, value: float, info):
        return _finite(value, info.field_name)

    def to_fusion_payload(self) -> Dict[str, Any]:
        payload = {
            "truth": self.truth,
            "indeterminacy": self.indeterminacy,
            "falsity": self.falsity,
            "weight": self.weight,
            "intersection_indeterminacy": self.intersection_indeterminacy,
        }
        if self.label:
            payload["label"] = self.label
        return payload


class NidusFusionProfileRequest(BaseModel):
    sources: List[NidusFusionSource] = Field(default_factory=list)

    @field_validator("sources")
    @classmethod
    def validate_sources(cls, value: List[NidusFusionSource]):
        if not value:
            raise ValueError("sources must contain at least one source")
        if len(value) > MAX_EVENTS:
            raise ValueError(f"At most {MAX_EVENTS} sources are accepted")
        return value

    def dump_sources(self) -> List[Dict[str, Any]]:
        return [source.to_fusion_payload() for source in self.sources]


class NidusPartialMembershipMeanRequest(BaseModel):
    values: List[float] = Field(default_factory=list)
    memberships: List[float] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_lengths(self):
        if not self.values:
            raise ValueError("values must not be empty")
        if len(self.values) != len(self.memberships):
            raise ValueError("values and memberships must have the same length")
        if len(self.values) > MAX_EVENTS:
            raise ValueError(f"At most {MAX_EVENTS} values are accepted")
        return self

    @field_validator("values", "memberships")
    @classmethod
    def validate_numeric_lists(cls, value: List[float], info):
        for item in value:
            _finite(item, info.field_name)
        if info.field_name == "memberships" and any(float(item) < 0.0 for item in value):
            raise ValueError("memberships must be non-negative")
        return value


class CommandRequest(BaseModel):
    payload: Optional[RuntimeRunRequest] = None
    observations: Optional[List[Observation]] = None
    samples: Optional[List[List[Observation]]] = None
    labels: Optional[List[int]] = None
    epochs: int = Field(default=24, ge=0, le=256)
    test_size: float = Field(default=0.25, ge=0.0, le=0.9)
    state_basis: Literal["binary", "neutrobit"] = "binary"
    puncture_delta: Optional[float] = Field(default=None, gt=0.0)
    observer_strength: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    fractal_dimension: Optional[float] = None
    fractal_dimension_min: Optional[float] = None
    fractal_dimension_max: Optional[float] = None
    fractal_admissible: bool = True
    fractal_measurement_method: Optional[str] = Field(default=None, max_length=120)
    fractal_scale: Optional[str] = Field(default=None, max_length=120)
    plugin_hook_enabled: bool = False
    plugin_set: PLUGIN_SET = "mvp5"
    plugin_context: Dict[str, Any] = Field(default_factory=dict)
    cpai_context: Dict[str, Any] = Field(default_factory=dict)
    include_plugin_trace: bool = True
    neurobit: Optional[NeuroBitTunnelRequest] = None
    penrose_hameroff_enabled: bool = False
    objective_reduction_energy_joule: Optional[float] = None
    coherence_time_s: Optional[float] = Field(default=None, ge=0.0)
    anesthetic_damping: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    microtubule_frequency_hz: Optional[float] = Field(default=None, ge=0.0)
    spin_network_vertices: Optional[List[List[float]]] = None
    hydra_em_enabled: bool = False
    gpcn_set_phi_enabled: bool = False
    orch_or_simulation_enabled: bool = False
    microtubule_proxy_count: int = Field(default=8, ge=0, le=256)
    microtubule_coupling_strength: float = Field(default=0.5, ge=0.0, le=1.0)
    quasicrystal_projection_enabled: bool = True
    plithogenic_contradiction_threshold: float = Field(default=0.35, ge=0.0, le=1.0)
    lattice_seed: int = Field(default=0, ge=0)
    observation_scale_min: float = Field(default=0.01, gt=0.0)
    observation_scale_max: float = Field(default=1.0, gt=0.0)
    gravity_null_test_enabled: bool = False
    gravity_null_test_seed: int = Field(default=734, ge=0)
    gravity_null_test_shots: int = Field(default=512, ge=16, le=100000)
    gravity_null_test_local_noise: float = Field(default=0.02, ge=0.0, le=1.0)
    gravity_null_test_leakage: float = Field(default=0.0, ge=0.0, le=1.0)
    gravity_null_test_mass_dispersion: float = Field(default=0.0, ge=0.0, le=1.0)
    gravity_null_test_chamber_contradiction: float = Field(default=0.25, ge=0.0, le=1.0)
    multiverse_experiments_enabled: bool = False
    multiverse_experiment_ids: List[MULTIVERSE_EXPERIMENT_ID] = Field(default_factory=list)
    multiverse_experiment_seed: int = Field(default=2026, ge=0)
    multiverse_experiment_shots: int = Field(default=512, ge=16, le=100000)
    multiverse_branch_coherence: float = Field(default=0.82, ge=0.0, le=1.0)
    multiverse_measurement_strength: float = Field(default=0.35, ge=0.0, le=1.0)
    multiverse_interference_visibility: float = Field(default=0.72, ge=0.0, le=1.0)
    multiverse_entanglement_fidelity: float = Field(default=0.84, ge=0.0, le=1.0)
    multiverse_classical_leakage: float = Field(default=0.0, ge=0.0, le=1.0)
    multiverse_memory_erasure: float = Field(default=1.0, ge=0.0, le=1.0)
    multiverse_scale_claim_strength: float = Field(default=0.65, ge=0.0, le=1.0)
    time_physics_experiments_enabled: bool = False
    time_physics_experiment_ids: List[TIME_PHYSICS_EXPERIMENT_ID] = Field(default_factory=list)
    time_physics_experiment_seed: int = Field(default=2026, ge=0)
    time_physics_experiment_shots: int = Field(default=512, ge=16, le=100000)
    time_physics_temporal_flow_strength: float = Field(default=0.74, ge=0.0, le=1.0)
    time_physics_relative_velocity_fraction: float = Field(default=0.35, ge=0.0, le=1.0)
    time_physics_simultaneity_offset: float = Field(default=0.40, ge=0.0, le=1.0)
    time_physics_entropy_gradient: float = Field(default=0.78, ge=0.0, le=1.0)
    time_physics_entanglement_growth: float = Field(default=0.62, ge=0.0, le=1.0)
    time_physics_decoherence_strength: float = Field(default=0.66, ge=0.0, le=1.0)
    time_physics_cosmological_boundary_pressure: float = Field(default=0.55, ge=0.0, le=1.0)
    time_physics_paradox_pressure: float = Field(default=0.15, ge=0.0, le=1.0)

    @model_validator(mode="before")
    @classmethod
    def accept_fractal_aliases(cls, values):
        return _copy_fractal_aliases(values)


class CommandResponse(BaseModel):
    success: bool
    output: str
    type: str
    data: Dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    detail: str
    code: Literal["validation_error", "not_found", "runtime_error"] = "runtime_error"
