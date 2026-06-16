"""Deterministic family and capability registry for Network Designer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from .graph import NetworkFamily


@dataclass(frozen=True)
class FamilyDescriptor:
    """Registry descriptor for a supported family."""

    family: NetworkFamily
    supports_qiskit_lane: bool
    allows_cycles: bool
    description: str
    default_node_type: str


_REGISTRY: Dict[NetworkFamily, FamilyDescriptor] = {
    NetworkFamily.NEURAL_NETWORK: FamilyDescriptor(
        family=NetworkFamily.NEURAL_NETWORK,
        supports_qiskit_lane=False,
        allows_cycles=False,
        description="Deterministic TorchSurrogate neural preset and placeholders.",
        default_node_type="neural_gate",
    ),
    NetworkFamily.QUANTUM_QNN: FamilyDescriptor(
        family=NetworkFamily.QUANTUM_QNN,
        supports_qiskit_lane=True,
        allows_cycles=False,
        description="Quantum QNN graph placeholder with visible Qiskit lane.",
        default_node_type="quantum_layer",
    ),
    NetworkFamily.SPIDERWEB_NETWORK: FamilyDescriptor(
        family=NetworkFamily.SPIDERWEB_NETWORK,
        supports_qiskit_lane=False,
        allows_cycles=True,
        description="Local spiderweb graph with iterative local propagation.",
        default_node_type="spiderweb_node",
    ),
    NetworkFamily.MEMORY_GRAPH: FamilyDescriptor(
        family=NetworkFamily.MEMORY_GRAPH,
        supports_qiskit_lane=False,
        allows_cycles=False,
        description="Memory-graph placeholder with deterministic accumulation.",
        default_node_type="memory_node",
    ),
    NetworkFamily.CROSSMODAL_GRAPH: FamilyDescriptor(
        family=NetworkFamily.CROSSMODAL_GRAPH,
        supports_qiskit_lane=False,
        allows_cycles=False,
        description="Crossmodal fusion preset with deterministic merge behavior.",
        default_node_type="crossmodal_node",
    ),
    NetworkFamily.LOGIC_DECISION_NETWORK: FamilyDescriptor(
        family=NetworkFamily.LOGIC_DECISION_NETWORK,
        supports_qiskit_lane=False,
        allows_cycles=False,
        description="Logic / decision-path placeholder with deterministic decisions.",
        default_node_type="logic_node",
    ),
    NetworkFamily.CUSTOM_NETWORK: FamilyDescriptor(
        family=NetworkFamily.CUSTOM_NETWORK,
        supports_qiskit_lane=False,
        allows_cycles=False,
        description="Blank custom workflow container for future user extensions.",
        default_node_type="custom_node",
    ),
}


def get_descriptor(family: NetworkFamily | str) -> FamilyDescriptor:
    descriptor = _REGISTRY.get(_coerce_family(family))
    if descriptor is None:
        raise ValueError(f"unsupported network family: {family}")
    return descriptor


def _coerce_family(family: NetworkFamily | str) -> NetworkFamily:
    if isinstance(family, NetworkFamily):
        return family
    try:
        return NetworkFamily(str(family))
    except ValueError as exc:
        raise ValueError(f"unsupported network family: {family}") from exc


def supports_qiskit_lane(family: NetworkFamily | str) -> bool:
    return get_descriptor(family).supports_qiskit_lane


def supports_cycles(family: NetworkFamily | str) -> bool:
    return get_descriptor(family).allows_cycles


def all_descriptors() -> Tuple[FamilyDescriptor, ...]:
    return tuple(_REGISTRY.values())


def all_families() -> Tuple[str, ...]:
    return tuple(descriptor.family.value for descriptor in all_descriptors())
