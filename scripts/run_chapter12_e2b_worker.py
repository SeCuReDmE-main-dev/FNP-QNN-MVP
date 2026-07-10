"""Lightweight E2B worker for chapter-12 benchmark shards."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import sys
import time
import types


ROOT = Path(__file__).resolve().parents[1]
if "core" not in sys.modules:
    package = types.ModuleType("core")
    package.__path__ = [str(ROOT / "core")]
    sys.modules["core"] = package

from core.neutrino_chapter12_models import (  # noqa: E402
    Chapter12ValidationError,
    REQUIRED_CARRIERS,
    detector_projection_profile,
    ten_carrier_profile,
    toy_medium_profile,
)
from core.neutrino_chapter12_validation import neutrino_chapter12_validation  # noqa: E402


GUARD_FIELDS = (
    "physical_model_validated",
    "repetition_is_experimental_evidence",
    "real_detection_claim",
    "candidate_as_proof",
    "trace_is_neutrino",
    "secondary_as_primary_interaction",
    "msw_measurement_claim",
    "hidden_randomness",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=("baseline", "repeat", "stochastic", "carrier", "medium", "detector", "guard"), required=True)
    parser.add_argument("--runs", type=int, default=1000)
    parser.add_argument("--index", type=int, default=0)
    parser.add_argument("--case", default="vacuum")
    parser.add_argument("--field", default="candidate_as_proof")
    parser.add_argument("--seed", type=int, default=734)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fixture = json.loads((ROOT / "tests" / "fixtures" / "neutrino_chapter12_valid_admission.json").read_text(encoding="utf-8"))
    request = fixture["chapter12_validation_request"]
    started = time.perf_counter()
    if args.task == "baseline":
        result = neutrino_chapter12_validation(fixture)
        payload = {
            "task": args.task,
            "passed": result.get("proof_state") == "P2_internal_repeatability",
            "proof_state": result.get("proof_state"),
            "fingerprint": result.get("reference_run", {}).get("fingerprint"),
        }
    elif args.task == "repeat":
        payload = repeat_task(request, args.runs)
    elif args.task == "stochastic":
        payload = stochastic_task(request, args.runs, args.seed)
    elif args.task == "carrier":
        payload = carrier_task(request, args.index)
    elif args.task == "medium":
        payload = medium_task(request, args.case)
    elif args.task == "detector":
        payload = detector_task(request, args.case, args.seed)
    else:
        payload = guard_task(fixture, args.field)
    elapsed = time.perf_counter() - started
    payload["elapsed_seconds"] = elapsed
    payload["worker_python"] = sys.version.split()[0]
    payload["platform"] = sys.platform
    print(json.dumps(payload, sort_keys=True))
    return 0 if payload.get("passed") else 1


def repeat_task(request: dict, runs: int) -> dict:
    if not 1 <= runs <= 1_000_000:
        return {"task": "repeat", "passed": False, "reason": "invalid_run_count"}
    fingerprints = set()
    for _ in range(runs):
        carrier = ten_carrier_profile(request["carriers"])
        medium = toy_medium_profile(request["medium_request"])
        detector = detector_projection_profile(request["detector_request"])
        values = [carrier["composite_tension"], medium["medium_tension"], detector["detector_tension"]]
        fingerprints.add(hashlib.sha256(json.dumps(values, separators=(",", ":")).encode()).hexdigest())
    return {
        "task": "repeat",
        "runs": runs,
        "unique_fingerprints": len(fingerprints),
        "passed": len(fingerprints) == 1,
    }


def stochastic_task(request: dict, runs: int, seed: int) -> dict:
    if not 1 <= runs <= 1_000_000:
        return {"task": "stochastic", "passed": False, "reason": "invalid_run_count"}
    values = []
    for index in range(runs):
        detector_request = copy.deepcopy(request["detector_request"])
        detector_request["noise"] = {"mode": "gaussian_seeded", "seed": seed + index, "std": [0.01, 0.01]}
        values.append(detector_projection_profile(detector_request)["detector_tension"])
    replay = copy.deepcopy(request["detector_request"])
    replay["noise"] = {"mode": "gaussian_seeded", "seed": seed, "std": [0.01, 0.01]}
    same_seed = detector_projection_profile(replay) == detector_projection_profile(replay)
    return {
        "task": "stochastic",
        "runs": runs,
        "seed_start": seed,
        "minimum": min(values),
        "maximum": max(values),
        "mean": sum(values) / len(values),
        "same_seed_exact_replay": same_seed,
        "passed": same_seed and all(math.isfinite(value) for value in values),
    }


def carrier_task(request: dict, index: int) -> dict:
    if not 0 <= index < len(REQUIRED_CARRIERS):
        return {"task": "carrier", "passed": False, "reason": "invalid_index"}
    carriers = request["carriers"]
    baseline = ten_carrier_profile(carriers)
    name = carriers[index]["name"]
    try:
        ten_carrier_profile([item for item in carriers if item["name"] != name])
        ablation_blocked = False
    except Chapter12ValidationError as exc:
        ablation_blocked = exc.code == "missing_or_unknown_carrier"
    perturbations = []
    for delta in (-0.01, 0.01):
        changed = copy.deepcopy(carriers)
        changed[index]["tension"] += delta
        result = ten_carrier_profile(changed)
        expected = carriers[index]["weight"] / baseline["total_weight"] * delta
        actual = result["composite_tension"] - baseline["composite_tension"]
        perturbations.append(math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12))
    return {
        "task": "carrier",
        "carrier": name,
        "ablation_blocked": ablation_blocked,
        "perturbations_passed": all(perturbations),
        "passed": ablation_blocked and all(perturbations),
    }


def medium_task(request: dict, case: str) -> dict:
    theta = 0.6
    energy = 0.6
    delta_m2 = 0.0025
    cases = {
        "vacuum": {"level": "vacuum", "particle_kind": "neutrino", "theta_rad": theta},
        "context": {"level": "context_only"},
        "matter": {
            "level": "toy_matter_model",
            "particle_kind": "neutrino",
            "energy_gev": energy,
            "delta_m2_ev2": delta_m2,
            "theta_rad": theta,
            "matter_potential_ev": 7.6e-14,
        },
        "antimatter": {
            "level": "toy_matter_model",
            "particle_kind": "antineutrino",
            "energy_gev": energy,
            "delta_m2_ev2": delta_m2,
            "theta_rad": theta,
            "matter_potential_ev": 7.6e-14,
        },
        "resonance": {
            "level": "toy_matter_model",
            "particle_kind": "neutrino",
            "energy_gev": energy,
            "delta_m2_ev2": delta_m2,
            "theta_rad": theta,
            "matter_potential_ev": math.cos(2.0 * theta) * delta_m2 / (2.0 * energy * 1.0e9),
        },
    }
    if case not in cases:
        return {"task": "medium", "passed": False, "reason": "invalid_case"}
    result = toy_medium_profile(cases[case])
    passed = result["status"] == ("suspended" if case == "context" else "computed")
    if case == "resonance":
        passed = passed and result["resonance_residual"] <= 1e-12
    return {"task": "medium", "case": case, "result": result, "passed": passed}


def detector_task(request: dict, case: str, seed: int) -> dict:
    detector = copy.deepcopy(request["detector_request"])
    expected_error = None
    if case == "ideal":
        detector.update({"response_matrix": [[1.0, 0.0], [0.0, 1.0]], "background_status": "none_by_model"})
        detector.pop("background", None)
    elif case == "seeded":
        detector["noise"] = {"mode": "gaussian_seeded", "seed": seed, "std": [0.01, 0.01]}
    elif case == "missing_background":
        detector.pop("background_status", None)
        expected_error = "missing_detector_background"
    elif case == "dimension_mismatch":
        detector["response_matrix"] = [[1.0], [0.0]]
        expected_error = "detector_dimension_mismatch"
    elif case != "toy":
        return {"task": "detector", "passed": False, "reason": "invalid_case"}
    try:
        result = detector_projection_profile(detector)
        return {"task": "detector", "case": case, "result": result, "passed": expected_error is None}
    except Chapter12ValidationError as exc:
        return {"task": "detector", "case": case, "error": exc.code, "passed": exc.code == expected_error}


def guard_task(fixture: dict, field: str) -> dict:
    if field not in GUARD_FIELDS:
        return {"task": "guard", "passed": False, "reason": "invalid_field"}
    payload = copy.deepcopy(fixture)
    payload["chapter12_validation_request"][field] = True
    result = neutrino_chapter12_validation(payload)
    return {
        "task": "guard",
        "field": field,
        "decision": result["decision"],
        "passed": result["decision"]["status"] == "blocked",
    }


if __name__ == "__main__":
    raise SystemExit(main())
