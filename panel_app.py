"""HoloViz Panel dashboard for the local FNP-QNN simulator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

import pandas as pd
import panel as pn

from api.main import (
    _encode_observations,
    _legacy_runtime_result,
    _runtime_result,
    build_demo_observations,
    cerebrum_runtime_bridge,
    phi_engine,
    qnn_nucleus,
)

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


def _brand_hero() -> pn.Row:
    return pn.Row(
        pn.pane.Image(str(LOGO_UI_ASSET), height=190, sizing_mode="fixed", css_classes=["hero-logo"]),
        pn.Column(
            pn.pane.HTML(
                """
                <div class="hero-copy">
                  <div class="brand-kicker">simulatez - comprenez - innovez</div>
                  <h2>FNP-QNN Quantum Simulator</h2>
                  <p>
                    A vibrant local research control room for Cerebrum-style memory streams,
                    LVFM graph signals, and QNN smoke paths. Built for exploration, bounded
                    for non-clinical research.
                  </p>
                </div>
                """,
                sizing_mode="stretch_width",
            ),
            sizing_mode="stretch_width",
        ),
        pn.pane.Image(str(STENCIL_MAIN_ASSET), height=190, sizing_mode="fixed", css_classes=["hero-vector"]),
        css_classes=["brand-hero"],
        sizing_mode="stretch_width",
    )


def _asset_strip() -> pn.Row:
    return pn.Row(
        pn.Column(
            pn.pane.Image(str(MURAL_UI_ASSET), height=190, sizing_mode="stretch_width"),
            pn.pane.Markdown("### Street-lab identity\nHigh-energy research mural for first impression."),
            css_classes=["brand-card"],
            sizing_mode="stretch_width",
        ),
        pn.Column(
            pn.pane.Image(str(STENCIL_MAIN_ASSET), height=190, sizing_mode="stretch_width"),
            pn.pane.Markdown("### Qubit stencil\nNotebook-style mascot for the research identity."),
            css_classes=["brand-card"],
            sizing_mode="stretch_width",
        ),
        pn.Column(
            pn.pane.Image(str(STENCIL_AVATAR_STRIP_ASSET), height=190, sizing_mode="stretch_width"),
            pn.pane.Markdown("### Expressions\nMascot states for future onboarding and feedback."),
            css_classes=["brand-card"],
            sizing_mode="stretch_width",
        ),
        pn.Column(
            pn.pane.Image(str(MUG_UI_ASSET), height=190, sizing_mode="stretch_width"),
            pn.pane.Markdown("### Product palette\nBlue, green, orange, navy, and clean white."),
            css_classes=["brand-card"],
            sizing_mode="stretch_width",
        ),
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


def run_panel_simulation(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _runtime_result(payload, run_qnn=bool(payload.get("run_qnn")))


def encode_panel_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    observations = payload.get("memories") or payload.get("observations") or build_demo_observations()
    return _encode_observations(observations)


def legacy_panel_replay() -> Dict[str, Any]:
    return _legacy_runtime_result()


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

    status_pane = pn.pane.Markdown(_status_markdown())
    summary_pane = pn.pane.Markdown("### Latest run\nRun the simulator to populate this panel.")
    raw_json_pane = pn.pane.JSON({}, depth=3, name="Raw result")
    command_output = pn.pane.Markdown("Ready.")

    events_table = pn.widgets.Tabulator(_events_frame({}), height=260, pagination="remote", page_size=8)
    pairs_table = pn.widgets.Tabulator(_pairs_frame({}), height=260, pagination="remote", page_size=8)
    benchmark_table = pn.widgets.Tabulator(_benchmark_frame({}), height=260, pagination="remote", page_size=8)

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

    run_button.on_click(on_run)
    encode_button.on_click(on_encode)
    legacy_button.on_click(on_legacy)
    reset_button.on_click(on_reset)

    action_tiles = pn.Row(
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
        sizing_mode="stretch_width",
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

    template = pn.template.FastListTemplate(
        title="FNP-QNN Control Room",
        site="SeCuReDMe",
        logo=str(ATOM_ASSET),
        sidebar=[
            status_pane,
            pn.pane.Image(str(STENCIL_GUIDE_ASSET), height=150),
            pn.pane.Image(str(SHIRT_UI_ASSET), height=170),
            controls,
            pn.Card(command_output, title="Command output"),
        ],
        main=[
            _brand_hero(),
            _vector_dock(),
            action_tiles,
            pn.Row(summary_pane, css_classes=["brand-card"]),
            pn.Tabs(
                ("Events", events_table),
                ("Pairs", pairs_table),
                ("QNN benchmark", benchmark_table),
                ("Raw JSON", raw_json_pane),
                dynamic=True,
            ),
            _asset_strip(),
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
