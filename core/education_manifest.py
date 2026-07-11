"""Versioned, fixture-oriented contracts for the public education suite.

The manifest is deliberately data-only. It tells a student or teacher what a
lab is expected to produce without making the education layer a second
simulator implementation.
"""

from dataclasses import asdict, dataclass
from typing import Any


LAB_MANIFEST_SCHEMA = "fnp-qnn.education.lab-manifest"
LAB_MANIFEST_VERSION = "1.0.0"


@dataclass(frozen=True)
class LabManifest:
    """Stable learning contract shared by future UI and operator surfaces."""

    lab_id: str
    title: str
    audience: tuple[str, ...]
    objective: str
    input_profile: str
    expected_evidence: tuple[str, ...]
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation of this manifest."""

        return asdict(self)


_LAB_MANIFESTS = (
    LabManifest(
        lab_id="memory-to-evidence",
        title="Memory to Evidence",
        audience=("student", "teacher"),
        objective="Trace a bounded memory event through encoding, network output, and human review.",
        input_profile="fixture:education.basic-memory-event.v1",
        expected_evidence=("input summary", "feature vector", "run seed", "review boundary"),
        claim_boundary="Alpha-local non-clinical educational simulation; local evidence is not authority.",
    ),
    LabManifest(
        lab_id="neurobit-gate-trace",
        title="NeuroBit Gate Trace",
        audience=("student", "teacher"),
        objective="Inspect a deterministic neutrosophic gate trace and explain its bounded state metadata.",
        input_profile="fixture:education.neurobit-gate-profile.v1",
        expected_evidence=("T/I/F profile", "gate sequence", "operation descriptors", "review boundary"),
        claim_boundary="Alpha-local educational trace only; not a physical, clinical, security, or production claim.",
    ),
)


def list_lab_manifests() -> tuple[LabManifest, ...]:
    """Return the approved immutable catalog in deterministic order."""

    return _LAB_MANIFESTS


def get_lab_manifest(lab_id: str) -> LabManifest:
    """Return one approved manifest or raise a clear lookup error."""

    for manifest in _LAB_MANIFESTS:
        if manifest.lab_id == lab_id:
            return manifest
    raise KeyError(f"Unknown education lab manifest: {lab_id}")


def manifest_catalog() -> dict[str, Any]:
    """Return the versioned catalog for API, Panel, CLI, or export adapters."""

    return {
        "schema": LAB_MANIFEST_SCHEMA,
        "version": LAB_MANIFEST_VERSION,
        "labs": [manifest.to_dict() for manifest in _LAB_MANIFESTS],
    }
