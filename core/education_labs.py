"""Age-aware educational lab scaffolding for the FNP-QNN simulator.

This module translates core simulator outputs into structured, classroom-facing
learning activities for students age 14+.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Sequence, Tuple

from .neurobit_gate_tunnel import NeuroBitProfile, run_neurobit_gates, run_neurobit_tunnel_demo

MIN_LEARNER_AGE = 14


@dataclass(frozen=True)
class LearningActivity:
    """Contract for one bounded learning activity."""

    activity_id: str
    title: str
    concept: str
    age_min: int
    age_max: int
    question: str
    expected_discovery: str
    profile: Mapping[str, float]
    steps: Sequence[str]
    follow_up: str
    puzzle_hint: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "activity_id": self.activity_id,
            "title": self.title,
            "concept": self.concept,
            "age_min": self.age_min,
            "age_max": self.age_max,
            "question": self.question,
            "expected_discovery": self.expected_discovery,
            "steps": list(self.steps),
            "follow_up": self.follow_up,
            "puzzle_hint": self.puzzle_hint,
            "profile": dict(self.profile),
        }


def build_learning_activities() -> List[LearningActivity]:
    """Return the default set of age-14+ learning activities."""
    return [
        LearningActivity(
            activity_id="neurobit-balance-lab",
            title="Truth vs Uncertainty balancing lab",
            concept="NeuroBit gate sequencing and expectation signatures",
            age_min=MIN_LEARNER_AGE,
            age_max=99,
            question="What happens to the expectation vector when truth grows and uncertainty grows?",
            expected_discovery=(
                "As truth increases, the weighted expectation signature shifts toward the first measurement axis; "
                "more indeterminacy introduces phase-driven variation."
            ),
            profile={"truth": 0.55, "indeterminacy": 0.30, "falsity": 0.15, "delta_falsity": 0.0},
            steps=(
                "Run the base NeuroBit profile and note the gate sequence.",
                "Increase truth and decrease indeterminacy by 0.20 in one step.",
                "Compare expectation signatures side-by-side.",
                "Answer: Which axis changed the most and why the result is bounded?",
            ),
            follow_up="Try one value with zero indeterminacy and one with very high indeterminacy.",
            puzzle_hint="Keep every profile normalized so comparisons stay fair.",
        ),
        LearningActivity(
            activity_id="neurobit-friction-lab",
            title="Uncertainty friction lab",
            concept="Bounded T/I/F metadata and reversibility risks",
            age_min=MIN_LEARNER_AGE,
            age_max=99,
            question="Does adding uncertainty make the run feel more 'noisy' in metadata?",
            expected_discovery=(
                "Higher indeterminacy raises reversible/noise tradeoff metrics in the metadata while still staying "
                "within deterministic fallback bounds."
            ),
            profile={"truth": 0.40, "indeterminacy": 0.45, "falsity": 0.15, "delta_falsity": 0.0},
            steps=(
                "Run the profile and capture reversibility metadata.",
                "Run a low-indeterminacy variation for comparison.",
                "Record expected_discovery before looking at implementation code.",
                "Check that conclusions match evidence, then discuss uncertainty as bounded risk.",
            ),
            follow_up="Explain how uncertainty changes are observable without using clinical or physics claims.",
            puzzle_hint="Focus on 'information_loss_risk' and 'undefined_transform_risk'.",
        ),
        LearningActivity(
            activity_id="neurobit-noise-quiz",
            title="Noise fingerprint quiz",
            concept="Tunnel-noise preview and deterministic signatures",
            age_min=MIN_LEARNER_AGE,
            age_max=99,
            question="Can you predict the deterministic noise fingerprint before reading the full output?",
            expected_discovery=(
                "Noise previews are synthetic and deterministic from profile and payload bytes, not cryptographic."
            ),
            profile={"truth": 0.55, "indeterminacy": 0.30, "falsity": 0.15, "delta_falsity": 0.05},
            steps=(
                "Run tunnel demo with short text and observe 'noise_preview' length and values.",
                "Change only one profile value and rerun.",
                "Confirm sequence_id changes predictably in your own notes.",
                "Label the boundary: fun simulator experiment, not encryption.",
            ),
            follow_up="Compare two inputs with the same profile but different text lengths.",
            puzzle_hint="Keep payload text small; this is a deterministic fingerprint exercise.",
        ),
    ]


def validate_learner_age(age_years: int) -> None:
    """Guardrail to enforce age-first framing."""
    if age_years < MIN_LEARNER_AGE:
        raise ValueError("learning lab is designed for age 14+ learners")


def _as_dict(obj: Mapping[str, Any]) -> Dict[str, Any]:
    return dict(obj)


def _profile_from_activity(activity: LearningActivity) -> NeuroBitProfile:
    payload = _as_dict(activity.profile)
    return NeuroBitProfile(
        truth=payload.get("truth", 0.55),
        indeterminacy=payload.get("indeterminacy", 0.30),
        falsity=payload.get("falsity", 0.15),
        delta_falsity=payload.get("delta_falsity", 0.0),
    )


def _signature_from_expectation(expectation: Sequence[float]) -> Dict[str, Any]:
    if not expectation:
        return {"dominant_axis": None, "dominant_magnitude": 0.0, "summary": "no expectation values"}
    dominant_axis = max(range(len(expectation)), key=lambda index: abs(float(expectation[index])))
    dominant_magnitude = float(abs(float(expectation[dominant_axis])))
    direction = "positive" if float(expectation[dominant_axis]) >= 0 else "negative"
    return {
        "dominant_axis": dominant_axis,
        "dominant_magnitude": round(dominant_magnitude, 6),
        "direction": direction,
        "summary": f"axis {dominant_axis} dominates ({direction}, |value|={dominant_magnitude:.6f})",
        "length": len(expectation),
    }


def run_learning_activity(activity: LearningActivity, include_tunnel_demo: bool = False) -> Dict[str, Any]:
    """Execute one activity and return structured evidence for classroom review."""
    profile = _profile_from_activity(activity)
    result = run_neurobit_gates(profile, n_qubits=4)
    payload = {
        "activity_id": activity.activity_id,
        "title": activity.title,
        "concept": activity.concept,
        "age_range": {"age_min": activity.age_min, "age_max": activity.age_max},
        "question": activity.question,
        "expected_discovery": activity.expected_discovery,
            "expected_to_observe": {
                "sequence": result["sequence"],
                "backend": result["backend"],
                "qiskit_available": result["qiskit_available"],
                "reversibility": result["reversibility_profile"],
                "observation": _signature_from_expectation(result["expectation_vector"]),
                "follows_learning_contract": [
                    "non_clinical",
                    "bounded_output",
                    "age_aware",
                ],
            },
        "steps": list(activity.steps),
    }
    if include_tunnel_demo:
        tunnel = run_neurobit_tunnel_demo(profile, data="learner_14_plus_challenge")
        payload["tunnel_preview"] = {
            "backend": tunnel["backend"],
            "sequence_id": tunnel["sequence_id"],
            "noise_preview": tunnel["noise_preview"],
            "research_boundary": tunnel["research_boundary"],
        }
    return payload


def build_learning_pack(age_years: int = MIN_LEARNER_AGE, include_tunnel_demo: bool = False) -> Dict[str, Any]:
    """Build a learner-safe pack of activities and run them for immediate classroom use."""
    validate_learner_age(age_years)
    activities = [activity for activity in build_learning_activities() if activity.age_min <= age_years <= activity.age_max]
    results = [run_learning_activity(activity, include_tunnel_demo=include_tunnel_demo) for activity in activities]
    return {
        "learner_policy": {
            "min_age": MIN_LEARNER_AGE,
            "max_age": 99,
            "age_years": age_years,
            "status": "age_ok",
        },
        "activities": results,
        "boundary": [
            "Not clinical, diagnostic, therapeutic, emergency, or production public software.",
            "Experiments are deterministic local simulations with bounded outputs.",
            "Tunnel demos are educational fingerprints, not security or encryption mechanisms.",
        ],
        "next_steps": [
            "Try swapping one profile value at a time.",
            "Record how sequence and reversibility metadata change.",
            "Compare two age-appropriate hypotheses across runs.",
        ],
    }


__all__ = [
    "LearningActivity",
    "MIN_LEARNER_AGE",
    "build_learning_activities",
    "build_learning_pack",
    "run_learning_activity",
    "validate_learner_age",
]
