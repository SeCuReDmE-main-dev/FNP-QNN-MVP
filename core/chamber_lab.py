"""Synthia-gated visual chamber contract for the local FNP-QNN dashboard.

The chamber is a presentation of one admitted configuration.  Its ten carrier
values are semantic inputs, not ten physical objects and not a calculation of
``D_f``, ``dF`` or ``i_fractal``.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .neutrino_admission_gate import validate_synthia_admission
from .neutrino_chapter12_models import (
    Chapter12ValidationError,
    REQUIRED_CARRIERS,
    canonical_fingerprint,
    ten_carrier_profile,
)


HIERARCHY = "I -> I_system^S -> D_f -> dF -> i_fractal"
RESEARCH_BOUNDARY = (
    "Alpha-local research visualization only. It is not a clinical, detector, "
    "or physical-validation instrument."
)

_BASE_PRESETS = {
    "neutrino_chamber": {
        "label": "Neutrino chamber",
        "family": "core",
        "description": "Ten-carrier neutrino configuration with staged propagation and projection.",
        "style": {"color": "#55d9ff", "roughness": 0.24, "metallic": 0.18, "translucency": 0.55, "pattern_scale": 1.0, "light_intensity": 1.1, "environment": "deep-space"},
    },
    "phi_cube_plithogenic": {
        "label": "Phi cube plithogenic",
        "family": "core",
        "description": "A bounded phi/cube visual grammar; it remains a display preset until Synthia admits the exact carrier packet.",
        "style": {"color": "#fdaa37", "roughness": 0.38, "metallic": 0.42, "translucency": 0.18, "pattern_scale": 1.618, "light_intensity": 0.92, "environment": "warm-studio"},
    },
}

_PLUGIN_LABELS = {
    "p011_fractales_atomiques": "P011 · Fractales atomiques",
    "p046_rossler_beaulieu_cubic_framework": "P046 · Rössler–Beaulieu cubic",
    "p097_fbm_tuner": "P097 · fBm tuner",
    "p109_dual_triplex": "P109 · Dual triplex",
    "p114_ffed_neutrosophic_consensus": "P114 · Neutrosophic consensus",
}

# Kept as display metadata so this admission-only module does not initialize
# the optional FfeD/CPAI runtime. The ids mirror core.ffed_plugin_bridge.MVP5_PLUGIN_IDS.
MVP5_VISUAL_PLUGIN_IDS = tuple(_PLUGIN_LABELS)


class ChamberLabError(ValueError):
    """Public-safe error that does not expose an untrusted payload."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def list_chamber_presets() -> list[dict[str, object]]:
    """Return visual metadata only; selection never creates an admitted scene."""

    presets: list[dict[str, object]] = []
    for preset_id, preset in _BASE_PRESETS.items():
        presets.append({"preset_id": preset_id, **preset, "requires_synthia_admission": True})
    for plugin_id in MVP5_VISUAL_PLUGIN_IDS:
        presets.append(
            {
                "preset_id": plugin_id,
                "label": _PLUGIN_LABELS.get(plugin_id, plugin_id),
                "family": "mvp5_plugin",
                "description": "Existing MVP5 plugin visual overlay; it does not alter FNP-QNN values.",
                "requires_synthia_admission": True,
            }
        )
    return presets


def chamber_lab_status() -> dict[str, object]:
    return {
        "status": "ready",
        "renderer": "threejs_embedded_local",
        "admission_authority": "Synthia",
        "formalizer": "QuaNThoR chamber formalizer",
        "fallback": {
            "enabled": True,
            "operators": ["Codex", "Gemini"],
            "action": "show_warning_then_run_doctor_and_retry",
            "hard_stop": "refuse_chamber_when_synthia_is_unavailable_or_rejects",
        },
        "required_carriers": list(REQUIRED_CARRIERS),
        "hierarchy": HIERARCHY,
        "boundary": RESEARCH_BOUNDARY,
    }


def build_chamber_scene(
    admission_packet: Mapping[str, Any],
    carriers: Sequence[Mapping[str, Any]],
    preset_id: str = "neutrino_chamber",
    style: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    """Build an immutable display contract after Synthia and ten-carrier checks.

    A rejected/missing Synthia packet returns a hard refusal record. Invalid
    carrier or display input is rejected as a validation error for the caller.
    """

    selected = _resolve_preset(preset_id)
    decision = validate_synthia_admission(admission_packet)
    if not decision.can_compute_fnp:
        return {
            "status": "rejected",
            "scene": None,
            "admission": decision.as_dict(),
            "refusal": {
                "authority": "Synthia",
                "reason_codes": list(decision.reason_codes),
                "next_action": "refuse_chamber",
                "doctor": {"command": "fnp-qnn doctor --full", "tui_command": "/doctor"},
                "fallback": "Codex/Gemini may diagnose or help formalize, but cannot admit a chamber.",
            },
            "hierarchy": HIERARCHY,
            "boundary": RESEARCH_BOUNDARY,
        }

    try:
        profile = ten_carrier_profile(carriers)
    except Chapter12ValidationError as exc:
        raise ChamberLabError(exc.code) from exc

    display_style = _normalize_style({**selected.get("style", {}), **dict(style or {})})
    contributions = profile["contributions"]
    layers = _semantic_layers(contributions)
    scene = {
        "schema_version": "fnp-qnn.chamber-lab.v1",
        "preset": {"preset_id": preset_id, "label": selected["label"], "family": selected["family"]},
        "carrier_order": list(REQUIRED_CARRIERS),
        "carrier_count": 10,
        "semantic_layers": layers,
        "carrier_profile": profile,
        "display_style": display_style,
        "renderer_contract": {
            "renderer": "threejs_embedded_local",
            "one_chamber": True,
            "ten_variables_not_objects": True,
            "camera": {"orbit": True, "limits": {"min_distance": 3.0, "max_distance": 18.0}},
            "key_light": {"drag": True, "intensity_limits": [0.1, 3.0]},
            "environments": ["deep-space", "warm-studio", "cool-lab"],
        },
        "hierarchy": HIERARCHY,
        "boundary": RESEARCH_BOUNDARY,
    }
    scene["scene_fingerprint"] = canonical_fingerprint(scene)
    return {
        "status": "accepted",
        "scene": scene,
        "admission": decision.as_dict(),
        "boundary": RESEARCH_BOUNDARY,
    }


def _resolve_preset(preset_id: str) -> dict[str, object]:
    preset_id = str(preset_id or "neutrino_chamber").strip()
    if preset_id in _BASE_PRESETS:
        return dict(_BASE_PRESETS[preset_id])
    if preset_id in MVP5_VISUAL_PLUGIN_IDS:
        return {
            "label": _PLUGIN_LABELS.get(preset_id, preset_id),
            "family": "mvp5_plugin",
            "style": _BASE_PRESETS["neutrino_chamber"]["style"],
        }
    raise ChamberLabError("unknown_chamber_preset")


def _normalize_style(candidate: Mapping[str, Any]) -> dict[str, object]:
    color = str(candidate.get("color", "#55d9ff")).strip()
    if not color.startswith("#") or len(color) not in {4, 7}:
        raise ChamberLabError("invalid_chamber_color")
    environment = str(candidate.get("environment", "deep-space")).strip()
    if environment not in {"deep-space", "warm-studio", "cool-lab"}:
        raise ChamberLabError("invalid_chamber_environment")
    return {
        "color": color,
        "roughness": _bounded(candidate.get("roughness", 0.3), 0.02, 1.0, "invalid_chamber_roughness"),
        "metallic": _bounded(candidate.get("metallic", 0.2), 0.0, 1.0, "invalid_chamber_metallic"),
        "translucency": _bounded(candidate.get("translucency", 0.4), 0.0, 0.95, "invalid_chamber_translucency"),
        "pattern_scale": _bounded(candidate.get("pattern_scale", 1.0), 0.25, 4.0, "invalid_chamber_pattern_scale"),
        "light_intensity": _bounded(candidate.get("light_intensity", 1.0), 0.1, 3.0, "invalid_chamber_light_intensity"),
        "environment": environment,
    }


def _bounded(value: Any, minimum: float, maximum: float, code: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ChamberLabError(code) from exc
    if not minimum <= number <= maximum:
        raise ChamberLabError(code)
    return number


def _semantic_layers(contributions: Sequence[Mapping[str, Any]]) -> list[dict[str, object]]:
    by_name = {str(item["name"]): item for item in contributions}
    groups = (
        ("source", ("I_source",), "origin carrier"),
        ("propagation", ("I_flavor", "I_mass", "I_mix", "I_phase"), "propagation configuration"),
        ("medium", ("I_medium",), "medium context"),
        ("interaction", ("I_interaction",), "interaction context"),
        ("projection", ("I_secondary", "I_detector"), "secondary response and detector projection"),
        ("uncertainty", ("I_uncertainty",), "uncertainty envelope"),
    )
    return [
        {
            "layer_id": layer_id,
            "label": label,
            "carrier_names": list(names),
            "carriers": [dict(by_name[name]) for name in names],
        }
        for layer_id, names, label in groups
    ]
