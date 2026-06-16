"""HoloViz Panel dashboard for the local FNP-QNN simulator."""

from __future__ import annotations

import json
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

pn.extension("tabulator", notifications=True, sizing_mode="stretch_width")

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

    run_button = pn.widgets.Button(label="Run simulation", color="primary")
    encode_button = pn.widgets.Button(label="Encode only", color="success")
    legacy_button = pn.widgets.Button(label="Legacy demo", color="light")
    reset_button = pn.widgets.Button(label="Reset demo", color="light")

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
            update_runtime(_runtime_result(payload, run_qnn=bool(payload.get("run_qnn"))))
            command_output.object = "Simulation complete."
        except Exception as exc:  # pragma: no cover - UI safety path
            command_output.object = f"Simulation failed: `{exc}`"

    def on_encode(_event: Any) -> None:
        try:
            payload = current_payload()
            observations = payload.get("memories") or payload.get("observations") or build_demo_observations()
            encoded = _encode_observations(observations)
            raw_json_pane.object = encoded
            command_output.object = "Payload encoded without runtime/QNN execution."
        except Exception as exc:  # pragma: no cover - UI safety path
            command_output.object = f"Encode failed: `{exc}`"

    def on_legacy(_event: Any) -> None:
        try:
            update_runtime(_legacy_runtime_result())
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

    controls = pn.Card(
        label_input,
        epochs_input,
        run_qnn_input,
        reset_button,
        payload_editor,
        pn.Row(run_button, encode_button, legacy_button),
        title="Payload builder",
        collapsed=False,
    )

    template = pn.template.FastListTemplate(
        title="FNP-QNN HoloViz Panel",
        sidebar=[status_pane, controls, pn.Card(command_output, title="Command output")],
        main=[
            pn.Row(summary_pane),
            pn.Tabs(
                ("Events", events_table),
                ("Pairs", pairs_table),
                ("QNN benchmark", benchmark_table),
                ("Raw JSON", raw_json_pane),
                dynamic=True,
            ),
        ],
        accent_base_color="#2f6f9f",
        header_background="#102033",
    )
    return template


app = create_app()
app.servable()
