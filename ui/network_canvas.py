"""Network Designer canvas-style UI scaffold."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import panel as pn

from core.network_designer import (
    NetworkGraph,
    build_graph,
    execute_network,
    list_available_backends,
    list_presets,
    serialize_graph,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
CANVAS_STYLE_PATH = ROOT_DIR / "web" / "network_designer" / "network_canvas.css"
CANVAS_SCRIPT_PATH = ROOT_DIR / "web" / "network_designer" / "network_canvas.js"


def build_network_designer_canvas() -> pn.Column:
    """Build a lightweight operator canvas skeleton (no drag/drop yet)."""
    presets = sorted(list_presets(), key=lambda preset: preset.preset_id)
    preset_selector = pn.widgets.Select(
        name="Preset",
        options={f"{p.family.value} · {p.preset_id}": p.preset_id for p in presets},
        value=presets[0].preset_id,
    )

    backend_selector = pn.widgets.Select(name="Backend", options=_available_backends(presets[0].family.value))
    features_input = pn.widgets.TextAreaInput(
        name="Features JSON",
        value="{}",
        height=100,
        placeholder='{"input": 0.5, "encoder": 0.25}',
    )
    run_button = pn.widgets.Button(name="Run network graph", button_type="primary")
    palette = _build_palette(presets)
    canvas = pn.pane.HTML(_empty_canvas_markup(), height=340, margin=0)
    inspector = pn.pane.JSON({}, depth=2, name="Inspector", height=180)
    command_log = pn.pane.Markdown("Aucun run effectué.")
    graph_json_pane = pn.pane.JSON({}, depth=3, height=220)

    _load_canvas_assets(canvas)
    _refresh_canvas(graph_json_pane, canvas, preset_selector.value)

    def on_preset_change(event: Any) -> None:
        backend_selector.options = _available_backends(_preset_family(event.new))
        backend_selector.value = next(iter(backend_selector.options.values()), "torch_surrogate")
        _refresh_canvas(graph_json_pane, canvas, event.new)
        command_log.object = f"Preset sélectionné: {event.new}"

    def on_run(_event: Any) -> None:
        graph = _build_graph_for_preset(preset_selector.value)
        features = _parse_features(features_input.value)
        if features is None:
            command_log.object = "Features JSON invalide: fournir un objet {'node_id': float}"
            return
        result = execute_network(graph=graph, input_features=features, backend=backend_selector.value)
        graph_json_pane.object = json.loads(serialize_graph(graph))
        canvas.object = _render_canvas(graph, result.outputs)
        inspector.object = {
            "status": result.status,
            "backend": result.backend,
            "family": result.family,
            "warnings": list(result.warnings),
            "errors": list(result.errors),
        }
        command_log.object = f"Execution: {result.status} ({result.backend})"

    preset_selector.param.watch(on_preset_change, "value")
    run_button.on_click(on_run)

    return pn.Card(
        pn.Row(
            pn.Column(
                pn.pane.Markdown("### Palette"),
                palette,
                pn.Spacer(height=8),
                preset_selector,
                backend_selector,
                features_input,
                run_button,
                command_log,
                width=320,
                css_classes=["network-canvas-controls"],
            ),
            pn.Column(
                pn.pane.Markdown("### Canvas"),
                canvas,
                pn.pane.Markdown("### Inspector"),
                inspector,
                graph_json_pane,
            ),
            sizing_mode="stretch_width",
            css_classes=["network-designer-layout"],
        ),
        title="Network Designer (canvas scaffold)",
        collapsed=False,
        css_classes=["operator-card"],
    )


def _available_backends(family: str) -> Dict[str, str]:
    backends = list_available_backends(family)
    options: Dict[str, str] = {}
    for backend in backends:
        options[f"{backend['name']} ({backend.get('label', backend['name'])})"] = backend["name"]
    return options


def _preset_family(preset_id: str) -> str:
    for preset in list_presets():
        if preset.preset_id == preset_id:
            return preset.family.value
    raise KeyError(f"Preset not found: {preset_id}")


def _build_graph_for_preset(preset_id: str) -> NetworkGraph:
    for preset in list_presets():
        if preset.preset_id == preset_id:
            return build_graph(preset.family)
    raise KeyError(f"Preset not found: {preset_id}")


def _parse_features(raw: str) -> Dict[str, float] | None:
    try:
        payload = json.loads((raw or "{}").strip() or "{}")
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    values: Dict[str, float] = {}
    for key, value in payload.items():
        if isinstance(value, (int, float)):
            values[str(key)] = float(value)
    return values


def _refresh_canvas(graph_json_pane: pn.pane.JSON, canvas: pn.pane.HTML, preset_id: str) -> None:
    graph = _build_graph_for_preset(preset_id)
    graph_json = json.loads(serialize_graph(graph))
    graph_json_pane.object = graph_json
    canvas.object = _render_canvas(graph, {})


def _render_canvas(graph: NetworkGraph, outputs: Dict[str, float]) -> str:
    lines: List[str] = ['<div class="fnp-network-canvas">']
    for node in graph.nodes.values():
        value = outputs.get(node.node_id, None)
        value_text = "n/a" if value is None else f"{float(value):.6f}"
        lines.append(
            f'<article class="fnp-node">'
            f'<h4>{node.label}</h4>'
            f'<p><span class="meta">id:</span> {node.node_id}</p>'
            f'<p><span class="meta">family:</span> {node.family}</p>'
            f'<p><span class="meta">type:</span> {node.node_type}</p>'
            f'<p><span class="meta">value:</span> {value_text}</p>'
            f"</article>"
        )
    lines.append("</div>")
    return "\n".join(lines)


def _empty_canvas_markup() -> str:
    return '<div class="fnp-network-canvas"><div class="placeholder">Sélectionnez un preset pour voir le graphe.</div></div>'


def _build_palette(presets: Any) -> pn.pane.HTML:
    family_buckets = {}
    for preset in presets:
        family_buckets.setdefault(preset.family.value, []).append(preset.name)
    items = []
    for family in sorted(family_buckets):
        entries = "".join(f"<li>{item}</li>" for item in family_buckets[family])
        items.append(f"<details><summary>{family}</summary><ul>{entries}</ul></details>")
    return pn.pane.HTML("<div class=\"fnp-palette\">" + "".join(items) + "</div>", height=170)


def _load_canvas_assets(canvas: pn.pane.HTML) -> None:
    css = ""
    if CANVAS_STYLE_PATH.exists():
        css = CANVAS_STYLE_PATH.read_text(encoding="utf-8")
    js = ""
    if CANVAS_SCRIPT_PATH.exists():
        js = CANVAS_SCRIPT_PATH.read_text(encoding="utf-8")
    if css or js:
        prefix = ""
        if css:
            prefix += f"<style>{css}</style>"
        if js:
            prefix += f"<script>{js}</script>"
        canvas.object = prefix + canvas.object
