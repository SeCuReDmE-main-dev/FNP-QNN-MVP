"""Core primitives for the FNP-QNN research prototype."""

from .cerebrum_adapter import CerebrumAdapter, CerebrumFeatureBundle, CrossModalEvent
from .phi_framework import PhiFramework, QuantumState
from .qnn_nucleus import QNNBenchmarkResult, QNNCandidate, QNNNucleus

__version__ = "1.1.0-research"
__author__ = "SeCuReDmE Innovation Lab"

__all__ = [
    "PhiFramework",
    "QuantumState",
    "CrossModalEvent",
    "CerebrumFeatureBundle",
    "CerebrumAdapter",
    "QNNCandidate",
    "QNNBenchmarkResult",
    "QNNNucleus",
]
