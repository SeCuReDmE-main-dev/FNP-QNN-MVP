"""Deterministic simulator profiles for five bounded multiverse experiments.

The profiles are educational branch-accounting simulations derived from the
Quantum Paradoxes source set. They are not evidence that many-worlds is
physically true and they do not create signalling or ontology claims.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
from statistics import mean
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .axiomatic_chamber import HIERARCHY, clamp01, finite_float


RI_QUANTUM_PARADOXES_MULTIVERSE_2026 = "RI_QUANTUM_PARADOXES_MULTIVERSE_2026"
VIOLARIS_QUANTUM_PARADOXES_SERIES = "VIOLARIS_QUANTUM_PARADOXES_SERIES"
VIOLARIS_INTERBRANCH_COMMUNICATION_2026 = "VIOLARIS_INTERBRANCH_COMMUNICATION_2026"
LOCAL_RUNTIME_SOURCE_ID = "LOCAL_RUNTIME"

SOURCE_LEDGER: Dict[str, str] = {
    RI_QUANTUM_PARADOXES_MULTIVERSE_2026: (
        "https://www.youtube.com/watch?v=B1WP3jgavbA and "
        "https://www.rigb.org/whats-on/quantum-paradoxes-testing-multiverse-tech-revolution"
    ),
    VIOLARIS_QUANTUM_PARADOXES_SERIES: "https://www.mariaviolaris.com/quantum-paradoxes/",
    VIOLARIS_INTERBRANCH_COMMUNICATION_2026: "https://arxiv.org/abs/2601.08102",
    LOCAL_RUNTIME_SOURCE_ID: "local deterministic simulator implementation",
}

MULTIVERSE_EXPERIMENT_IDS: Tuple[str, ...] = (
    "deutsch_quantum_computation_origin",
    "elitzur_vaidman_bomb_tester",
    "entanglement_teleportation_branch_accounting",
    "google_quantum_computer_scale_review",
    "wigner_friend_inter_branch_communication",
)

MULTIVERSE_RESEARCH_BOUNDARY = (
    "alpha-local educational branch-accounting simulation only; not validation of many-worlds ontology, "
    "not faster-than-light signalling, not a production-public physics claim, and not clinical or security behavior"
)

FORBIDDEN_CLAIMS = (
    "many-worlds is physically true",
    "inter-branch communication is operational in nature",
    "quantum supremacy validates a multiverse ontology",
    "teleportation permits faster-than-light signalling",
    "interaction-free measurement proves unobserved worlds",
)


@dataclass(frozen=True)
class MultiverseExperimentConfig:
    """Shared inputs for deterministic five-lane simulator profiles."""

    experiment_id: str = "deutsch_quantum_computation_origin"
    seed: int = 2026
    shots: int = 512
    branch_coherence: float = 0.82
    measurement_strength: float = 0.35
    interference_visibility: float = 0.72
    entanglement_fidelity: float = 0.84
    classical_leakage: float = 0.0
    memory_erasure: float = 1.0
    scale_claim_strength: float = 0.65
    include_qiskit_preview: bool = False
    source_i: str = "fractal_boundary"

    def __post_init__(self) -> None:
        if self.experiment_id not in MULTIVERSE_EXPERIMENT_IDS:
            raise ValueError(f"unknown multiverse experiment id: {self.experiment_id}")
        seed = int(round(finite_float(self.seed, "seed")))
        shots = int(round(finite_float(self.shots, "shots")))
        if shots < 16 or shots > 100000:
            raise ValueError("shots must be between 16 and 100000")
        object.__setattr__(self, "seed", seed)
        object.__setattr__(self, "shots", shots)
        for field_name in (
            "branch_coherence",
            "measurement_strength",
            "interference_visibility",
            "entanglement_fidelity",
            "classical_leakage",
            "memory_erasure",
            "scale_claim_strength",
        ):
            object.__setattr__(self, field_name, clamp01(getattr(self, field_name)))

    def with_experiment(self, experiment_id: str) -> "MultiverseExperimentConfig":
        return MultiverseExperimentConfig(
            experiment_id=experiment_id,
            seed=self.seed,
            shots=self.shots,
            branch_coherence=self.branch_coherence,
            measurement_strength=self.measurement_strength,
            interference_visibility=self.interference_visibility,
            entanglement_fidelity=self.entanglement_fidelity,
            classical_leakage=self.classical_leakage,
            memory_erasure=self.memory_erasure,
            scale_claim_strength=self.scale_claim_strength,
            include_qiskit_preview=self.include_qiskit_preview,
            source_i=self.source_i,
        )

    def payload(self) -> Dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "seed": self.seed,
            "shots": self.shots,
            "branch_coherence": self.branch_coherence,
            "measurement_strength": self.measurement_strength,
            "interference_visibility": self.interference_visibility,
            "entanglement_fidelity": self.entanglement_fidelity,
            "classical_leakage": self.classical_leakage,
            "memory_erasure": self.memory_erasure,
            "scale_claim_strength": self.scale_claim_strength,
            "include_qiskit_preview": self.include_qiskit_preview,
            "source_i": self.source_i,
        }


def _safe_round(value: float) -> float:
    return round(clamp01(value), 6)


def _feature_vector(config: MultiverseExperimentConfig, lane_signal: float, claim_safety: float) -> List[float]:
    return [
        _safe_round(config.branch_coherence),
        _safe_round(config.measurement_strength),
        _safe_round(config.interference_visibility),
        _safe_round(config.entanglement_fidelity),
        _safe_round(config.classical_leakage),
        _safe_round(config.memory_erasure),
        _safe_round(lane_signal),
        _safe_round(claim_safety),
    ]


def _branch_count(config: MultiverseExperimentConfig, probability: float) -> int:
    return int(round(config.shots * clamp01(probability)))


def _hierarchy_integrity(config: MultiverseExperimentConfig, d_f: float) -> Dict[str, Any]:
    return {
        "hierarchy": HIERARCHY,
        "I": "source observation envelope only",
        "I_system^S": config.source_i,
        "D_f": _safe_round(config.branch_coherence * config.interference_visibility),
        "dF": _safe_round(d_f),
        "i_fractal_candidate": None if config.classical_leakage > 0.0 else "simulator_branch_accounting_candidate",
        "dF_is_not_generic_I": True,
    }


def _shared_profile(
    config: MultiverseExperimentConfig,
    *,
    lane_name: str,
    chapter_reference: str,
    claim_tested: str,
    classification: str,
    evidence_profile: Dict[str, Any],
    simulator_mapping: Dict[str, Any],
    feature_vector: Sequence[float],
    d_f: float,
    source_ids: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    sources = list(source_ids or (RI_QUANTUM_PARADOXES_MULTIVERSE_2026, VIOLARIS_QUANTUM_PARADOXES_SERIES))
    if LOCAL_RUNTIME_SOURCE_ID not in sources:
        sources.append(LOCAL_RUNTIME_SOURCE_ID)
    profile: Dict[str, Any] = {
        "model": "fnp_qnn_multiverse_experiment_profile_v1",
        "experiment_id": config.experiment_id,
        "lane_name": lane_name,
        "chapter_reference": chapter_reference,
        "source_ids": sources,
        "config": config.payload(),
        "claim_tested": claim_tested,
        "classification": classification,
        "evidence_profile": evidence_profile,
        "simulator_mapping": simulator_mapping,
        "feature_vector": [float(item) for item in feature_vector],
        "feature_dimension": len(feature_vector),
        "hierarchy": HIERARCHY,
        "hierarchy_integrity": _hierarchy_integrity(config, d_f),
        "forbidden_claims": list(FORBIDDEN_CLAIMS),
        "research_boundary": MULTIVERSE_RESEARCH_BOUNDARY,
        "claim_boundary": (
            "The simulator may compare branch-accounting explanations; it must not assert "
            "that the source experiment validates a real multiverse."
        ),
    }
    if config.include_qiskit_preview:
        profile["qiskit_preview"] = qiskit_multiverse_preview(config.experiment_id)
    return profile


def _deutsch_lane(config: MultiverseExperimentConfig) -> Dict[str, Any]:
    reversible_signal = clamp01(
        config.branch_coherence * config.interference_visibility * (1.0 - config.classical_leakage)
    )
    classical_replay = clamp01(config.measurement_strength * (1.0 - config.interference_visibility))
    d_f = clamp01(1.0 - reversible_signal + config.classical_leakage)
    features = _feature_vector(config, reversible_signal, 1.0 - config.classical_leakage)
    return _shared_profile(
        config,
        lane_name="Deutsch quantum-computing test",
        chapter_reference="How the Multiverse Debate Created Quantum Computing",
        claim_tested="Quantum-computation speedup can be modelled as reversible branch-accounting evidence.",
        classification="reversible_quantum_computation_evidence_not_ontology_claim",
        evidence_profile={
            "reversible_quantum_computation_signal": _safe_round(reversible_signal),
            "classical_replay_pressure": _safe_round(classical_replay),
            "expected_interfering_shots": _branch_count(config, reversible_signal),
            "interpretation": "simulation evidence for reversible interference bookkeeping, not ontology validation",
        },
        simulator_mapping={
            "inputs": ["oracle_branch", "interference_visibility", "classical_leakage"],
            "branch_accounting": "constructive interference is tracked as a reversible computation feature",
            "forbidden_inference": "do not infer physically real parallel worlds from the profile",
        },
        feature_vector=features,
        d_f=d_f,
    )


def _bomb_lane(config: MultiverseExperimentConfig) -> Dict[str, Any]:
    interaction_free_positive = clamp01(
        0.25 * config.interference_visibility * (1.0 - config.measurement_strength) * (1.0 - config.classical_leakage)
    )
    detonation_risk = clamp01(config.measurement_strength * (1.0 - config.memory_erasure))
    negative_case = clamp01(1.0 - interaction_free_positive - detonation_risk)
    d_f = clamp01(abs(interaction_free_positive - detonation_risk) + config.classical_leakage)
    features = _feature_vector(config, interaction_free_positive, 1.0 - detonation_risk)
    return _shared_profile(
        config,
        lane_name="Elitzur-Vaidman bomb tester",
        chapter_reference="The Quantum Bomb Tester",
        claim_tested="Interaction-free detection can be represented as positive and negative branch cases.",
        classification="interaction_free_detection_with_positive_negative_cases",
        evidence_profile={
            "interaction_free_positive_rate": _safe_round(interaction_free_positive),
            "negative_case_rate": _safe_round(negative_case),
            "detonation_or_absorption_risk": _safe_round(detonation_risk),
            "positive_case_shots": _branch_count(config, interaction_free_positive),
            "negative_case_shots": _branch_count(config, negative_case),
        },
        simulator_mapping={
            "live_bomb": "positive interaction-free branch when interference is broken without absorption",
            "dud_bomb": "negative branch when interference remains available",
            "local_guard": "classical leakage and measurement strength remain explicit contamination terms",
        },
        feature_vector=features,
        d_f=d_f,
    )


def _teleportation_lane(config: MultiverseExperimentConfig) -> Dict[str, Any]:
    entanglement_accounting = clamp01(config.entanglement_fidelity * config.branch_coherence)
    classical_channel_required = clamp01(1.0 - config.classical_leakage)
    no_signalling_guard = clamp01(classical_channel_required * (1.0 - 0.5 * config.measurement_strength))
    lane_signal = clamp01(entanglement_accounting * no_signalling_guard)
    d_f = clamp01(1.0 - no_signalling_guard + config.classical_leakage)
    features = _feature_vector(config, lane_signal, no_signalling_guard)
    return _shared_profile(
        config,
        lane_name="Entanglement and teleportation branch accounting",
        chapter_reference="Quantum Entanglement and Teleportation",
        claim_tested="Teleportation requires entanglement plus a classical channel and does not permit signalling.",
        classification="entanglement_accounting_without_signalling",
        evidence_profile={
            "entanglement_accounting": _safe_round(entanglement_accounting),
            "classical_channel_required": _safe_round(classical_channel_required),
            "no_signalling_guard": _safe_round(no_signalling_guard),
            "teleportation_transfer_score": _safe_round(lane_signal),
        },
        simulator_mapping={
            "entangled_resource": "tracked through entanglement_fidelity",
            "classical_channel": "mandatory reconstruction side channel",
            "signalling_boundary": "output stays invalid for faster-than-light messaging",
        },
        feature_vector=features,
        d_f=d_f,
    )


def _google_scale_lane(config: MultiverseExperimentConfig) -> Dict[str, Any]:
    scale_evidence = clamp01(config.scale_claim_strength * config.interference_visibility)
    noise_review = clamp01(config.classical_leakage + (1.0 - config.branch_coherence) * 0.5)
    ontology_claim_risk = clamp01(config.scale_claim_strength * config.classical_leakage)
    lane_signal = clamp01(scale_evidence * (1.0 - noise_review))
    d_f = clamp01(noise_review + ontology_claim_risk)
    features = _feature_vector(config, lane_signal, 1.0 - ontology_claim_risk)
    return _shared_profile(
        config,
        lane_name="Google-scale quantum-computer evidence review",
        chapter_reference="Does Google's Quantum Computer Prove the Multiverse?",
        claim_tested="Large quantum-computer results can be reviewed as scale evidence without ontology promotion.",
        classification="scale_evidence_review_not_multiverse_validation",
        evidence_profile={
            "scale_evidence_score": _safe_round(scale_evidence),
            "noise_and_leakage_review": _safe_round(noise_review),
            "ontology_claim_risk": _safe_round(ontology_claim_risk),
            "review_signal": _safe_round(lane_signal),
        },
        simulator_mapping={
            "evidence_review": "treats quantum-computer scale as a review object",
            "claim_boundary": "prevents promotion from computational evidence to multiverse validation",
            "qnn_use": "adds a bounded evidence-review feature vector only when opted in",
        },
        feature_vector=features,
        d_f=d_f,
    )


def _wigner_lane(config: MultiverseExperimentConfig) -> Dict[str, Any]:
    admissibility = clamp01(config.memory_erasure * (1.0 - config.classical_leakage))
    friend_record_pressure = clamp01(config.measurement_strength * (1.0 - config.memory_erasure))
    inter_branch_signal = clamp01(config.branch_coherence * config.interference_visibility * admissibility)
    classification = (
        "inter_branch_protocol_admissible_in_simulator"
        if admissibility >= 0.8 and friend_record_pressure <= 0.1
        else "inter_branch_protocol_suspended_by_memory_record_constraints"
    )
    d_f = clamp01(1.0 - admissibility + friend_record_pressure + config.classical_leakage)
    features = _feature_vector(config, inter_branch_signal, admissibility)
    return _shared_profile(
        config,
        lane_name="Wigner-friend inter-branch communication",
        chapter_reference="Communicating Across the Multiverse",
        claim_tested="Inter-branch protocol metadata is admissible only with memory erasure and leakage constraints.",
        classification=classification,
        evidence_profile={
            "admissibility": _safe_round(admissibility),
            "memory_erasure_required": True,
            "friend_record_pressure": _safe_round(friend_record_pressure),
            "inter_branch_signal": _safe_round(inter_branch_signal),
            "admissibility_constraints": [
                "memory_erasure close to one",
                "classical_leakage close to zero",
                "friend record pressure close to zero",
            ],
        },
        simulator_mapping={
            "wigner_friend": "record-bearing observer creates a constraint term",
            "inter_branch_protocol": "simulator metadata only; disabled when records remain",
            "source_paper": VIOLARIS_INTERBRANCH_COMMUNICATION_2026,
        },
        feature_vector=features,
        d_f=d_f,
        source_ids=(
            RI_QUANTUM_PARADOXES_MULTIVERSE_2026,
            VIOLARIS_QUANTUM_PARADOXES_SERIES,
            VIOLARIS_INTERBRANCH_COMMUNICATION_2026,
        ),
    )


LANE_BUILDERS: Dict[str, Callable[[MultiverseExperimentConfig], Dict[str, Any]]] = {
    "deutsch_quantum_computation_origin": _deutsch_lane,
    "elitzur_vaidman_bomb_tester": _bomb_lane,
    "entanglement_teleportation_branch_accounting": _teleportation_lane,
    "google_quantum_computer_scale_review": _google_scale_lane,
    "wigner_friend_inter_branch_communication": _wigner_lane,
}


def qiskit_multiverse_preview(experiment_id: str) -> Dict[str, Any]:
    """Return a dependency-gated educational Qiskit preview."""

    if experiment_id not in MULTIVERSE_EXPERIMENT_IDS:
        raise ValueError(f"unknown multiverse experiment id: {experiment_id}")
    available = importlib.util.find_spec("qiskit") is not None
    return {
        "model": "qiskit_multiverse_experiment_preview_v1",
        "available": available,
        "status": "preview_only" if available else "unavailable",
        "experiment_id": experiment_id,
        "operations": [
            {"gate": "h", "target": "branch_register"},
            {"gate": "cx", "control": "branch_register", "target": "evidence_register"},
            {"gate": "measure", "target": "evidence_register", "relation": "simulator_feature_preview"},
        ],
        "interpretation": "educational circuit sketch only; no Qiskit dependency required",
        "research_boundary": MULTIVERSE_RESEARCH_BOUNDARY,
    }


def run_multiverse_experiment(
    config: Optional[MultiverseExperimentConfig] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Run one deterministic multiverse experiment profile."""

    active_config = config or MultiverseExperimentConfig(**kwargs)
    return LANE_BUILDERS[active_config.experiment_id](active_config)


def _average_vectors(vectors: Iterable[Sequence[float]]) -> List[float]:
    rows = [list(row) for row in vectors]
    if not rows:
        return []
    width = len(rows[0])
    return [_safe_round(mean(row[index] for row in rows)) for index in range(width)]


def run_all_multiverse_experiments(
    config: Optional[MultiverseExperimentConfig] = None,
    *,
    experiment_ids: Optional[Sequence[str]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Run all configured multiverse profiles and return an aggregate vector."""

    base_config = config or MultiverseExperimentConfig(
        experiment_id=(experiment_ids[0] if experiment_ids else MULTIVERSE_EXPERIMENT_IDS[0]),
        **kwargs,
    )
    ids = tuple(experiment_ids or MULTIVERSE_EXPERIMENT_IDS)
    profiles = [run_multiverse_experiment(base_config.with_experiment(experiment_id)) for experiment_id in ids]
    aggregate_vector = _average_vectors(profile["feature_vector"] for profile in profiles)
    source_ids = sorted({source for profile in profiles for source in profile["source_ids"]})
    return {
        "model": "fnp_qnn_multiverse_experiment_suite_v1",
        "source_ids": source_ids,
        "experiment_count": len(profiles),
        "experiment_ids": [profile["experiment_id"] for profile in profiles],
        "profiles": profiles,
        "classifications": {profile["experiment_id"]: profile["classification"] for profile in profiles},
        "feature_vector": aggregate_vector,
        "feature_dimension": len(aggregate_vector),
        "hierarchy": HIERARCHY,
        "forbidden_claims": list(FORBIDDEN_CLAIMS),
        "research_boundary": MULTIVERSE_RESEARCH_BOUNDARY,
    }


def multiverse_experiments_status() -> Dict[str, Any]:
    return {
        "status": "ok",
        "feature": "quantum-paradoxes-multiverse-experiments",
        "experiment_ids": list(MULTIVERSE_EXPERIMENT_IDS),
        "available_primitives": [
            "MultiverseExperimentConfig",
            "run_multiverse_experiment",
            "run_all_multiverse_experiments",
            "qiskit_multiverse_preview",
        ],
        "endpoints": [
            "GET /fnp-qnn/multiverse-experiments/status",
            "POST /fnp-qnn/multiverse-experiments/run",
            "POST /fnp-qnn/multiverse-experiments/run-all",
        ],
        "source_ids": list(SOURCE_LEDGER),
        "hierarchy": HIERARCHY,
        "research_boundary": MULTIVERSE_RESEARCH_BOUNDARY,
    }


__all__ = [
    "FORBIDDEN_CLAIMS",
    "MULTIVERSE_EXPERIMENT_IDS",
    "MULTIVERSE_RESEARCH_BOUNDARY",
    "RI_QUANTUM_PARADOXES_MULTIVERSE_2026",
    "SOURCE_LEDGER",
    "VIOLARIS_INTERBRANCH_COMMUNICATION_2026",
    "VIOLARIS_QUANTUM_PARADOXES_SERIES",
    "MultiverseExperimentConfig",
    "multiverse_experiments_status",
    "qiskit_multiverse_preview",
    "run_all_multiverse_experiments",
    "run_multiverse_experiment",
]
