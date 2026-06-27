"""Deterministic simulator profiles for bounded time-physics experiments.

The profiles are educational time-accounting simulations derived from the
Jim Al-Khalili / Big Think source set. They do not prove eternalism, time
travel, quantum gravity, or any physical ontology.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
from statistics import mean
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from .axiomatic_chamber import HIERARCHY, clamp01, finite_float


BIG_THINK_TIME_VIDEO_2026 = "BIG_THINK_TIME_VIDEO_2026"
BIG_THINK_BLOCK_UNIVERSE_TRANSCRIPT_2026 = "BIG_THINK_BLOCK_UNIVERSE_TRANSCRIPT_2026"
ALKHALILI_CHEN_DECOHERENT_ARROW_2024 = "ALKHALILI_CHEN_DECOHERENT_ARROW_2024"
PUP_ON_TIME_CONTEXT_2026 = "PUP_ON_TIME_CONTEXT_2026"
LOCAL_RUNTIME_SOURCE_ID = "LOCAL_RUNTIME"

PRIOR_MARIA_MULTIVERSE_SOURCE_IDS: Tuple[str, ...] = (
    "RI_QUANTUM_PARADOXES_MULTIVERSE_2026",
    "VIOLARIS_QUANTUM_PARADOXES_SERIES",
    "VIOLARIS_INTERBRANCH_COMMUNICATION_2026",
)

SOURCE_LEDGER: Dict[str, str] = {
    BIG_THINK_TIME_VIDEO_2026: "https://www.youtube.com/watch?v=8xp3Bs6nZ-Y",
    BIG_THINK_BLOCK_UNIVERSE_TRANSCRIPT_2026: (
        "https://bigthink.com/series/the-big-think-interview/block-universe-alkhalili/"
    ),
    ALKHALILI_CHEN_DECOHERENT_ARROW_2024: "https://arxiv.org/abs/2405.03418",
    PUP_ON_TIME_CONTEXT_2026: "https://princetonuniversitypress.substack.com/p/quantum-entanglement-and-the-illusion",
    LOCAL_RUNTIME_SOURCE_ID: "local deterministic simulator implementation",
}

TIME_PHYSICS_EXPERIMENT_IDS: Tuple[str, ...] = (
    "manifest_vs_physical_time_flow",
    "relativistic_time_dilation_block_universe",
    "relativity_of_simultaneity_now",
    "thermodynamic_entropy_arrow",
    "entanglement_decoherence_arrow",
    "cosmological_boundary_time_travel",
)

TIME_PHYSICS_RESEARCH_BOUNDARY = (
    "alpha-local educational time-physics simulation only; not proof that time is unreal, "
    "not proof of eternalism, not operational time travel, not quantum-gravity validation, "
    "and not clinical, security, or production-public behavior"
)

FORBIDDEN_CLAIMS = (
    "time travel works",
    "the simulator proves eternalism",
    "the block universe proves fatalism",
    "entanglement sends signals through time",
    "quantum gravity is validated",
    "physics has found an absolute universal now",
)


@dataclass(frozen=True)
class TimePhysicsExperimentConfig:
    """Shared inputs for deterministic time-physics simulator profiles."""

    experiment_id: str = "manifest_vs_physical_time_flow"
    seed: int = 2026
    shots: int = 512
    temporal_flow_strength: float = 0.74
    relative_velocity_fraction: float = 0.35
    simultaneity_offset: float = 0.40
    entropy_gradient: float = 0.78
    entanglement_growth: float = 0.62
    decoherence_strength: float = 0.66
    cosmological_boundary_pressure: float = 0.55
    paradox_pressure: float = 0.15
    include_qiskit_preview: bool = False
    source_i: str = "fractal_boundary"

    def __post_init__(self) -> None:
        if self.experiment_id not in TIME_PHYSICS_EXPERIMENT_IDS:
            raise ValueError(f"unknown time physics experiment id: {self.experiment_id}")
        seed = int(round(finite_float(self.seed, "seed")))
        shots = int(round(finite_float(self.shots, "shots")))
        if shots < 16 or shots > 100000:
            raise ValueError("shots must be between 16 and 100000")
        object.__setattr__(self, "seed", seed)
        object.__setattr__(self, "shots", shots)
        for field_name in (
            "temporal_flow_strength",
            "relative_velocity_fraction",
            "simultaneity_offset",
            "entropy_gradient",
            "entanglement_growth",
            "decoherence_strength",
            "cosmological_boundary_pressure",
            "paradox_pressure",
        ):
            object.__setattr__(self, field_name, clamp01(getattr(self, field_name)))

    def with_experiment(self, experiment_id: str) -> "TimePhysicsExperimentConfig":
        return TimePhysicsExperimentConfig(
            experiment_id=experiment_id,
            seed=self.seed,
            shots=self.shots,
            temporal_flow_strength=self.temporal_flow_strength,
            relative_velocity_fraction=self.relative_velocity_fraction,
            simultaneity_offset=self.simultaneity_offset,
            entropy_gradient=self.entropy_gradient,
            entanglement_growth=self.entanglement_growth,
            decoherence_strength=self.decoherence_strength,
            cosmological_boundary_pressure=self.cosmological_boundary_pressure,
            paradox_pressure=self.paradox_pressure,
            include_qiskit_preview=self.include_qiskit_preview,
            source_i=self.source_i,
        )

    def payload(self) -> Dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "seed": self.seed,
            "shots": self.shots,
            "temporal_flow_strength": self.temporal_flow_strength,
            "relative_velocity_fraction": self.relative_velocity_fraction,
            "simultaneity_offset": self.simultaneity_offset,
            "entropy_gradient": self.entropy_gradient,
            "entanglement_growth": self.entanglement_growth,
            "decoherence_strength": self.decoherence_strength,
            "cosmological_boundary_pressure": self.cosmological_boundary_pressure,
            "paradox_pressure": self.paradox_pressure,
            "include_qiskit_preview": self.include_qiskit_preview,
            "source_i": self.source_i,
        }


def _safe_round(value: float) -> float:
    return round(clamp01(value), 6)


def _feature_vector(config: TimePhysicsExperimentConfig, lane_signal: float, claim_safety: float) -> List[float]:
    return [
        _safe_round(config.temporal_flow_strength),
        _safe_round(config.relative_velocity_fraction),
        _safe_round(config.simultaneity_offset),
        _safe_round(config.entropy_gradient),
        _safe_round(config.entanglement_growth),
        _safe_round(config.decoherence_strength),
        _safe_round(lane_signal),
        _safe_round(claim_safety),
    ]


def _sample_count(config: TimePhysicsExperimentConfig, probability: float) -> int:
    return int(round(config.shots * clamp01(probability)))


def _hierarchy_integrity(config: TimePhysicsExperimentConfig, d_f: float) -> Dict[str, Any]:
    return {
        "hierarchy": HIERARCHY,
        "I": "source observation envelope only",
        "I_system^S": config.source_i,
        "D_f": _safe_round((config.entropy_gradient + config.decoherence_strength) / 2.0),
        "dF": _safe_round(d_f),
        "i_fractal_candidate": None if config.paradox_pressure > 0.5 else "simulator_time_accounting_candidate",
        "dF_is_not_generic_I": True,
    }


def _shared_profile(
    config: TimePhysicsExperimentConfig,
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
    sources = list(
        source_ids
        or (
            BIG_THINK_TIME_VIDEO_2026,
            BIG_THINK_BLOCK_UNIVERSE_TRANSCRIPT_2026,
            PUP_ON_TIME_CONTEXT_2026,
        )
    )
    if LOCAL_RUNTIME_SOURCE_ID not in sources:
        sources.append(LOCAL_RUNTIME_SOURCE_ID)
    profile: Dict[str, Any] = {
        "model": "fnp_qnn_time_physics_experiment_profile_v1",
        "experiment_id": config.experiment_id,
        "lane_name": lane_name,
        "chapter_reference": chapter_reference,
        "source_ids": sources,
        "related_prior_work_source_ids": list(PRIOR_MARIA_MULTIVERSE_SOURCE_IDS),
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
        "research_boundary": TIME_PHYSICS_RESEARCH_BOUNDARY,
        "claim_boundary": (
            "The simulator may compare time-accounting explanations; it must not assert "
            "that the source video proves a physical ontology or operational time travel."
        ),
    }
    if config.include_qiskit_preview:
        profile["qiskit_preview"] = qiskit_time_physics_preview(config.experiment_id)
    return profile


def _manifest_flow_lane(config: TimePhysicsExperimentConfig) -> Dict[str, Any]:
    perceived_flow = config.temporal_flow_strength
    physical_flow_pressure = clamp01(1.0 - config.simultaneity_offset)
    lane_signal = clamp01(perceived_flow * (1.0 - 0.5 * config.relative_velocity_fraction))
    claim_safety = clamp01(1.0 - abs(perceived_flow - physical_flow_pressure))
    d_f = clamp01(abs(perceived_flow - physical_flow_pressure) + config.paradox_pressure)
    return _shared_profile(
        config,
        lane_name="Manifest vs physical time flow",
        chapter_reference="Does time flow?",
        claim_tested="Human time-flow experience can be represented separately from physical time-coordinate claims.",
        classification="manifest_time_flow_separated_from_physical_ontology",
        evidence_profile={
            "perceived_flow_score": _safe_round(perceived_flow),
            "physical_flow_pressure": _safe_round(physical_flow_pressure),
            "experience_coordinate_gap": _safe_round(abs(perceived_flow - physical_flow_pressure)),
            "bounded_flow_signal": _safe_round(lane_signal),
            "sampled_flow_events": _sample_count(config, lane_signal),
        },
        simulator_mapping={
            "manifest_time": "observer-experience feature, not proof of objective flow",
            "physical_time": "coordinate/accounting feature, not ontology validation",
            "forbidden_inference": "do not claim the simulator proves time is unreal",
        },
        feature_vector=_feature_vector(config, lane_signal, claim_safety),
        d_f=d_f,
    )


def _relativistic_time_lane(config: TimePhysicsExperimentConfig) -> Dict[str, Any]:
    velocity = min(config.relative_velocity_fraction, 0.999999)
    gamma_proxy = clamp01(1.0 - (1.0 - velocity * velocity) ** 0.5)
    block_consistency = clamp01((gamma_proxy + config.simultaneity_offset) / 2.0)
    lane_signal = clamp01(block_consistency * (1.0 - config.paradox_pressure))
    d_f = clamp01(config.paradox_pressure + (1.0 - block_consistency) * 0.5)
    return _shared_profile(
        config,
        lane_name="Relativistic time dilation and block-universe accounting",
        chapter_reference="Einstein, relativity, and the block universe",
        claim_tested="Relative motion changes clock accounting without promoting deterministic fatalism.",
        classification="relativistic_clock_accounting_not_fatalism_proof",
        evidence_profile={
            "relative_velocity_fraction": _safe_round(velocity),
            "gamma_proxy": _safe_round(gamma_proxy),
            "block_consistency": _safe_round(block_consistency),
            "bounded_relativistic_signal": _safe_round(lane_signal),
        },
        simulator_mapping={
            "time_dilation": "local bounded clock-accounting proxy",
            "block_universe": "interpretive source context only",
            "forbidden_inference": "do not infer fatalism or completed ontology from a simulator score",
        },
        feature_vector=_feature_vector(config, lane_signal, 1.0 - config.paradox_pressure),
        d_f=d_f,
    )


def _simultaneity_lane(config: TimePhysicsExperimentConfig) -> Dict[str, Any]:
    now_fragility = clamp01(config.simultaneity_offset * config.relative_velocity_fraction)
    local_now_stability = clamp01(1.0 - now_fragility)
    lane_signal = clamp01(now_fragility * (1.0 - config.paradox_pressure))
    d_f = clamp01(now_fragility + config.paradox_pressure * 0.5)
    return _shared_profile(
        config,
        lane_name="Relativity of simultaneity and the missing universal now",
        chapter_reference="Physicists cannot find a universal now",
        claim_tested="Different observer frames can disagree on simultaneity without implying an absolute universal now.",
        classification="local_now_only_no_universal_now_claim",
        evidence_profile={
            "now_fragility": _safe_round(now_fragility),
            "local_now_stability": _safe_round(local_now_stability),
            "frame_offset_events": _sample_count(config, now_fragility),
            "absolute_now_supported": False,
        },
        simulator_mapping={
            "observer_frame": "local frame-dependent ordering",
            "now": "local label only",
            "forbidden_inference": "do not claim physics found an absolute universal now",
        },
        feature_vector=_feature_vector(config, lane_signal, local_now_stability),
        d_f=d_f,
    )


def _entropy_arrow_lane(config: TimePhysicsExperimentConfig) -> Dict[str, Any]:
    thermodynamic_arrow = clamp01(config.entropy_gradient * (1.0 - config.paradox_pressure))
    reversibility_pressure = clamp01((1.0 - config.entropy_gradient) + config.paradox_pressure)
    lane_signal = clamp01(thermodynamic_arrow * (1.0 - 0.25 * reversibility_pressure))
    d_f = clamp01(reversibility_pressure)
    return _shared_profile(
        config,
        lane_name="Thermodynamic entropy arrow",
        chapter_reference="The arrow of time and entropy",
        claim_tested="Macroscopic arrow-of-time behavior can be modelled as entropy-gradient accounting.",
        classification="thermodynamic_arrow_boundary_condition_profile",
        evidence_profile={
            "thermodynamic_arrow": _safe_round(thermodynamic_arrow),
            "reversibility_pressure": _safe_round(reversibility_pressure),
            "entropy_gradient_events": _sample_count(config, thermodynamic_arrow),
            "second_law_context": "simulator trend only, not universal law inference",
        },
        simulator_mapping={
            "entropy_gradient": "bounded macrostate ordering proxy",
            "low_entropy_boundary": "source-context initial-condition proxy",
            "forbidden_inference": "do not infer exact cosmological entropy from the simulator",
        },
        feature_vector=_feature_vector(config, lane_signal, 1.0 - config.paradox_pressure),
        d_f=d_f,
        source_ids=(
            BIG_THINK_TIME_VIDEO_2026,
            BIG_THINK_BLOCK_UNIVERSE_TRANSCRIPT_2026,
            PUP_ON_TIME_CONTEXT_2026,
        ),
    )


def _entanglement_decoherence_lane(config: TimePhysicsExperimentConfig) -> Dict[str, Any]:
    decoherent_arrow = clamp01(config.entanglement_growth * config.decoherence_strength)
    low_entanglement_boundary = clamp01(1.0 - config.entanglement_growth * 0.5)
    lane_signal = clamp01(decoherent_arrow * (1.0 - config.paradox_pressure))
    d_f = clamp01(abs(config.entropy_gradient - decoherent_arrow) + config.paradox_pressure)
    return _shared_profile(
        config,
        lane_name="Entanglement and decoherence arrow",
        chapter_reference="Quantum entanglement and the arrow of time",
        claim_tested="A decoherent arrow can be represented as entanglement-growth metadata with boundary-condition caveats.",
        classification="decoherent_arrow_entanglement_past_hypothesis_profile",
        evidence_profile={
            "decoherent_arrow": _safe_round(decoherent_arrow),
            "low_entanglement_boundary": _safe_round(low_entanglement_boundary),
            "entanglement_growth_events": _sample_count(config, config.entanglement_growth),
            "source_hypothesis": "Entanglement Past Hypothesis",
        },
        simulator_mapping={
            "entanglement_entropy": "bounded partition-relative proxy",
            "decoherence": "feature trend, not a physical measurement",
            "forbidden_inference": "do not claim entanglement sends signals through time",
        },
        feature_vector=_feature_vector(config, lane_signal, 1.0 - config.paradox_pressure),
        d_f=d_f,
        source_ids=(
            BIG_THINK_TIME_VIDEO_2026,
            BIG_THINK_BLOCK_UNIVERSE_TRANSCRIPT_2026,
            ALKHALILI_CHEN_DECOHERENT_ARROW_2024,
            PUP_ON_TIME_CONTEXT_2026,
        ),
    )


def _cosmological_boundary_lane(config: TimePhysicsExperimentConfig) -> Dict[str, Any]:
    boundary_signal = clamp01(config.cosmological_boundary_pressure * config.entropy_gradient)
    paradox_guard = clamp01(1.0 - config.paradox_pressure)
    time_travel_admissibility = clamp01(paradox_guard * (1.0 - boundary_signal * 0.25))
    lane_signal = clamp01(boundary_signal * time_travel_admissibility)
    d_f = clamp01(config.paradox_pressure + (1.0 - time_travel_admissibility))
    classification = (
        "cosmological_boundary_profile_time_travel_rejected"
        if config.paradox_pressure >= 0.25
        else "cosmological_boundary_profile_time_travel_suspended"
    )
    return _shared_profile(
        config,
        lane_name="Cosmological boundary and time-travel paradox guard",
        chapter_reference="Beginning/end of the universe and time travel paradoxes",
        claim_tested="Cosmological boundary and paradox metadata can be tracked without claiming operational time travel.",
        classification=classification,
        evidence_profile={
            "cosmological_boundary_signal": _safe_round(boundary_signal),
            "paradox_pressure": _safe_round(config.paradox_pressure),
            "time_travel_admissibility": _safe_round(time_travel_admissibility),
            "operational_time_travel_supported": False,
        },
        simulator_mapping={
            "cosmological_boundary": "initial/final-condition source context",
            "time_travel": "paradox-guarded thought-experiment metadata only",
            "forbidden_inference": "do not claim time travel works",
        },
        feature_vector=_feature_vector(config, lane_signal, time_travel_admissibility),
        d_f=d_f,
    )


LANE_BUILDERS: Dict[str, Callable[[TimePhysicsExperimentConfig], Dict[str, Any]]] = {
    "manifest_vs_physical_time_flow": _manifest_flow_lane,
    "relativistic_time_dilation_block_universe": _relativistic_time_lane,
    "relativity_of_simultaneity_now": _simultaneity_lane,
    "thermodynamic_entropy_arrow": _entropy_arrow_lane,
    "entanglement_decoherence_arrow": _entanglement_decoherence_lane,
    "cosmological_boundary_time_travel": _cosmological_boundary_lane,
}


def qiskit_time_physics_preview(experiment_id: str) -> Dict[str, Any]:
    """Return a dependency-gated educational Qiskit preview."""

    if experiment_id not in TIME_PHYSICS_EXPERIMENT_IDS:
        raise ValueError(f"unknown time physics experiment id: {experiment_id}")
    available = importlib.util.find_spec("qiskit") is not None
    return {
        "model": "qiskit_time_physics_experiment_preview_v1",
        "available": available,
        "status": "preview_only" if available else "unavailable",
        "experiment_id": experiment_id,
        "operations": [
            {"gate": "h", "target": "time_register"},
            {"gate": "cx", "control": "time_register", "target": "arrow_register"},
            {"gate": "measure", "target": "arrow_register", "relation": "simulator_feature_preview"},
        ],
        "interpretation": "educational circuit sketch only; no Qiskit dependency required",
        "research_boundary": TIME_PHYSICS_RESEARCH_BOUNDARY,
    }


def run_time_physics_experiment(
    config: Optional[TimePhysicsExperimentConfig] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Run one deterministic time-physics experiment profile."""

    active_config = config or TimePhysicsExperimentConfig(**kwargs)
    return LANE_BUILDERS[active_config.experiment_id](active_config)


def _average_vectors(vectors: Iterable[Sequence[float]]) -> List[float]:
    rows = [list(row) for row in vectors]
    if not rows:
        return []
    width = len(rows[0])
    return [_safe_round(mean(row[index] for row in rows)) for index in range(width)]


def run_all_time_physics_experiments(
    config: Optional[TimePhysicsExperimentConfig] = None,
    *,
    experiment_ids: Optional[Sequence[str]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Run all configured time-physics profiles and return an aggregate vector."""

    base_config = config or TimePhysicsExperimentConfig(
        experiment_id=(experiment_ids[0] if experiment_ids else TIME_PHYSICS_EXPERIMENT_IDS[0]),
        **kwargs,
    )
    ids = tuple(experiment_ids or TIME_PHYSICS_EXPERIMENT_IDS)
    profiles = [run_time_physics_experiment(base_config.with_experiment(experiment_id)) for experiment_id in ids]
    aggregate_vector = _average_vectors(profile["feature_vector"] for profile in profiles)
    source_ids = sorted({source for profile in profiles for source in profile["source_ids"]})
    return {
        "model": "fnp_qnn_time_physics_experiment_suite_v1",
        "source_ids": source_ids,
        "related_prior_work_source_ids": list(PRIOR_MARIA_MULTIVERSE_SOURCE_IDS),
        "experiment_count": len(profiles),
        "experiment_ids": [profile["experiment_id"] for profile in profiles],
        "profiles": profiles,
        "classifications": {profile["experiment_id"]: profile["classification"] for profile in profiles},
        "feature_vector": aggregate_vector,
        "feature_dimension": len(aggregate_vector),
        "hierarchy": HIERARCHY,
        "forbidden_claims": list(FORBIDDEN_CLAIMS),
        "citation_integrity": {
            "time_physics_source_ids": [
                BIG_THINK_TIME_VIDEO_2026,
                BIG_THINK_BLOCK_UNIVERSE_TRANSCRIPT_2026,
                ALKHALILI_CHEN_DECOHERENT_ARROW_2024,
                PUP_ON_TIME_CONTEXT_2026,
            ],
            "prior_maria_multiverse_source_ids": list(PRIOR_MARIA_MULTIVERSE_SOURCE_IDS),
            "source_sets_are_separate": True,
        },
        "research_boundary": TIME_PHYSICS_RESEARCH_BOUNDARY,
    }


def time_physics_experiments_status() -> Dict[str, Any]:
    return {
        "status": "ok",
        "feature": "jim-alkhalili-time-physics-experiments",
        "experiment_ids": list(TIME_PHYSICS_EXPERIMENT_IDS),
        "available_primitives": [
            "TimePhysicsExperimentConfig",
            "run_time_physics_experiment",
            "run_all_time_physics_experiments",
            "qiskit_time_physics_preview",
        ],
        "endpoints": [
            "GET /fnp-qnn/time-physics-experiments/status",
            "POST /fnp-qnn/time-physics-experiments/run",
            "POST /fnp-qnn/time-physics-experiments/run-all",
        ],
        "source_ids": list(SOURCE_LEDGER),
        "related_prior_work_source_ids": list(PRIOR_MARIA_MULTIVERSE_SOURCE_IDS),
        "hierarchy": HIERARCHY,
        "research_boundary": TIME_PHYSICS_RESEARCH_BOUNDARY,
    }


__all__ = [
    "ALKHALILI_CHEN_DECOHERENT_ARROW_2024",
    "BIG_THINK_BLOCK_UNIVERSE_TRANSCRIPT_2026",
    "BIG_THINK_TIME_VIDEO_2026",
    "FORBIDDEN_CLAIMS",
    "PRIOR_MARIA_MULTIVERSE_SOURCE_IDS",
    "PUP_ON_TIME_CONTEXT_2026",
    "SOURCE_LEDGER",
    "TIME_PHYSICS_EXPERIMENT_IDS",
    "TIME_PHYSICS_RESEARCH_BOUNDARY",
    "TimePhysicsExperimentConfig",
    "qiskit_time_physics_preview",
    "run_all_time_physics_experiments",
    "run_time_physics_experiment",
    "time_physics_experiments_status",
]
