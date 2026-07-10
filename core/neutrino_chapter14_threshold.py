"""Bounded Chapter-14 matrix engine for an admitted Synthia threshold packet."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping

SCHEMA_VERSION = "fnp.neutrino_chapter14_threshold.v1"
CARRIERS = (
    "local_matching", "aperiodicity", "inflation_deflation", "fivefold_orientation",
    "tile_frequency", "adjacency", "substitution_depth", "phason_susceptibility",
    "defect_density", "scale_transfer",
)
CLAIM_BOUNDARY = "P2 internal repeatability only; matrix simulation is not detection or physical substrate validation"


def neutrino_chapter14_threshold(payload: Mapping[str, Any]) -> dict[str, object]:
    reasons = _admission_reasons(payload)
    request = payload.get("chapter14_matrix_request")
    if not isinstance(request, Mapping):
        reasons.append("missing_chapter14_matrix_request")
        request = {}
    reasons.extend(_request_reasons(request))
    reasons = list(dict.fromkeys(reasons))
    if reasons:
        return _stop(reasons)

    carriers = request["carriers"]
    contributions = [
        {"name": row["name"], "weight": float(row["weight"]), "tension": float(row["tension"]), "weighted_contribution": float(row["weight"]) * float(row["tension"])}
        for row in carriers
    ]
    total_weight = sum(x["weight"] for x in contributions)
    composed = sum(x["weighted_contribution"] for x in contributions) / total_weight
    a_adj = _matrix(request["A_adj"])
    s_sub = _matrix(request["S_sub"])
    p_phason = _matrix(request["P_phason"])
    q_t = _vector(request["q_t"])
    q_sub = _matvec(s_sub, q_t)
    q_next_raw = _matvec(p_phason, q_sub)
    q_next = _normalize(q_next_raw)
    adjacency_energy = sum(a_adj[i][j] * abs(q_t[i] - q_t[j]) for i in range(len(q_t)) for j in range(len(q_t))) / 2.0
    d_f = 1.0 + _clamp01(composed)
    d_f_hat = _clamp(d_f, 1.0, 2.0)
    friction = _clamp01(0.65 * composed + 0.25 * _clamp01(adjacency_energy) + 0.10 * float(request["phason_uncertainty"]))
    candidate = _clamp01((d_f_hat - 1.0) * (1.0 - friction))
    trace = {"q_t": q_t, "q_after_substitution": q_sub, "q_t_plus_1": q_next, "changed_indices": [i for i, (a, b) in enumerate(zip(q_t, q_next)) if abs(a - b) > 1e-12]}
    fingerprint_payload = {"carriers": contributions, "A_adj": a_adj, "S_sub": s_sub, "P_phason": p_phason, "trace": trace, "D_f": d_f_hat, "dF": friction}
    fingerprint = hashlib.sha256(json.dumps(fingerprint_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "success": True,
        "type": "fnp_neutrino_chapter14_threshold",
        "schema_version": SCHEMA_VERSION,
        "decision": {"status": "accepted", "reason_codes": ["synthia_chapter14_admitted", "matrix_contract_valid"], "next_action": "emit_bounded_threshold_evidence"},
        "carrier_composition": {"count": 10, "total_weight": total_weight, "composed_tension": composed, "contributions": contributions},
        "matrices": {"A_adj": a_adj, "S_sub": s_sub, "P_phason": p_phason},
        "state_trace": trace,
        "D_f": d_f,
        "D_f_hat": d_f_hat,
        "dF": friction,
        "i_fractal_candidate": candidate,
        "fingerprint_sha256": fingerprint,
        "proof_state": "P2_internal_repeatability",
        "physical_model_validated": False,
        "substrate_validated": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def neutrino_chapter14_threshold_from_file(path: str | Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("chapter14 threshold input must contain a JSON object")
    return neutrino_chapter14_threshold(payload)


def _admission_reasons(payload: Mapping[str, Any]) -> list[str]:
    packet = payload.get("LexPacket_neutrino")
    if not isinstance(packet, Mapping): return ["missing_synthia_lex_packet"]
    profile = packet.get("chapter14_threshold_profile")
    if not isinstance(profile, Mapping): return ["missing_synthia_chapter14_profile"]
    reading = profile.get("SynthiaReading_14")
    if profile.get("profile_version") != "chapter14.threshold_public_safe.v1": return ["invalid_synthia_chapter14_profile"]
    if profile.get("chapter14_status") != "ready_for_fnp_threshold_calculation": return ["chapter14_not_admitted_by_synthia"]
    if not isinstance(reading, Mapping) or reading.get("approved_for_fnp_threshold_calculation") is not True: return ["chapter14_not_admitted_by_synthia"]
    boundary = profile.get("capability_boundary")
    if not isinstance(boundary, Mapping) or boundary.get("physical_model_validated") is not False: return ["physical_validation_claim"]
    return []


def _request_reasons(request: Mapping[str, Any]) -> list[str]:
    reasons = []
    rows = request.get("carriers")
    names = [str(x.get("name")) for x in rows if isinstance(x, Mapping)] if isinstance(rows, list) else []
    if len(names) != 10 or set(names) != set(CARRIERS) or len(set(names)) != 10: reasons.append("invalid_ten_carrier_vector")
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, Mapping) or not _finite_bounded(row.get("tension")) or not _finite_positive(row.get("weight")): reasons.append("invalid_carrier_value"); break
    q = request.get("q_t")
    n = len(q) if isinstance(q, list) else 0
    if n == 0 or not all(_finite(x) for x in q): reasons.append("invalid_state_vector")
    for key in ("A_adj", "S_sub", "P_phason"):
        matrix = request.get(key)
        if not _square_finite(matrix, n): reasons.append(f"invalid_{key}_dimensions")
    if request.get("physical_model_validated") is not False: reasons.append("physical_validation_claim")
    if request.get("real_detection_claim") is True: reasons.append("real_detection_claim")
    if request.get("substrate_validated") is True: reasons.append("substrate_validation_claim")
    if not _finite_bounded(request.get("phason_uncertainty")): reasons.append("invalid_phason_uncertainty")
    return reasons


def _matrix(value): return [[float(x) for x in row] for row in value]
def _vector(value): return [float(x) for x in value]
def _matvec(matrix, vector): return [sum(a * b for a, b in zip(row, vector)) for row in matrix]
def _normalize(vector):
    total = sum(abs(x) for x in vector)
    return [0.0 for _ in vector] if total == 0 else [x / total for x in vector]
def _finite(value): return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))
def _finite_bounded(value): return _finite(value) and 0.0 <= float(value) <= 1.0
def _finite_positive(value): return _finite(value) and float(value) > 0.0
def _square_finite(value, n): return isinstance(value, list) and len(value) == n and all(isinstance(row, list) and len(row) == n and all(_finite(x) for x in row) for row in value)
def _clamp(value, low, high): return max(low, min(high, value))
def _clamp01(value): return _clamp(value, 0.0, 1.0)


def _stop(reasons):
    return {"success":False,"type":"fnp_neutrino_chapter14_threshold","schema_version":SCHEMA_VERSION,"decision":{"status":"blocked","reason_codes":reasons,"next_action":"repair_chapter14_contract"},"fnp_computation_performed":False,"physical_model_validated":False,"substrate_validated":False,"claim_boundary":CLAIM_BOUNDARY}
