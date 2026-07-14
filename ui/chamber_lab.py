"""Panel controls for the local, Synthia-gated Three.js chamber viewer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import panel as pn
import param

from core.chamber_lab import ChamberLabError, build_chamber_scene, list_chamber_presets


ROOT_DIR = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT_DIR / "web" / "chamber_lab"
STYLE_PATH = ASSET_DIR / "chamber_lab.css"


class ChamberViewer(pn.reactive.ReactiveHTML):
    """Shadow-DOM-safe Three.js viewer driven by an admitted scene contract."""

    scene = param.Dict(default={})

    _template = '<div id="stage" class="fnp-chamber-stage" role="img" aria-label="Interactive FNP-QNN chamber visualization"></div>'
    _scripts = {
        "render": """
            if (!data.scene || !data.scene.display_style) {
              stage.innerHTML = '<div class="fnp-chamber-empty">No chamber is rendered until Synthia accepts the supplied packet.</div>';
              return;
            }
            import('/web/chamber_lab/chamber_lab.js').then(() => {
              window.fnpChamberRender(stage, data.scene);
            }).catch(() => {
              stage.innerHTML = '<div class="fnp-chamber-empty">Local Three.js renderer unavailable.</div>';
            });
        """,
        "scene": "self.render()",
    }


def build_chamber_lab_panel() -> pn.Card:
    """Build one chamber editor; it never uses a scene before Synthia accepts it."""

    preset_options = {item["label"]: item["preset_id"] for item in list_chamber_presets()}
    preset = pn.widgets.Select(label="Preset", options=preset_options, value="neutrino_chamber")
    admission_input = pn.widgets.TextAreaInput(
        label="Synthia admission packet JSON",
        value="{}",
        min_height=130,
        placeholder="Paste the admitted LexPacket_neutrino here.",
    )
    carriers_input = pn.widgets.TextAreaInput(
        label="Ten carrier variables JSON",
        value="[]",
        min_height=175,
        placeholder='[{"name":"I_source", "tension":0.2, "weight":1, "role":"...", "source_fields":["..."], "TIF":{"T":0.8,"I":0.2,"F":0}}]',
    )
    color = pn.widgets.ColorPicker(label="Color", value="#55d9ff")
    roughness = pn.widgets.FloatSlider(label="Roughness", value=0.24, start=0.02, end=1.0, step=0.01)
    metallic = pn.widgets.FloatSlider(label="Metallic", value=0.18, start=0.0, end=1.0, step=0.01)
    translucency = pn.widgets.FloatSlider(label="Translucency", value=0.55, start=0.0, end=0.95, step=0.01)
    pattern_scale = pn.widgets.FloatSlider(label="Pattern scale", value=1.0, start=0.25, end=4.0, step=0.01)
    light_intensity = pn.widgets.FloatSlider(label="Key light", value=1.1, start=0.1, end=3.0, step=0.01)
    environment = pn.widgets.Select(label="Environment", options=["deep-space", "warm-studio", "cool-lab"], value="deep-space")
    build_button = pn.widgets.Button(label="Validate with Synthia & create chamber", color="primary", sizing_mode="stretch_width")
    status = pn.pane.Markdown("Paste an admitted Synthia packet and all ten carrier variables to create a chamber.")
    output = ChamberViewer(
        scene={},
        height=500,
        sizing_mode="stretch_width",
        stylesheets=[STYLE_PATH.read_text(encoding="utf-8")],
    )
    inspection = pn.pane.JSON({}, depth=2, height=220, sizing_mode="stretch_width")
    state: dict[str, Any] = {"admission": None, "carriers": None, "result": None}

    def style_values() -> dict[str, Any]:
        return {
            "color": color.value,
            "roughness": roughness.value,
            "metallic": metallic.value,
            "translucency": translucency.value,
            "pattern_scale": pattern_scale.value,
            "light_intensity": light_intensity.value,
            "environment": environment.value,
        }

    def render() -> None:
        if state["admission"] is None or state["carriers"] is None:
            return
        try:
            result = build_chamber_scene(state["admission"], state["carriers"], preset.value, style_values())
        except ChamberLabError as exc:
            status.object = f"**Chamber input rejected:** `{exc.code}`"
            return
        state["result"] = result
        inspection.object = result
        if result["status"] != "accepted":
            status.object = "**Chamber refused.** Synthia has not admitted this packet; the visualizer remains disabled."
            output.scene = {}
            return
        status.object = "**Chamber admitted by Synthia.** Orbit to inspect; hold Shift while dragging to move the key light."
        output.scene = result["scene"]

    def on_build(_event: Any) -> None:
        try:
            admission = json.loads(admission_input.value.strip() or "{}")
            carriers = json.loads(carriers_input.value.strip() or "[]")
        except json.JSONDecodeError as exc:
            status.object = f"**Invalid JSON:** `{exc.msg}`"
            return
        if not isinstance(admission, dict) or not isinstance(carriers, list):
            status.object = "**Invalid chamber data:** admission must be an object and carriers must be a list."
            return
        state["admission"] = admission
        state["carriers"] = carriers
        render()

    for widget in (preset, color, roughness, metallic, translucency, pattern_scale, light_intensity, environment):
        widget.param.watch(lambda _event: render(), "value")
    build_button.on_click(on_build)

    controls = pn.Column(
        pn.pane.Markdown("### Chamber configuration\nExactly ten semantic variables configure one chamber; they are not ten objects."),
        preset,
        pn.Row(color, environment),
        roughness,
        metallic,
        translucency,
        pattern_scale,
        light_intensity,
        build_button,
        sizing_mode="stretch_width",
    )
    intake = pn.Column(admission_input, carriers_input, sizing_mode="stretch_width")
    return pn.Card(
        pn.Row(pn.Column(controls, intake, width=420), pn.Column(status, output, inspection, sizing_mode="stretch_width"), sizing_mode="stretch_width"),
        title="Synthia-gated Chamber Lab · Three.js local",
        collapsed=False,
        sizing_mode="stretch_width",
    )
