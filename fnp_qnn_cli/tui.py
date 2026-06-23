"""Textual TUI for the FNP-QNN local research simulator."""

from __future__ import annotations

import json
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


class TextualUnavailable(RuntimeError):
    """Raised when the optional Textual runtime is not installed."""


def _require_textual():
    try:
        from textual.app import App, ComposeResult
        from textual.containers import Horizontal, Vertical
        from textual.widgets import Button, Footer, Header, Input, Label, ListItem, ListView, Static
    except Exception as exc:  # pragma: no cover - depends on local installation.
        raise TextualUnavailable("Textual is not installed. Install project dependencies, then run fnp-qnn-tui.") from exc
    return App, ComposeResult, Horizontal, Vertical, Button, Footer, Header, Input, Label, ListItem, ListView, Static


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
    App, ComposeResult, Horizontal, Vertical, Button, Footer, Header, Input, Label, ListItem, ListView, Static = (
        _require_textual()
    )

    class FNPQNNTui(App):
        CSS = """
        Screen {
            layout: vertical;
        }
        #body {
            height: 1fr;
        }
        #nav {
            width: 28;
            border: solid $primary;
            padding: 1;
        }
        #main {
            width: 1fr;
            border: solid $accent;
            padding: 1;
        }
        #context {
            height: auto;
            border: tall $surface;
            padding: 1;
            margin-bottom: 1;
        }
        #actions {
            height: auto;
            margin-bottom: 1;
        }
        #prompt {
            dock: bottom;
            border: solid $primary;
            margin-top: 1;
        }
        #output {
            height: 1fr;
            overflow-y: scroll;
            border: tall $surface;
            padding: 1;
        }
        .boundary {
            color: $warning;
            margin-top: 1;
        }
        Button {
            margin-right: 1;
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
            with Horizontal(id="body"):
                with Vertical(id="nav"):
                    yield Label("FNP-QNN CLI")
                    yield Static("OpenClaw-style local control\nCodex/Gemini-like prompt\nNo arbitrary shell", id="context")
                    yield ListView(
                        ListItem(Label("Status"), id="nav-status"),
                        ListItem(Label("Runtime"), id="nav-runtime"),
                        ListItem(Label("QNN"), id="nav-qnn"),
                        ListItem(Label("NeuroBit"), id="nav-neurobit"),
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
                        "Ready.\n\n"
                        "Prompt commands:\n"
                        "/status\n/runtime\n/qnn\n/neurobit\n/doctor\n/core list\n/celebrum clip\n/help",
                        id="output",
                    )
                    yield Input(placeholder="Type /status, /doctor, /runtime, /qnn, /celebrum clip ...", id="prompt")
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
                            "/doctor - full local diagnostics\n"
                            "/core list - curated core adapters\n"
                            "/celebrum clip - sanitized AI CLI function contract"
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
