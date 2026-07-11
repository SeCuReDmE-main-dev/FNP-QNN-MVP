"""Shared versioned run contract for API, Panel, CLI, and evidence exports."""

import json
from dataclasses import dataclass
from typing import Any

from core.education_progress import EducationProgress, build_education_progress
from core.education_review import TeacherReview, build_teacher_review


RUN_CONTRACT_SCHEMA = "fnp-qnn.education.run-contract"
RUN_CONTRACT_VERSION = "1.0.0"


@dataclass(frozen=True)
class EducationRunContract:
    """Canonical cross-surface representation of one supervised lab run."""

    lab_id: str
    seed: int
    progress: EducationProgress
    review: TeacherReview

    def to_dict(self) -> dict[str, Any]:
        """Return the stable envelope consumed by adapters and exporters."""

        return {
            "schema": RUN_CONTRACT_SCHEMA,
            "version": RUN_CONTRACT_VERSION,
            "lab_id": self.lab_id,
            "seed": self.seed,
            "progress": self.progress.to_dict(),
            "review": self.review.to_dict(),
        }

    def to_json(self) -> str:
        """Return deterministic JSON for evidence files and transport."""

        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


def build_education_run_contract(
    lab_id: str,
    seed: int,
    state: str,
    completed_steps: int,
    total_steps: int,
    trace_labels: tuple[str, ...],
    export_status: str,
    rejection_reason: str | None = None,
) -> EducationRunContract:
    """Build one validated contract for every local education surface."""

    progress = build_education_progress(state, completed_steps, total_steps, rejection_reason)
    review = build_teacher_review(lab_id, seed, trace_labels, export_status)
    return EducationRunContract(lab_id=review.lab_id, seed=review.seed, progress=progress, review=review)
