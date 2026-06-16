"""Public NeuroBit gate primitives for the FNP-QNN MVP.

This module is the AGENTS.md-aligned public contract for the lightweight
NeuroBit lane. It intentionally keeps Qiskit and TorchQuantum optional.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from .neurobit_gate_tunnel import (
    NeuroBitProfile,
    build_gate_parameters,
    build_neurobit_gate_sequence,
    counts_to_expectation_vector,
    gate_matrix,
    hadamard_gate_matrix,
    run_neurobit_gates,
    w_gate_matrix,
    x_gate_matrix,
    y_gate_matrix,
    z_gate_matrix,
)

NeutrosophicGateProfile = NeuroBitProfile


def build_neutrosophic_gate_sequence(profile: Optional[NeuroBitProfile] = None) -> List[str]:
    """Return the deterministic NeuroBit gate sequence for a profile."""
    return build_neurobit_gate_sequence(profile)


def apply_gate_sequence_qiskit(
    circuit: Any,
    sequence: Sequence[str],
    wires: Sequence[int],
    profile: Optional[NeuroBitProfile] = None,
) -> List[Dict[str, Any]]:
    """Apply a NeuroBit sequence to a Qiskit-like circuit.

    The function accepts a Qiskit circuit object but does not require Qiskit at
    import time. If Qiskit's `UnitaryGate` is unavailable, W is decomposed into
    portable single-qubit rotations.
    """
    if not wires:
        return []

    try:  # pragma: no cover - optional dependency branch.
        from qiskit.circuit.library import UnitaryGate
    except Exception:  # pragma: no cover
        UnitaryGate = None

    normalized = (profile or NeuroBitProfile()).normalized()
    params = build_gate_parameters(normalized)
    trace: List[Dict[str, Any]] = []

    for index, gate_name in enumerate(sequence):
        wire = wires[index % len(wires)]
        gate = str(gate_name).strip().lower()
        if gate in {"h", "hadamard"}:
            circuit.h(wire)
            trace.append({"wire": wire, "gate": "H", "params": {}})
        elif gate == "x":
            circuit.x(wire)
            trace.append({"wire": wire, "gate": "X", "params": {"theta": params["theta_x"]}})
        elif gate == "y":
            circuit.ry(params["theta_y"], wire)
            trace.append({"wire": wire, "gate": "RY", "params": {"theta": params["theta_y"]}})
        elif gate == "z":
            circuit.rz(params["theta_z"], wire)
            trace.append({"wire": wire, "gate": "RZ", "params": {"theta": params["theta_z"]}})
        elif gate == "w":
            if UnitaryGate is not None:
                circuit.append(UnitaryGate(w_gate_matrix(), label="W"), [wire])
            else:
                circuit.rz(params["phase"], wire)
                circuit.ry(math.pi / 2.0, wire)
                circuit.rz(-params["phase"], wire)
                circuit.ry(-math.pi / 2.0, wire)
            trace.append({"wire": wire, "gate": "W", "params": {"phase": params["phase"]}})
        else:
            raise ValueError(f"Unsupported NeuroBit gate: {gate_name}")
    return trace


def to_torchquantum_ops(
    profile: Optional[NeuroBitProfile],
    wires: Sequence[int],
) -> List[Tuple[str, int, Tuple[float, ...]]]:
    """Return backend-neutral TorchQuantum-style operation descriptors.

    This is a plain data contract and does not import TorchQuantum.
    """
    if not wires:
        return []

    normalized = (profile or NeuroBitProfile()).normalized()
    params = build_gate_parameters(normalized)
    ops: List[Tuple[str, int, Tuple[float, ...]]] = []
    for index, gate_name in enumerate(build_neurobit_gate_sequence(normalized)):
        wire = wires[index % len(wires)]
        gate = gate_name.lower()
        if gate in {"h", "hadamard"}:
            ops.append(("h", wire, ()))
        elif gate == "x":
            ops.append(("rx", wire, (params["theta_x"],)))
        elif gate == "y":
            ops.append(("ry", wire, (params["theta_y"],)))
        elif gate == "z":
            ops.append(("rz", wire, (params["theta_z"],)))
        elif gate == "w":
            ops.extend(
                [
                    ("rz", wire, (params["phase"],)),
                    ("ry", wire, (math.pi / 2.0,)),
                    ("rz", wire, (-params["phase"],)),
                    ("ry", wire, (-math.pi / 2.0,)),
                ]
            )
        else:
            raise ValueError(f"Unsupported NeuroBit gate: {gate_name}")
    return ops


def gate_matrix_json(name: str) -> List[List[Dict[str, float]]]:
    """Serialize a complex gate matrix into JSON-friendly real/imag pairs."""
    matrix = gate_matrix(name)
    return [
        [{"real": round(float(value.real), 12), "imag": round(float(value.imag), 12)} for value in row]
        for row in matrix
    ]


__all__ = [
    "NeuroBitProfile",
    "NeutrosophicGateProfile",
    "apply_gate_sequence_qiskit",
    "build_gate_parameters",
    "build_neurobit_gate_sequence",
    "build_neutrosophic_gate_sequence",
    "counts_to_expectation_vector",
    "gate_matrix",
    "gate_matrix_json",
    "hadamard_gate_matrix",
    "run_neurobit_gates",
    "to_torchquantum_ops",
    "w_gate_matrix",
    "x_gate_matrix",
    "y_gate_matrix",
    "z_gate_matrix",
]
