"""Chapter-13 distributed worker gate for the four-run E2B campaign."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping

from .ffed_plugin_bridge import FfeDPluginBridge
from .neutrino_admission_gate import validate_synthia_admission
from .neutrino_chapter12_validation import neutrino_chapter12_validation


SCHEMA_VERSION = "fnp.neutrino_chapter13_distributed_worker.v1"
RUN_PROFILES = {
    "run_1_all_valid",
    "run_2_quarter_false",
    "run_3_three_quarter_false",
    "run_4_seeded_random_mix",
}
WORKER_MODES = {"valid", "bounded_chaos"}
FAULT_TYPES = (
    "terminate_process",
    "timeout",
    "truncate_result",
    "delete_workspace",
    "memory_pressure",
    "disk_pressure",
    "local_connection_failure",
    "duplicate_task",
    "interrupt_atomic_write",
    "telemetry_outage",
)
CLAIM_BOUNDARY = (
    "distributed software validation only; p114 cannot override Synthia; p046 schedules bounded faults; "
    "simulation is not detection; physical_model_validated=false"
)


def neutrino_chapter13_distributed_worker(
    payload: Mapping[str, Any],
    *,
    pluginpack_path: str | Path | None = None,
) -> dict[str, object]:
    admission = validate_synthia_admission(payload)
    if not admission.can_compute_fnp:
        return _stop("blocked", list(admission.reason_codes), "synthia_admission_stopped")
    profile = admission.admitted_chapter13_distributed_validation
    if profile is None:
        return _stop("blocked", ["missing_chapter13_distributed_profile"], "restore_synthia_chapter13_profile")

    request = payload.get("chapter13_worker_request")
    if not isinstance(request, Mapping):
        return _stop("blocked", ["missing_chapter13_worker_request"], "supply_worker_request")
    request_reasons = _request_reasons(request)
    if request_reasons:
        return _stop("blocked", request_reasons, "repair_worker_request")

    bridge = FfeDPluginBridge(pluginpack_path=pluginpack_path)
    p114_request = profile.get("p114_consensus_request")
    items = p114_request.get("items", []) if isinstance(p114_request, Mapping) else []
    p114 = bridge.run_p114_consensus(items, mode="decision")
    if p114.get("status") in {"disabled", "error"} or p114.get("success") is not True:
        return _stop("suspended", ["p114_plugin_unavailable"], "restore_required_pluginpack", p114=p114)
    if p114.get("action") == "ask_clarification":
        return _stop("suspended", ["p114_clarification_required"], "clarify_before_fnp", p114=p114)
    if p114.get("action") == "escalate_or_reject":
        return _stop("rejected", ["p114_consensus_rejected"], "reject_before_fnp", p114=p114)
    if not bool((p114.get("cli_gate") or {}).get("allow_lvfm_admission")):
        return _stop("blocked", ["p114_gate_not_admitted"], "repair_consensus", p114=p114)

    worker_mode = str(request.get("worker_mode"))
    if worker_mode == "bounded_chaos":
        p046 = bridge.run_p046_schedule(request.get("p046_configuration") if isinstance(request.get("p046_configuration"), Mapping) else None)
        if p046.get("success") is not True:
            return _stop(
                "blocked",
                [str(code) for code in p046.get("reason_codes", ["p046_schedule_blocked"])],
                "repair_p046_schedule",
                p114=p114,
                p046=p046,
            )
        try:
            schedule = _fault_schedule(p046.get("trajectory", []), request)
        except (TypeError, ValueError) as exc:
            return _stop(
                "blocked",
                ["p046_invalid_trajectory"],
                "repair_p046_schedule",
                p114=p114,
                p046={**p046, "trajectory_error": str(exc)},
            )
        return {
            "success": True,
            "type": "fnp_neutrino_chapter13_distributed_worker",
            "schema_version": SCHEMA_VERSION,
            "decision": {
                "status": "fault_schedule_ready",
                "reason_codes": ["p114_admitted", "p046_bounded_schedule_valid"],
                "next_action": "execute_faults_in_disposable_e2b_workspace",
            },
            "worker": _worker_identity(request),
            "p114_consensus": _compact_p114(p114),
            "p046_schedule": schedule,
            "fnp_computation_performed": False,
            "physical_model_validated": False,
            "claim_boundary": CLAIM_BOUNDARY,
        }

    readout = neutrino_chapter12_validation(payload)
    if readout.get("decision", {}).get("status") != "accepted":
        reasons = readout.get("decision", {}).get("reason_codes", ["chapter12_reference_readout_blocked"])
        return _stop("blocked", [str(code) for code in reasons], "repair_chapter12_reference", p114=p114)
    return {
        "success": True,
        "type": "fnp_neutrino_chapter13_distributed_worker",
        "schema_version": SCHEMA_VERSION,
        "decision": {
            "status": "accepted",
            "reason_codes": ["synthia_admitted", "p114_admitted", "chapter12_reference_valid"],
            "next_action": "execute_signed_worker_bundle",
        },
        "worker": _worker_identity(request),
        "p114_consensus": _compact_p114(p114),
        "execution_permission": {
            "task_bundle": [dict(task) for task in request["tasks"]],
            "task_count": 4,
            "manifest_hash": request["task_manifest_hash"],
            "expected_outcome": request["expected_outcome"],
        },
        "reference_readout": {
            "proof_state": readout.get("proof_state"),
            "fingerprint": readout.get("reference_run", {}).get("fingerprint"),
            "D_f": readout.get("D_f"),
            "D_f_hat": readout.get("D_f_hat"),
            "dF": readout.get("dF"),
            "i_fractal_candidate": readout.get("i_fractal_candidate"),
        },
        "fnp_computation_performed": True,
        "physical_model_validated": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def neutrino_chapter13_distributed_worker_from_file(
    path: str | Path,
    *,
    pluginpack_path: str | Path | None = None,
) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("chapter13 distributed worker input must contain a JSON object")
    return neutrino_chapter13_distributed_worker(payload, pluginpack_path=pluginpack_path)


def _request_reasons(request: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    if str(request.get("run_profile")) not in RUN_PROFILES:
        reasons.append("invalid_run_profile")
    worker_index = request.get("worker_index")
    if not isinstance(worker_index, int) or isinstance(worker_index, bool) or not 0 <= worker_index < 67:
        reasons.append("invalid_worker_index")
    if request.get("shard_count") != 67:
        reasons.append("invalid_shard_count")
    if str(request.get("worker_mode")) not in WORKER_MODES:
        reasons.append("invalid_worker_mode")
    tasks = request.get("tasks")
    if not isinstance(tasks, list) or len(tasks) != 4:
        reasons.append("invalid_worker_task_bundle")
    elif any(not isinstance(task, Mapping) or not str(task.get("task_id", "")).strip() for task in tasks):
        reasons.append("invalid_worker_task_bundle")
    if not _is_sha256(request.get("task_manifest_hash")):
        reasons.append("invalid_task_manifest_hash")
    if not str(request.get("expected_outcome", "")).strip():
        reasons.append("missing_expected_outcome")
    if request.get("physical_model_validated") is not False:
        reasons.append("physical_validation_claim")
    if request.get("real_detection_claim") is True:
        reasons.append("real_detection_claim")
    return reasons


def _fault_schedule(trajectory: object, request: Mapping[str, Any]) -> dict[str, object]:
    if not isinstance(trajectory, list) or len(trajectory) < 4:
        raise ValueError("p046 trajectory must contain at least four points")
    instructions = []
    for index, point in enumerate(trajectory[:4]):
        if not isinstance(point, list) or len(point) != 3:
            raise ValueError("p046 trajectory points must be three-dimensional")
        values = [float(value) for value in point]
        if not all(math.isfinite(value) for value in values):
            raise ValueError("p046 trajectory points must be finite")
        selector = int(abs(values[0] * 1000.0 + values[1] * 100.0 + values[2] * 10.0)) % len(FAULT_TYPES)
        intensity = max(0.05, min(1.0, sum(abs(value) for value in values) / 30.0))
        instructions.append(
            {
                "task_id": request["tasks"][index]["task_id"],
                "fault_type": FAULT_TYPES[selector],
                "intensity": round(intensity, 6),
                "workspace_scope": "/tmp/neutrino-validation/<worker-hash>",
                "unbounded": False,
            }
        )
    canonical = json.dumps(instructions, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "schema_version": "fnp.neutrino_chapter13_fault_schedule.v1",
        "instructions": instructions,
        "schedule_sha256": hashlib.sha256(canonical).hexdigest(),
        "replay_required": True,
    }


def _worker_identity(request: Mapping[str, Any]) -> dict[str, object]:
    return {
        "run_profile": str(request.get("run_profile")),
        "worker_index": int(request.get("worker_index", -1)),
        "shard_count": int(request.get("shard_count", 0)),
        "worker_mode": str(request.get("worker_mode")),
    }


def _compact_p114(p114: Mapping[str, Any]) -> dict[str, object]:
    return {
        "plugin_id": p114.get("plugin_id"),
        "status": p114.get("status"),
        "action": p114.get("action"),
        "consensus": dict(p114.get("consensus") or {}),
        "cli_gate": dict(p114.get("cli_gate") or {}),
    }


def _stop(
    status: str,
    reasons: list[str],
    next_action: str,
    *,
    p114: Mapping[str, Any] | None = None,
    p046: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "success": False,
        "type": "fnp_neutrino_chapter13_distributed_worker",
        "schema_version": SCHEMA_VERSION,
        "decision": {"status": status, "reason_codes": reasons, "next_action": next_action},
        "fnp_computation_performed": False,
        "physical_model_validated": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    if p114 is not None:
        payload["p114_consensus"] = _compact_p114(p114)
    if p046 is not None:
        payload["p046_schedule"] = {
            "status": p046.get("status"),
            "reason_codes": list(p046.get("reason_codes", [])),
            "metrics": dict(p046.get("metrics") or {}),
        }
    return payload


def _is_sha256(value: object) -> bool:
    text = str(value or "").strip().lower()
    return len(text) == 64 and all(character in "0123456789abcdef" for character in text)


__all__ = [
    "SCHEMA_VERSION",
    "neutrino_chapter13_distributed_worker",
    "neutrino_chapter13_distributed_worker_from_file",
]
