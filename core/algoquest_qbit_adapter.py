"""AlgoQuest/Qbit Education adapter hook for FNP-QNN."""

APP_SLUG = "fnpqnn"
HUB_SLUG = "algoquest"


def build_learning_event_stub(artifact_ref: str, *, score: float = 93) -> dict:
    return {
        "schema": "securedme.education.student-learning-event.v1",
        "app_slug": APP_SLUG,
        "artifact_ref": artifact_ref,
        "skill_area": "fnpqnn_simulation",
        "difficulty_band": "beginner",
        "score": score,
        "threshold": 93,
        "attempt_count": 1,
        "blocked_reason": "",
        "next_step_hint": "Open AlgoQuest to translate the simulation into a beginner-safe challenge.",
        "qbit_help_accepted": False,
        "risk_flags": [],
        "contract_version": "v1",
        "raw_secret_stored": False,
        "dry_run": True,
    }
