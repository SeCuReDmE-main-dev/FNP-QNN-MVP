"""Deterministic Network Designer presets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Tuple

from .graph import NetworkEdge, NetworkFamily, NetworkGraph, NetworkNode, NetworkPort, NetworkPortDirection
from .registry import all_families


def _node(
    node_id: str,
    family: NetworkFamily,
    node_type: str,
    label: str,
    *,
    ports: Tuple[tuple[str, NetworkPortDirection], ...],
) -> NetworkNode:
    return NetworkNode(
        node_id=node_id,
        family=family.value,
        node_type=node_type,
        label=label,
        ports=tuple(
            NetworkPort(
                port_id=port_id,
                direction=direction,
                label=f"{label}:{port_id}",
            )
            for port_id, direction in ports
        ),
    )


@dataclass(frozen=True)
class NetworkPreset:
    """Named deterministic graph template."""

    family: NetworkFamily
    preset_id: str
    name: str
    description: str
    graph_builder: Callable[[], NetworkGraph]
    metadata: Dict[str, str]


def _build_neural_network_preset() -> NetworkGraph:
    graph = NetworkGraph(family=NetworkFamily.NEURAL_NETWORK.value, metadata={"preset": "neural_network_v1"})
    input_node = _node(
        "input",
        NetworkFamily.NEURAL_NETWORK,
        "input_node",
        "Input Source",
        ports=(("out", NetworkPortDirection.OUTPUT),),
    )
    hidden_node = _node(
        "encoder",
        NetworkFamily.NEURAL_NETWORK,
        "dense_node",
        "Encoder",
        ports=(
            ("in", NetworkPortDirection.INPUT),
            ("out", NetworkPortDirection.OUTPUT),
        ),
    )
    output_node = _node(
        "output",
        NetworkFamily.NEURAL_NETWORK,
        "output_node",
        "Output Sink",
        ports=(("in", NetworkPortDirection.INPUT),),
    )
    graph.add_node(input_node)
    graph.add_node(hidden_node)
    graph.add_node(output_node)
    graph.add_edge(NetworkEdge("input", "out", "encoder", "in", 1.0))
    graph.add_edge(NetworkEdge("encoder", "out", "output", "in", 0.9))
    return graph


def _build_quantum_qnn_preset() -> NetworkGraph:
    graph = NetworkGraph(family=NetworkFamily.QUANTUM_QNN.value, metadata={"preset": "quantum_qnn_v1"})
    input_node = _node(
        "input",
        NetworkFamily.QUANTUM_QNN,
        "quantum_input",
        "Quantum Input",
        ports=(("out", NetworkPortDirection.OUTPUT),),
    )
    quantum_node = _node(
        "quantum_layer",
        NetworkFamily.QUANTUM_QNN,
        "quantum_layer",
        "Quantum QNN Layer",
        ports=(
            ("in", NetworkPortDirection.INPUT),
            ("out", NetworkPortDirection.OUTPUT),
        ),
    )
    output_node = _node(
        "output",
        NetworkFamily.QUANTUM_QNN,
        "output_node",
        "Quantum Output",
        ports=(("in", NetworkPortDirection.INPUT),),
    )
    graph.add_node(input_node)
    graph.add_node(quantum_node)
    graph.add_node(output_node)
    graph.add_edge(NetworkEdge("input", "out", "quantum_layer", "in", 1.0))
    graph.add_edge(NetworkEdge("quantum_layer", "out", "output", "in", 1.0))
    return graph


def _build_spiderweb_preset() -> NetworkGraph:
    graph = NetworkGraph(
        family=NetworkFamily.SPIDERWEB_NETWORK.value,
        metadata={"preset": "spiderweb_network_v1"},
    )
    input_node = _node(
        "source",
        NetworkFamily.SPIDERWEB_NETWORK,
        "spider_input",
        "Spider Source",
        ports=(("out", NetworkPortDirection.OUTPUT),),
    )
    hub_node = _node(
        "hub",
        NetworkFamily.SPIDERWEB_NETWORK,
        "spiderhub",
        "Spider Hub",
        ports=(
            ("in", NetworkPortDirection.INPUT),
            ("out", NetworkPortDirection.OUTPUT),
        ),
    )
    leg_node = _node(
        "leg",
        NetworkFamily.SPIDERWEB_NETWORK,
        "spider_leg",
        "Spider Leg",
        ports=(
            ("in", NetworkPortDirection.INPUT),
            ("out", NetworkPortDirection.OUTPUT),
        ),
    )
    output_node = _node(
        "output",
        NetworkFamily.SPIDERWEB_NETWORK,
        "output_node",
        "Spider Output",
        ports=(("in", NetworkPortDirection.INPUT),),
    )
    graph.add_node(input_node)
    graph.add_node(hub_node)
    graph.add_node(leg_node)
    graph.add_node(output_node)
    graph.add_edge(NetworkEdge("source", "out", "hub", "in", 1.0))
    graph.add_edge(NetworkEdge("hub", "out", "leg", "in", 0.9))
    graph.add_edge(NetworkEdge("leg", "out", "hub", "in", 0.75))
    graph.add_edge(NetworkEdge("hub", "out", "output", "in", 1.0))
    return graph


def _build_memory_graph_preset() -> NetworkGraph:
    graph = NetworkGraph(family=NetworkFamily.MEMORY_GRAPH.value, metadata={"preset": "memory_graph_v1"})
    input_node = _node(
        "memory_input",
        NetworkFamily.MEMORY_GRAPH,
        "memory_input",
        "Memory Input",
        ports=(("out", NetworkPortDirection.OUTPUT),),
    )
    memory_node = _node(
        "memory_store",
        NetworkFamily.MEMORY_GRAPH,
        "memory_buffer",
        "Memory Store",
        ports=(
            ("in", NetworkPortDirection.INPUT),
            ("out", NetworkPortDirection.OUTPUT),
        ),
    )
    output_node = _node(
        "memory_output",
        NetworkFamily.MEMORY_GRAPH,
        "memory_output",
        "Memory Output",
        ports=(("in", NetworkPortDirection.INPUT),),
    )
    graph.add_node(input_node)
    graph.add_node(memory_node)
    graph.add_node(output_node)
    graph.add_edge(NetworkEdge("memory_input", "out", "memory_store", "in", 1.0))
    graph.add_edge(NetworkEdge("memory_store", "out", "memory_output", "in", 1.0))
    return graph


def _build_crossmodal_graph_preset() -> NetworkGraph:
    graph = NetworkGraph(family=NetworkFamily.CROSSMODAL_GRAPH.value, metadata={"preset": "crossmodal_graph_v1"})
    audio_node = _node(
        "audio_input",
        NetworkFamily.CROSSMODAL_GRAPH,
        "audio_source",
        "Audio Input",
        ports=(("out", NetworkPortDirection.OUTPUT),),
    )
    visual_node = _node(
        "visual_input",
        NetworkFamily.CROSSMODAL_GRAPH,
        "visual_source",
        "Visual Input",
        ports=(("out", NetworkPortDirection.OUTPUT),),
    )
    fusion_node = _node(
        "fusion",
        NetworkFamily.CROSSMODAL_GRAPH,
        "fusion_node",
        "Crossmodal Fusion",
        ports=(
            ("audio_in", NetworkPortDirection.INPUT),
            ("visual_in", NetworkPortDirection.INPUT),
            ("out", NetworkPortDirection.OUTPUT),
        ),
    )
    output_node = _node(
        "crossmodal_output",
        NetworkFamily.CROSSMODAL_GRAPH,
        "output_node",
        "Crossmodal Output",
        ports=(("in", NetworkPortDirection.INPUT),),
    )
    graph.add_node(audio_node)
    graph.add_node(visual_node)
    graph.add_node(fusion_node)
    graph.add_node(output_node)
    graph.add_edge(NetworkEdge("audio_input", "out", "fusion", "audio_in", 1.0))
    graph.add_edge(NetworkEdge("visual_input", "out", "fusion", "visual_in", 1.0))
    graph.add_edge(NetworkEdge("fusion", "out", "crossmodal_output", "in", 1.0))
    return graph


def _build_logic_decision_preset() -> NetworkGraph:
    graph = NetworkGraph(
        family=NetworkFamily.LOGIC_DECISION_NETWORK.value,
        metadata={"preset": "logic_decision_network_v1"},
    )
    input_node = _node(
        "decision_input",
        NetworkFamily.LOGIC_DECISION_NETWORK,
        "input_node",
        "Decision Input",
        ports=(("out", NetworkPortDirection.OUTPUT),),
    )
    decision_node = _node(
        "rule_node",
        NetworkFamily.LOGIC_DECISION_NETWORK,
        "rule_node",
        "Rule Node",
        ports=(
            ("in", NetworkPortDirection.INPUT),
            ("out", NetworkPortDirection.OUTPUT),
        ),
    )
    output_node = _node(
        "decision_output",
        NetworkFamily.LOGIC_DECISION_NETWORK,
        "output_node",
        "Decision Output",
        ports=(("in", NetworkPortDirection.INPUT),),
    )
    graph.add_node(input_node)
    graph.add_node(decision_node)
    graph.add_node(output_node)
    graph.add_edge(NetworkEdge("decision_input", "out", "rule_node", "in", 1.0))
    graph.add_edge(NetworkEdge("rule_node", "out", "decision_output", "in", 1.0))
    return graph


def _build_gravity_null_test_preset() -> NetworkGraph:
    graph = NetworkGraph(
        family=NetworkFamily.GRAVITY_NULL_TEST.value,
        metadata={
            "preset": "gravity_null_test_v1",
            "sequence_export": "optional",
            "qiskit_preview": "optional",
            "e2b_datadog_review": "optional",
        },
    )
    source_node = _node(
        "source_ledger",
        NetworkFamily.GRAVITY_NULL_TEST,
        "video_source_ledger",
        "Video Source Ledger",
        ports=(("out", NetworkPortDirection.OUTPUT),),
    )
    entangled_node = _node(
        "entangled_ab",
        NetworkFamily.GRAVITY_NULL_TEST,
        "entangled_pair",
        "A-B Entangled Pair",
        ports=(("in", NetworkPortDirection.INPUT), ("out", NetworkPortDirection.OUTPUT)),
    )
    probe_node = _node(
        "probe_c",
        NetworkFamily.GRAVITY_NULL_TEST,
        "uncorrelated_probe",
        "C Probe",
        ports=(("out", NetworkPortDirection.OUTPUT),),
    )
    chamber_node = _node(
        "axiomatic_chamber",
        NetworkFamily.GRAVITY_NULL_TEST,
        "gpcn_chamber",
        "Axiomatic Chamber",
        ports=(
            ("ab_in", NetworkPortDirection.INPUT),
            ("c_in", NetworkPortDirection.INPUT),
            ("out", NetworkPortDirection.OUTPUT),
        ),
    )
    classifier_node = _node(
        "residual_classifier",
        NetworkFamily.GRAVITY_NULL_TEST,
        "residual_frustration_classifier",
        "Residual Classifier",
        ports=(("in", NetworkPortDirection.INPUT), ("out", NetworkPortDirection.OUTPUT)),
    )
    review_node = _node(
        "e2b_datadog_review",
        NetworkFamily.GRAVITY_NULL_TEST,
        "micro_vm_telemetry_review",
        "E2B Datadog Review",
        ports=(("in", NetworkPortDirection.INPUT),),
    )
    for node in (source_node, entangled_node, probe_node, chamber_node, classifier_node, review_node):
        graph.add_node(node)
    graph.add_edge(NetworkEdge("source_ledger", "out", "entangled_ab", "in", 1.0))
    graph.add_edge(NetworkEdge("entangled_ab", "out", "axiomatic_chamber", "ab_in", 1.0))
    graph.add_edge(NetworkEdge("probe_c", "out", "axiomatic_chamber", "c_in", 0.7))
    graph.add_edge(NetworkEdge("axiomatic_chamber", "out", "residual_classifier", "in", 1.0))
    graph.add_edge(NetworkEdge("residual_classifier", "out", "e2b_datadog_review", "in", 1.0))
    return graph


def _build_multiverse_experiments_preset() -> NetworkGraph:
    graph = NetworkGraph(
        family=NetworkFamily.MULTIVERSE_EXPERIMENTS.value,
        metadata={
            "preset": "multiverse_experiments_v1",
            "source": "quantum_paradoxes_maria_violaris",
            "qiskit_preview": "optional",
            "claim_boundary": "simulator_evidence_only",
        },
    )
    source_node = _node(
        "source_ledger",
        NetworkFamily.MULTIVERSE_EXPERIMENTS,
        "source_ledger",
        "Quantum Paradoxes Sources",
        ports=(("out", NetworkPortDirection.OUTPUT),),
    )
    lanes = (
        ("deutsch_lane", "deutsch_quantum_computation_origin", "Deutsch Computation"),
        ("bomb_lane", "elitzur_vaidman_bomb_tester", "Bomb Tester"),
        ("teleportation_lane", "entanglement_teleportation_branch_accounting", "Teleportation Accounting"),
        ("google_scale_lane", "google_quantum_computer_scale_review", "Google Scale Review"),
        ("wigner_lane", "wigner_friend_inter_branch_communication", "Wigner Friend"),
    )
    classifier_node = _node(
        "claim_boundary_classifier",
        NetworkFamily.MULTIVERSE_EXPERIMENTS,
        "claim_boundary_classifier",
        "Claim Boundary Classifier",
        ports=(("in", NetworkPortDirection.INPUT), ("out", NetworkPortDirection.OUTPUT)),
    )
    output_node = _node(
        "suite_output",
        NetworkFamily.MULTIVERSE_EXPERIMENTS,
        "suite_output",
        "Suite Output",
        ports=(("in", NetworkPortDirection.INPUT),),
    )
    graph.add_node(source_node)
    graph.add_node(classifier_node)
    graph.add_node(output_node)
    for node_id, experiment_id, label in lanes:
        lane_node = _node(
            node_id,
            NetworkFamily.MULTIVERSE_EXPERIMENTS,
            "multiverse_experiment_node",
            label,
            ports=(("in", NetworkPortDirection.INPUT), ("out", NetworkPortDirection.OUTPUT)),
        )
        graph.add_node(lane_node)
        graph.add_edge(NetworkEdge("source_ledger", "out", node_id, "in", 1.0))
        graph.add_edge(NetworkEdge(node_id, "out", "claim_boundary_classifier", "in", 0.8))
        graph.nodes[node_id].metadata["experiment_id"] = experiment_id
    graph.add_edge(NetworkEdge("claim_boundary_classifier", "out", "suite_output", "in", 1.0))
    return graph


def _build_time_physics_experiments_preset() -> NetworkGraph:
    graph = NetworkGraph(
        family=NetworkFamily.TIME_PHYSICS_EXPERIMENTS.value,
        metadata={
            "preset": "time_physics_experiments_v1",
            "source": "jim_alkhalili_time_physics",
            "qiskit_preview": "optional",
            "claim_boundary": "simulator_evidence_only",
        },
    )
    source_node = _node(
        "source_ledger",
        NetworkFamily.TIME_PHYSICS_EXPERIMENTS,
        "source_ledger",
        "Time Physics Sources",
        ports=(("out", NetworkPortDirection.OUTPUT),),
    )
    lanes = (
        ("flow_lane", "manifest_vs_physical_time_flow", "Manifest Time Flow"),
        ("dilation_lane", "relativistic_time_dilation_block_universe", "Time Dilation"),
        ("now_lane", "relativity_of_simultaneity_now", "Relativity of Now"),
        ("entropy_lane", "thermodynamic_entropy_arrow", "Entropy Arrow"),
        ("decoherence_lane", "entanglement_decoherence_arrow", "Decoherence Arrow"),
        ("boundary_lane", "cosmological_boundary_time_travel", "Cosmology Boundary"),
    )
    classifier_node = _node(
        "claim_boundary_classifier",
        NetworkFamily.TIME_PHYSICS_EXPERIMENTS,
        "claim_boundary_classifier",
        "Claim Boundary Classifier",
        ports=(("in", NetworkPortDirection.INPUT), ("out", NetworkPortDirection.OUTPUT)),
    )
    output_node = _node(
        "suite_output",
        NetworkFamily.TIME_PHYSICS_EXPERIMENTS,
        "suite_output",
        "Suite Output",
        ports=(("in", NetworkPortDirection.INPUT),),
    )
    graph.add_node(source_node)
    graph.add_node(classifier_node)
    graph.add_node(output_node)
    for node_id, experiment_id, label in lanes:
        lane_node = _node(
            node_id,
            NetworkFamily.TIME_PHYSICS_EXPERIMENTS,
            "time_physics_experiment_node",
            label,
            ports=(("in", NetworkPortDirection.INPUT), ("out", NetworkPortDirection.OUTPUT)),
        )
        graph.add_node(lane_node)
        graph.add_edge(NetworkEdge("source_ledger", "out", node_id, "in", 1.0))
        graph.add_edge(NetworkEdge(node_id, "out", "claim_boundary_classifier", "in", 0.8))
        graph.nodes[node_id].metadata["experiment_id"] = experiment_id
    graph.add_edge(NetworkEdge("claim_boundary_classifier", "out", "suite_output", "in", 1.0))
    return graph


def _build_custom_network_preset() -> NetworkGraph:
    graph = NetworkGraph(family=NetworkFamily.CUSTOM_NETWORK.value, metadata={"preset": "custom_network_v1"})
    input_node = _node(
        "custom_input",
        NetworkFamily.CUSTOM_NETWORK,
        "custom_input",
        "Custom Input",
        ports=(("out", NetworkPortDirection.OUTPUT),),
    )
    custom_node = _node(
        "custom_block",
        NetworkFamily.CUSTOM_NETWORK,
        "custom_block",
        "Custom Block",
        ports=(
            ("in", NetworkPortDirection.INPUT),
            ("out", NetworkPortDirection.OUTPUT),
        ),
    )
    output_node = _node(
        "custom_output",
        NetworkFamily.CUSTOM_NETWORK,
        "custom_output",
        "Custom Output",
        ports=(("in", NetworkPortDirection.INPUT),),
    )
    graph.add_node(input_node)
    graph.add_node(custom_node)
    graph.add_node(output_node)
    graph.add_edge(NetworkEdge("custom_input", "out", "custom_block", "in", 1.0))
    graph.add_edge(NetworkEdge("custom_block", "out", "custom_output", "in", 1.0))
    return graph


_PRESETS: Dict[NetworkFamily, NetworkPreset] = {
    NetworkFamily.NEURAL_NETWORK: NetworkPreset(
        family=NetworkFamily.NEURAL_NETWORK,
        preset_id="neural_network_v1",
        name="Neural Network Preset",
        description="Dense-style deterministic placeholder pipeline for TorchSurrogate.",
        graph_builder=_build_neural_network_preset,
        metadata={"qiskit_available": "false"},
    ),
    NetworkFamily.QUANTUM_QNN: NetworkPreset(
        family=NetworkFamily.QUANTUM_QNN,
        preset_id="quantum_qnn_v1",
        name="Quantum QNN Preset",
        description="Quantum QNN placeholder with visible Qiskit lane.",
        graph_builder=_build_quantum_qnn_preset,
        metadata={"qiskit_available": "true"},
    ),
    NetworkFamily.SPIDERWEB_NETWORK: NetworkPreset(
        family=NetworkFamily.SPIDERWEB_NETWORK,
        preset_id="spiderweb_network_v1",
        name="Spiderweb Network Preset",
        description="Local iterative spiderweb propagation with one deterministic cycle.",
        graph_builder=_build_spiderweb_preset,
        metadata={"qiskit_available": "false"},
    ),
    NetworkFamily.MEMORY_GRAPH: NetworkPreset(
        family=NetworkFamily.MEMORY_GRAPH,
        preset_id="memory_graph_v1",
        name="Memory Graph Preset",
        description="Memory-chain placeholder for event encoding replay.",
        graph_builder=_build_memory_graph_preset,
        metadata={"qiskit_available": "false"},
    ),
    NetworkFamily.CROSSMODAL_GRAPH: NetworkPreset(
        family=NetworkFamily.CROSSMODAL_GRAPH,
        preset_id="crossmodal_graph_v1",
        name="Crossmodal Graph Preset",
        description="Dual input crossmodal fusion placeholder.",
        graph_builder=_build_crossmodal_graph_preset,
        metadata={"qiskit_available": "false"},
    ),
    NetworkFamily.LOGIC_DECISION_NETWORK: NetworkPreset(
        family=NetworkFamily.LOGIC_DECISION_NETWORK,
        preset_id="logic_decision_network_v1",
        name="Logic Decision Preset",
        description="Deterministic rule/decision path placeholder.",
        graph_builder=_build_logic_decision_preset,
        metadata={"qiskit_available": "false"},
    ),
    NetworkFamily.GRAVITY_NULL_TEST: NetworkPreset(
        family=NetworkFamily.GRAVITY_NULL_TEST,
        preset_id="gravity_null_test_v1",
        name="Gravity Null-Test Preset",
        description="Axiomatic chamber workflow for entangled-pair residual and telemetry review.",
        graph_builder=_build_gravity_null_test_preset,
        metadata={"qiskit_available": "optional", "e2b_datadog_review": "true"},
    ),
    NetworkFamily.MULTIVERSE_EXPERIMENTS: NetworkPreset(
        family=NetworkFamily.MULTIVERSE_EXPERIMENTS,
        preset_id="multiverse_experiments_v1",
        name="Multiverse Experiments Preset",
        description="Five-lane Quantum Paradoxes simulator graph with explicit claim-boundary classifier.",
        graph_builder=_build_multiverse_experiments_preset,
        metadata={"qiskit_available": "optional", "claim_boundary": "simulator_evidence_only"},
    ),
    NetworkFamily.TIME_PHYSICS_EXPERIMENTS: NetworkPreset(
        family=NetworkFamily.TIME_PHYSICS_EXPERIMENTS,
        preset_id="time_physics_experiments_v1",
        name="Time Physics Experiments Preset",
        description="Six-lane time-physics simulator graph with explicit claim-boundary classifier.",
        graph_builder=_build_time_physics_experiments_preset,
        metadata={"qiskit_available": "optional", "claim_boundary": "simulator_evidence_only"},
    ),
    NetworkFamily.CUSTOM_NETWORK: NetworkPreset(
        family=NetworkFamily.CUSTOM_NETWORK,
        preset_id="custom_network_v1",
        name="Custom Network Preset",
        description="Minimal custom network placeholder.",
        graph_builder=_build_custom_network_preset,
        metadata={"qiskit_available": "false"},
    ),
}


def get_preset(family: str | NetworkFamily) -> NetworkPreset:
    coerce_family = family if isinstance(family, NetworkFamily) else NetworkFamily(family)
    if coerce_family not in _PRESETS:
        raise ValueError(f"unsupported network family: {family}")
    return _PRESETS[coerce_family]


def build_graph(family: str | NetworkFamily) -> NetworkGraph:
    return get_preset(family).graph_builder()


def list_presets() -> Tuple[NetworkPreset, ...]:
    return tuple(_PRESETS[NetworkFamily(family_id)] for family_id in all_families())


def get_supported_families() -> Tuple[str, ...]:
    return all_families()
