"""Read-only FNP-QNN projection for the separate QCG Companion.

The adapter deliberately accepts only a compact runtime summary. It never
receives raw observations, source code, files, credentials, provider data, or
human-authority commands. ``get_snapshot`` returns the exact bounded snapshot
shape consumed by the QCG Companion; navigation remains a local Panel concern.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any
from uuid import UUID

ADAPTER_SCHEMA = "securedme.fnp-qnn.qcg-companion-adapter.v1"
NAVIGATION_SCHEMA = "securedme.fnp-qnn.qcg-navigation-result.v1"
QCG_SNAPSHOT_SCHEMA = "qcg-console-snapshot.v2"

_STATE_KEYS = frozenset(
    {
        "run_id",
        "status",
        "events_count",
        "pairs_count",
        "feature_dimension",
        "evidence_count",
    }
)
_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9_-]{2,63}$")
_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
_STATUS_TO_PHASE = MappingProxyType(
    {
        "idle": "empty",
        "ready": "partial",
        "running": "active",
        "completed": "active",
        "cancelled": "cancelled",
        "error": "error",
        "recovery": "recovery",
        "unavailable": "unavailable",
    }
)
_MAX_COUNT = 1_000_000_000


@dataclass(frozen=True)
class CompanionNavigationTarget:
    """One allowlisted local destination in the current FNP-QNN Panel."""

    key: str
    label: str
    panel_tab_index: int | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "panel_tab_index": self.panel_tab_index,
        }


PANEL_NAVIGATION_TARGETS: Mapping[str, CompanionNavigationTarget] = MappingProxyType(
    {
        "overview": CompanionNavigationTarget("overview", "Control Room", None),
        "events": CompanionNavigationTarget("events", "Events", 0),
        "pairs": CompanionNavigationTarget("pairs", "Pairs", 1),
        "qnn_benchmark": CompanionNavigationTarget("qnn_benchmark", "QNN benchmark", 2),
        "neurobit": CompanionNavigationTarget("neurobit", "NeuroBit", 3),
        "raw_json": CompanionNavigationTarget("raw_json", "Raw JSON", 4),
        "network_designer": CompanionNavigationTarget("network_designer", "Network Designer", 5),
        "network_designer_canvas": CompanionNavigationTarget(
            "network_designer_canvas", "Network Designer Canvas", 6
        ),
        "chamber_lab": CompanionNavigationTarget("chamber_lab", "Chamber Lab", 7),
    }
)


class FnpQnnQcgCompanionAdapter:
    """Build sanitized snapshots and resolve allowlisted local navigation."""

    def __init__(self, session_id: str) -> None:
        self.session_id = _canonical_uuid(session_id)

    def get_snapshot(self, state: Mapping[str, Any] | None = None) -> dict[str, Any]:
        """Return one read-only snapshot accepted by the QCG v2 sanitizer."""

        summary = _bounded_state(state or {})
        digest = _digest(summary)
        artifact_id = summary.get("run_id", "fnp-qnn-runtime")
        phase = _STATUS_TO_PHASE[summary.get("status", "idle")]
        return {
            "schema_version": QCG_SNAPSHOT_SCHEMA,
            # The inspected FNP-QNN page owns the source snapshot. QCG renders
            # the same bounded state in its separate Companion side panel.
            "surface": "web",
            "session_id": self.session_id,
            "phase": phase,
            # This adapter cannot create QCG consent or human decisions.
            "authority_state": "unavailable",
            "artifact": {
                "id": artifact_id,
                "digest": digest,
                "format": "fnp-qnn-state",
                "profile": "alpha-local",
                "compiler_status": "not_applicable",
            },
            "effects": {
                "inspections": 1,
                "evaluations": 0,
                "local_simulations": 0,
                "metadata_validations": 1,
                "qpu_submissions": 0,
                "evidence_exports": 0,
            },
            "storage_mode": "memory",
            "available_commands": [],
            "invocations": [],
            "collaboration": {
                "participants": [],
                "messages": [],
                "open_reviews": 0,
                "memory_tombstones": [],
            },
            "tools": [],
        }

    def navigation_manifest(self) -> list[dict[str, Any]]:
        """Return the fixed public-safe FNP-QNN navigation allowlist."""

        return [target.to_dict() for target in PANEL_NAVIGATION_TARGETS.values()]

    def navigate(
        self,
        target: str,
        activate_panel_tab: Callable[[int], None] | None = None,
    ) -> dict[str, Any]:
        """Resolve and optionally apply a local Panel tab selection.

        ``overview`` identifies the page-level control-room section and has no
        Panel tab index. Every other target can be applied by passing the
        existing Panel tab controller as ``activate_panel_tab``.
        """

        if not isinstance(target, str) or target not in PANEL_NAVIGATION_TARGETS:
            raise ValueError("navigation target is not allowlisted")
        selected = PANEL_NAVIGATION_TARGETS[target]
        activation = "resolved"
        if selected.panel_tab_index is not None and activate_panel_tab is not None:
            activate_panel_tab(selected.panel_tab_index)
            activation = "applied"
        return {
            "schema_version": NAVIGATION_SCHEMA,
            "accepted": True,
            "target": selected.key,
            "label": selected.label,
            "panel_tab_index": selected.panel_tab_index,
            "activation": activation,
            "local_only": True,
        }

    def build_envelope(
        self,
        state: Mapping[str, Any] | None = None,
        current_target: str = "overview",
    ) -> dict[str, Any]:
        """Return a deterministic proof envelope without extending QCG."""

        navigation = self.navigate(current_target)
        return {
            "schema_version": ADAPTER_SCHEMA,
            "adapter_id": "fnp-qnn-to-qcg-companion",
            "mode": "read_only",
            "snapshot": self.get_snapshot(state),
            "navigation": {
                "current": navigation,
                "targets": self.navigation_manifest(),
            },
        }

    def to_json(
        self,
        state: Mapping[str, Any] | None = None,
        current_target: str = "overview",
    ) -> str:
        """Serialize the proof envelope with stable key ordering."""

        return json.dumps(
            self.build_envelope(state, current_target),
            sort_keys=True,
            separators=(",", ":"),
        )


def _canonical_uuid(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("session_id must be a UUID string")
    try:
        parsed = UUID(value)
    except (ValueError, AttributeError) as exc:
        raise ValueError("session_id must be a valid UUID") from exc
    canonical = str(parsed)
    if not _UUID.fullmatch(canonical):
        raise ValueError("session_id must be a QCG-compatible UUID")
    return canonical


def _bounded_state(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError("state must be a mapping")
    unknown = set(value) - _STATE_KEYS
    if unknown:
        raise ValueError(f"state contains non-allowlisted fields: {', '.join(sorted(map(str, unknown)))}")

    run_id = value.get("run_id", "fnp-qnn-runtime")
    if not isinstance(run_id, str) or not _IDENTIFIER.fullmatch(run_id):
        raise ValueError("run_id must be a bounded lowercase identifier")

    status = value.get("status", "idle")
    if not isinstance(status, str) or status not in _STATUS_TO_PHASE:
        raise ValueError("status is not allowlisted")

    result: dict[str, Any] = {"run_id": run_id, "status": status}
    for key in ("events_count", "pairs_count", "feature_dimension", "evidence_count"):
        item = value.get(key, 0)
        if isinstance(item, bool) or not isinstance(item, int) or not 0 <= item <= _MAX_COUNT:
            raise ValueError(f"{key} must be a bounded non-negative integer")
        result[key] = item
    return result


def _digest(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


__all__ = [
    "ADAPTER_SCHEMA",
    "NAVIGATION_SCHEMA",
    "PANEL_NAVIGATION_TARGETS",
    "QCG_SNAPSHOT_SCHEMA",
    "CompanionNavigationTarget",
    "FnpQnnQcgCompanionAdapter",
]
