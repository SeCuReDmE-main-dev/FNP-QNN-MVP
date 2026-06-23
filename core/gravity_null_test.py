"""Deterministic axiomatic-chamber gravity null-test simulator.

This module turns the proposed A-B entangled pair plus C uncorrelated probe
experiment into local simulator metadata. It is deliberately bounded: residuals
are classified as proof-of-principle chamber signals, not as physical proof.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import math
import random
from statistics import mean
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from .axiomatic_chamber import (
    HIERARCHY,
    RESEARCH_BOUNDARY,
    AxiomaticChamberContext,
    ChamberBounds,
    admissibility_profile,
    clamp01,
    finite_float,
)
from .hydra_em_gpcn_math import gpcn_set_phi_profile
from .neutrosophic_quantum_primitives import fractal_carrier_profile, partial_entanglement_profile
from .penrose_hameroff_math import twistor_nonlocality_profile


VIDEO_SOURCE_IDS = [
    "VEDRAL_VIDEO_1_TESTING_QUANTUM_GRAVITY_REALITY",
    "VEDRAL_VIDEO_2_THIS_QUANTUM_GRAVITY_EXPERIMENT",
]
SEQUENCE_SOURCE_ID = "SEQUENCE_QUANTUM_NETWORK_SIMULATOR"


@dataclass(frozen=True)
class GravityNullTestConfig:
    """Input parameters for the deterministic proof-of-principle run."""

    seed: int = 734
    shots: int = 512
    entanglement_correlation: float = 0.92
    probe_bias: float = 0.5
    local_noise: float = 0.02
    leakage: float = 0.0
    chamber_contradiction: float = 0.25
    mass_dispersion: float = 0.0
    alpha_wave_frequency: float = 1.0
    beta_wave_frequency: float = 1.0
    omega_wave_frequency: float = 1.0
    d_min: float = 0.1
    d_max: float = 10.0
    D_min: float = 1.0
    D_max: float = 2.0
    delta_ns_threshold: float = 0.05
    frustration_threshold: float = 0.55
    include_sequence_export: bool = False
    include_qiskit_preview: bool = False
    source_i: str = "fractal_boundary"
    graviton_external_bound_ev: Optional[float] = None
    graviton_bound_source: Optional[str] = None

    def __post_init__(self) -> None:
        seed = int(round(finite_float(self.seed, "seed")))
        shots = int(round(finite_float(self.shots, "shots")))
        if shots < 16 or shots > 100000:
            raise ValueError("shots must be between 16 and 100000")
        object.__setattr__(self, "seed", seed)
        object.__setattr__(self, "shots", shots)
        for field_name in (
            "entanglement_correlation",
            "probe_bias",
            "local_noise",
            "leakage",
            "chamber_contradiction",
            "mass_dispersion",
        ):
            object.__setattr__(self, field_name, clamp01(getattr(self, field_name)))
        for field_name in ("alpha_wave_frequency", "beta_wave_frequency", "omega_wave_frequency"):
            value = finite_float(getattr(self, field_name), field_name)
            if value < 0.0:
                raise ValueError(f"{field_name} must be non-negative")
            object.__setattr__(self, field_name, value)
        # Validate bounds early.
        ChamberBounds(
            d_min=self.d_min,
            d_max=self.d_max,
            D_min=self.D_min,
            D_max=self.D_max,
            delta_ns_threshold=self.delta_ns_threshold,
            frustration_threshold=self.frustration_threshold,
        )
        if self.graviton_external_bound_ev is not None:
            bound = finite_float(self.graviton_external_bound_ev, "graviton_external_bound_ev")
            if bound < 0.0:
                raise ValueError("graviton_external_bound_ev must be non-negative")
            object.__setattr__(self, "graviton_external_bound_ev", bound)

    @property
    def bounds(self) -> ChamberBounds:
        return ChamberBounds(
            d_min=self.d_min,
            d_max=self.d_max,
            D_min=self.D_min,
            D_max=self.D_max,
            delta_ns_threshold=self.delta_ns_threshold,
            frustration_threshold=self.frustration_threshold,
        )


def simulate_entangled_pair(config: GravityNullTestConfig) -> List[Dict[str, int]]:
    """Generate A-B outcomes with no local B marginal dependence by default."""

    rng = random.Random(config.seed)
    records: List[Dict[str, int]] = []
    flip_probability = (1.0 - config.entanglement_correlation) / 2.0
    for _ in range(config.shots):
        alice_setting = rng.randint(0, 1)
        a_outcome = rng.randint(0, 1)
        b_outcome = a_outcome if rng.random() >= flip_probability else 1 - a_outcome
        # Explicitly model forbidden classical leakage as simulator contamination.
        if config.leakage > 0.0 and rng.random() < config.leakage:
            b_outcome = alice_setting
        if config.local_noise > 0.0 and rng.random() < config.local_noise:
            b_outcome = 1 - b_outcome
        records.append({"A_setting": alice_setting, "A": a_outcome, "B": b_outcome})
    return records


def simulate_uncorrelated_probe(config: GravityNullTestConfig) -> List[int]:
    """Generate separable C probe outcomes with local noise only."""

    rng = random.Random(config.seed + 101)
    outcomes: List[int] = []
    for _ in range(config.shots):
        probability = clamp01(config.probe_bias + (rng.random() - 0.5) * config.local_noise)
        outcomes.append(1 if rng.random() < probability else 0)
    return outcomes


def simulate_local_coupling(
    entangled_records: Sequence[Mapping[str, int]],
    probe_outcomes: Sequence[int],
    config: GravityNullTestConfig,
) -> List[Dict[str, int]]:
    """Apply explicit C-to-B coupling as local contamination metadata."""

    rng = random.Random(config.seed + 202)
    coupled: List[Dict[str, int]] = []
    for index, record in enumerate(entangled_records):
        item = dict(record)
        probe = int(probe_outcomes[index % len(probe_outcomes)])
        item["C"] = probe
        if config.mass_dispersion > 0.0 and rng.random() < config.mass_dispersion:
            item["B"] = probe
            item["local_coupling_applied"] = 1
        else:
            item["local_coupling_applied"] = 0
        coupled.append(item)
    return coupled


def no_signalling_residual(records: Sequence[Mapping[str, int]]) -> Dict[str, Any]:
    """Return the absolute B marginal difference conditioned on A setting."""

    groups = {0: [], 1: []}
    for item in records:
        setting = int(item.get("A_setting", 0))
        groups[setting].append(int(item.get("B", 0)))
    p0 = mean(groups[0]) if groups[0] else 0.0
    p1 = mean(groups[1]) if groups[1] else 0.0
    delta = abs(p1 - p0)
    return {
        "model": "no_signalling_residual_v1",
        "P_B_given_A_setting_0": float(p0),
        "P_B_given_A_setting_1": float(p1),
        "Delta_NS": float(delta),
        "sample_counts": {"A_setting_0": len(groups[0]), "A_setting_1": len(groups[1])},
        "interpretation": "B marginal dependence check; residual is not by itself physical proof",
    }


def frustration_index(
    *,
    entanglement_correlation: float,
    local_noise: float,
    leakage: float,
    chamber_contradiction: float,
    mass_dispersion: float,
    alpha_wave_frequency: float,
    beta_wave_frequency: float,
    omega_wave_frequency: float,
) -> Dict[str, Any]:
    """Return a bounded frustration score for competing explanatory sources."""

    correlation = clamp01(entanglement_correlation)
    noise = clamp01(local_noise)
    leak = clamp01(leakage)
    contradiction = clamp01(chamber_contradiction)
    dispersion = clamp01(mass_dispersion)
    wave_values = [
        finite_float(alpha_wave_frequency, "alpha_wave_frequency"),
        finite_float(beta_wave_frequency, "beta_wave_frequency"),
        finite_float(omega_wave_frequency, "omega_wave_frequency"),
    ]
    max_wave = max(wave_values) if max(wave_values) > 0.0 else 1.0
    wave_spread = (max(wave_values) - min(wave_values)) / max_wave
    local_pressure = clamp01((noise + leak + dispersion) / 3.0)
    competing_pressure = clamp01(correlation * (contradiction + wave_spread) / 2.0)
    frustration = clamp01(0.45 * competing_pressure + 0.35 * local_pressure + 0.20 * contradiction)
    return {
        "model": "f_chamber_frustration_index_v1",
        "F_chamber": frustration,
        "components": {
            "entanglement_correlation": correlation,
            "local_noise": noise,
            "leakage": leak,
            "mass_dispersion": dispersion,
            "chamber_contradiction": contradiction,
            "wave_spread": clamp01(wave_spread),
            "local_pressure": local_pressure,
            "competing_pressure": competing_pressure,
        },
        "interpretation": "bounded simulator frustration score, not a physical force measurement",
    }


def simulate_frustrated_state(config: GravityNullTestConfig) -> Dict[str, Any]:
    """Build the B-state frustration profile for the chamber."""

    return frustration_index(
        entanglement_correlation=config.entanglement_correlation,
        local_noise=config.local_noise,
        leakage=config.leakage,
        chamber_contradiction=config.chamber_contradiction,
        mass_dispersion=config.mass_dispersion,
        alpha_wave_frequency=config.alpha_wave_frequency,
        beta_wave_frequency=config.beta_wave_frequency,
        omega_wave_frequency=config.omega_wave_frequency,
    )


def gq_super_equation(
    *,
    delta_ns: float,
    F_chamber: float,
    D_f_hat: float,
    local_noise: float,
    leakage: float,
    mass_dispersion: float,
) -> Dict[str, Any]:
    """Bounded explanatory score for simulator comparison only."""

    score = clamp01(
        0.30 * clamp01(delta_ns)
        + 0.25 * clamp01(F_chamber)
        + 0.20 * clamp01(D_f_hat)
        + 0.10 * clamp01(local_noise)
        + 0.10 * clamp01(leakage)
        + 0.05 * clamp01(mass_dispersion)
    )
    return {
        "model": "gq_super_equation_v1",
        "GQ_super_equation": score,
        "terms": {
            "Delta_NS": clamp01(delta_ns),
            "F_chamber": clamp01(F_chamber),
            "D_f_hat": clamp01(D_f_hat),
            "local_noise": clamp01(local_noise),
            "leakage": clamp01(leakage),
            "mass_dispersion": clamp01(mass_dispersion),
        },
        "interpretation": "bounded explanatory simulator score; not a physical law",
        "research_boundary": RESEARCH_BOUNDARY,
    }


def d_f_from_residuals(config: GravityNullTestConfig, delta_ns: float, frustration: float) -> float:
    unresolved = clamp01(
        0.35 * (abs(delta_ns) / max(config.delta_ns_threshold, 1e-12))
        + 0.35 * frustration
        + 0.15 * config.local_noise
        + 0.10 * config.leakage
        + 0.05 * config.mass_dispersion
    )
    return config.D_min + (config.D_max - config.D_min) * unresolved


def graviton_constraint_profile(
    external_bound_ev: Optional[float] = None,
    source: Optional[str] = None,
) -> Dict[str, Any]:
    """Placeholder for externally sourced graviton-mass constraints."""

    if external_bound_ev is None or source is None:
        return {
            "model": "graviton_constraint_profile_v1",
            "status": "constraint_profile_pending_external_data",
            "exact_graviton_mass_ev": None,
            "external_bound_ev": None,
            "source": source,
            "required_before_use": [
                "peer-reviewed or official bound",
                "explicit formula",
                "external observed data",
            ],
            "forbidden_claim": "do not claim exact graviton mass from simulator output",
            "research_boundary": RESEARCH_BOUNDARY,
        }
    bound = finite_float(external_bound_ev, "external_bound_ev")
    return {
        "model": "graviton_constraint_profile_v1",
        "status": "external_bound_recorded_not_inferred",
        "exact_graviton_mass_ev": None,
        "external_bound_ev": bound,
        "source": str(source),
        "forbidden_claim": "do not claim exact graviton mass from simulator output",
        "research_boundary": RESEARCH_BOUNDARY,
    }


def sequence_event_spec(profile: Mapping[str, Any]) -> Dict[str, Any]:
    """Export a SeQUeNCe-ready topology/event specification without importing SeQUeNCe."""

    return {
        "model": "sequence_event_spec_v1",
        "target": "SeQUeNCe optional bridge",
        "requires_sequence_runtime": False,
        "nodes": [
            {"id": "Alice_A", "role": "remote entangled partner"},
            {"id": "Bob_B", "role": "local entangled target"},
            {"id": "Probe_C", "role": "uncorrelated local probe"},
        ],
        "links": [
            {"source": "Alice_A", "target": "Bob_B", "type": "entanglement_context"},
            {"source": "Probe_C", "target": "Bob_B", "type": "local_coupling_guarded"},
        ],
        "events": [
            {"name": "prepare_AB_entanglement", "owned_by": "FNP-QNN"},
            {"name": "sample_C_uncorrelated_probe", "owned_by": "FNP-QNN"},
            {"name": "measure_B_marginals_by_A_setting", "owned_by": "FNP-QNN"},
            {"name": "classify_Delta_NS_and_F_chamber", "owned_by": "FNP-QNN"},
        ],
        "feature_vector": list(profile.get("feature_vector", [])),
        "research_boundary": RESEARCH_BOUNDARY,
    }


def qiskit_circuit_preview() -> Dict[str, Any]:
    """Return a dependency-gated educational circuit preview."""

    available = importlib.util.find_spec("qiskit") is not None
    return {
        "model": "qiskit_gravity_null_test_preview_v1",
        "available": available,
        "status": "preview_only" if available else "unavailable",
        "operations": [
            {"gate": "h", "target": "A"},
            {"gate": "cx", "control": "A", "target": "B"},
            {"gate": "measure", "target": "B", "conditioned_by": "A_setting"},
            {"gate": "measure", "target": "C", "relation": "uncorrelated_probe"},
        ],
        "interpretation": "educational circuit sketch only; no Qiskit dependency required",
        "research_boundary": RESEARCH_BOUNDARY,
    }


def run_gravity_null_test(config: Optional[GravityNullTestConfig] = None, **kwargs: Any) -> Dict[str, Any]:
    """Run the complete deterministic null-test profile."""

    active_config = config or GravityNullTestConfig(**kwargs)
    chamber = AxiomaticChamberContext(bounds=active_config.bounds)
    entangled_records = simulate_entangled_pair(active_config)
    probe = simulate_uncorrelated_probe(active_config)
    coupled_records = simulate_local_coupling(entangled_records, probe, active_config)
    residual = no_signalling_residual(coupled_records)
    frustration = simulate_frustrated_state(active_config)
    delta_ns = residual["Delta_NS"]
    f_chamber = frustration["F_chamber"]
    d_f = d_f_from_residuals(active_config, delta_ns, f_chamber)
    carrier = fractal_carrier_profile(
        d_f,
        active_config.D_min,
        active_config.D_max,
        system="axiomatic-chamber-gravity-null-test",
        measurement_method="dmin-dmax-super-equation",
        scale="alpha-beta-omega-proof-of-principle",
        domain="B_local_target_residual",
        admissible=True,
    )
    adm = admissibility_profile(
        delta_ns=delta_ns,
        frustration=f_chamber,
        leakage=active_config.leakage + active_config.mass_dispersion,
        local_noise=active_config.local_noise,
        bounds=active_config.bounds,
        source_i=active_config.source_i,
    )
    if adm["Adm"] != "suspended" or adm["classification"] in {
        "no_detected_remote_influence",
        "local_coupling_or_shared_noise",
    }:
        carrier["i_fractal_candidate"] = None
    gq = gq_super_equation(
        delta_ns=delta_ns,
        F_chamber=f_chamber,
        D_f_hat=carrier["D_f_hat"] or 0.0,
        local_noise=active_config.local_noise,
        leakage=active_config.leakage,
        mass_dispersion=active_config.mass_dispersion,
    )
    ab_entanglement = partial_entanglement_profile(
        correlation=active_config.entanglement_correlation,
        separability=1.0 - active_config.entanglement_correlation,
        decoherence=active_config.local_noise,
        delta_falsity=f_chamber,
    )
    c_probe = partial_entanglement_profile(
        correlation=0.0,
        separability=1.0,
        decoherence=active_config.local_noise,
        delta_falsity=active_config.mass_dispersion,
    )
    gpcn = gpcn_set_phi_profile(
        local_point_count=3,
        observation_scale_min=active_config.d_min,
        observation_scale_max=active_config.d_max,
        d_f=d_f,
        d_min=active_config.D_min,
        d_max=active_config.D_max,
        adm=adm["classification"] not in {"local_coupling_or_shared_noise"},
        i_system_source=active_config.source_i,
    )
    twistor = twistor_nonlocality_profile(
        active_config.entanglement_correlation,
        gq["GQ_super_equation"],
        {
            "Delta_NS": delta_ns,
            "F_chamber": f_chamber,
            "mass_dispersion": active_config.mass_dispersion,
        },
    )
    feature_vector = [
        clamp01(delta_ns / max(active_config.delta_ns_threshold, 1e-12)),
        f_chamber,
        carrier["D_f_hat"] or 0.0,
        gq["GQ_super_equation"],
        active_config.entanglement_correlation,
        active_config.local_noise,
        active_config.leakage,
        active_config.mass_dispersion,
    ]
    profile: Dict[str, Any] = {
        "model": "axiomatic_chamber_gravity_null_test_v1",
        "source_ids": VIDEO_SOURCE_IDS + ["FNG_GPCN_SET_PHI_FINAL_PDF", SEQUENCE_SOURCE_ID],
        "config": {
            "seed": active_config.seed,
            "shots": active_config.shots,
            "entanglement_correlation": active_config.entanglement_correlation,
            "probe_bias": active_config.probe_bias,
            "local_noise": active_config.local_noise,
            "leakage": active_config.leakage,
            "mass_dispersion": active_config.mass_dispersion,
            "chamber_contradiction": active_config.chamber_contradiction,
            "alpha_wave_frequency": active_config.alpha_wave_frequency,
            "beta_wave_frequency": active_config.beta_wave_frequency,
            "omega_wave_frequency": active_config.omega_wave_frequency,
        },
        "chamber": chamber.payload(),
        "roles": {
            "A": "remote entangled partner",
            "B": "local target particle entangled with A",
            "C": "uncorrelated local probe or mass-source candidate",
        },
        "no_signalling": residual,
        "frustrated_state": frustration,
        "fractal_carrier": carrier,
        "admissibility": adm,
        "gq_super_equation": gq,
        "partial_entanglement": {"AB": ab_entanglement, "C_probe": c_probe},
        "axiomatic_container": gpcn,
        "twistor_nonlocality_metadata": twistor,
        "graviton_constraint": graviton_constraint_profile(
            active_config.graviton_external_bound_ev,
            active_config.graviton_bound_source,
        ),
        "classification": adm["classification"],
        "feature_vector": feature_vector,
        "feature_dimension": len(feature_vector),
        "hierarchy": HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }
    if active_config.include_sequence_export:
        profile["sequence_event_spec"] = sequence_event_spec(profile)
    if active_config.include_qiskit_preview:
        profile["qiskit_circuit_preview"] = qiskit_circuit_preview()
    return profile


def gravity_null_test_status() -> Dict[str, Any]:
    return {
        "status": "ok",
        "feature": "axiomatic-chamber-gravity-null-test",
        "available_primitives": [
            "simulate_entangled_pair",
            "simulate_uncorrelated_probe",
            "simulate_local_coupling",
            "no_signalling_residual",
            "frustration_index",
            "gq_super_equation",
            "graviton_constraint_profile",
            "sequence_event_spec",
            "qiskit_circuit_preview",
        ],
        "endpoints": [
            "GET /fnp-qnn/gravity-null-test/status",
            "POST /fnp-qnn/gravity-null-test/run",
        ],
        "hierarchy": HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


__all__ = [
    "GravityNullTestConfig",
    "gravity_null_test_status",
    "graviton_constraint_profile",
    "gq_super_equation",
    "frustration_index",
    "no_signalling_residual",
    "qiskit_circuit_preview",
    "run_gravity_null_test",
    "sequence_event_spec",
    "simulate_entangled_pair",
    "simulate_frustrated_state",
    "simulate_local_coupling",
    "simulate_uncorrelated_probe",
]
