"""Curated local command registry for FNP-QNN CLI surfaces."""

from __future__ import annotations

import json
import math
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from api.main import _command_response
from api.schemas import CommandRequest, NeuroBitTunnelRequest, RuntimeRunRequest
from core import (
    bell_state_reference_profile,
    cpai_mesh_profile,
    deformation_invariant_signature,
    gravity_null_test_status,
    microtubule_proxy_phi_profile,
    nonstandard_neighborhood_profile,
    normalize_fractal_dimension,
    observer_effect_profile,
    partial_entanglement_profile,
    partial_membership_mean,
    plithogenic_attribute_profile,
    plithogenic_contradiction_degree,
    plithogenic_multi_to_uni_decision,
    plithogenic_probability_family_profile,
    punctured_surface_state,
    source_weighted_triplet_fusion,
    topological_axiom_profile,
    triplet_quality_profile,
)

RESEARCH_BOUNDARY = (
    "Alpha-local research simulator. Not clinical, diagnostic, therapeutic, "
    "emergency, safety-critical, or production-public software. Results are "
    "local simulation evidence only."
)

HIERARCHY_BOUNDARY = "I -> I_system^S -> D_f -> dF -> i_fractal"

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class RegistryCommand:
    name: str
    description: str
    runner: Callable[[dict[str, Any]], dict[str, Any]]


def json_safe(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return json_safe(value.model_dump())
    if hasattr(value, "__dict__") and not isinstance(value, type):
        return json_safe(vars(value))
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [json_safe(item) for item in value]
    if isinstance(value, float):
        if math.isfinite(value):
            return value
        return str(value)
    return value


def load_json_payload(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    payload_path = Path(path)
    with payload_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("payload JSON must contain an object")
    return payload


def command_response(command_name: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    request = CommandRequest(**(payload or {}))
    response = _command_response(command_name, request)
    result = response.model_dump()
    result["research_boundary"] = RESEARCH_BOUNDARY
    result["hierarchy_boundary"] = HIERARCHY_BOUNDARY
    return json_safe(result)


def runtime_run(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    request_payload = RuntimeRunRequest(**(payload or {}))
    return command_response("cerebrum-runtime-run", {"payload": request_payload.model_dump(exclude_none=True)})


def qnn_smoke(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    request_payload = dict(payload or {})
    request_payload.setdefault("epochs", 4)
    request_payload.setdefault("test_size", 0.0)
    return command_response("qnn-smoke", request_payload)


def neurobit_gates(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    neurobit = NeuroBitTunnelRequest(**(payload or {}))
    return command_response("neurobit-gates", {"neurobit": neurobit.model_dump(exclude_none=True)})


def neurobit_tunnel(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    neurobit = NeuroBitTunnelRequest(**(payload or {}))
    return command_response("neurobit-tunnel-demo", {"neurobit": neurobit.model_dump(exclude_none=True)})


def _wrap_core(name: str, data: Any) -> dict[str, Any]:
    return {
        "success": True,
        "type": "core-profile",
        "name": name,
        "research_boundary": RESEARCH_BOUNDARY,
        "hierarchy_boundary": HIERARCHY_BOUNDARY,
        "data": json_safe(data),
    }


def _source_fusion_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    sources = payload.get("sources")
    if isinstance(sources, list) and sources:
        return sources
    return [
        {"truth": 0.55, "indeterminacy": 0.3, "falsity": 0.15, "weight": 1.0},
        {"truth": 0.45, "indeterminacy": 0.4, "falsity": 0.2, "weight": 0.7},
    ]


def _values_payload(payload: dict[str, Any]) -> tuple[list[float], list[float]]:
    values = payload.get("values") if isinstance(payload.get("values"), list) else [0.2, 0.5, 0.8]
    memberships = payload.get("memberships") if isinstance(payload.get("memberships"), list) else [0.5, 1.0, 0.7]
    return [float(item) for item in values], [float(item) for item in memberships]


def _sample_events(payload: dict[str, Any]) -> list[dict[str, Any]]:
    events = payload.get("events")
    if isinstance(events, list) and events:
        return events
    return [
        {"modality": "audio", "value": 0.2, "timestamp": 0.0, "label": "tone"},
        {"modality": "video", "value": 0.7, "timestamp": 0.5, "label": "motion"},
    ]


def _sample_pairs(payload: dict[str, Any]) -> list[dict[str, Any]]:
    pairs = payload.get("pairs")
    if isinstance(pairs, list) and pairs:
        return pairs
    return [{"left": "audio", "right": "video", "temporal_delta": 0.5, "relation": "demo"}]


CORE_COMMANDS: dict[str, RegistryCommand] = {
    "cpai-mesh": RegistryCommand(
        "cpai-mesh",
        "Local CPAI mesh routing profile.",
        lambda payload: _wrap_core("cpai-mesh", cpai_mesh_profile(**payload)),
    ),
    "gravity-status": RegistryCommand(
        "gravity-status",
        "Gravity null-test status contract.",
        lambda payload: _wrap_core("gravity-status", gravity_null_test_status()),
    ),
    "bell-reference": RegistryCommand(
        "bell-reference",
        "Bell-state reference profile.",
        lambda payload: _wrap_core("bell-reference", bell_state_reference_profile()),
    ),
    "normalize-df": RegistryCommand(
        "normalize-df",
        "Normalize D_f into bounded D_f_hat.",
        lambda payload: _wrap_core(
            "normalize-df",
            {
                "D_f_hat": normalize_fractal_dimension(
                    float(payload.get("D_f", payload.get("fractal_dimension", 1.5))),
                    float(payload.get("D_min", payload.get("fractal_dimension_min", 1.0))),
                    float(payload.get("D_max", payload.get("fractal_dimension_max", 2.0))),
                )
            },
        ),
    ),
    "observer-effect": RegistryCommand(
        "observer-effect",
        "Neutrosophic observer effect profile.",
        lambda payload: _wrap_core(
            "observer-effect",
            observer_effect_profile(
                payload.get("state", {"truth": 0.4, "indeterminacy": 0.3, "falsity": 0.3}),
                float(payload.get("observer_strength", 0.5)),
                float(payload.get("decoherence", 0.05)),
            ),
        ),
    ),
    "partial-entanglement": RegistryCommand(
        "partial-entanglement",
        "Partial entanglement profile.",
        lambda payload: _wrap_core(
            "partial-entanglement",
            partial_entanglement_profile(
                float(payload.get("correlation", 0.7)),
                None if payload.get("separability") is None else float(payload["separability"]),
                float(payload.get("decoherence", 0.05)),
                float(payload.get("delta_falsity", payload.get("dF", 0.0))),
            ),
        ),
    ),
    "punctured-surface": RegistryCommand(
        "punctured-surface",
        "Punctured surface state profile.",
        lambda payload: _wrap_core(
            "punctured-surface",
            punctured_surface_state(
                float(payload.get("delta", payload.get("puncture_delta", 0.1))),
                float(payload.get("width", 8.0)),
                float(payload.get("height", 8.0)),
            ),
        ),
    ),
    "triplet-quality": RegistryCommand(
        "triplet-quality",
        "Nidus Idearum triplet quality profile.",
        lambda payload: _wrap_core(
            "triplet-quality",
            triplet_quality_profile(
                float(payload.get("truth", payload.get("T", 0.55))),
                float(payload.get("indeterminacy", payload.get("I", 0.3))),
                float(payload.get("falsity", payload.get("F", 0.15))),
            ),
        ),
    ),
    "source-fusion": RegistryCommand(
        "source-fusion",
        "Source-weighted triplet fusion profile.",
        lambda payload: _wrap_core("source-fusion", source_weighted_triplet_fusion(_source_fusion_payload(payload))),
    ),
    "partial-mean": RegistryCommand(
        "partial-mean",
        "Partial-membership mean.",
        lambda payload: _wrap_core("partial-mean", partial_membership_mean(*_values_payload(payload))),
    ),
    "plithogenic-attribute": RegistryCommand(
        "plithogenic-attribute",
        "Plithogenic attribute profile.",
        lambda payload: _wrap_core("plithogenic-attribute", plithogenic_attribute_profile(_sample_events(payload))),
    ),
    "plithogenic-contradiction": RegistryCommand(
        "plithogenic-contradiction",
        "Plithogenic contradiction degree.",
        lambda payload: _wrap_core(
            "plithogenic-contradiction",
            plithogenic_contradiction_degree(
                payload.get("left", {"truth": 0.6, "indeterminacy": 0.2, "falsity": 0.2}),
                payload.get("right", {"truth": 0.3, "indeterminacy": 0.4, "falsity": 0.3}),
                float(payload.get("overlap_score", 1.0)),
            ),
        ),
    ),
    "plithogenic-family": RegistryCommand(
        "plithogenic-family",
        "Plithogenic probability family profile.",
        lambda payload: _wrap_core(
            "plithogenic-family",
            plithogenic_probability_family_profile(
                payload.get("plithogenic_profile", {"truth": 0.5, "indeterminacy": 0.3, "falsity": 0.2})
            ),
        ),
    ),
    "plithogenic-decision": RegistryCommand(
        "plithogenic-decision",
        "Plithogenic multi-to-uni decision profile.",
        lambda payload: _wrap_core(
            "plithogenic-decision",
            plithogenic_multi_to_uni_decision(
                payload.get(
                    "profiles",
                    [
                        {"truth": 0.55, "indeterminacy": 0.25, "falsity": 0.2},
                        {"truth": 0.45, "indeterminacy": 0.35, "falsity": 0.2},
                    ],
                ),
                str(payload.get("operator", "conjunction")),
            ),
        ),
    ),
    "topology-axiom": RegistryCommand(
        "topology-axiom",
        "Revolutionary topology axiom profile.",
        lambda payload: _wrap_core(
            "topology-axiom",
            topological_axiom_profile(
                payload.get("universe", ["audio", "video"]),
                payload.get("open_sets", [[], ["audio"], ["video"], ["audio", "video"]]),
            ),
        ),
    ),
    "topology-neighborhood": RegistryCommand(
        "topology-neighborhood",
        "Nonstandard neighborhood profile.",
        lambda payload: _wrap_core(
            "topology-neighborhood",
            nonstandard_neighborhood_profile(
                float(payload.get("value", 0.51)),
                float(payload.get("center", 0.5)),
                float(payload.get("epsilon", 0.1)),
                str(payload.get("mode", "binad")),
            ),
        ),
    ),
    "topology-signature": RegistryCommand(
        "topology-signature",
        "Deformation invariant signature.",
        lambda payload: _wrap_core(
            "topology-signature", deformation_invariant_signature(_sample_events(payload), _sample_pairs(payload))
        ),
    ),
    "microtubule-proxy": RegistryCommand(
        "microtubule-proxy",
        "Hydra/GPCN microtubule proxy phi profile.",
        lambda payload: _wrap_core(
            "microtubule-proxy",
            microtubule_proxy_phi_profile(
                proxy_index=int(payload.get("proxy_index", 0)),
                frequency_hz=None if payload.get("frequency_hz") is None else float(payload["frequency_hz"]),
                coherence_time_s=None if payload.get("coherence_time_s") is None else float(payload["coherence_time_s"]),
                anesthetic_damping=float(payload.get("anesthetic_damping", 0.0)),
                coupling_strength=float(payload.get("coupling_strength", 0.5)),
                neighborhood_weight=float(payload.get("neighborhood_weight", 0.5)),
                reduction_pressure=float(payload.get("reduction_pressure", 0.2)),
                contradiction_threshold=float(payload.get("contradiction_threshold", 0.35)),
            ),
        ),
    ),
}


def list_core_commands() -> list[dict[str, str]]:
    return [{"name": item.name, "description": item.description} for item in CORE_COMMANDS.values()]


def run_core_command(name: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        command = CORE_COMMANDS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown core command '{name}'") from exc
    return command.runner(payload or {})
