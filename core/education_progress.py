"""Progress and recovery contract for supervised education runs."""

from dataclasses import asdict, dataclass
from typing import Any


RUN_STATES = frozenset({"not_started", "in_progress", "awaiting_review", "completed", "rejected"})
RECOVERY_ACTIONS = {
    "not_started": "start_lab",
    "in_progress": "resume_run",
    "awaiting_review": "open_teacher_review",
    "completed": "export_evidence",
    "rejected": "review_rejection",
}
STATE_MESSAGES = {
    "not_started": "Choose an approved lab to begin.",
    "in_progress": "Resume the run from its last recorded step.",
    "awaiting_review": "Ask a teacher to review the run evidence.",
    "completed": "Review the evidence before exporting it.",
    "rejected": "Read the rejection reason, correct the input, and retry.",
}


@dataclass(frozen=True)
class EducationProgress:
    """Serializable progress state shared by student and teacher surfaces."""

    state: str
    completed_steps: int
    total_steps: int
    percent_complete: int
    recovery_action: str
    message: str
    rejection_reason: str | None
    human_review_required: bool

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible progress payload."""

        return asdict(self)


def build_education_progress(
    state: str,
    completed_steps: int,
    total_steps: int,
    rejection_reason: str | None = None,
) -> EducationProgress:
    """Build a bounded progress state and its next safe recovery action."""

    if state not in RUN_STATES:
        raise ValueError(f"Unsupported education run state: {state}")
    if isinstance(completed_steps, bool) or not isinstance(completed_steps, int):
        raise ValueError("completed_steps must be an integer")
    if isinstance(total_steps, bool) or not isinstance(total_steps, int) or total_steps <= 0:
        raise ValueError("total_steps must be a positive integer")
    if completed_steps < 0 or completed_steps > total_steps:
        raise ValueError("completed_steps must be between zero and total_steps")
    if state == "completed" and completed_steps != total_steps:
        raise ValueError("completed runs must have all steps completed")
    if state == "rejected" and not isinstance(rejection_reason, str):
        raise ValueError("rejected runs require a rejection reason")
    if state != "rejected" and rejection_reason is not None:
        raise ValueError("rejection_reason is only valid for rejected runs")

    percent_complete = int((completed_steps / total_steps) * 100)
    return EducationProgress(
        state=state,
        completed_steps=completed_steps,
        total_steps=total_steps,
        percent_complete=percent_complete,
        recovery_action=RECOVERY_ACTIONS[state],
        message=STATE_MESSAGES[state],
        rejection_reason=rejection_reason.strip() if rejection_reason else None,
        human_review_required=state in {"awaiting_review", "completed", "rejected"},
    )
