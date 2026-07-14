"""HoloViz Panel dashboard for the local FNP-QNN simulator."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

import pandas as pd
import panel as pn
from ui.chamber_lab import build_chamber_lab_panel
from ui.network_canvas import build_network_designer_canvas

from api.main import (
    _encode_observations,
    _legacy_runtime_result,
    _runtime_result,
    build_demo_observations,
    cerebrum_runtime_bridge,
    phi_engine,
    qnn_nucleus,
)
from core import NeuroBitProfile, run_neurobit_gates, run_neurobit_tunnel_demo
from core.network_designer import build_graph, execute_network, list_available_backends, list_presets, serialize_graph

PROJECT_ROOT = Path(__file__).resolve().parent
ASSET_DIR = PROJECT_ROOT / "assets"
GENERATED_ASSET_DIR = ASSET_DIR / "generated"
LOGO_ASSET = ASSET_DIR / "logo1.png"
LOGO_UI_ASSET = GENERATED_ASSET_DIR / "logo-ui-thumb.png"
MASCOT_ASSET = ASSET_DIR / "mascoote qbit.png"
STENCIL_ASSET = ASSET_DIR / "qbits stancil.png"
STENCIL_UI_ASSET = GENERATED_ASSET_DIR / "qbit-stencil-ui-thumb.png"
STENCIL_MAIN_ASSET = GENERATED_ASSET_DIR / "qbit-stencil-main.png"
STENCIL_LAB_ASSET = GENERATED_ASSET_DIR / "qbit-stencil-lab.png"
STENCIL_ORBIT_ASSET = GENERATED_ASSET_DIR / "qbit-stencil-orbit.png"
STENCIL_GUIDE_ASSET = GENERATED_ASSET_DIR / "qbit-stencil-guide.png"
STENCIL_AVATAR_STRIP_ASSET = GENERATED_ASSET_DIR / "qbit-stencil-avatar-strip.png"
ATOM_ASSET = GENERATED_ASSET_DIR / "atom-normalized-dark.png"
ATOM_BACK_LOGO_ASSET = GENERATED_ASSET_DIR / "atom-back-logo-dark.png"
VECTOR_BRAIN_NETWORK_ASSET = GENERATED_ASSET_DIR / "vector-01-brain-network.png"
VECTOR_ORBIT_HEAD_ASSET = GENERATED_ASSET_DIR / "vector-02-orbit-head.png"
VECTOR_CIRCUIT_BRAIN_ASSET = GENERATED_ASSET_DIR / "vector-03-circuit-brain.png"
VECTOR_WAVE_BRAIN_ASSET = GENERATED_ASSET_DIR / "vector-04-wave-brain.png"
VECTOR_CUBE_RESEARCH_ASSET = GENERATED_ASSET_DIR / "vector-05-cube-research.png"
MURAL_ASSET = ASSET_DIR / "mural fnp-qnn.png"
MURAL_UI_ASSET = GENERATED_ASSET_DIR / "mural-ui-thumb.png"
VECTOR_ASSET = ASSET_DIR / "vector template.png"
MUG_ASSET = ASSET_DIR / "template tasse bleu.png"
MUG_UI_ASSET = GENERATED_ASSET_DIR / "mug-blue-ui-thumb.png"
SHIRT_ASSET = ASSET_DIR / "tshirt vert template.png"
SHIRT_UI_ASSET = GENERATED_ASSET_DIR / "shirt-green-ui-thumb.png"

_NETWORK_PRESET_LIST = tuple(list_presets())
NETWORK_PRESETS = {preset.preset_id: preset for preset in _NETWORK_PRESET_LIST}
NETWORK_PRESET_OPTIONS = {
    f"{preset.family.value}: {preset.name}": preset.preset_id
    for preset in sorted(_NETWORK_PRESET_LIST, key=lambda p: p.preset_id)
}

BRAND_CSS = """
:root {
  --fnp-navy: #0d183d;
  --fnp-blue: #1e3aba;
  --fnp-cyan: #55d9ff;
  --fnp-green: #36837e;
  --fnp-orange: #fdaa37;
  --fnp-paper: #f2f6fa;
  --fnp-ink: #081225;
}

body {
  background:
    radial-gradient(circle at 12% 4%, rgba(85, 217, 255, 0.18), transparent 26rem),
    radial-gradient(circle at 88% 7%, rgba(253, 170, 55, 0.16), transparent 22rem),
    linear-gradient(180deg, #071025 0%, #f2f6fa 34%, #edf4fb 100%) !important;
}

.bk-FastListTemplate {
  --design-primary-color: var(--fnp-blue);
}

#header {
  background: linear-gradient(90deg, #071025 0%, #0d183d 48%, #12356f 100%) !important;
  border-bottom: 3px solid var(--fnp-orange);
  box-shadow: 0 12px 34px rgba(8, 18, 37, 0.25);
}

#sidebar {
  background:
    linear-gradient(180deg, rgba(13, 24, 61, 0.98), rgba(12, 32, 62, 0.96)) !important;
  border-right: 1px solid rgba(85, 217, 255, 0.24);
}

#sidebar h3,
#sidebar p,
#sidebar li,
#sidebar strong,
#sidebar code {
  color: #f2f6fa !important;
}

#sidebar code {
  background: rgba(85, 217, 255, 0.14);
  border: 1px solid rgba(85, 217, 255, 0.25);
  border-radius: 6px;
  padding: 2px 6px;
}

.brand-hero {
  border: 1px solid rgba(85, 217, 255, 0.28);
  border-radius: 18px;
  overflow: hidden;
  background:
    linear-gradient(135deg, rgba(13, 24, 61, 0.94), rgba(30, 58, 186, 0.82)),
    linear-gradient(90deg, rgba(253, 170, 55, 0.22), transparent);
  box-shadow: 0 22px 60px rgba(13, 24, 61, 0.22);
}

.hero-copy {
  color: #f2f6fa;
  padding: 24px 18px 18px 6px;
}

.hero-copy h2 {
  color: #ffffff;
  font-size: 2.0rem;
  line-height: 1.05;
  margin: 0 0 10px;
}

.hero-copy p {
  color: rgba(242, 246, 250, 0.84);
  font-size: 1rem;
}

.hero-logo,
.hero-vector {
  padding: 12px;
  margin: 12px;
  border-radius: 22px;
  background:
    linear-gradient(#f2f6fa, #f2f6fa) padding-box,
    linear-gradient(135deg, var(--fnp-cyan), var(--fnp-orange), var(--fnp-green)) border-box;
  border: 2px solid transparent;
  box-shadow: 0 16px 36px rgba(8, 18, 37, 0.32);
}

.hero-vector {
  background:
    linear-gradient(180deg, rgba(242, 246, 250, 0.94), rgba(255, 255, 255, 0.86)) padding-box,
    linear-gradient(135deg, rgba(253, 170, 55, 0.95), rgba(85, 217, 255, 0.95)) border-box;
}

.brand-kicker {
  color: var(--fnp-orange);
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.app-tile {
  border: 1px solid rgba(85, 217, 255, 0.28);
  border-radius: 18px;
  padding: 12px;
  background:
    radial-gradient(circle at 14% 14%, rgba(85, 217, 255, 0.22), transparent 7rem),
    linear-gradient(145deg, rgba(13, 24, 61, 0.98), rgba(19, 53, 111, 0.96));
  box-shadow: 0 16px 34px rgba(8, 18, 37, 0.22);
}

.app-tile h3 {
  color: #ffffff;
  margin: 0;
}

.app-tile p {
  color: rgba(242, 246, 250, 0.78);
  margin: 4px 0 10px;
}

.app-tile button {
  min-height: 44px;
  border-radius: 14px !important;
  font-weight: 800 !important;
  letter-spacing: 0.02em;
}

.atom-badge {
  display: grid;
  place-items: center;
  width: fit-content;
  margin: 0 auto 8px;
  padding: 8px;
  border-radius: 22px;
  background:
    radial-gradient(circle at 22% 18%, rgba(85, 217, 255, 0.28), transparent 4rem),
    linear-gradient(145deg, #071025, #0d183d);
  border: 2px solid rgba(253, 170, 55, 0.82);
  box-shadow:
    0 16px 30px rgba(8, 18, 37, 0.30),
    inset 0 0 0 1px rgba(255, 255, 255, 0.12);
}

.atom-badge img,
.atom-badge canvas {
  border-radius: 16px;
}

.brand-card img,
.brand-card canvas {
  border-radius: 14px;
  border: 1px solid rgba(13, 24, 61, 0.14);
  box-shadow: 0 10px 26px rgba(8, 18, 37, 0.12);
}

.vector-dock {
  gap: 14px;
}

.vector-card {
  border-radius: 18px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.90);
  border: 2px solid rgba(13, 24, 61, 0.10);
  box-shadow: 0 12px 28px rgba(13, 24, 61, 0.12);
}

.vector-card h3 {
  margin: 4px 0 0;
  color: var(--fnp-navy);
  font-size: 1rem;
}

.vector-card p {
  margin: 2px 0 0;
  color: #465571;
  font-size: 0.84rem;
}

.vector-card img,
.vector-card canvas {
  border-radius: 16px;
  padding: 8px;
  background: #ffffff;
}

.vector-blue {
  border-color: rgba(30, 58, 186, 0.72);
}

.vector-green {
  border-color: rgba(54, 131, 126, 0.78);
}

.vector-orange {
  border-color: rgba(253, 170, 55, 0.88);
}

.vector-navy {
  border-color: rgba(13, 24, 61, 0.82);
}

.vector-cyan {
  border-color: rgba(85, 217, 255, 0.86);
}

.tile-run button {
  background: linear-gradient(90deg, var(--fnp-blue), #16a7d8) !important;
}

.tile-encode button {
  background: linear-gradient(90deg, var(--fnp-green), #1aa86f) !important;
}

.tile-legacy button {
  background: linear-gradient(90deg, var(--fnp-orange), #ff6f1d) !important;
  color: #081225 !important;
}

.brand-card {
  border-radius: 18px;
  border: 1px solid rgba(13, 24, 61, 0.12);
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 12px 32px rgba(13, 24, 61, 0.11);
  overflow: hidden;
}

.brand-card h3 {
  color: var(--fnp-navy);
}

.brand-card p,
.brand-card li {
  color: #24324f;
}

.bk-card {
  border-radius: 16px !important;
}

.tabulator {
  border-radius: 14px;
  border: 1px solid rgba(13, 24, 61, 0.10);
}

.operator-card {
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(13, 24, 61, 0.12);
  box-shadow: 0 10px 28px rgba(13, 24, 61, 0.10);
}

.signal-card {
  border-radius: 18px;
  background:
    radial-gradient(circle at 16% 12%, rgba(85, 217, 255, 0.20), transparent 7rem),
    linear-gradient(145deg, rgba(13, 24, 61, 0.98), rgba(19, 53, 111, 0.96));
  border: 1px solid rgba(85, 217, 255, 0.28);
  box-shadow: 0 16px 34px rgba(8, 18, 37, 0.22);
}

.boundary-card {
  border-radius: 14px;
  background: rgba(253, 170, 55, 0.12);
  border: 1px solid rgba(253, 170, 55, 0.46);
  color: var(--fnp-ink);
}

.visual-guide-card {
  border-radius: 14px;
  border: 1px solid rgba(13, 24, 61, 0.12);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 12px 24px rgba(13, 24, 61, 0.09);
}

.network-card {
  border-radius: 16px;
  background: rgba(13, 24, 61, 0.04);
  border: 1px solid rgba(13, 24, 61, 0.12);
}
"""

pn.extension("tabulator", notifications=True, sizing_mode="stretch_width", raw_css=[BRAND_CSS])

DEFAULT_PAYLOAD: Dict[str, Any] = {
    "label": 1,
    "epochs": 12,
    "run_qnn": True,
    "memories": [
        {
            "modality": "audio",
            "starting_time": 0.0,
            "ending_time": 1.4,
            "value": 0.73,
            "label": "rhythm",
            "source": "panel-demo",
            "payload_ref": "audio-001",
        },
        {
            "modality": "video",
            "starting_time": 0.8,
            "ending_time": 2.2,
            "value": 0.61,
            "label": "motion",
            "source": "panel-demo",
            "payload_ref": "video-001",
        },
        {
            "modality": "text",
            "starting_time": 1.6,
            "ending_time": 2.9,
            "value": 0.54,
            "label": "caption",
            "source": "panel-demo",
            "payload_ref": "text-001",
        },
        {
            "modality": "stimuli",
            "starting_time": 2.4,
            "ending_time": 3.0,
            "value": 0.82,
            "label": "trigger",
            "source": "panel-demo",
            "payload_ref": "stimuli-001",
        },
    ],
}


def _pretty(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def _table(rows: Iterable[Dict[str, Any]], columns: List[str]) -> pd.DataFrame:
    frame = pd.DataFrame(list(rows))
    if frame.empty:
        return pd.DataFrame(columns=columns)
    return frame.reindex(columns=[column for column in columns if column in frame.columns])


def _events_frame(runtime: Dict[str, Any]) -> pd.DataFrame:
    return _table(
        runtime.get("events", []),
        ["modality", "starting_time", "ending_time", "value", "label", "source", "payload_ref"],
    )


def _pairs_frame(runtime: Dict[str, Any]) -> pd.DataFrame:
    return _table(
        runtime.get("pairs", []),
        ["direction", "timestamp1", "timestamp2", "overlap_score", "source1", "source2"],
    )


def _benchmark_frame(runtime: Dict[str, Any]) -> pd.DataFrame:
    return _table(
        runtime.get("benchmark", []),
        [
            "candidate",
            "available",
            "backend",
            "train_accuracy",
            "test_accuracy",
            "predicted_probability",
            "feature_dimension",
            "notes",
        ],
    )


def _summary(runtime: Dict[str, Any]) -> str:
    qnn = runtime.get("qnn_result") or {}
    lvfm = runtime.get("lvfm") or {}
    decision = lvfm.get("decision") or {}
    probability = qnn.get("predicted_probability")
    probability_text = "not run" if probability is None else f"{float(probability):.3f}"
    return "\n".join(
        [
            "### Latest run",
            f"- Events: **{len(runtime.get('events', []))}**",
            f"- Crossmodal pairs: **{len(runtime.get('pairs', []))}**",
            f"- Feature dimension: **{runtime.get('feature_dimension', 0)}**",
            f"- QNN backend: **{qnn.get('backend', 'not run')}**",
            f"- Predicted probability: **{probability_text}**",
            f"- LVFM gate: **{decision.get('label', 'not evaluated')}**",
        ]
    )


def _status_markdown() -> str:
    status = cerebrum_runtime_bridge.status(qnn_nucleus=qnn_nucleus)
    candidates = ", ".join(candidate.name for candidate in qnn_nucleus.candidate_matrix())
    return "\n".join(
        [
            "### Runtime status",
            f"- API: **healthy**",
            f"- Runtime bridge: **{status.get('bridge', 'unknown')}**",
            f"- QNN backend: **{status.get('qnn_backend', 'unknown')}**",
            f"- Golden ratio: **{phi_engine.phi:.12f}**",
            f"- Candidates: `{candidates}`",
            "",
            "Research boundary: alpha-local, non-clinical simulator. Not diagnostic, therapeutic, safety, emergency, or production-public software.",
        ]
    )


def _compact_hero_status() -> pn.Row:
    return pn.Row(
        pn.pane.Markdown("## FNP-QNN Control Room"),
        pn.pane.Image(str(ATOM_ASSET), height=54, width=54, css_classes=["atom-badge"]),
        pn.pane.Markdown(
            """
            Local alpha research simulator for memory-event streams, feature encoding,
            deterministic fallback execution, optional quantum lane previews, and evidence
            inspection.  
            Boundary: non-clinical, non-diagnostic, non-therapeutic, and non-production-public.
            """,
            css_classes=["hero-copy"],
            width=900,
        ),
        css_classes=["operator-card"],
        sizing_mode="stretch_width",
    )


def _small_visual_guide() -> pn.Column:
    return pn.Column(
        pn.pane.Markdown("### Visual guide"),
        pn.pane.Image(str(STENCIL_GUIDE_ASSET), height=126, width=126, css_classes=["atom-badge"]),
        pn.pane.Markdown(
            "- Build inputs in the payload builder.\n"
            "- Run simulation, inspect tables, and verify raw JSON.\n"
            "- Use Network Designer section for contract previews."
        ),
        css_classes=["visual-guide-card"],
        sizing_mode="stretch_width",
    )


def _operator_action_grid(
    run_button: pn.widgets.Button,
    encode_button: pn.widgets.Button,
    legacy_button: pn.widgets.Button,
    neurobit_gates_button: pn.widgets.Button,
    neurobit_tunnel_button: pn.widgets.Button,
    network_designer_button: pn.widgets.Button,
    network_export_button: pn.widgets.Button,
) -> pn.Row:
    return pn.Row(
        pn.Column(
            pn.pane.Image(str(VECTOR_ORBIT_HEAD_ASSET), height=74, align="center", css_classes=["atom-badge"]),
            pn.pane.HTML("<h3>Run</h3><p>Build stream, graph state, QNN smoke and benchmark.</p>"),
            run_button,
            css_classes=["app-tile", "tile-run"],
            sizing_mode="stretch_width",
        ),
        pn.Column(
            pn.pane.Image(str(VECTOR_BRAIN_NETWORK_ASSET), height=74, align="center", css_classes=["atom-badge"]),
            pn.pane.HTML("<h3>Encode</h3><p>Convert memory observations into feature vectors.</p>"),
            encode_button,
            css_classes=["app-tile", "tile-encode"],
            sizing_mode="stretch_width",
        ),
        pn.Column(
            pn.pane.Image(str(VECTOR_CUBE_RESEARCH_ASSET), height=74, align="center", css_classes=["atom-badge"]),
            pn.pane.HTML("<h3>Legacy</h3><p>Replay the bundled Cerebrum fixture safely.</p>"),
            legacy_button,
            css_classes=["app-tile", "tile-legacy"],
            sizing_mode="stretch_width",
        ),
        pn.Column(
            pn.pane.Image(str(VECTOR_CIRCUIT_BRAIN_ASSET), height=74, align="center", css_classes=["atom-badge"]),
            pn.pane.HTML("<h3>NeuroBit</h3><p>Run H/W/X/Y/Z gates and tunnel noise.</p>"),
            neurobit_gates_button,
            neurobit_tunnel_button,
            css_classes=["app-tile", "tile-run"],
            sizing_mode="stretch_width",
        ),
        pn.Column(
            pn.pane.Image(str(VECTOR_CUBE_RESEARCH_ASSET), height=74, align="center", css_classes=["atom-badge"]),
            pn.pane.HTML("<h3>Network Designer</h3><p>Open the graph preset execution panel below.</p>"),
            network_designer_button,
            css_classes=["app-tile"],
            sizing_mode="stretch_width",
        ),
        pn.Column(
            pn.pane.Image(str(VECTOR_WAVE_BRAIN_ASSET), height=74, align="center", css_classes=["atom-badge"]),
            pn.pane.HTML("<h3>Export Evidence</h3><p>Prepare structured run output for institutional review.</p>"),
            network_export_button,
            css_classes=["app-tile", "tile-encode"],
            sizing_mode="stretch_width",
        ),
        sizing_mode="stretch_width",
    )


def _latest_run_overview(summary_pane: pn.pane.Markdown) -> pn.Row:
    return pn.Row(summary_pane, css_classes=["operator-card"])


def _evidence_tabs(
    events_table: pn.widgets.Tabulator,
    pairs_table: pn.widgets.Tabulator,
    benchmark_table: pn.widgets.Tabulator,
    neurobit_json_pane: pn.pane.JSON,
    raw_json_pane: pn.pane.JSON,
    network_output: pn.Card,
    network_canvas_panel: pn.Column,
    chamber_lab_panel: pn.Card,
) -> pn.Tabs:
    return pn.Tabs(
        ("Events", events_table),
        ("Pairs", pairs_table),
        ("QNN benchmark", benchmark_table),
        ("NeuroBit", neurobit_json_pane),
        ("Raw JSON", raw_json_pane),
        ("Network Designer", network_output),
        ("Network Designer Canvas", network_canvas_panel),
        ("Chamber Lab", chamber_lab_panel),
        dynamic=True,
    )


def _collapsed_brand_assets() -> pn.Card:
    return pn.Card(_brand_gallery(), title="Brand / Visual Identity", collapsed=True)


def _brand_gallery() -> pn.Row:
    return pn.Row(
        pn.Card(pn.pane.Image(str(MURAL_UI_ASSET), height=170), sizing_mode="stretch_both"),
        pn.Card(pn.pane.Image(str(STENCIL_AVATAR_STRIP_ASSET), height=170), sizing_mode="stretch_both"),
        pn.Card(pn.pane.Image(str(MUG_UI_ASSET), height=170), sizing_mode="stretch_both"),
        sizing_mode="stretch_width",
    )


def _vector_dock() -> pn.Row:
    items = [
        ("Stream", "memory graph", VECTOR_BRAIN_NETWORK_ASSET, "vector-blue"),
        ("Orbit", "QNN candidate", VECTOR_ORBIT_HEAD_ASSET, "vector-cyan"),
        ("Circuit", "signal logic", VECTOR_CIRCUIT_BRAIN_ASSET, "vector-orange"),
        ("Wave", "runtime pulse", VECTOR_WAVE_BRAIN_ASSET, "vector-green"),
        ("Cube", "research core", VECTOR_CUBE_RESEARCH_ASSET, "vector-navy"),
    ]
    return pn.Row(
        *[
            pn.Column(
                pn.pane.Image(str(asset), height=92, align="center"),
                pn.pane.HTML(f"<h3>{title}</h3><p>{subtitle}</p>"),
                css_classes=["vector-card", tone],
                sizing_mode="stretch_width",
            )
            for title, subtitle, asset, tone in items
        ],
        css_classes=["vector-dock"],
        sizing_mode="stretch_width",
    )


def _network_backend_options(preset_id: str) -> Dict[str, str]:
    preset = NETWORK_PRESETS[preset_id]
    options: Dict[str, str] = {}
    for backend in list_available_backends(preset.family.value):
        label = f"{backend['name']}: {backend['label']}"
        if not backend["available"]:
            label += " (unavailable)"
        options[label] = backend["name"]
    return options


def _parse_network_features(value: str) -> Dict[str, Any] | list[float] | None:
    value = value.strip()
    if not value:
        return None
    raw = json.loads(value)
    if isinstance(raw, dict):
        return {str(key): float(v) for key, v in raw.items() if isinstance(v, (int, float))}
    if isinstance(raw, list):
        return [float(item) for item in raw if isinstance(item, (int, float))]
    raise ValueError("network input must be a JSON object or array of numbers")


def _network_execution_payload(graph_preset_id: str) -> Dict[str, Any]:
    graph = build_graph(NETWORK_PRESETS[graph_preset_id].family)
    return {"graph": graph, "graph_json": serialize_graph(graph)}


def run_panel_simulation(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _runtime_result(payload, run_qnn=bool(payload.get("run_qnn")))


def encode_panel_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    observations = payload.get("memories") or payload.get("observations") or build_demo_observations()
    return _encode_observations(observations)


def legacy_panel_replay() -> Dict[str, Any]:
    return _legacy_runtime_result()


def run_panel_neurobit_gates(profile: Dict[str, float]) -> Dict[str, Any]:
    return run_neurobit_gates(
        NeuroBitProfile(
            truth=float(profile.get("truth", 0.55)),
            indeterminacy=float(profile.get("indeterminacy", 0.30)),
            falsity=float(profile.get("falsity", 0.15)),
            delta_falsity=float(profile.get("delta_falsity", profile.get("dF", 0.0))),
        )
    )


def run_panel_neurobit_tunnel(profile: Dict[str, float], data: str = "neurobit-demo") -> Dict[str, Any]:
    return run_neurobit_tunnel_demo(
        NeuroBitProfile(
            truth=float(profile.get("truth", 0.55)),
            indeterminacy=float(profile.get("indeterminacy", 0.30)),
            falsity=float(profile.get("falsity", 0.15)),
            delta_falsity=float(profile.get("delta_falsity", profile.get("dF", 0.0))),
        ),
        data=data,
    )


def create_app() -> pn.template.FastListTemplate:
    payload_editor = pn.widgets.TextAreaInput(
        label="Runtime payload JSON",
        value=_pretty(DEFAULT_PAYLOAD),
        min_height=360,
        sizing_mode="stretch_both",
    )
    label_input = pn.widgets.FloatInput(label="Label", value=1.0, start=0.0, end=1.0, step=0.05)
    epochs_input = pn.widgets.IntInput(label="Epochs", value=12, start=0, end=256, step=1)
    run_qnn_input = pn.widgets.Checkbox(label="Run QNN smoke path", value=True)

    run_button = pn.widgets.Button(label="Run simulation", color="primary", sizing_mode="stretch_width")
    encode_button = pn.widgets.Button(label="Encode only", color="success", sizing_mode="stretch_width")
    legacy_button = pn.widgets.Button(label="Legacy demo", color="light", sizing_mode="stretch_width")
    reset_button = pn.widgets.Button(label="Reset demo", color="light", sizing_mode="stretch_width")
    neurobit_gates_button = pn.widgets.Button(label="NeuroBit gates", color="primary", sizing_mode="stretch_width")
    neurobit_tunnel_button = pn.widgets.Button(label="Tunnel noise", color="warning", sizing_mode="stretch_width")
    network_designer_button = pn.widgets.Button(label="Network Designer", color="primary", sizing_mode="stretch_width")
    network_export_button = pn.widgets.Button(label="Export evidence", color="light", sizing_mode="stretch_width")

    truth_slider = pn.widgets.FloatSlider(label="Truth", value=0.55, start=0.0, end=1.0, step=0.01)
    indeterminacy_slider = pn.widgets.FloatSlider(label="Indeterminacy", value=0.30, start=0.0, end=1.0, step=0.01)
    falsity_slider = pn.widgets.FloatSlider(label="Falsity", value=0.15, start=0.0, end=1.0, step=0.01)
    delta_falsity_slider = pn.widgets.FloatSlider(label="dF", value=0.0, start=-1.0, end=1.0, step=0.01)
    tunnel_data_input = pn.widgets.TextInput(label="Tunnel demo data", value="neurobit-demo")
    network_preset_select = pn.widgets.Select(
        label="Network preset",
        options=NETWORK_PRESET_OPTIONS,
        value=next(iter(NETWORK_PRESET_OPTIONS.values())),
        width=360,
    )
    default_preset_id = network_preset_select.value
    network_backend_select = pn.widgets.Select(
        label="Execution backend",
        options=_network_backend_options(default_preset_id),
        value=next(iter(_network_backend_options(default_preset_id).values())),
        width=220,
    )
    network_inputs = pn.widgets.TextAreaInput(
        label="Network input features JSON",
        value="{}",
        min_height=120,
        sizing_mode="stretch_width",
    )
    run_network_button = pn.widgets.Button(label="Run Network Designer graph", color="primary", sizing_mode="stretch_width")

    status_pane = pn.pane.Markdown(_status_markdown())
    summary_pane = pn.pane.Markdown("### Latest run\nRun the simulator to populate this panel.")
    raw_json_pane = pn.pane.JSON({}, depth=3, name="Raw result")
    neurobit_json_pane = pn.pane.JSON({}, depth=3, name="NeuroBit result")
    command_output = pn.pane.Markdown("Ready.")

    events_table = pn.widgets.Tabulator(_events_frame({}), height=260, pagination="remote", page_size=8)
    pairs_table = pn.widgets.Tabulator(_pairs_frame({}), height=260, pagination="remote", page_size=8)
    benchmark_table = pn.widgets.Tabulator(_benchmark_frame({}), height=260, pagination="remote", page_size=8)
    network_graph_json = pn.pane.JSON({}, depth=3, name="Network graph JSON")
    network_execution_json = pn.pane.JSON({}, depth=3, name="Network execution")

    def current_payload() -> Dict[str, Any]:
        payload = json.loads(payload_editor.value.strip() or "{}")
        payload["label"] = float(label_input.value)
        payload["epochs"] = int(epochs_input.value)
        payload["run_qnn"] = bool(run_qnn_input.value)
        return payload

    def update_runtime(runtime: Dict[str, Any]) -> None:
        summary_pane.object = _summary(runtime)
        events_table.value = _events_frame(runtime)
        pairs_table.value = _pairs_frame(runtime)
        benchmark_table.value = _benchmark_frame(runtime)
        raw_json_pane.object = runtime

    def current_neurobit_profile() -> Dict[str, float]:
        return {
            "truth": float(truth_slider.value),
            "indeterminacy": float(indeterminacy_slider.value),
            "falsity": float(falsity_slider.value),
            "delta_falsity": float(delta_falsity_slider.value),
        }

    def on_run(_event: Any) -> None:
        try:
            payload = current_payload()
            update_runtime(run_panel_simulation(payload))
            command_output.object = "Simulation complete."
        except Exception as exc:  # pragma: no cover - UI safety path
            command_output.object = f"Simulation failed: `{exc}`"

    def on_encode(_event: Any) -> None:
        try:
            payload = current_payload()
            raw_json_pane.object = encode_panel_payload(payload)
            command_output.object = "Payload encoded without runtime/QNN execution."
        except Exception as exc:  # pragma: no cover - UI safety path
            command_output.object = f"Encode failed: `{exc}`"

    def on_legacy(_event: Any) -> None:
        try:
            update_runtime(legacy_panel_replay())
            command_output.object = "Legacy fixture replay complete."
        except Exception as exc:  # pragma: no cover - UI safety path
            command_output.object = f"Legacy replay failed: `{exc}`"

    def on_reset(_event: Any) -> None:
        payload_editor.value = _pretty(DEFAULT_PAYLOAD)
        label_input.value = float(DEFAULT_PAYLOAD["label"])
        epochs_input.value = int(DEFAULT_PAYLOAD["epochs"])
        run_qnn_input.value = bool(DEFAULT_PAYLOAD["run_qnn"])
        command_output.object = "Demo payload reset."

    def on_neurobit_gates(_event: Any) -> None:
        try:
            neurobit_json_pane.object = run_panel_neurobit_gates(current_neurobit_profile())
            command_output.object = "NeuroBit gates complete."
        except Exception as exc:  # pragma: no cover - UI safety path
            command_output.object = f"NeuroBit gates failed: `{exc}`"

    def on_neurobit_tunnel(_event: Any) -> None:
        try:
            neurobit_json_pane.object = run_panel_neurobit_tunnel(
                current_neurobit_profile(),
                data=tunnel_data_input.value or "neurobit-demo",
            )
            command_output.object = "NeuroBit tunnel noise demo complete."
        except Exception as exc:  # pragma: no cover - UI safety path
            command_output.object = f"NeuroBit tunnel failed: `{exc}`"

    def on_preset_change(_event: Any) -> None:
        preset_id = network_preset_select.value
        options = _network_backend_options(preset_id)
        network_backend_select.options = options
        if network_backend_select.value not in options.values():
            network_backend_select.value = next(iter(options.values()))
        graph_data = _network_execution_payload(preset_id)
        network_graph_json.object = json.loads(graph_data["graph_json"])

    def on_run_network(_event: Any) -> None:
        try:
            preset_id = network_preset_select.value
            preset = NETWORK_PRESETS[preset_id]
            graph = build_graph(preset.family)
            features = _parse_network_features(network_inputs.value)
            result = execute_network(graph, input_features=features, backend=network_backend_select.value)
            network_execution_json.object = asdict(result)
            command_output.object = f"Network Designer execution: {result.status} ({result.backend})"
        except Exception as exc:  # pragma: no cover - UI safety path
            network_execution_json.object = {"error": str(exc)}
            command_output.object = f"Network Designer failed: `{exc}`"

    def on_network_designer_focus(_event: Any) -> None:
        command_output.object = "Open the Network Designer tab in this panel to inspect preset execution."

    def on_network_export(_event: Any) -> None:
        command_output.object = "Evidence export placeholder: use terminal/export scripts to capture current JSON tabs."

    run_button.on_click(on_run)
    encode_button.on_click(on_encode)
    legacy_button.on_click(on_legacy)
    reset_button.on_click(on_reset)
    neurobit_gates_button.on_click(on_neurobit_gates)
    neurobit_tunnel_button.on_click(on_neurobit_tunnel)
    run_network_button.on_click(on_run_network)
    network_preset_select.param.watch(on_preset_change, "value")
    network_designer_button.on_click(on_network_designer_focus)
    network_export_button.on_click(on_network_export)
    on_preset_change(None)

    action_tiles = _operator_action_grid(
        run_button=run_button,
        encode_button=encode_button,
        legacy_button=legacy_button,
        neurobit_gates_button=neurobit_gates_button,
        neurobit_tunnel_button=neurobit_tunnel_button,
        network_designer_button=network_designer_button,
        network_export_button=network_export_button,
    )

    controls = pn.Card(
        label_input,
        epochs_input,
        run_qnn_input,
        reset_button,
        payload_editor,
        title="Payload builder",
        collapsed=False,
    )

    neurobit_controls = pn.Card(
        truth_slider,
        indeterminacy_slider,
        falsity_slider,
        delta_falsity_slider,
        tunnel_data_input,
        title="NeuroBit profile",
        collapsed=False,
    )

    network_controls = pn.Card(
        network_preset_select,
        network_backend_select,
        network_inputs,
        run_network_button,
        width=420,
        title="Network Designer (backend contract)",
        collapsed=False,
    )

    network_output = pn.Card(
        network_graph_json,
        network_execution_json,
        title="Network Designer output",
        collapsed=False,
        sizing_mode="stretch_width",
    )
    network_canvas_panel = build_network_designer_canvas()
    chamber_lab_panel = build_chamber_lab_panel()

    template = pn.template.FastListTemplate(
        title="FNP-QNN Control Room",
        site="SeCuReDMe",
        logo=str(ATOM_ASSET),
        sidebar=[
            status_pane,
            controls,
            pn.Card(command_output, title="Command output"),
            pn.Card(_small_visual_guide(), title="Visual guide", collapsed=True),
        ],
        main=[
            _compact_hero_status(),
            _vector_dock(),
            action_tiles,
            _latest_run_overview(summary_pane),
            pn.Row(neurobit_controls, network_controls, sizing_mode="stretch_width"),
            _evidence_tabs(
                events_table,
                pairs_table,
                benchmark_table,
                neurobit_json_pane,
                raw_json_pane,
                network_output,
                network_canvas_panel,
                chamber_lab_panel,
            ),
            _collapsed_brand_assets(),
        ],
        accent_base_color="#2f6f9f",
        header_background="#0d183d",
        background_color="#f2f6fa",
        neutral_color="#0d183d",
        main_max_width="1480px",
        sidebar_width=370,
    )
    return template


app = create_app()
app.servable()
