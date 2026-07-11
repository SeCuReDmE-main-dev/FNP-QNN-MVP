"""Human-review summary contract for the supervised education path."""

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from typing import Any

from core.education_manifest import LAB_MANIFEST_VERSION, get_lab_manifest


EXPORT_STATUSES = frozenset({"not_started", "pending", "ready"})


@dataclass(frozen=True)
class TeacherReview:
    """Small, redaction-friendly view model for teacher review surfaces."""

    lab_id: str
    manifest_version: str
    seed: int
    trace_labels: tuple[str, ...]
    claim_boundary: str
    export_status: str
    human_review_required: bool
    review_status: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible review payload."""

        return asdict(self)


def build_teacher_review(
    lab_id: str,
    seed: int,
    trace_labels: Iterable[str],
    export_status: str,
) -> TeacherReview:
    """Build a bounded review summary without exposing raw run payloads."""

    manifest = get_lab_manifest(lab_id)
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError("Teacher review seed must be a non-negative integer")
    if export_status not in EXPORT_STATUSES:
        raise ValueError(f"Unsupported education export status: {export_status}")

    normalized_labels = []
    for label in trace_labels:
        if not isinstance(label, str) or not label.strip():
            raise ValueError("Teacher review trace labels must be non-empty strings")
        clean_label = label.strip()
        if clean_label not in normalized_labels:
            normalized_labels.append(clean_label)

    review_status = "ready_for_human_review" if normalized_labels and export_status == "ready" else "incomplete"
    return TeacherReview(
        lab_id=manifest.lab_id,
        manifest_version=LAB_MANIFEST_VERSION,
        seed=seed,
        trace_labels=tuple(normalized_labels),
        claim_boundary=manifest.claim_boundary,
        export_status=export_status,
        human_review_required=True,
        review_status=review_status,
    )
