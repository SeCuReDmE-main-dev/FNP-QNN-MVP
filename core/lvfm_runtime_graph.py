"""LVFM register graph utilities for Cerebrum runtime snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Sequence, Tuple


def _to_float(value: Any, *, label: str) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be numeric")
    return numeric


@dataclass(frozen=True)
class RegisterBit:
    """Immutable T / I(dF) / F triple for one graph register."""

    t: float
    d_f: float
    f: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "t", _to_float(self.t, label="t"))
        object.__setattr__(self, "d_f", _to_float(self.d_f, label="dF"))
        object.__setattr__(self, "f", _to_float(self.f, label="f"))

        if self.t < 0.0 or self.d_f < 0.0 or self.f < 0.0:
            raise ValueError("T, dF, and F must be non-negative")

    @property
    def i_mass(self) -> float:
        return self.d_f

    def normalized(self) -> "RegisterBit":
        total = self.t + self.d_f + self.f
        if total <= 0:
            return RegisterBit(1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)
        scale = 1.0 / total
        return RegisterBit(self.t * scale, self.d_f * scale, self.f * scale)

    def clamp01(self) -> "RegisterBit":
        def _clamp(value: float) -> float:
            if value < 0.0:
                return 0.0
            if value > 1.0:
                return 1.0
            return value

        return RegisterBit(_clamp(self.t), _clamp(self.d_f), _clamp(self.f))


@dataclass(frozen=True)
class RegisterKey:
    """Register key anchored to a graph node."""

    node_id: str
    bit: RegisterBit
    register_weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id must be non-empty")
        if self.register_weight <= 0.0:
            raise ValueError("register_weight must be strictly positive")


@dataclass(frozen=True)
class LVFMDirection:
    source: str
    target: str
    weight: float

    def __post_init__(self) -> None:
        if self.weight <= 0.0:
            raise ValueError("edge weight must be strictly positive")


@dataclass(frozen=True)
class LVFMDecision:
    verdict: str
    trace_line: str
    t_mass: float
    i_mass: float
    f_mass: float
    confidence: float
    notes: Tuple[str, ...]


def _coerce_bit(value: Mapping[str, Any] | RegisterBit | Sequence[float] | Tuple[float, float, float]) -> RegisterBit:
    if isinstance(value, RegisterBit):
        return value
    if isinstance(value, Mapping):
        return RegisterBit(value.get("t", 0.0), value.get("dF", value.get("i", 0.0)), value.get("f", 0.0))
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise TypeError("Bit payload must be a mapping or sequence.")
    if len(value) < 3:
        raise ValueError("Bit payload requires at least three numbers.")
    return RegisterBit(value[0], value[1], value[2])


class LVFMRuntimeGraph:
    """Weighted graph container with deterministic graph snapshots and trace output."""

    def __init__(self) -> None:
        self.nodes: Dict[str, RegisterKey] = {}
        self.adjacency: Dict[str, Dict[str, float]] = {}

    def register_node(
        self,
        node_id: str,
        bit: Mapping[str, Any] | RegisterBit | Sequence[float] | Tuple[float, float, float],
        register_weight: float = 1.0,
        metadata: Mapping[str, Any] | None = None,
    ) -> RegisterKey:
        register_key = RegisterKey(
            node_id=node_id,
            bit=_coerce_bit(bit).normalized().clamp01(),
            register_weight=max(1e-9, float(register_weight)),
            metadata=dict(metadata or {}),
        )
        self.nodes[node_id] = register_key
        return register_key

    def add_edge(self, source: str, target: str, weight: float = 1.0) -> None:
        if source not in self.nodes or target not in self.nodes:
            raise ValueError("both source and target nodes must be registered")
        if weight <= 0.0:
            raise ValueError("edge weight must be strictly positive")
        direction = LVFMDirection(source=source, target=target, weight=max(1e-9, float(weight)))
        self.adjacency.setdefault(source, {})[target] = direction.weight

    def node_count(self) -> int:
        return len(self.nodes)

    def edge_count(self) -> int:
        return sum(len(targets) for targets in self.adjacency.values())

    def _ordered_node_ids(self) -> List[str]:
        return sorted(self.nodes)

    def compact_snapshot(self) -> Dict[str, Dict[str, float]]:
        """Per-node compacted T / I(dF) / F view."""
        output: Dict[str, Dict[str, float]] = {}
        for node_id in self._ordered_node_ids():
            key = self.nodes[node_id]
            bit = key.bit.normalized().clamp01()
            output[node_id] = {
                "T": round(bit.t, 6),
                "I": round(bit.i_mass, 6),
                "dF": round(bit.d_f, 6),
                "F": round(bit.f, 6),
                "register_weight": round(key.register_weight, 6),
            }
        return output

    def weighted_trace(self) -> str:
        traces = []
        for node_id in self._ordered_node_ids():
            key = self.nodes[node_id]
            bit = key.bit.normalized().clamp01()
            traces.append(
                (
                    f"{node_id}:T={bit.t:.3f} "
                    f"I={bit.i_mass:.3f} "
                    f"dF={bit.d_f:.3f} "
                    f"F={bit.f:.3f} "
                    f"w={key.register_weight:.3f}"
                )
            )
        return " | ".join(traces)

    def adjacency_matrix(self) -> List[List[float]]:
        node_ids = self._ordered_node_ids()
        index = {node_id: i for i, node_id in enumerate(node_ids)}
        matrix = [[0.0 for _ in node_ids] for _ in node_ids]
        for source, targets in self.adjacency.items():
            source_index = index[source]
            for target, weight in targets.items():
                matrix[source_index][index[target]] = weight
        return matrix

    def evaluate_gate(self) -> LVFMDecision:
        if not self.nodes:
            return LVFMDecision(
                verdict="hold",
                trace_line="T=0.000|I=0.000|dF=0.000|F=0.000|nodes=0|edges=0|verdict=hold",
                t_mass=0.0,
                i_mass=0.0,
                f_mass=0.0,
                confidence=0.0,
                notes=("graph empty",),
            )

        t_mass = 0.0
        i_mass = 0.0
        f_mass = 0.0
        notes: List[str] = []

        total_weight = 0.0
        node_ids = self._ordered_node_ids()
        for source_id, source_key in self.nodes.items():
            fanout = sum(self.adjacency.get(source_id, {}).values()) or 1.0
            edge_weight = fanout / max(1, len(node_ids))
            bit = source_key.bit.normalized().clamp01()
            source_weight = source_key.register_weight * max(1e-12, fanout)

            t_mass += bit.t * source_weight
            i_mass += bit.i_mass * source_weight * edge_weight
            f_mass += bit.f * source_weight
            total_weight += source_weight

            if bit.i_mass > 0.5:
                notes.append(f"{source_id}:high_i={bit.i_mass:.3f}")
            if bit.f > 0.6:
                notes.append(f"{source_id}:high_f={bit.f:.3f}")
            if fanout > 0.0:
                notes.append(f"{source_id}:fanout={fanout:.3f}")

        denom = max(total_weight + total_weight * min(i_mass, 1.0), 1e-12)
        t_norm = t_mass / denom
        i_norm = i_mass / denom
        f_norm = f_mass / denom
        confidence = (t_mass - f_mass) / max(total_weight, 1e-12)
        verdict = "allow" if confidence >= -0.1 and f_norm <= 0.75 and i_norm <= 0.95 else "hold"

        trace_line = (
            f"T={t_norm:.3f}|I={i_norm:.3f}|dF={i_norm:.3f}|"
            f"F={f_norm:.3f}|nodes={self.node_count()}|edges={self.edge_count()}|verdict={verdict}"
        )
        if not notes:
            notes = ["no-risk-flags"]
        return LVFMDecision(
            verdict=verdict,
            trace_line=trace_line,
            t_mass=t_norm,
            i_mass=i_norm,
            f_mass=f_norm,
            confidence=confidence,
            notes=tuple(notes),
        )

    def to_snapshot(self) -> Dict[str, Any]:
        decision = self.evaluate_gate()
        return {
            "snapshot": {
                "compact": self.compact_snapshot(),
                "trace": self.weighted_trace(),
            },
            "decision": {
                "verdict": decision.verdict,
                "trace_line": decision.trace_line,
                "t_mass": round(decision.t_mass, 6),
                "i_mass": round(decision.i_mass, 6),
                "f_mass": round(decision.f_mass, 6),
                "confidence": round(decision.confidence, 6),
                "notes": list(decision.notes),
            },
            "node_weights": {
                node_id: {
                    "register_weight": round(key.register_weight, 6),
                    "metadata": key.metadata,
                }
                for node_id, key in self.nodes.items()
            },
            "edge_weights": {
                source: {target: weight for target, weight in targets.items()}
                for source, targets in self.adjacency.items()
            },
            "adjacency_matrix": self.adjacency_matrix(),
            "node_ids": self._ordered_node_ids(),
        }
