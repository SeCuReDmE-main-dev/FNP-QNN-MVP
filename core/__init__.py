"""Core primitives for the FNP-QNN research prototype."""

from .cerebrum_adapter import CerebrumAdapter, CerebrumFeatureBundle, CrossModalEvent
from .cerebrum_runtime_bridge import CerebrumMemoryEvent, CerebrumRuntimeBridge, CerebrumRuntimeState, CrossModalPair
from .lvfm_runtime_graph import (
    LVFMRuntimeGraph,
    LVFMDecision,
    LVFMDirection,
    RegisterBit,
    RegisterKey,
)
from .life_science_port import LifeScienceObservationPort
from .phi_framework import PhiFramework, QuantumState
from .qnn_nucleus import QNNBenchmarkResult, QNNCandidate, QNNNucleus
from .neurobit_gate_tunnel import (
    NeuroBitProfile,
    run_neurobit_gates,
    run_neurobit_tunnel_demo,
)
from .experiment_seed import ExperimentSeedManager
from .quantum_feature_transforms import (
    complex_wavefunction_to_amplitude_phase_features,
    structure_vector_to_phi_scaled_state,
)
from .neutrosophic_quantum_primitives import (
    CoherentNeutroState,
    DecoherentNeutroState,
    FractalCarrierContext,
    NeutrobitState,
    fractal_carrier_profile,
    neutrobit_features_from_vector,
    neutrosophic_gate_algebra,
    neutrosophic_measurement,
    normalize_fractal_dimension,
    observer_effect_profile,
    partial_entanglement_profile,
    punctured_surface_state,
    punctured_wave_state,
)
from .runtime_state_store import RuntimeStateStore

__version__ = "1.2.0-research"
__author__ = "SeCuReDmE Innovation Lab"

__all__ = [
    "PhiFramework",
    "QuantumState",
    "CrossModalEvent",
    "CerebrumFeatureBundle",
    "CerebrumAdapter",
    "CerebrumMemoryEvent",
    "CrossModalPair",
    "CerebrumRuntimeState",
    "CerebrumRuntimeBridge",
    "RegisterBit",
    "RegisterKey",
    "LVFMDirection",
    "LVFMDecision",
    "LVFMRuntimeGraph",
    "LifeScienceObservationPort",
    "QNNCandidate",
    "QNNBenchmarkResult",
    "QNNNucleus",
    "NeuroBitProfile",
    "run_neurobit_gates",
    "run_neurobit_tunnel_demo",
    "ExperimentSeedManager",
    "complex_wavefunction_to_amplitude_phase_features",
    "structure_vector_to_phi_scaled_state",
    "CoherentNeutroState",
    "DecoherentNeutroState",
    "FractalCarrierContext",
    "NeutrobitState",
    "fractal_carrier_profile",
    "neutrobit_features_from_vector",
    "neutrosophic_gate_algebra",
    "neutrosophic_measurement",
    "normalize_fractal_dimension",
    "observer_effect_profile",
    "partial_entanglement_profile",
    "punctured_surface_state",
    "punctured_wave_state",
    "RuntimeStateStore",
]
