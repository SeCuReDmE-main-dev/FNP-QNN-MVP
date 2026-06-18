"""Lightweight NeuroBit gates and tunnel-noise demo.

This module adapts the small, deterministic part of the external FNP-QNN
neutrosophic gate work without importing its heavy quanvolution/runtime stack.
It is a local research simulation surface, not a security or clinical system.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from .neutrosophic_quantum_primitives import (
    NeutrobitState,
    fractal_carrier_profile,
    neutrosophic_gate_algebra,
    neutrosophic_measurement,
    observer_effect_profile,
    partial_entanglement_profile,
    punctured_surface_state,
    punctured_wave_state,
)

try:  # pragma: no cover - optional runtime path.
    from qiskit import Aer, QuantumCircuit, execute
    from qiskit.circuit.library import UnitaryGate

    QISKIT_GATE_AVAILABLE = True
except Exception:  # pragma: no cover - expected in lightweight local installs.
    Aer = None
    QuantumCircuit = None
    UnitaryGate = None
    execute = None
    QISKIT_GATE_AVAILABLE = False


@dataclass(frozen=True)
class NeuroBitProfile:
    """Bounded T/I/F/dF profile for local NeuroBit gate scheduling."""

    truth: float = 0.55
    indeterminacy: float = 0.30
    falsity: float = 0.15
    delta_falsity: float = 0.0
    state_basis: str = "binary"
    puncture_delta: Optional[float] = None
    observer_strength: Optional[float] = None
    surface_width: Optional[float] = None
    surface_height: Optional[float] = None
    fractal_dimension: Optional[float] = None
    fractal_dimension_min: Optional[float] = None
    fractal_dimension_max: Optional[float] = None
    fractal_admissible: bool = True
    fractal_measurement_method: Optional[str] = None
    fractal_scale: Optional[str] = None

    def normalized(self) -> "NeuroBitProfile":
        truth = max(float(self.truth), 0.0)
        indeterminacy = max(float(self.indeterminacy), 0.0)
        falsity = max(float(self.falsity), 0.0)
        state_basis = self.state_basis if self.state_basis in {"binary", "neutrobit"} else "binary"
        puncture_delta = None if self.puncture_delta is None else max(float(self.puncture_delta), 0.0)
        observer_strength = None if self.observer_strength is None else min(1.0, max(float(self.observer_strength), 0.0))
        surface_width = None if self.surface_width is None else max(float(self.surface_width), 0.0)
        surface_height = None if self.surface_height is None else max(float(self.surface_height), 0.0)
        fractal_dimension = None if self.fractal_dimension is None else float(self.fractal_dimension)
        fractal_dimension_min = None if self.fractal_dimension_min is None else float(self.fractal_dimension_min)
        fractal_dimension_max = None if self.fractal_dimension_max is None else float(self.fractal_dimension_max)
        total = truth + indeterminacy + falsity
        if total <= 0.0:
            return NeuroBitProfile(
                truth=1.0 / 3.0,
                indeterminacy=1.0 / 3.0,
                falsity=1.0 / 3.0,
                delta_falsity=float(self.delta_falsity),
                state_basis=state_basis,
                puncture_delta=puncture_delta,
                observer_strength=observer_strength,
                surface_width=surface_width,
                surface_height=surface_height,
                fractal_dimension=fractal_dimension,
                fractal_dimension_min=fractal_dimension_min,
                fractal_dimension_max=fractal_dimension_max,
                fractal_admissible=bool(self.fractal_admissible),
                fractal_measurement_method=self.fractal_measurement_method,
                fractal_scale=self.fractal_scale,
            )
        return NeuroBitProfile(
            truth=truth / total,
            indeterminacy=indeterminacy / total,
            falsity=falsity / total,
            delta_falsity=float(self.delta_falsity),
            state_basis=state_basis,
            puncture_delta=puncture_delta,
            observer_strength=observer_strength,
            surface_width=surface_width,
            surface_height=surface_height,
            fractal_dimension=fractal_dimension,
            fractal_dimension_min=fractal_dimension_min,
            fractal_dimension_max=fractal_dimension_max,
            fractal_admissible=bool(self.fractal_admissible),
            fractal_measurement_method=self.fractal_measurement_method,
            fractal_scale=self.fractal_scale,
        )

    @property
    def metadata(self) -> Dict[str, Any]:
        normalized = self.normalized()
        payload = {
            "truth": float(normalized.truth),
            "indeterminacy": float(normalized.indeterminacy),
            "falsity": float(normalized.falsity),
            "delta_falsity": float(normalized.delta_falsity),
            "puncture_delta": float(normalized.puncture_delta or 0.0),
        }
        if normalized.observer_strength is not None:
            payload["observer_strength"] = float(normalized.observer_strength)
        if normalized.surface_width is not None:
            payload["surface_width"] = float(normalized.surface_width)
        if normalized.surface_height is not None:
            payload["surface_height"] = float(normalized.surface_height)
        if normalized.fractal_dimension is not None:
            payload["fractal_dimension"] = float(normalized.fractal_dimension)
        if normalized.fractal_dimension_min is not None:
            payload["fractal_dimension_min"] = float(normalized.fractal_dimension_min)
        if normalized.fractal_dimension_max is not None:
            payload["fractal_dimension_max"] = float(normalized.fractal_dimension_max)
        payload["fractal_admissible"] = bool(normalized.fractal_admissible)
        if normalized.fractal_measurement_method is not None:
            payload["fractal_measurement_method"] = str(normalized.fractal_measurement_method)
        if normalized.fractal_scale is not None:
            payload["fractal_scale"] = str(normalized.fractal_scale)
        return payload


def profile_from_mapping(payload: Optional[Mapping[str, Any]]) -> NeuroBitProfile:
    payload = payload or {}
    return NeuroBitProfile(
        truth=float(payload.get("truth", 0.55)),
        indeterminacy=float(payload.get("indeterminacy", payload.get("i", 0.30))),
        falsity=float(payload.get("falsity", 0.15)),
        delta_falsity=float(payload.get("delta_falsity", payload.get("dF", 0.0))),
        state_basis=str(payload.get("state_basis", "binary")),
        puncture_delta=payload.get("puncture_delta"),
        observer_strength=payload.get("observer_strength"),
        surface_width=payload.get("surface_width"),
        surface_height=payload.get("surface_height"),
        fractal_dimension=payload.get("fractal_dimension", payload.get("D_f")),
        fractal_dimension_min=payload.get("fractal_dimension_min", payload.get("D_min")),
        fractal_dimension_max=payload.get("fractal_dimension_max", payload.get("D_max")),
        fractal_admissible=bool(payload.get("fractal_admissible", True)),
        fractal_measurement_method=payload.get("fractal_measurement_method"),
        fractal_scale=payload.get("fractal_scale"),
    )


def fractal_carrier_for_profile(profile: NeuroBitProfile) -> Optional[Dict[str, Any]]:
    normalized = profile.normalized()
    if (
        normalized.fractal_dimension is None
        or normalized.fractal_dimension_min is None
        or normalized.fractal_dimension_max is None
    ):
        return None
    return fractal_carrier_profile(
        normalized.fractal_dimension,
        normalized.fractal_dimension_min,
        normalized.fractal_dimension_max,
        measurement_method=normalized.fractal_measurement_method or "provided-fractal-dimension",
        scale=normalized.fractal_scale,
        domain="neurobit-profile",
        admissible=normalized.fractal_admissible,
    )


def hadamard_gate_matrix() -> np.ndarray:
    scale = 1.0 / math.sqrt(2)
    return np.array([[scale, scale], [scale, -scale]], dtype=complex)


def x_gate_matrix() -> np.ndarray:
    return np.array([[0, 1], [1, 0]], dtype=complex)


def y_gate_matrix() -> np.ndarray:
    return np.array([[0, -1j], [1j, 0]], dtype=complex)


def z_gate_matrix() -> np.ndarray:
    return np.array([[1, 0], [0, -1]], dtype=complex)


def w_gate_matrix() -> np.ndarray:
    return np.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]], dtype=complex) / 2.0


def gate_matrix(name: str) -> np.ndarray:
    gate = str(name).strip().lower()
    if gate in {"h", "hadamard"}:
        return hadamard_gate_matrix()
    if gate == "w":
        return w_gate_matrix()
    if gate == "x":
        return x_gate_matrix()
    if gate == "y":
        return y_gate_matrix()
    if gate == "z":
        return z_gate_matrix()
    raise ValueError(f"Unknown NeuroBit gate: {name}")


def build_neurobit_gate_sequence(profile: Optional[NeuroBitProfile] = None) -> List[str]:
    normalized = (profile or NeuroBitProfile()).normalized()
    sequence = ["hadamard"]
    if normalized.indeterminacy > 0.05:
        # W is the explicit local marker for the |I> basis contribution.
        sequence.append("w")
    if normalized.truth > 0.15:
        sequence.append("x")
    if normalized.falsity > 0.10:
        sequence.append("y")
    if normalized.truth + normalized.falsity < 0.85:
        sequence.append("z")
    return sequence


def build_gate_parameters(profile: Optional[NeuroBitProfile] = None) -> Dict[str, float]:
    normalized = (profile or NeuroBitProfile()).normalized()
    return {
        "theta_x": float(math.pi * normalized.truth),
        "theta_y": float(math.pi * normalized.indeterminacy),
        "theta_z": float(math.pi * normalized.falsity),
        "phase": float(math.pi * (normalized.truth + normalized.indeterminacy) / 2.0),
        "delta_falsity": float(normalized.delta_falsity),
        "indeterminate_basis_weight": float(normalized.indeterminacy),
    }


def gate_semantics(sequence: Sequence[str]) -> List[Dict[str, Any]]:
    meanings = {
        "hadamard": "binary superposition seed for the local gate demo",
        "w": "local |I> marker for indeterminate-basis contribution",
        "x": "truth-weighted binary inversion lane",
        "y": "indeterminacy-weighted phase rotation lane",
        "z": "falsity/phase contrast lane",
    }
    return [
        {
            "gate": "H" if gate == "hadamard" else gate.upper(),
            "meaning": meanings.get(gate, "local educational gate marker"),
        }
        for gate in sequence
    ]


def reversibility_profile(sequence: Sequence[str], profile: Optional[NeuroBitProfile] = None) -> Dict[str, Any]:
    normalized = (profile or NeuroBitProfile()).normalized()
    has_indeterminate_gate = any(gate == "w" for gate in sequence)
    information_loss_risk = min(1.0, normalized.indeterminacy + abs(normalized.delta_falsity))
    undefined_transform_risk = min(1.0, normalized.indeterminacy if has_indeterminate_gate else 0.0)
    return {
        "reversible": bool(information_loss_risk < 0.5 and undefined_transform_risk < 0.5),
        "information_loss_risk": float(information_loss_risk),
        "undefined_transform_risk": float(undefined_transform_risk),
        "notes": "Educational trace metadata only; not a proof of physical reversible quantum execution.",
    }


def counts_to_expectation_vector(counts: Mapping[str, int], n_qubits: int, shots: int) -> np.ndarray:
    if shots <= 0:
        shots = max(sum(int(value) for value in counts.values()), 1)
    values = np.zeros(n_qubits, dtype=float)
    for bitstring, count in counts.items():
        padded = str(bitstring).strip().zfill(n_qubits)
        probability = int(count) / shots
        for index, bit in enumerate(reversed(padded[-n_qubits:])):
            values[index] += (1.0 if bit == "0" else -1.0) * probability
    return values.astype(float)


def _complex_matrix_json(matrix: np.ndarray) -> List[List[Dict[str, float]]]:
    return [
        [{"real": round(float(value.real), 12), "imag": round(float(value.imag), 12)} for value in row]
        for row in matrix
    ]


def _apply_gate_sequence_qiskit(profile: NeuroBitProfile, n_qubits: int) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    if not QISKIT_GATE_AVAILABLE or QuantumCircuit is None or Aer is None or execute is None:
        raise RuntimeError("Qiskit gate execution is not available")

    sequence = build_neurobit_gate_sequence(profile)
    params = build_gate_parameters(profile)
    circuit = QuantumCircuit(n_qubits, n_qubits)
    trace: List[Dict[str, Any]] = []
    for index, gate_name in enumerate(sequence):
        wire = index % n_qubits
        gate = gate_name.lower()
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
    circuit.measure_all()
    backend = Aer.get_backend("qasm_simulator")
    counts = execute(circuit, backend, shots=256).result().get_counts(circuit)
    return trace, {str(key): int(value) for key, value in counts.items()}


def _fallback_counts(profile: NeuroBitProfile, n_qubits: int, shots: int = 256) -> Dict[str, int]:
    normalized = profile.normalized()
    seed = int(
        (
            normalized.truth * 997
            + normalized.indeterminacy * 577
            + normalized.falsity * 389
            + abs(normalized.delta_falsity) * 211
        )
    )
    state_count = 2**n_qubits
    primary = seed % state_count
    secondary = (primary ^ max(1, int(round(normalized.indeterminacy * state_count)))) % state_count
    primary_shots = max(1, int(round(shots * (0.58 + 0.28 * normalized.truth))))
    primary_shots = min(primary_shots, shots)
    return {
        format(primary, f"0{n_qubits}b"): primary_shots,
        format(secondary, f"0{n_qubits}b"): shots - primary_shots,
    }


def run_neurobit_gates(profile: Optional[NeuroBitProfile] = None, n_qubits: int = 4) -> Dict[str, Any]:
    if n_qubits <= 0:
        raise ValueError("n_qubits must be positive")
    normalized = (profile or NeuroBitProfile()).normalized()
    sequence = build_neurobit_gate_sequence(normalized)
    neutro_state = NeutrobitState.from_tif(
        truth=normalized.truth,
        indeterminacy=normalized.indeterminacy,
        falsity=normalized.falsity,
    )
    measurement = neutrosophic_measurement(neutro_state)
    entanglement = partial_entanglement_profile(
        correlation=normalized.truth,
        separability=normalized.falsity,
        decoherence=normalized.indeterminacy,
        delta_falsity=normalized.delta_falsity,
    )
    observer_effect = None
    if normalized.observer_strength is not None:
        observer_effect = observer_effect_profile(
            {"T": measurement["T"], "I": measurement["I"], "F": measurement["F"]},
            observer_strength=normalized.observer_strength,
            decoherence=normalized.indeterminacy,
        )
    gate_and = neutrosophic_gate_algebra(
        "and",
        {"T": normalized.truth, "I": normalized.indeterminacy, "F": normalized.falsity},
        {"T": measurement["T"], "I": measurement["I"], "F": measurement["F"]},
    )
    punctured_wave = None
    if normalized.puncture_delta is not None and normalized.puncture_delta > 0.0:
        punctured_wave = punctured_wave_state(
            delta=normalized.puncture_delta,
            length=max(float(normalized.puncture_delta), float(n_qubits) * float(normalized.puncture_delta)),
        )
    punctured_surface = None
    if (
        normalized.puncture_delta is not None
        and normalized.puncture_delta > 0.0
        and normalized.surface_width is not None
        and normalized.surface_height is not None
    ):
        punctured_surface = punctured_surface_state(
            delta=normalized.puncture_delta,
            width=normalized.surface_width,
            height=normalized.surface_height,
        )
    fractal_carrier = fractal_carrier_for_profile(normalized)
    backend = "deterministic_fallback"
    try:
        trace, counts = _apply_gate_sequence_qiskit(normalized, n_qubits)
        backend = "qiskit_qasm_simulator"
    except Exception:
        params = build_gate_parameters(normalized)
        trace = [
            {
                "wire": index % n_qubits,
                "gate": "H" if gate_name == "hadamard" else gate_name.upper(),
                "params": {} if gate_name == "hadamard" else params,
            }
            for index, gate_name in enumerate(sequence)
        ]
        counts = _fallback_counts(normalized, n_qubits)

    expectation = counts_to_expectation_vector(counts, n_qubits=n_qubits, shots=sum(counts.values()))
    return {
        "status": "ok",
        "backend": backend,
        "qiskit_available": QISKIT_GATE_AVAILABLE,
        "research_boundary": "local deterministic non-clinical simulation; not a security or clinical proof",
        "profile": normalized.metadata,
        "state_basis": normalized.state_basis,
        "hierarchy": "I -> I_system^S -> D_f -> dF -> i_fractal",
        "sequence": sequence,
        "parameters": build_gate_parameters(normalized),
        "gate_semantics": gate_semantics(sequence),
        "reversibility_profile": reversibility_profile(sequence, normalized),
        "gate_algebra_preview": gate_and,
        "neutrobit_measurement": measurement,
        "observer_effect": observer_effect,
        "partial_entanglement": entanglement,
        "fractal_carrier": fractal_carrier,
        "i_fractal_candidate": None if fractal_carrier is None else fractal_carrier["i_fractal_candidate"],
        "punctured_wave": punctured_wave,
        "punctured_surface": punctured_surface,
        "trace": trace,
        "counts": counts,
        "expectation_vector": [round(float(value), 6) for value in expectation.tolist()],
        "gate_matrices": {gate: _complex_matrix_json(gate_matrix(gate)) for gate in ["hadamard", "w", "x", "y", "z"]},
    }


def _fibonacci_sequence(length: int) -> List[float]:
    if length <= 0:
        return []
    sequence = [1.0, 1.0]
    while len(sequence) < length:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence[:length]


def run_neurobit_tunnel_demo(
    profile: Optional[NeuroBitProfile] = None,
    data: bytes | str = b"neurobit-demo",
) -> Dict[str, Any]:
    normalized = (profile or NeuroBitProfile()).normalized()
    data_bytes = data.encode("utf-8") if isinstance(data, str) else bytes(data)
    gates = run_neurobit_gates(normalized, n_qubits=4)
    sequence = _fibonacci_sequence(max(len(data_bytes), 12))
    counts = gates["counts"]
    total = max(sum(int(value) for value in counts.values()), 1)
    probabilities = {key: int(value) / total for key, value in counts.items()}
    phi = (1.0 + math.sqrt(5.0)) / 2.0

    noise: List[float] = []
    for index, value in enumerate(sequence):
        state_key = format(index % 16, "04b")
        probability = probabilities.get(state_key, 0.0)
        noise.append(round(float(value * probability * phi), 6))

    noisy_preview = [
        int((byte + int(abs(noise[index]) * 1000)) % 256)
        for index, byte in enumerate(data_bytes[: len(noise)])
    ]
    sequence_id = int(sum((index + 1) * ord(char) for index, char in enumerate("".join(sorted(counts)))) % 100000)
    return {
        "status": "ok",
        "backend": gates["backend"],
        "research_boundary": "deterministic Fibonacci/noise simulation only; not encryption and not a security guarantee",
        "profile": normalized.metadata,
        "fractal_carrier": gates.get("fractal_carrier"),
        "i_fractal_candidate": gates.get("i_fractal_candidate"),
        "sequence_id": sequence_id,
        "gate_trace": gates["trace"],
        "quantum_state": counts,
        "fibonacci_sequence": [round(float(value), 6) for value in sequence[:12]],
        "noise_preview": noise[:12],
        "noisy_data_preview": noisy_preview[:12],
        "data_length": len(data_bytes),
    }
