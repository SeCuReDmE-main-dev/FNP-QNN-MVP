from __future__ import annotations

import json
from pathlib import Path

from core.chamber_lab import build_chamber_scene, list_chamber_presets
from core.neutrino_chapter12_models import REQUIRED_CARRIERS


FIXTURE = Path(__file__).parent / "fixtures" / "neutrino_chapter12_valid_admission.json"


def _carriers():
    return [
        {
            "name": name,
            "tension": index / 20,
            "weight": 1.0 + index / 10,
            "role": f"role:{name}",
            "source_fields": [f"field:{name}"],
            "TIF": {"T": 0.6, "I": 0.3, "F": 0.1},
        }
        for index, name in enumerate(REQUIRED_CARRIERS)
    ]


def _admission():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_chamber_scene_requires_synthia_then_uses_exactly_ten_variables():
    result = build_chamber_scene(_admission(), _carriers(), "neutrino_chamber")

    assert result["status"] == "accepted"
    assert result["scene"]["carrier_count"] == 10
    assert result["scene"]["renderer_contract"]["ten_variables_not_objects"] is True
    assert result["scene"]["hierarchy"] == "I -> I_system^S -> D_f -> dF -> i_fractal"


def test_chamber_is_refused_when_synthia_packet_is_missing():
    result = build_chamber_scene({}, _carriers())

    assert result["status"] == "rejected"
    assert result["refusal"]["next_action"] == "refuse_chamber"
    assert result["scene"] is None


def test_all_agreed_base_and_mvp5_presets_are_exposed():
    ids = {item["preset_id"] for item in list_chamber_presets()}

    assert {"neutrino_chamber", "phi_cube_plithogenic"}.issubset(ids)
    assert len(ids) == 7
