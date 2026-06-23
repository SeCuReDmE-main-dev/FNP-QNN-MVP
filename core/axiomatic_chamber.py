"""Axiomatic chamber primitives for bounded local simulator experiments.

These helpers define measurement-room metadata. They do not assert physical
quantum gravity, faster-than-light signalling, or exact graviton mass.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Dict, Mapping, Optional, Tuple


HIERARCHY = "I -> I_system^S -> D_f -> dF -> i_fractal"
RESEARCH_BOUNDARY = (
    "alpha-local educational simulation only; proof-of-principle chamber isolation, "
    "not physical quantum-gravity proof, faster-than-light signalling, exact graviton mass, "
    "clinical behavior, security behavior, or production-public claim"
)


def finite_float(value: Any, label: str) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be numeric")
    if not math.isfinite(numeric):
        raise ValueError(f"{label} must be finite")
    return numeric


def clamp01(value: Any) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(numeric):
        return 0.0
    return max(0.0, min(1.0, numeric))


@dataclass(frozen=True)
class ChamberBounds:
    """Local chamber bounds; these are not universal physical constants."""

    d_min: float = 0.1
    d_max: float = 10.0
    D_min: float = 1.0
    D_max: float = 2.0
    delta_ns_threshold: float = 0.05
    frustration_threshold: float = 0.55

    def __post_init__(self) -> None:
        d_min = finite_float(self.d_min, "d_min")
        d_max = finite_float(self.d_max, "d_max")
        d_lower = finite_float(self.D_min, "D_min")
        d_upper = finite_float(self.D_max, "D_max")
        delta_threshold = finite_float(self.delta_ns_threshold, "delta_ns_threshold")
        frustration_threshold = finite_float(self.frustration_threshold, "frustration_threshold")
        if d_min < 0.0:
            raise ValueError("d_min must be non-negative")
        if d_max <= d_min:
            raise ValueError("d_max must be greater than d_min")
        if d_upper <= d_lower:
            raise ValueError("D_max must be greater than D_min")
        if delta_threshold <= 0.0:
            raise ValueError("delta_ns_threshold must be positive")
        if not 0.0 <= frustration_threshold <= 1.0:
            raise ValueError("frustration_threshold must be between 0 and 1")
        object.__setattr__(self, "d_min", d_min)
        object.__setattr__(self, "d_max", d_max)
        object.__setattr__(self, "D_min", d_lower)
        object.__setattr__(self, "D_max", d_upper)
        object.__setattr__(self, "delta_ns_threshold", delta_threshold)
        object.__setattr__(self, "frustration_threshold", frustration_threshold)

    def normalized_distance(self, distance: Any) -> float:
        value = finite_float(distance, "distance")
        return clamp01((value - self.d_min) / (self.d_max - self.d_min))

    def payload(self) -> Dict[str, Any]:
        return {
            "d_min": self.d_min,
            "d_max": self.d_max,
            "D_min": self.D_min,
            "D_max": self.D_max,
            "delta_ns_threshold": self.delta_ns_threshold,
            "frustration_threshold": self.frustration_threshold,
            "interpretation": "local measurement chamber bounds, not universal constants",
        }


@dataclass(frozen=True)
class SourceRole:
    """A role inside the test chamber."""

    role_id: str
    label: str
    relation: str
    entangled_with: Tuple[str, ...] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not str(self.role_id).strip():
            raise ValueError("role_id must be non-empty")
        if not str(self.label).strip():
            raise ValueError("label must be non-empty")
        object.__setattr__(self, "role_id", str(self.role_id))
        object.__setattr__(self, "label", str(self.label))
        object.__setattr__(self, "relation", str(self.relation or "unclassified"))
        object.__setattr__(self, "entangled_with", tuple(str(item) for item in self.entangled_with))
        object.__setattr__(self, "metadata", dict(self.metadata))

    def payload(self) -> Dict[str, Any]:
        return {
            "role_id": self.role_id,
            "label": self.label,
            "relation": self.relation,
            "entangled_with": list(self.entangled_with),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class AxiomaticChamberContext:
    """Container that keeps experiment roles, domains, and bounds explicit."""

    chamber_id: str = "axiomatic-gravity-null-test"
    Omega: str = "local-proof-of-principle-observation-domain"
    C_alpha: str = "entangled-pair-room"
    C_beta: str = "uncorrelated-probe-room"
    bounds: ChamberBounds = field(default_factory=ChamberBounds)
    roles: Tuple[SourceRole, ...] = field(
        default_factory=lambda: (
            SourceRole("A", "remote entangled partner", "entangled_remote", ("B",)),
            SourceRole("B", "local target particle", "entangled_local_target", ("A",)),
            SourceRole("C", "uncorrelated probe or local mass source", "separable_local_probe", ()),
        )
    )
    source_ids: Tuple[str, ...] = (
        "VEDRAL_VIDEO_1_TESTING_QUANTUM_GRAVITY_REALITY",
        "VEDRAL_VIDEO_2_THIS_QUANTUM_GRAVITY_EXPERIMENT",
        "FNG_GPCN_SET_PHI_FINAL_PDF",
        "SEQUENCE_QUANTUM_NETWORK_SIMULATOR",
    )

    def payload(self) -> Dict[str, Any]:
        return {
            "model": "axiomatic_chamber_context_v1",
            "chamber_id": self.chamber_id,
            "Omega": self.Omega,
            "C_alpha": self.C_alpha,
            "C_beta": self.C_beta,
            "bounds": self.bounds.payload(),
            "roles": [role.payload() for role in self.roles],
            "source_ids": list(self.source_ids),
            "hierarchy": HIERARCHY,
            "research_boundary": RESEARCH_BOUNDARY,
        }


def dmin_dmax_chamber_bounds(
    d_min: float = 0.1,
    d_max: float = 10.0,
    D_min: float = 1.0,
    D_max: float = 2.0,
    *,
    delta_ns_threshold: float = 0.05,
    frustration_threshold: float = 0.55,
) -> Dict[str, Any]:
    """Return validated chamber bounds and hierarchy metadata."""

    bounds = ChamberBounds(
        d_min=d_min,
        d_max=d_max,
        D_min=D_min,
        D_max=D_max,
        delta_ns_threshold=delta_ns_threshold,
        frustration_threshold=frustration_threshold,
    )
    return {
        "model": "dmin_dmax_chamber_bounds_v1",
        "bounds": bounds.payload(),
        "hierarchy": HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


def admissibility_profile(
    *,
    delta_ns: float,
    frustration: float,
    leakage: float,
    local_noise: float,
    bounds: Optional[ChamberBounds] = None,
    source_i: str = "fractal_boundary",
) -> Dict[str, Any]:
    """Classify whether a residual may enter the local i_fractal lane."""

    active_bounds = bounds or ChamberBounds()
    delta = abs(finite_float(delta_ns, "delta_ns"))
    frustration_value = clamp01(frustration)
    leakage_value = clamp01(leakage)
    noise_value = clamp01(local_noise)
    fractal_sources = {"fractal_boundary", "fractal_projection", "fractal_growth", "geometric_multiscale"}
    if leakage_value > 0.0 or noise_value >= 0.35:
        adm = "rejected"
        classification = "local_coupling_or_shared_noise"
        reason = "local leakage or high local noise explains the residual before any i_fractal reading"
    elif delta <= active_bounds.delta_ns_threshold:
        adm = "suspended"
        classification = "no_detected_remote_influence"
        reason = "probe residual remains within the chamber no-signalling threshold"
    elif source_i not in fractal_sources:
        adm = "suspended"
        classification = "residual_source_not_fractal"
        reason = "the unresolved source is not eligible for i_fractal"
    elif frustration_value >= active_bounds.frustration_threshold:
        adm = "suspended"
        classification = "frustrated_state_requires_external_validation"
        reason = "frustration is visible but cannot become a physical proof in this simulator"
    else:
        adm = "suspended"
        classification = "anomaly_requires_external_validation"
        reason = "residual is above threshold but needs independent physical evidence"
    return {
        "model": "axiomatic_chamber_admissibility_v1",
        "Adm": adm,
        "classification": classification,
        "reason": reason,
        "source_i": source_i,
        "Delta_NS": delta,
        "F_chamber": frustration_value,
        "leakage": leakage_value,
        "local_noise": noise_value,
        "hierarchy": HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }
