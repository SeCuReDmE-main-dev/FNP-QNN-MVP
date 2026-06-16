"""UI helpers for the future Network Designer panel experience."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Dict, List, Tuple

import panel as pn

from core.network_designer import (
    NetworkExecutionResult,
    build_graph,
    execute_network,
    list_available_backends,
    list_presets,
)


def list_preset_cards() -> List[Dict[str, str]]:
    """Return deterministic preset metadata for panel controls."""
    cards: List[Dict[str, str]] = []
    for preset in list_presets():
        cards.append(
            {
                "id": preset.preset_id,
                "name": preset.name,
                "family": preset.family.value,
                "description": preset.description,
            }
        )
    return cards


def backend_options_for_preset(preset_id: str) -> List[str]:
    """Return backend ids that are valid for a given preset."""
    preset = _get_preset_for_id(preset_id)
    return [entry["name"] for entry in list_available_backends(preset.family.value)]


def parse_features_json(raw: str) -> Tuple[Dict[str, Any], List[str]]:
    """Parse optional JSON features from a text input.

    Returns:
        (features, errors)
    """
    trimmed = (raw or "{}").strip()
    if not trimmed:
        return {}, []
    try:
        payload = json.loads(trimmed)
    except json.JSONDecodeError as exc:
        return {}, [f"Invalid JSON feature payload: {exc}"]
    if not isinstance(payload, dict):
        return {}, ["Feature payload must be a JSON object."]
    return payload, []


def execute_preset_graph(
    preset_id: str,
    backend: str,
    raw_feature_json: str,
) -> Tuple[Dict[str, Any], List[str]]:
    """Run a preset through the backend contract."""
    preset = _get_preset_for_id(preset_id)
    graph = build_graph(preset.family.value)
    features, parse_errors = parse_features_json(raw_feature_json)
    if parse_errors:
        return {}, parse_errors
    result = execute_network(graph=graph, input_features=features, backend=backend)
    return _serialize_execution_result(result), []


def _serialize_execution_result(result: NetworkExecutionResult) -> Dict[str, Any]:
    serialized = asdict(result)
    # panel.json-friendly lists for deterministic logs and transport
    serialized["trace"] = list(serialized["trace"])
    serialized["warnings"] = list(serialized["warnings"])
    serialized["errors"] = list(serialized["errors"])
    return serialized


def build_network_designer_panel() -> pn.Column:
    """Build a minimal backend-contract-first Network Designer UI card."""
    presets = list_preset_cards()
    preset_selector = pn.widgets.Select(
        name="Preset",
        options=[preset["id"] for preset in presets],
        value=presets[0]["id"] if presets else "neural_network_v1",
    )
    backend_selector = pn.widgets.Select(
        name="Backend",
        options=backend_options_for_preset(presets[0]["id"]) if presets else [],
        value="torch_surrogate",
    )
    feature_input = pn.widgets.TextAreaInput(
        name="Features",
        value="{}",
        height=120,
        placeholder='{"input": 0.5, "encoder": 0.25}',
    )
    run_button = pn.widgets.Button(name="Run (Contract)", button_type="primary")
    status = pn.pane.Markdown("Aucun run exécuté.", sizing_mode="stretch_width")
    output = pn.pane.JSON({}, height=220, name="Execution output", sizing_mode="stretch_width")

    def on_preset_change(event: Any) -> None:
        options = backend_options_for_preset(event.new)
        backend_selector.options = options
        if options:
            backend_selector.value = options[0]
        status.object = f"Preset choisi: {event.new}"

    def on_run(_event: Any) -> None:
        data, parse_errors = parse_features_json(feature_input.value)
        if parse_errors:
            status.object = parse_errors[0]
            output.object = {"status": "invalid", "errors": parse_errors}
            return
        preset = _get_preset_for_id(preset_selector.value)
        graph = build_graph(preset.family.value)
        result = execute_network(graph=graph, input_features=data, backend=backend_selector.value)
        output.object = _serialize_execution_result(result)
        status.object = f"Execution: {result.status} ({result.backend})"

    preset_selector.param.watch(on_preset_change, "value")
    run_button.on_click(on_run)

    return pn.Card(
        pn.Column(
            preset_selector,
            backend_selector,
            feature_input,
            run_button,
            status,
            output,
        ),
        title="Network Designer (backend contract)",
        css_classes=["operator-card"],
        collapsible=True,
        collapsed=True,
    )


def _get_preset_for_id(preset_id: str):
    for preset in list_presets():
        if preset.preset_id == preset_id:
            return preset
    raise KeyError(f"Unknown preset id: {preset_id}")
