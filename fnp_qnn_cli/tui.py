"""Textual TUI for the FNP-QNN local research simulator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .doctor import run_doctor
from .registry import (
    HIERARCHY_BOUNDARY,
    RESEARCH_BOUNDARY,
    command_response,
    list_core_commands,
    neurobit_gates,
    qnn_smoke,
    runtime_run,
)
from core.ffed_plugin_bridge import FfeDPluginBridge


LOGO_ASSETS = {
    "main_big": "assets/logo/ASCII full logo.png",
    "top_small": "assets/logo/ASCII logo 1.png",
    "bottom_center": "assets/logo/ASCII logo 5.png",
}

FNPQNN_MAIN_TERMINAL_LOGO = r"""
+--------------------------------------------------------------+
| FNP-QNN                                      QUANTUM SIMULATOR |
| Project GWNRE                       alpha-local research TUI |
| Collider-inspired source: ASCII full logo.png                |
| Knowledge  *  Innovation  *  Collaboration                   |
+--------------------------------------------------------------+
"""

FNPQNN_TOP_TERMINAL_LOGO = r"""
FNP-QNN / Quantum Simulator
Native tools -> gateway -> LVFM
"""

FNPQNN_BOTTOM_TERMINAL_LOGO = r"""
[ FNP-QNN | inspired by cosmos | driven by science ]
"""

RETRO_82_FLASH = r"""
  FNP-QNN RETRO 82 FLASH
  ======================
  mountain lens mode  |  blue ink glass  |  gold horizon line

       /\        ____        /\
      /  \______/ 82 \______/  \
     /____\    QUANTUM     /____\
          \__ LOCAL SIM __/

  private operator egg: enabled only by hidden command
"""

BRAND_FACTS = {
    "palette_source": [
        LOGO_ASSETS["main_big"],
        LOGO_ASSETS["top_small"],
        LOGO_ASSETS["bottom_center"],
    ],
    "ink": "#001020",
    "paper": "#f4efe6",
    "quantum_blue": "#0020a0",
    "deep_navy": "#07131c",
    "neuro_gold": "#b08a3c",
    "graphite": "#101820",
    "line_gray": "#d8d2c8",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def logo_asset_path(name: str) -> Path:
    return _repo_root() / LOGO_ASSETS[name]


def main_logo_terminal() -> str:
    return FNPQNN_MAIN_TERMINAL_LOGO


def top_logo_terminal() -> str:
    return FNPQNN_TOP_TERMINAL_LOGO


def bottom_logo_terminal() -> str:
    return FNPQNN_BOTTOM_TERMINAL_LOGO


class TextualUnavailable(RuntimeError):
    """Raised when the optional Textual runtime is not installed."""


def _require_textual():
    try:
        from textual.app import App, ComposeResult
        from textual.containers import Horizontal, Vertical
        from textual.widgets import Button, Footer, Header, Input, Label, ListItem, ListView, Static
        try:
            from textual_image.widget import Image as TerminalImage
        except Exception:
            TerminalImage = None
    except Exception as exc:  # pragma: no cover - depends on local installation.
        raise TextualUnavailable("Textual is not installed. Install project dependencies, then run fnp-qnn-tui.") from exc
    return App, ComposeResult, Horizontal, Vertical, Button, Footer, Header, Input, Label, ListItem, ListView, Static, TerminalImage


def _format_payload(payload: dict[str, Any]) -> str:
    if "output" in payload:
        output = str(payload["output"])
        data = payload.get("data")
        if data:
            return output + "\n\n" + json.dumps(data, indent=2, sort_keys=True)[:6000]
        return output
    if "totals" in payload:
        lines = [
            f"Doctor status: {payload['status']}",
            f"Pass={payload['totals']['pass']} Warn={payload['totals']['warn']} Fail={payload['totals']['fail']}",
            "",
        ]
        for check in payload["checks"]:
            lines.append(f"[{check['status']}] {check['name']}: {check['detail']}")
        return "\n".join(lines)
    return json.dumps(payload, indent=2, sort_keys=True)[:6000]


def create_app():
    App, ComposeResult, Horizontal, Vertical, Button, Footer, Header, Input, Label, ListItem, ListView, Static, TerminalImage = (
        _require_textual()
    )

    def image_widget(asset_name: str, fallback: str, *, id: str):
        if TerminalImage is None:
            return Static(fallback, id=id)
        return TerminalImage(str(logo_asset_path(asset_name)), id=id)

    class FNPQNNTui(App):
        CSS = """
        Screen {
            layout: vertical;
            background: #07131c;
            color: #f4efe6;
        }
        #body {
            height: 1fr;
        }
        #brand {
            height: 15;
            background: #07131c;
            color: #f4efe6;
            border-bottom: solid #b08a3c;
            padding: 0 1;
        }
        #brand-top {
            height: 4;
            background: #101820;
            color: #f4efe6;
            border-bottom: solid #b08a3c;
            padding: 0 1;
        }
        #brand-top-image {
            width: 34;
            height: 4;
            color: #f4efe6;
            text-style: bold;
        }
        #brand-top-meta {
            width: 1fr;
            color: #d8d2c8;
            padding: 0 2;
        }
        #brand-image {
            width: 1fr;
            height: 14;
            color: #f4efe6;
            text-style: bold;
            text-align: center;
        }
        #brand-meta {
            width: 42;
            color: #b08a3c;
            padding: 1 2;
        }
        #gate-strip {
            height: auto;
            background: #101820;
            color: #d8d2c8;
            padding: 0 1;
            border-bottom: solid #b08a3c;
        }
        #nav {
            width: 29;
            background: #07131c;
            border-right: solid #303030;
            padding: 1;
        }
        #main {
            width: 1fr;
            background: #101820;
            padding: 1;
        }
        #context {
            height: auto;
            border: solid #303030;
            padding: 1;
            margin-bottom: 1;
            color: #d8d2c8;
        }
        #actions {
            height: auto;
            margin-bottom: 1;
        }
        #prompt {
            dock: bottom;
            border: solid #b08a3c;
            margin-top: 1;
            background: #07131c;
        }
        #brand-footer-image {
            height: 5;
            width: 34;
            color: #b08a3c;
            text-align: center;
            padding: 0 1;
        }
        #output {
            height: 1fr;
            overflow-y: scroll;
            border: solid #303030;
            padding: 1;
            background: #07131c;
            color: #f4efe6;
        }
        .boundary {
            color: #b08a3c;
            margin-top: 1;
        }
        .nav-title {
            color: #f4efe6;
            text-style: bold;
        }
        .accent {
            color: #b08a3c;
        }
        Button {
            margin-right: 1;
        }
        Button.-primary {
            background: #001020;
            color: #f4efe6;
        }
        Button.-warning {
            background: #b08a3c;
            color: #001020;
        }
        """
        TITLE = "FNP-QNN Control Terminal"
        SUB_TITLE = "alpha-local non-clinical simulator"
        BINDINGS = [
            ("q", "quit", "Quit"),
            ("d", "doctor", "Doctor"),
            ("s", "status", "Status"),
            ("r", "runtime", "Runtime"),
        ]

        def compose(self) -> ComposeResult:
            yield Header()
            with Horizontal(id="brand-top"):
                yield image_widget("top_small", top_logo_terminal(), id="brand-top-image")
                yield Static(
                    "Research simulator | non-clinical | no raw provider secrets\n"
                    f"Top asset: {LOGO_ASSETS['top_small']}",
                    id="brand-top-meta",
                )
            with Horizontal(id="brand"):
                yield image_widget("main_big", main_logo_terminal(), id="brand-image")
                yield Static(
                    "Quick controls\n"
                    "s: status\n"
                    "r: runtime\n"
                    "d: doctor\n"
                    f"main: {LOGO_ASSETS['main_big']}",
                    id="brand-meta",
                )
            yield Static(
                "Gate strip: p114 consensus -> Obsidian/RAG admission -> LVFM runtime. Raw tokens never enter the stream.",
                id="gate-strip",
            )
            with Horizontal(id="body"):
                with Vertical(id="nav"):
                    yield Label("FNP-QNN CLI", classes="nav-title")
                    yield Static(
                        "Local simulator\nGateway-aware\nSecret-safe\nNo arbitrary shell",
                        id="context",
                    )
                    yield ListView(
                        ListItem(Label("Status"), id="nav-status"),
                        ListItem(Label("Runtime"), id="nav-runtime"),
                        ListItem(Label("QNN"), id="nav-qnn"),
                        ListItem(Label("NeuroBit"), id="nav-neurobit"),
                        ListItem(Label("p114 Consensus"), id="nav-p114"),
                        ListItem(Label("Core Profiles"), id="nav-core"),
                        ListItem(Label("Network Designer"), id="nav-network"),
                        ListItem(Label("Operator"), id="nav-operator"),
                        ListItem(Label("Doctor"), id="nav-doctor"),
                        id="nav-list",
                    )
                with Vertical(id="main"):
                    yield Label("Agent Terminal", id="section-title")
                    with Horizontal(id="actions"):
                        yield Button("Status", id="run-status", variant="primary")
                        yield Button("Runtime", id="run-runtime")
                        yield Button("QNN Smoke", id="run-qnn")
                        yield Button("NeuroBit", id="run-neurobit")
                        yield Button("Doctor", id="run-doctor", variant="warning")
                    yield Static(
                        "Ready.\n\nType a command or use the buttons above.\n\n"
                        "/status    runtime bridge status\n"
                        "/runtime   Cerebrum runtime smoke\n"
                        "/qnn       deterministic QNN smoke\n"
                        "/neurobit  NeuroBit gates profile\n"
                        "/p114      neutrosophic consensus gate\n"
                        "/doctor    full local diagnostics\n"
                        "/help      command list",
                        id="output",
                    )
                    yield Input(placeholder="Type /status, /doctor, /runtime, /qnn, /p114, /celebrum clip ...", id="prompt")
                    yield image_widget("bottom_center", bottom_logo_terminal(), id="brand-footer-image")
                    yield Static(RESEARCH_BOUNDARY + "\n" + HIERARCHY_BOUNDARY, classes="boundary")
            yield Footer()

        def _show(self, title: str, payload: dict[str, Any]) -> None:
            self.query_one("#section-title", Label).update(title)
            self.query_one("#output", Static).update(_format_payload(payload))

        def _append(self, command: str, payload: dict[str, Any]) -> None:
            output = self.query_one("#output", Static)
            output.update(f"> {command}\n\n{_format_payload(payload)}")

        def _run_prompt_command(self, command: str) -> None:
            normalized = command.strip()
            if not normalized:
                return
            if normalized in {"/help", "help"}:
                self._append(
                    normalized,
                    {
                        "success": True,
                        "output": (
                            "Available prompt commands:\n"
                            "/status - runtime bridge status\n"
                            "/runtime - Cerebrum runtime smoke\n"
                            "/qnn - deterministic QNN smoke\n"
                            "/neurobit - NeuroBit gates smoke\n"
                            "/p114 - native neutrosophic T/I/F consensus gate\n"
                            "/doctor - full local diagnostics\n"
                            "/core list - curated core adapters\n"
                            "/celebrum clip - sanitized AI CLI function contract\n"
                            "hidden: /82"
                        ),
                        "research_boundary": RESEARCH_BOUNDARY,
                    },
                )
            elif normalized in {"/status", "status"}:
                self._append(normalized, command_response("cerebrum-runtime-status"))
            elif normalized in {"/runtime", "runtime", "/cerebrum run"}:
                self._append(normalized, runtime_run({"epochs": 2}))
            elif normalized in {"/qnn", "qnn", "/qnn smoke"}:
                self._append(normalized, qnn_smoke({"epochs": 2, "test_size": 0.0}))
            elif normalized in {"/neurobit", "neurobit"}:
                self._append(normalized, neurobit_gates({"truth": 0.5}))
            elif normalized in {"/p114", "p114", "/ffed p114"}:
                self._append(
                    normalized,
                    FfeDPluginBridge().run_p114_consensus(
                        [
                            "verified evidence passed with implementation proof",
                            "partial risk remains pending",
                        ]
                    ),
                )
            elif normalized in {"/82", "82", "/retro-82", "retro-82", "/vuarnet"}:
                self._append(
                    normalized,
                    {
                        "success": True,
                        "type": "operator-easter-egg",
                        "year": 1982,
                        "style": "retro mountain lens flash",
                        "output": RETRO_82_FLASH,
                        "palette": {
                            "ink": BRAND_FACTS["ink"],
                            "paper": BRAND_FACTS["paper"],
                            "gold": BRAND_FACTS["neuro_gold"],
                            "deep_navy": BRAND_FACTS["deep_navy"],
                        },
                        "trademark_boundary": "No external brand artwork or logos are embedded.",
                    },
                )
            elif normalized in {"/doctor", "doctor"}:
                self._append(normalized, run_doctor(full=True, probe_services=True))
            elif normalized in {"/core list", "core list"}:
                self._append(normalized, {"success": True, "data": list_core_commands()})
            elif normalized in {"/celebrum clip", "celebrum clip"}:
                from .celebrum import celebrum_clip_function

                self._append(normalized, celebrum_clip_function({"source": "tui", "token": "redacted"}))
            else:
                self._append(
                    normalized,
                    {
                        "success": False,
                        "error": "Unknown prompt command. Use /help.",
                        "research_boundary": RESEARCH_BOUNDARY,
                    },
                )

        def action_status(self) -> None:
            self._show("Status", command_response("cerebrum-runtime-status"))

        def action_runtime(self) -> None:
            self._show("Runtime", runtime_run({"epochs": 2}))

        def action_doctor(self) -> None:
            self._show("Doctor", run_doctor(full=True, probe_services=True))

        def on_button_pressed(self, event) -> None:
            if event.button.id == "run-status":
                self.action_status()
            elif event.button.id == "run-runtime":
                self.action_runtime()
            elif event.button.id == "run-qnn":
                self._show("QNN Smoke", qnn_smoke({"epochs": 2, "test_size": 0.0}))
            elif event.button.id == "run-neurobit":
                self._show("NeuroBit", neurobit_gates({"truth": 0.5}))
            elif event.button.id == "run-doctor":
                self.action_doctor()

        def on_input_submitted(self, event) -> None:
            self._run_prompt_command(event.value)
            self.query_one("#prompt", Input).value = ""

        def on_list_view_selected(self, event) -> None:
            item_id = event.item.id
            if item_id == "nav-status":
                self.action_status()
            elif item_id == "nav-runtime":
                self.action_runtime()
            elif item_id == "nav-qnn":
                self._show("QNN Smoke", qnn_smoke({"epochs": 2, "test_size": 0.0}))
            elif item_id == "nav-neurobit":
                self._show("NeuroBit", neurobit_gates({"truth": 0.5}))
            elif item_id == "nav-p114":
                self._show(
                    "p114 Consensus",
                    FfeDPluginBridge().run_p114_consensus(
                        [
                            "verified evidence passed with implementation proof",
                            "partial risk remains pending",
                        ]
                    ),
                )
            elif item_id == "nav-core":
                self._show(
                    "Core Profiles",
                    {"success": True, "data": list_core_commands(), "research_boundary": RESEARCH_BOUNDARY},
                )
            elif item_id == "nav-network":
                self._show(
                    "Network Designer",
                    {
                        "success": True,
                        "output": "Network Designer is available through the existing Panel/network UI.",
                        "research_boundary": RESEARCH_BOUNDARY,
                    },
                )
            elif item_id == "nav-operator":
                self._show(
                    "Operator",
                    {
                        "success": True,
                        "output": (
                            "Use direct commands:\n"
                            "fnp-qnn operator api serve --port 8000\n"
                            "fnp-qnn operator panel serve --port 5006\n"
                            "fnp-qnn validate tests\n"
                            "fnp-qnn validate alpha"
                        ),
                        "research_boundary": RESEARCH_BOUNDARY,
                    },
                )
            elif item_id == "nav-doctor":
                self.action_doctor()

    return FNPQNNTui()


def main() -> int:
    app = create_app()
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
