"""Core primitives for the FNP-QNN research prototype."""

from .cerebrum_adapter import CerebrumAdapter, CerebrumFeatureBundle, CrossModalEvent
from .cerebrum_runtime_bridge import CerebrumMemoryEvent, CerebrumRuntimeBridge, CerebrumRuntimeState, CrossModalPair
from .life_science_port import LifeScienceObservationPort
from .phi_framework import PhiFramework, QuantumState
from .qnn_nucleus import QNNBenchmarkResult, QNNCandidate, QNNNucleus

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
    "LifeScienceObservationPort",
    "QNNCandidate",
    "QNNBenchmarkResult",
    "QNNNucleus",
]
