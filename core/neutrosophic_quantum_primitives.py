"""Pure neutrosophic quantum primitives for the alpha-local simulator.

The functions in this module are source-backed simulation grammar, not claims
that the project implements a physical neutrosophic quantum computer.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Callable, Dict, Mapping, Optional, Sequence

import numpy as np


SOURCE_HIERARCHY = "I -> I_system^S -> D_f -> dF -> i_fractal"
RESEARCH_BOUNDARY = (
    "alpha-local educational simulation only; not a physical quantum proof, "
    "clinical system, security system, or production-public claim"
)


def _finite_float(value: Any, label: str) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be numeric")
    if not math.isfinite(numeric):
        raise ValueError(f"{label} must be finite")
    return numeric


def _finite_complex(value: Any, label: str) -> complex:
    try:
        numeric = complex(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be numeric")
    if not math.isfinite(numeric.real) or not math.isfinite(numeric.imag):
        raise ValueError(f"{label} must be finite")
    return numeric


def _bounded_nonnegative(value: Any, label: str) -> float:
    numeric = _finite_float(value, label)
    if numeric < 0.0:
        raise ValueError(f"{label} must be non-negative")
    return numeric


def _normalize_triplet(t: float, i: float, f: float) -> tuple[float, float, float]:
    total = t + i + f
    if total <= 0.0:
        return (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)
    return (t / total, i / total, f / total)


def _state_to_tif(state: Any, label: str = "state") -> tuple[float, float, float]:
    if isinstance(state, CoherentNeutroState):
        measurement = neutrosophic_measurement(state)
        return (measurement["T"], measurement["I"], measurement["F"])
    if isinstance(state, DecoherentNeutroState):
        measurement = neutrosophic_measurement(state)
        return (measurement["T"], measurement["I"], measurement["F"])
    if isinstance(state, NeutrobitState):
        measurement = neutrosophic_measurement(state)
        return (measurement["T"], measurement["I"], measurement["F"])
    if isinstance(state, Mapping):
        truth = _bounded_nonnegative(state.get("T", state.get("truth", 0.0)), f"{label}.T")
        indeterminacy = _bounded_nonnegative(
            state.get("I", state.get("indeterminacy", 0.0)),
            f"{label}.I",
        )
        falsity = _bounded_nonnegative(state.get("F", state.get("falsity", 0.0)), f"{label}.F")
        return _normalize_triplet(truth, indeterminacy, falsity)
    raise TypeError(f"{label} must be a neutrobit state, coherent/decoherent wrapper, or T/I/F mapping")


@dataclass(frozen=True)
class NeutrobitState:
    """Amplitude state over the simulation basis |0>, |1>, and |I>."""

    zero: complex = 0.0 + 0.0j
    one: complex = 0.0 + 0.0j
    indeterminate: complex = 1.0 + 0.0j

    def __post_init__(self) -> None:
        object.__setattr__(self, "zero", _finite_complex(self.zero, "zero"))
        object.__setattr__(self, "one", _finite_complex(self.one, "one"))
        object.__setattr__(self, "indeterminate", _finite_complex(self.indeterminate, "indeterminate"))

    @classmethod
    def from_probabilities(
        cls,
        zero: float = 0.0,
        one: float = 0.0,
        indeterminate: float = 1.0,
    ) -> "NeutrobitState":
        zero_p = _bounded_nonnegative(zero, "zero")
        one_p = _bounded_nonnegative(one, "one")
        indeterminate_p = _bounded_nonnegative(indeterminate, "indeterminate")
        zero_n, indeterminate_n, one_n = _normalize_triplet(zero_p, indeterminate_p, one_p)
        return cls(
            zero=complex(math.sqrt(zero_n), 0.0),
            one=complex(math.sqrt(one_n), 0.0),
            indeterminate=complex(math.sqrt(indeterminate_n), 0.0),
        )

    @classmethod
    def from_tif(cls, truth: float, indeterminacy: float, falsity: float) -> "NeutrobitState":
        """Build a state from T/I/F masses using |1> as T and |0> as F."""
        return cls.from_probabilities(
            zero=falsity,
            one=truth,
            indeterminate=indeterminacy,
        )

    def normalized(self) -> "NeutrobitState":
        values = np.asarray([self.zero, self.one, self.indeterminate], dtype=complex)
        norm = float(np.linalg.norm(values))
        if norm <= 0.0:
            return NeutrobitState.from_probabilities(1.0, 1.0, 1.0)
        values = values / norm
        return NeutrobitState(zero=values[0], one=values[1], indeterminate=values[2])

    def probabilities(self) -> Dict[str, float]:
        state = self.normalized()
        values = {
            "zero": abs(state.zero) ** 2,
            "one": abs(state.one) ** 2,
            "indeterminate": abs(state.indeterminate) ** 2,
        }
        total = max(sum(values.values()), 1e-12)
        return {key: float(value / total) for key, value in values.items()}

    def vector(self) -> np.ndarray:
        state = self.normalized()
        return np.asarray([state.zero, state.one, state.indeterminate], dtype=complex)


@dataclass(frozen=True)
class CoherentNeutroState:
    """Coherent simulation state before non-projective measurement."""

    state: NeutrobitState
    phase_lock: bool = True
    source: str = "neutrosophic-superposition"

    def decohere(self) -> "DecoherentNeutroState":
        return DecoherentNeutroState(
            probabilities=self.state.probabilities(),
            source=f"{self.source}:decohered",
        )


@dataclass(frozen=True)
class DecoherentNeutroState:
    """Probability distribution over |0>, |1>, and |I> after measurement."""

    probabilities: Mapping[str, float]
    source: str = "non-projective-measurement"

    def __post_init__(self) -> None:
        zero = _bounded_nonnegative(self.probabilities.get("zero", 0.0), "zero")
        one = _bounded_nonnegative(self.probabilities.get("one", 0.0), "one")
        indeterminate = _bounded_nonnegative(
            self.probabilities.get("indeterminate", 0.0),
            "indeterminate",
        )
        zero_n, indeterminate_n, one_n = _normalize_triplet(zero, indeterminate, one)
        object.__setattr__(
            self,
            "probabilities",
            {"zero": zero_n, "one": one_n, "indeterminate": indeterminate_n},
        )


def neutrosophic_measurement(
    state: NeutrobitState | CoherentNeutroState | DecoherentNeutroState,
) -> Dict[str, Any]:
    """Return a T/I/F-style non-projective measurement distribution."""
    if isinstance(state, CoherentNeutroState):
        decoherent = state.decohere()
    elif isinstance(state, DecoherentNeutroState):
        decoherent = state
    elif isinstance(state, NeutrobitState):
        decoherent = CoherentNeutroState(state=state).decohere()
    else:
        raise TypeError("state must be a neutrobit state or coherent/decoherent wrapper")

    probabilities = dict(decoherent.probabilities)
    return {
        "measurement": "non_projective_triplet",
        "basis_probabilities": probabilities,
        "T": probabilities["one"],
        "I": probabilities["indeterminate"],
        "F": probabilities["zero"],
        "hierarchy": SOURCE_HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
        "source": decoherent.source,
    }


def neutrosophic_gate_algebra(
    operation: str,
    left: Any,
    right: Optional[Any] = None,
) -> Dict[str, Any]:
    """Evaluate a bounded educational neutrosophic logic gate over T/I/F states."""
    op = str(operation).strip().lower().replace("-", "_")
    if op in {"not", "negation"}:
        left_t, left_i, left_f = _state_to_tif(left, "left")
        result_t, result_i, result_f = left_f, left_i, left_t
    elif op in {"and", "or", "if_then", "ifthen", "implies", "implication"}:
        if right is None:
            raise ValueError(f"{operation} requires a right operand")
        left_t, left_i, left_f = _state_to_tif(left, "left")
        right_t, right_i, right_f = _state_to_tif(right, "right")
        if op == "and":
            result_t = min(left_t, right_t)
            result_i = max(left_i, right_i)
            result_f = max(left_f, right_f)
        elif op == "or":
            result_t = max(left_t, right_t)
            result_i = max(left_i, right_i)
            result_f = min(left_f, right_f)
        else:
            not_left = {"T": left_f, "I": left_i, "F": left_t}
            return neutrosophic_gate_algebra("or", not_left, right)
    else:
        raise ValueError("operation must be one of: not, and, or, if_then")

    t_norm, i_norm, f_norm = _normalize_triplet(result_t, result_i, result_f)
    return {
        "model": "neutrosophic_gate_algebra",
        "operation": "if_then" if op in {"ifthen", "implies", "implication"} else op,
        "T": t_norm,
        "I": i_norm,
        "F": f_norm,
        "hierarchy": SOURCE_HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


def punctured_wave_state(
    delta: float,
    length: float,
    density_fn: Optional[Callable[[float], float]] = None,
) -> Dict[str, Any]:
    """Build a deterministic FPW-style ordered puncture state for a finite delta."""
    delta_value = _finite_float(delta, "delta")
    length_value = _finite_float(length, "length")
    if delta_value <= 0.0:
        raise ValueError("delta must be strictly positive")
    if length_value < 0.0:
        raise ValueError("length must be non-negative")
    if length_value == 0.0:
        return {
            "model": "finitesimally_punctured_wave",
            "delta": delta_value,
            "length": length_value,
            "count": 0,
            "positions": [],
            "amplitudes": [],
            "research_boundary": RESEARCH_BOUNDARY,
        }

    count = int(math.floor(length_value / delta_value)) + 1
    positions = np.linspace(0.0, delta_value * (count - 1), count, dtype=float)
    positions = np.minimum(positions, length_value)
    if density_fn is None:
        densities = 0.5 + 0.5 * np.cos((positions / max(length_value, delta_value)) * math.pi)
    else:
        densities = np.asarray([density_fn(float(position)) for position in positions], dtype=float)
    if not np.isfinite(densities).all():
        raise ValueError("density_fn must return finite values")
    densities = np.maximum(densities, 0.0)
    norm = float(np.linalg.norm(densities))
    amplitudes = densities / norm if norm > 0.0 else np.zeros_like(densities)
    return {
        "model": "finitesimally_punctured_wave",
        "delta": delta_value,
        "length": length_value,
        "count": int(count),
        "positions": [round(float(value), 12) for value in positions.tolist()],
        "amplitudes": [round(float(value), 12) for value in amplitudes.tolist()],
        "research_boundary": RESEARCH_BOUNDARY,
    }


def punctured_surface_state(
    delta: float,
    width: float,
    height: float,
    density_fn: Optional[Callable[[float, float], float]] = None,
) -> Dict[str, Any]:
    """Build a deterministic FPW-style 2D puncture grid for finite surfaces."""
    delta_value = _finite_float(delta, "delta")
    width_value = _finite_float(width, "width")
    height_value = _finite_float(height, "height")
    if delta_value <= 0.0:
        raise ValueError("delta must be strictly positive")
    if width_value < 0.0 or height_value < 0.0:
        raise ValueError("width and height must be non-negative")
    if width_value == 0.0 or height_value == 0.0:
        return {
            "model": "finitesimally_punctured_surface",
            "delta": delta_value,
            "width": width_value,
            "height": height_value,
            "count": 0,
            "points": [],
            "amplitudes": [],
            "research_boundary": RESEARCH_BOUNDARY,
        }

    x_count = int(math.floor(width_value / delta_value)) + 1
    y_count = int(math.floor(height_value / delta_value)) + 1
    xs = np.minimum(np.linspace(0.0, delta_value * (x_count - 1), x_count, dtype=float), width_value)
    ys = np.minimum(np.linspace(0.0, delta_value * (y_count - 1), y_count, dtype=float), height_value)
    points: list[tuple[float, float]] = []
    densities: list[float] = []
    for y in ys:
        for x in xs:
            points.append((float(x), float(y)))
            if density_fn is None:
                x_wave = 0.5 + 0.5 * math.cos((float(x) / max(width_value, delta_value)) * math.pi)
                y_wave = 0.5 + 0.5 * math.cos((float(y) / max(height_value, delta_value)) * math.pi)
                densities.append(x_wave * y_wave)
            else:
                densities.append(float(density_fn(float(x), float(y))))
    density_array = np.asarray(densities, dtype=float)
    if not np.isfinite(density_array).all():
        raise ValueError("density_fn must return finite values")
    density_array = np.maximum(density_array, 0.0)
    norm = float(np.linalg.norm(density_array))
    amplitudes = density_array / norm if norm > 0.0 else np.zeros_like(density_array)
    return {
        "model": "finitesimally_punctured_surface",
        "delta": delta_value,
        "width": width_value,
        "height": height_value,
        "count": int(len(points)),
        "points": [
            {"x": round(float(x), 12), "y": round(float(y), 12)}
            for x, y in points
        ],
        "amplitudes": [round(float(value), 12) for value in amplitudes.tolist()],
        "research_boundary": RESEARCH_BOUNDARY,
    }


def partial_entanglement_profile(
    correlation: float,
    separability: Optional[float] = None,
    decoherence: float = 0.0,
    delta_falsity: float = 0.0,
) -> Dict[str, Any]:
    """Map partial entanglement signals into a bounded T/I/F profile."""
    correlation_value = min(1.0, max(0.0, _finite_float(correlation, "correlation")))
    if separability is None:
        separability_value = 1.0 - correlation_value
    else:
        separability_value = min(1.0, max(0.0, _finite_float(separability, "separability")))
    decoherence_value = min(1.0, max(0.0, _finite_float(decoherence, "decoherence")))
    delta_value = _finite_float(delta_falsity, "delta_falsity")
    indeterminacy = min(1.0, decoherence_value + abs(delta_value))
    t_norm, i_norm, f_norm = _normalize_triplet(correlation_value, indeterminacy, separability_value)
    return {
        "model": "partial_entanglement_tif_profile",
        "raw": {
            "correlation": correlation_value,
            "decoherence": decoherence_value,
            "delta_falsity": delta_value,
            "separability": separability_value,
        },
        "T": t_norm,
        "I": i_norm,
        "F": f_norm,
        "hierarchy": SOURCE_HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


def observer_effect_profile(
    state: Any,
    observer_strength: float,
    decoherence: float = 0.0,
) -> Dict[str, Any]:
    """Map partial observer effect into a bounded T/I/F measurement profile."""
    strength_value = min(1.0, max(0.0, _finite_float(observer_strength, "observer_strength")))
    decoherence_value = min(1.0, max(0.0, _finite_float(decoherence, "decoherence")))
    truth, indeterminacy, falsity = _state_to_tif(state)
    effect = min(1.0, strength_value + decoherence_value)
    observed_truth = truth * (1.0 - effect)
    observed_falsity = falsity * (1.0 - effect)
    observed_indeterminacy = indeterminacy + effect * (truth + falsity)
    t_norm, i_norm, f_norm = _normalize_triplet(observed_truth, observed_indeterminacy, observed_falsity)
    return {
        "model": "partial_observer_effect_tif_profile",
        "observer_strength": strength_value,
        "decoherence": decoherence_value,
        "T": t_norm,
        "I": i_norm,
        "F": f_norm,
        "hierarchy": SOURCE_HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


def neutrobit_features_from_vector(
    vector: Sequence[float],
    puncture_delta: Optional[float] = None,
    observer_strength: Optional[float] = None,
) -> np.ndarray:
    """Create a compact neutrobit feature expansion from a real feature vector."""
    values = np.asarray(list(vector), dtype=np.float32).reshape(-1)
    if values.size == 0:
        measurement = neutrosophic_measurement(NeutrobitState.from_tif(0.0, 1.0, 0.0))
        return np.asarray([measurement["T"], measurement["I"], measurement["F"]], dtype=np.float32)

    bounded = np.abs(np.tanh(values))
    truth = float(np.mean(bounded))
    falsity = float(np.mean(1.0 - bounded))
    indeterminacy = float(np.std(bounded))
    measurement = neutrosophic_measurement(NeutrobitState.from_tif(truth, indeterminacy, falsity))
    entanglement = partial_entanglement_profile(
        correlation=truth,
        separability=falsity,
        decoherence=indeterminacy,
        delta_falsity=0.0 if puncture_delta is None else puncture_delta,
    )
    features = [
        measurement["T"],
        measurement["I"],
        measurement["F"],
        measurement["basis_probabilities"]["zero"],
        measurement["basis_probabilities"]["one"],
        measurement["basis_probabilities"]["indeterminate"],
        entanglement["T"],
        entanglement["I"],
        entanglement["F"],
    ]
    if puncture_delta is not None:
        wave = punctured_wave_state(
            delta=puncture_delta,
            length=max(float(puncture_delta), min(1.0, float(values.size) * float(puncture_delta))),
        )
        features.extend([min(1.0, wave["count"] / 128.0), float(wave["delta"])])
    if observer_strength is not None:
        observer = observer_effect_profile(
            {"T": measurement["T"], "I": measurement["I"], "F": measurement["F"]},
            observer_strength=observer_strength,
            decoherence=indeterminacy,
        )
        features.extend([observer["T"], observer["I"], observer["F"]])
    return np.asarray(features, dtype=np.float32)


__all__ = [
    "CoherentNeutroState",
    "DecoherentNeutroState",
    "NeutrobitState",
    "RESEARCH_BOUNDARY",
    "SOURCE_HIERARCHY",
    "neutrobit_features_from_vector",
    "neutrosophic_gate_algebra",
    "neutrosophic_measurement",
    "observer_effect_profile",
    "partial_entanglement_profile",
    "punctured_surface_state",
    "punctured_wave_state",
]
