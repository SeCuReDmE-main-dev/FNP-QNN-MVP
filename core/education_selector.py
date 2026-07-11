"""Safe selection helpers for approved education lab manifests."""

from collections.abc import Iterable

from core.education_manifest import LabManifest, get_lab_manifest, list_lab_manifests


APPROVED_AUDIENCES = frozenset({"student", "teacher"})


def select_lab_manifests(
    audience: str | None = None,
    lab_ids: Iterable[str] | None = None,
) -> tuple[LabManifest, ...]:
    """Return approved labs in catalog order for one supervised audience.

    Unknown audiences and IDs fail closed so UI adapters cannot silently invent
    or expose an unapproved learning activity.
    """

    if audience is not None and audience not in APPROVED_AUDIENCES:
        raise ValueError(f"Unsupported education audience: {audience}")

    requested_ids = None if lab_ids is None else set(lab_ids)
    if requested_ids is not None:
        for lab_id in requested_ids:
            get_lab_manifest(lab_id)

    selected = []
    for manifest in list_lab_manifests():
        if audience is not None and audience not in manifest.audience:
            continue
        if requested_ids is not None and manifest.lab_id not in requested_ids:
            continue
        selected.append(manifest)
    return tuple(selected)
