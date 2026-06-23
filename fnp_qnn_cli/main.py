"""Direct command-line interface for the FNP-QNN research simulator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from .agent_profiles import agent_profile, wake_prompt
from .auth import login, logout, status as auth_status, validate_token, web_login
from .celebrum import celebrum_clip_function, cerebrum_runtime_function
from .doctor import run_doctor
from .external_ai import (
    control_simulator,
    connect_antigravity,
    connect_codex,
    connect_ollama,
    external_ai_status,
    inspect_openclaw,
    simulator_control_tasks,
)
from .operator import alpha_command, api_serve_command, panel_serve_command, run_operator_command, tests_command
from .tui import BRAND_FACTS, RETRO_82_FLASH
from .mcp_bridge import mcp_control_simulator, mcp_manifest, provider_connection_status
from .onboarding import apply_onboarding, onboarding_questions
from .plugin_creator import create_ai_control_mcp_plugin, create_plugin_scaffold
from .registry import (
    RESEARCH_BOUNDARY,
    command_response,
    list_core_commands,
    load_json_payload,
    neurobit_gates,
    neurobit_tunnel,
    qnn_smoke,
    run_core_command,
    runtime_run,
)
from .support import all_provider_support_reports, provider_support_report
from core.ffed_plugin_bridge import FfeDPluginBridge, P114_PLUGIN_ID
from core.cloud_rag_bridge import (
    admission_to_runtime_payload,
    build_admission,
    cloud_kit_status,
    decrypt_admission,
    e2b_ingest_plan,
    e2b_smoke,
    encrypt_admission,
    generate_rag_key,
    load_env_file,
)


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _print_text(payload: dict[str, Any]) -> None:
    if "output" in payload:
        print(payload["output"])
    elif "totals" in payload:
        totals = payload["totals"]
        print(f"Doctor status: {payload['status']} | pass={totals['pass']} warn={totals['warn']} fail={totals['fail']}")
        for check in payload["checks"]:
            print(f"[{check['status']}] {check['name']}: {check['detail']}")
    elif "data" in payload and "name" in payload:
        print(f"{payload['name']}: ok")
        print(json.dumps(payload["data"], indent=2, sort_keys=True))
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    if payload.get("research_boundary"):
        print()
        print(payload["research_boundary"])


def _emit(payload: dict[str, Any], as_json: bool) -> int:
    if as_json:
        _print_json(payload)
    else:
        _print_text(payload)
    return 0 if payload.get("success", True) else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fnp-qnn",
        description="Local CLI for the FNP-QNN alpha-local research simulator.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")

    subparsers = parser.add_subparsers(dest="section", required=True)

    subparsers.add_parser("status", help="Show runtime bridge status.")

    cerebrum = subparsers.add_parser("cerebrum", help="Cerebrum CLI functions.")
    cerebrum_sub = cerebrum.add_subparsers(dest="cerebrum_command", required=True)
    cerebrum_sub.add_parser("status", help="Show Cerebrum runtime bridge status.")
    cerebrum_run = cerebrum_sub.add_parser("run", help="Run Cerebrum runtime as a Python CLI function.")
    cerebrum_run.add_argument("--payload", help="Path to Cerebrum runtime JSON payload.")
    cerebrum_run.add_argument("--epochs", type=int, default=2)
    cerebrum_sub.add_parser("legacy-demo", help="Run legacy Cerebrum fixture replay.")

    celebrum = subparsers.add_parser("celebrum", help="CeLeBrUm AI CLI adapters.")
    celebrum_sub = celebrum.add_subparsers(dest="celebrum_command", required=True)
    celebrum_clip = celebrum_sub.add_parser("clip", help="Create a sanitized CeLeBrUm AI CLI function contract.")
    celebrum_clip.add_argument("--payload", help="Path to JSON payload.")
    celebrum_clip.add_argument("--token", help="Token to compare against local auth fingerprint.")
    celebrum_clip.add_argument("--require-auth", action="store_true", help="Require token validation.")

    auth = subparsers.add_parser("auth", help="Responsible local token login helpers.")
    auth_sub = auth.add_subparsers(dest="auth_command", required=True)
    auth_login = auth_sub.add_parser("login", help="Store a local token fingerprint under .codex.")
    auth_login.add_argument("--token", required=True, help="Token to fingerprint. The raw token is not stored.")
    auth_login.add_argument("--label", default="local-test")
    auth_provider_login = auth_sub.add_parser("login-provider", help="Store a provider token fingerprint.")
    auth_provider_login.add_argument("provider", choices=["openai", "google", "ollama"])
    auth_provider_login.add_argument("--token", required=True, help="Token/API key to fingerprint. Raw value is not stored.")
    auth_provider_login.add_argument("--label", default=None)
    auth_web = auth_sub.add_parser("web-login", help="Show or open a provider web login/key flow.")
    auth_web.add_argument("provider", choices=["openai", "google", "ollama"])
    auth_web.add_argument("--open", action="store_true", help="Open the provider page in the default browser.")
    auth_web.add_argument("--run-gcloud", action="store_true", help="Run Google application-default OAuth login.")
    auth_web.add_argument("--run-ollama", action="store_true", help="Run Ollama CLI web sign-in.")
    auth_sub.add_parser("status", help="Show local auth status.")
    auth_sub.add_parser("logout", help="Remove local auth fingerprint.")
    auth_check = auth_sub.add_parser("check", help="Validate a supplied token or FNP_QNN_CLI_TOKEN.")
    auth_check.add_argument("--token", help="Token to compare against local auth fingerprint.")

    plugin = subparsers.add_parser("plugin", help="Local plugin scaffold helpers.")
    plugin_sub = plugin.add_subparsers(dest="plugin_command", required=True)
    plugin_create = plugin_sub.add_parser("create", help="Create a local .codex-plugin scaffold.")
    plugin_create.add_argument("name")
    plugin_create.add_argument("--path", help="Parent directory for plugin creation.")
    plugin_create.add_argument("--force", action="store_true")
    plugin_mcp = plugin_sub.add_parser("create-ai-control-mcp", help="Create the integrated FNP-QNN AI control MCP plugin.")
    plugin_mcp.add_argument("--path", help="Parent directory for plugin creation.")
    plugin_mcp.add_argument("--force", action="store_true")

    mcp = subparsers.add_parser("mcp", help="Local MCP server and provider bridge commands.")
    mcp_sub = mcp.add_subparsers(dest="mcp_command", required=True)
    mcp_sub.add_parser("manifest", help="Show the MCP tool manifest.")
    mcp_status = mcp_sub.add_parser("provider-status", help="Check provider connection for MCP control.")
    mcp_status.add_argument("provider", choices=["openai", "chatgpt", "google", "gemini", "ollama"])
    mcp_call = mcp_sub.add_parser("control", help="Call the simulator control MCP bridge directly.")
    mcp_call.add_argument("provider", choices=["openai", "chatgpt", "google", "gemini", "ollama"])
    mcp_call.add_argument("task", choices=["status", "doctor", "runtime", "qnn", "neurobit", "validate", "external-status"])
    mcp_call.add_argument("--execute", action="store_true")
    mcp_call.add_argument("--timeout", type=int, default=300)
    mcp_call.add_argument("--prompt")
    mcp_sub.add_parser("serve", help="Run the stdio MCP server.")

    onboarding = subparsers.add_parser("onboarding", help="Provider-approved user onboarding for simulator wiring.")
    onboarding_sub = onboarding.add_subparsers(dest="onboarding_command", required=True)
    onboarding_sub.add_parser("questions", help="Print the onboarding question set.")
    onboarding_apply = onboarding_sub.add_parser("apply", help="Apply onboarding answers into simulator context files.")
    onboarding_apply.add_argument("provider", choices=["openai", "chatgpt", "google", "gemini", "ollama"])
    onboarding_apply.add_argument("--answers", help="JSON file with answers keyed by question id.")
    onboarding_apply.add_argument("--approve-fingerprint", action="store_true")
    onboarding_apply.add_argument("--delegate", action="store_true", help="Create an agent handoff through the selected provider.")
    onboarding_apply.add_argument("--execute-delegate", action="store_true", help="Actually run the selected external agent.")
    onboarding_apply.add_argument("--primary-goal")
    onboarding_apply.add_argument("--audience")
    onboarding_apply.add_argument("--preferred-workflow")
    onboarding_apply.add_argument("--data-boundary")
    onboarding_apply.add_argument("--agent-role")
    onboarding_apply.add_argument("--ui-preference")
    onboarding_apply.add_argument("--success-signal")

    agent = subparsers.add_parser("agent", help="Provider-specific wake prompts and native tool profiles.")
    agent_sub = agent.add_subparsers(dest="agent_command", required=True)
    agent_profile_cmd = agent_sub.add_parser("profile", help="Show the selected provider/system profile.")
    agent_profile_cmd.add_argument("provider", choices=["openai", "chatgpt", "google", "gemini", "ollama"])
    agent_prompt_cmd = agent_sub.add_parser("wake-prompt", help="Print the provider-specific wake prompt.")
    agent_prompt_cmd.add_argument("provider", choices=["openai", "chatgpt", "google", "gemini", "ollama"])

    support = subparsers.add_parser("support", help="LLM-friendly support diagnostics for provider onboarding.")
    support_sub = support.add_subparsers(dest="support_command", required=True)
    support_provider = support_sub.add_parser("provider", help="Show one provider support report.")
    support_provider.add_argument("provider", choices=["openai", "chatgpt", "google", "gemini", "ollama"])
    support_sub.add_parser("all", help="Show support reports for all provider families.")

    external_ai = subparsers.add_parser("external-ai", help="Real external AI runtime connections.")
    external_ai_sub = external_ai.add_subparsers(dest="external_ai_command", required=True)
    external_ai_sub.add_parser("status", help="Detect Codex, Antigravity, OpenClaw, and auth profiles.")
    external_ai_sub.add_parser("inspect-openclaw", help="Inspect ~/.openclaw shape without reading secrets.")
    external_connect = external_ai_sub.add_parser("connect", help="Run a real external AI login/connect command.")
    external_connect.add_argument("target", choices=["codex", "antigravity", "ollama"])
    external_connect.add_argument("--device-auth", action="store_true", help="Use Codex device auth when target=codex.")
    external_connect.add_argument("--api-key-env", help="Read API key from this environment variable for Codex.")
    external_control_tasks = external_ai_sub.add_parser(
        "control-tasks",
        help="List allowlisted simulator control tasks for external AI tools.",
    )
    external_control_tasks.set_defaults(external_ai_command="control-tasks")
    external_control = external_ai_sub.add_parser(
        "control",
        help="Let Codex or Antigravity control an allowlisted simulator task.",
    )
    external_control.add_argument("task", choices=["status", "doctor", "runtime", "qnn", "neurobit", "validate", "external-status"])
    external_control.add_argument("--tool", choices=["auto", "codex", "antigravity", "ollama"], default="auto")
    external_control.add_argument("--execute", action="store_true", help="Actually run the selected external AI tool.")
    external_control.add_argument("--timeout", type=int, default=300)
    external_control.add_argument("--prompt", help="Additional operator note for the external AI tool.")

    skill = subparsers.add_parser("skill", help="Skill-style AI CLI functions.")
    skill_sub = skill.add_subparsers(dest="skill_command", required=True)
    skill_function = skill_sub.add_parser("function", help="Skill function commands.")
    skill_function_sub = skill_function.add_subparsers(dest="skill_function_command", required=True)
    skill_login = skill_function_sub.add_parser(
        "login-chatgpt",
        help="Store a local fingerprint for a ChatGPT/OpenAI account token.",
    )
    skill_login.add_argument("--token", required=True, help="Token/API key to fingerprint. Raw value is not stored.")
    skill_login.add_argument("--label", default="chatgpt-account")
    skill_google_login = skill_function_sub.add_parser(
        "login-google-ai-pro",
        help="Store a local fingerprint for a Google AI/Gemini token.",
    )
    skill_google_login.add_argument("--token", required=True, help="Token/API key to fingerprint. Raw value is not stored.")
    skill_ollama_login = skill_function_sub.add_parser(
        "login-ollama-cloud",
        help="Store a local fingerprint for an Ollama Cloud token/API key.",
    )
    skill_ollama_login.add_argument("--token", required=True, help="Token/API key to fingerprint. Raw value is not stored.")
    skill_ollama_login.add_argument("--label", default="ollama-cloud")
    skill_google_login.add_argument("--label", default="google-ai-pro")

    function = subparsers.add_parser("function", help="Direct AI CLI function aliases.")
    function_sub = function.add_subparsers(dest="function_command", required=True)
    function_login = function_sub.add_parser(
        "login-chatgpt",
        help="Store a local fingerprint for a ChatGPT/OpenAI account token.",
    )
    function_login.add_argument("--token", required=True, help="Token/API key to fingerprint. Raw value is not stored.")
    function_login.add_argument("--label", default="chatgpt-account")
    function_google_login = function_sub.add_parser(
        "login-google-ai-pro",
        help="Store a local fingerprint for a Google AI/Gemini token.",
    )
    function_google_login.add_argument("--token", required=True, help="Token/API key to fingerprint. Raw value is not stored.")
    function_ollama_login = function_sub.add_parser(
        "login-ollama-cloud",
        help="Store a local fingerprint for an Ollama Cloud token/API key.",
    )
    function_ollama_login.add_argument("--token", required=True, help="Token/API key to fingerprint. Raw value is not stored.")
    function_ollama_login.add_argument("--label", default="ollama-cloud")
    function_google_login.add_argument("--label", default="google-ai-pro")

    runtime = subparsers.add_parser("runtime", help="Runtime commands.")
    runtime_sub = runtime.add_subparsers(dest="runtime_command", required=True)
    runtime_run_parser = runtime_sub.add_parser("run", help="Run the Cerebrum runtime bridge.")
    runtime_run_parser.add_argument("--payload", help="Path to runtime JSON payload.")
    runtime_run_parser.add_argument("--epochs", type=int, default=None, help="Override runtime epochs.")

    ffed = subparsers.add_parser("ffed", help="FfeD plugin gates and consensus helpers.")
    ffed_sub = ffed.add_subparsers(dest="ffed_command", required=True)
    p114 = ffed_sub.add_parser("p114-consensus", help="Run native p114 neutrosophic T/I/F consensus.")
    p114.add_argument("--payload", help="JSON file with items/evidence and optional thresholds.")
    p114.add_argument("--item", action="append", default=[], help="Evidence text item to score.")
    p114.add_argument(
        "--mode",
        choices=["consensus", "decision", "score_evidence", "case_study_audit"],
        default="score_evidence",
    )

    cloud_kit = subparsers.add_parser("cloud-kit", help="Optional E2B and encrypted RAG bridge commands.")
    cloud_kit_sub = cloud_kit.add_subparsers(dest="cloud_kit_command", required=True)
    cloud_kit_sub.add_parser("status", help="Show cloud kit and encrypted RAG readiness.")
    cloud_e2b = cloud_kit_sub.add_parser("e2b-ingest-plan", help="Plan E2B external data ingestion into RAG/LVFM.")
    cloud_e2b.add_argument("--source", required=True)
    cloud_e2b.add_argument("--title", required=True)
    cloud_e2b.add_argument("--tool-route", default="gateway")
    cloud_smoke = cloud_kit_sub.add_parser("e2b-smoke", help="Run a real minimal E2B sandbox smoke test.")
    cloud_smoke.add_argument("--env-file", default=str(Path.home() / ".openclaw" / "workspace" / ".env"))
    cloud_kit_sub.add_parser("rag-keygen", help="Generate a Fernet key for FNP_QNN_RAG_ENCRYPTION_KEY.")
    rag_encrypt = cloud_kit_sub.add_parser("rag-encrypt", help="Encrypt a sanitized RAG admission envelope.")
    rag_encrypt.add_argument("--title", required=True)
    rag_encrypt.add_argument("--source", required=True)
    rag_encrypt.add_argument("--tool-route", default="gateway")
    rag_encrypt.add_argument("--content")
    rag_encrypt.add_argument("--content-file")
    rag_encrypt.add_argument("--tag", action="append", default=[])
    rag_runtime = cloud_kit_sub.add_parser("rag-runtime", help="Convert a sanitized RAG admission into a LVFM runtime result.")
    rag_runtime.add_argument("--title", required=True)
    rag_runtime.add_argument("--source", required=True)
    rag_runtime.add_argument("--tool-route", default="gateway")
    rag_runtime.add_argument("--content")
    rag_runtime.add_argument("--content-file")
    rag_runtime.add_argument("--tag", action="append", default=[])
    rag_runtime.add_argument("--skip-p114-gate", action="store_true", help="Do not run p114 before LVFM admission.")
    rag_runtime.add_argument(
        "--require-p114-approval",
        action="store_true",
        help="Fail instead of admitting when p114 asks for clarification or rejection.",
    )
    rag_decrypt = cloud_kit_sub.add_parser("rag-decrypt-runtime", help="Decrypt an envelope and convert it into a LVFM runtime result.")
    rag_decrypt.add_argument("--envelope", required=True, help="Path to encrypted RAG envelope JSON.")
    rag_decrypt.add_argument("--skip-p114-gate", action="store_true", help="Do not run p114 before LVFM admission.")
    rag_decrypt.add_argument(
        "--require-p114-approval",
        action="store_true",
        help="Fail instead of admitting when p114 asks for clarification or rejection.",
    )

    qnn = subparsers.add_parser("qnn", help="QNN commands.")
    qnn_sub = qnn.add_subparsers(dest="qnn_command", required=True)
    qnn_smoke_parser = qnn_sub.add_parser("smoke", help="Run deterministic QNN smoke path.")
    qnn_smoke_parser.add_argument("--payload", help="Path to QNN JSON payload.")
    qnn_smoke_parser.add_argument("--epochs", type=int, default=4)
    qnn_smoke_parser.add_argument("--test-size", type=float, default=0.0)

    neurobit = subparsers.add_parser("neurobit", help="NeuroBit commands.")
    neurobit_sub = neurobit.add_subparsers(dest="neurobit_command", required=True)
    gates = neurobit_sub.add_parser("gates", help="Run NeuroBit gate profile.")
    tunnel = neurobit_sub.add_parser("tunnel", help="Run NeuroBit tunnel demo.")
    for neurobit_parser in (gates, tunnel):
        neurobit_parser.add_argument("--payload", help="Path to NeuroBit JSON payload.")
        neurobit_parser.add_argument("--truth", type=float, default=None)
        neurobit_parser.add_argument("--indeterminacy", type=float, default=None)
        neurobit_parser.add_argument("--falsity", type=float, default=None)
        neurobit_parser.add_argument("--dF", dest="delta_falsity", type=float, default=None)
    tunnel.add_argument("--data", default=None, help="Tunnel demo data string.")

    legacy = subparsers.add_parser("legacy", help="Legacy fixture commands.")
    legacy_sub = legacy.add_subparsers(dest="legacy_command", required=True)
    legacy_sub.add_parser("demo", help="Run legacy fixture replay.")

    core = subparsers.add_parser("core", help="Curated core profile commands.")
    core_sub = core.add_subparsers(dest="core_command", required=True)
    core_sub.add_parser("list", help="List core profile adapters.")
    core_run = core_sub.add_parser("run", help="Run a core profile adapter.")
    core_run.add_argument("name", help="Core adapter name.")
    core_run.add_argument("--payload", help="Path to core JSON payload.")

    operator = subparsers.add_parser("operator", help="Local operator commands.")
    operator_sub = operator.add_subparsers(dest="operator_command", required=True)
    api = operator_sub.add_parser("api", help="API operator commands.")
    api_sub = api.add_subparsers(dest="api_command", required=True)
    api_serve = api_sub.add_parser("serve", help="Serve FastAPI locally.")
    api_serve.add_argument("--port", type=int, default=8000)
    panel = operator_sub.add_parser("panel", help="Panel operator commands.")
    panel_sub = panel.add_subparsers(dest="panel_command", required=True)
    panel_serve = panel_sub.add_parser("serve", help="Serve Panel locally.")
    panel_serve.add_argument("--port", type=int, default=5006)

    api_alias = subparsers.add_parser("api", help="Alias for API operator commands.")
    api_alias_sub = api_alias.add_subparsers(dest="api_alias_command", required=True)
    api_alias_serve = api_alias_sub.add_parser("serve", help="Serve FastAPI locally.")
    api_alias_serve.add_argument("--port", type=int, default=8000)

    panel_alias = subparsers.add_parser("panel", help="Alias for Panel operator commands.")
    panel_alias_sub = panel_alias.add_subparsers(dest="panel_alias_command", required=True)
    panel_alias_serve = panel_alias_sub.add_parser("serve", help="Serve Panel locally.")
    panel_alias_serve.add_argument("--port", type=int, default=5006)

    validate = subparsers.add_parser("validate", help="Run validation commands.")
    validate_sub = validate.add_subparsers(dest="validate_command", required=True)
    validate_sub.add_parser("alpha", help="Run alpha readiness validation.")
    validate_sub.add_parser("tests", help="Run unittest discovery.")

    doctor = subparsers.add_parser("doctor", help="Run local diagnostics.")
    doctor.add_argument("--full", action="store_true", help="Run slower in-process smoke checks.")
    doctor.add_argument("--no-probe-services", action="store_true", help="Skip local API/Panel service probes.")

    tui = subparsers.add_parser("tui", help="Open the interactive Textual TUI.")
    tui.add_argument("--dry-run", action="store_true", help="Verify TUI import without launching.")
    tui.add_argument("--retro-82", action="store_true", help=argparse.SUPPRESS)

    retro = subparsers.add_parser("retro-82", help=argparse.SUPPRESS)
    retro.add_argument("--flash", action="store_true", help=argparse.SUPPRESS)

    return parser


def _payload_with_overrides(path: str | None, overrides: dict[str, Any]) -> dict[str, Any]:
    payload = load_json_payload(path)
    for key, value in overrides.items():
        if value is not None:
            payload[key] = value
    return payload


def _content_arg(content: str | None, content_file: str | None) -> str:
    if content_file:
        return Path(content_file).read_text(encoding="utf-8")
    if content is not None:
        return content
    raise ValueError("--content or --content-file is required")


def _p114_items_from_admission(admission: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "label": str(admission.get("title") or "cloud-rag-admission"),
            "text": str(admission.get("content") or ""),
        },
        {
            "label": "source",
            "text": f"source evidence {admission.get('source', '')}",
        },
        {
            "label": "tool-route",
            "text": f"gateway route {admission.get('tool_route', 'gateway')}",
        },
    ]


def _attach_p114_gate(
    runtime_payload: dict[str, Any],
    admission: dict[str, Any],
    *,
    skip_gate: bool = False,
) -> dict[str, Any] | None:
    if skip_gate:
        return None
    gate = FfeDPluginBridge().run_p114_consensus(_p114_items_from_admission(admission), mode="score_evidence")
    runtime_payload.setdefault("plugin_context", {})["p114_consensus"] = gate
    for memory in runtime_payload.get("memories", []):
        if isinstance(memory, dict):
            memory.setdefault("provenance", {})["p114_gate"] = {
                "plugin_id": P114_PLUGIN_ID,
                "status": gate.get("cli_gate", {}).get("status"),
                "action": gate.get("action"),
                "consensus": gate.get("consensus"),
            }
    return gate


def _ffed_payload_items(payload_path: str | None, cli_items: list[str]) -> tuple[list[Any], dict[str, Any] | None]:
    payload = load_json_payload(payload_path)
    raw_items = payload.get("items", payload.get("evidence", [])) if isinstance(payload, dict) else []
    items = list(raw_items or [])
    items.extend(cli_items or [])
    thresholds = payload.get("thresholds") if isinstance(payload, dict) else None
    return items, thresholds if isinstance(thresholds, dict) else None


def run_args(args: argparse.Namespace) -> int:
    as_json = bool(args.json)

    if args.section == "status":
        return _emit(command_response("cerebrum-runtime-status"), as_json)

    if args.section == "cerebrum":
        if args.cerebrum_command == "status":
            return _emit(command_response("cerebrum-runtime-status"), as_json)
        if args.cerebrum_command == "run":
            payload = _payload_with_overrides(args.payload, {"epochs": args.epochs})
            return _emit(cerebrum_runtime_function(payload), as_json)
        if args.cerebrum_command == "legacy-demo":
            return _emit(command_response("cerebrum-runtime-legacy-demo"), as_json)

    if args.section == "celebrum" and args.celebrum_command == "clip":
        payload = load_json_payload(args.payload)
        return _emit(
            celebrum_clip_function(payload, token=args.token, require_auth=args.require_auth),
            as_json,
        )

    if args.section == "auth":
        if args.auth_command == "login":
            return _emit(login(args.token, args.label), as_json)
        if args.auth_command == "login-provider":
            label = args.label or f"{args.provider}-account"
            return _emit(login(args.token, label, args.provider), as_json)
        if args.auth_command == "web-login":
            return _emit(
                web_login(
                    args.provider,
                    open_browser=args.open,
                    run_gcloud=args.run_gcloud,
                    run_ollama=args.run_ollama,
                ),
                as_json,
            )
        if args.auth_command == "status":
            return _emit(auth_status(), as_json)
        if args.auth_command == "logout":
            return _emit(logout(), as_json)
        if args.auth_command == "check":
            return _emit(validate_token(args.token), as_json)

    if args.section == "plugin" and args.plugin_command == "create":
        return _emit(create_plugin_scaffold(args.name, args.path, args.force), as_json)

    if args.section == "plugin" and args.plugin_command == "create-ai-control-mcp":
        return _emit(create_ai_control_mcp_plugin(args.path, args.force), as_json)

    if args.section == "mcp":
        if args.mcp_command == "manifest":
            return _emit(mcp_manifest(), as_json)
        if args.mcp_command == "provider-status":
            return _emit(provider_connection_status(args.provider), as_json)
        if args.mcp_command == "control":
            return _emit(
                mcp_control_simulator(
                    args.provider,
                    args.task,
                    execute=args.execute,
                    timeout=args.timeout,
                    prompt=args.prompt,
                ),
                as_json,
            )
        if args.mcp_command == "serve":
            from .mcp_server import main as mcp_main

            return mcp_main()

    if args.section == "onboarding":
        if args.onboarding_command == "questions":
            return _emit(onboarding_questions(), as_json)
        if args.onboarding_command == "apply":
            return _emit(
                apply_onboarding(
                    args.provider,
                    answers_path=args.answers,
                    approve_fingerprint=args.approve_fingerprint,
                    overrides={
                        "primary_goal": args.primary_goal,
                        "audience": args.audience,
                        "preferred_workflow": args.preferred_workflow,
                        "data_boundary": args.data_boundary,
                        "agent_role": args.agent_role,
                        "ui_preference": args.ui_preference,
                        "success_signal": args.success_signal,
                    },
                    delegate=args.delegate,
                    execute_delegate=args.execute_delegate,
                ),
                as_json,
            )

    if args.section == "agent":
        if args.agent_command == "profile":
            return _emit({"success": True, "profile": agent_profile(args.provider)}, as_json)
        if args.agent_command == "wake-prompt":
            return _emit({"success": True, "provider": args.provider, "wake_prompt": wake_prompt(args.provider)}, as_json)

    if args.section == "support":
        if args.support_command == "provider":
            return _emit(provider_support_report(args.provider), as_json)
        if args.support_command == "all":
            return _emit(all_provider_support_reports(), as_json)

    if args.section == "external-ai":
        if args.external_ai_command == "status":
            return _emit(external_ai_status(), as_json)
        if args.external_ai_command == "inspect-openclaw":
            return _emit(inspect_openclaw(), as_json)
        if args.external_ai_command == "control-tasks":
            return _emit({"success": True, "tasks": simulator_control_tasks()}, as_json)
        if args.external_ai_command == "control":
            return _emit(
                control_simulator(
                    args.task,
                    tool=args.tool,
                    execute=args.execute,
                    timeout=args.timeout,
                    extra_prompt=args.prompt,
                ),
                as_json,
            )
        if args.external_ai_command == "connect":
            if args.target == "codex":
                api_key = None
                if args.api_key_env:
                    import os

                    api_key = os.environ.get(args.api_key_env)
                    if not api_key:
                        return _emit(
                            {"success": False, "provider": "codex", "error": f"{args.api_key_env} is not set"},
                            as_json,
                        )
                return _emit(connect_codex(device_auth=args.device_auth, api_key=api_key), as_json)
            if args.target == "antigravity":
                return _emit(connect_antigravity(), as_json)
            if args.target == "ollama":
                return _emit(connect_ollama(), as_json)

    if args.section == "skill" and args.skill_command == "function":
        if args.skill_function_command == "login-chatgpt":
            payload = login(args.token, args.label, "openai")
            payload["function"] = "login-chatgpt"
            payload["provider"] = "chatgpt-openai-token"
            payload["raw_token_stored"] = False
            return _emit(payload, as_json)
        if args.skill_function_command == "login-google-ai-pro":
            payload = login(args.token, args.label, "google")
            payload["function"] = "login-google-ai-pro"
            payload["provider"] = "google-ai-gemini-token"
            payload["raw_token_stored"] = False
            return _emit(payload, as_json)
        if args.skill_function_command == "login-ollama-cloud":
            payload = login(args.token, args.label, "ollama")
            payload["function"] = "login-ollama-cloud"
            payload["provider"] = "ollama-cloud-token"
            payload["raw_token_stored"] = False
            return _emit(payload, as_json)

    if args.section == "function":
        if args.function_command == "login-chatgpt":
            payload = login(args.token, args.label, "openai")
            payload["function"] = "login-chatgpt"
            payload["provider"] = "chatgpt-openai-token"
            payload["raw_token_stored"] = False
            return _emit(payload, as_json)
        if args.function_command == "login-google-ai-pro":
            payload = login(args.token, args.label, "google")
            payload["function"] = "login-google-ai-pro"
            payload["provider"] = "google-ai-gemini-token"
            payload["raw_token_stored"] = False
            return _emit(payload, as_json)
        if args.function_command == "login-ollama-cloud":
            payload = login(args.token, args.label, "ollama")
            payload["function"] = "login-ollama-cloud"
            payload["provider"] = "ollama-cloud-token"
            payload["raw_token_stored"] = False
            return _emit(payload, as_json)

    if args.section == "runtime" and args.runtime_command == "run":
        payload = _payload_with_overrides(args.payload, {"epochs": args.epochs})
        return _emit(runtime_run(payload), as_json)

    if args.section == "ffed":
        if args.ffed_command == "p114-consensus":
            items, thresholds = _ffed_payload_items(args.payload, args.item)
            return _emit(
                FfeDPluginBridge().run_p114_consensus(items, mode=args.mode, thresholds=thresholds),
                as_json,
            )

    if args.section == "cloud-kit":
        if args.cloud_kit_command == "status":
            return _emit({"success": True, "data": cloud_kit_status()}, as_json)
        if args.cloud_kit_command == "e2b-ingest-plan":
            return _emit(e2b_ingest_plan(args.source, args.title, args.tool_route), as_json)
        if args.cloud_kit_command == "e2b-smoke":
            return _emit(e2b_smoke(args.env_file), as_json)
        if args.cloud_kit_command == "rag-keygen":
            return _emit(generate_rag_key(), as_json)
        if args.cloud_kit_command == "rag-encrypt":
            content = _content_arg(args.content, args.content_file)
            admission = build_admission(args.title, content, args.source, args.tool_route, args.tag)
            return _emit(
                {
                    "success": True,
                    "admission": {key: admission[key] for key in ("title", "source", "tool_route", "content_sha256")},
                    "envelope": encrypt_admission(admission),
                },
                as_json,
            )
        if args.cloud_kit_command == "rag-runtime":
            content = _content_arg(args.content, args.content_file)
            admission = build_admission(args.title, content, args.source, args.tool_route, args.tag)
            runtime_payload = admission_to_runtime_payload(admission)
            p114_gate = _attach_p114_gate(runtime_payload, admission, skip_gate=args.skip_p114_gate)
            if args.require_p114_approval and p114_gate and not p114_gate.get("cli_gate", {}).get("allow_lvfm_admission"):
                return _emit(
                    {
                        "success": False,
                        "type": "cloud-rag",
                        "blocked_by": P114_PLUGIN_ID,
                        "p114_consensus": p114_gate,
                        "admission": {
                            "title": admission["title"],
                            "source": admission["source"],
                            "tool_route": admission["tool_route"],
                            "content_sha256": admission["content_sha256"],
                        },
                    },
                    as_json,
                )
            return _emit(
                {
                    "success": True,
                    "type": "cloud-rag",
                    "admission": {
                        "title": admission["title"],
                        "source": admission["source"],
                        "tool_route": admission["tool_route"],
                        "content_sha256": admission["content_sha256"],
                    },
                    "p114_consensus": p114_gate,
                    "runtime_payload": runtime_payload,
                    "runtime": runtime_run(runtime_payload),
                },
                as_json,
            )
        if args.cloud_kit_command == "rag-decrypt-runtime":
            envelope = load_json_payload(args.envelope)
            admission = decrypt_admission(envelope)
            runtime_payload = admission_to_runtime_payload(admission)
            p114_gate = _attach_p114_gate(runtime_payload, admission, skip_gate=args.skip_p114_gate)
            if args.require_p114_approval and p114_gate and not p114_gate.get("cli_gate", {}).get("allow_lvfm_admission"):
                return _emit(
                    {
                        "success": False,
                        "type": "cloud-rag",
                        "blocked_by": P114_PLUGIN_ID,
                        "p114_consensus": p114_gate,
                        "admission": {
                            "title": admission.get("title"),
                            "source": admission.get("source"),
                            "tool_route": admission.get("tool_route"),
                            "content_sha256": admission.get("content_sha256"),
                        },
                    },
                    as_json,
                )
            return _emit(
                {
                    "success": True,
                    "type": "cloud-rag",
                    "admission": {
                        "title": admission.get("title"),
                        "source": admission.get("source"),
                        "tool_route": admission.get("tool_route"),
                        "content_sha256": admission.get("content_sha256"),
                    },
                    "p114_consensus": p114_gate,
                    "runtime_payload": runtime_payload,
                    "runtime": runtime_run(runtime_payload),
                },
                as_json,
            )

    if args.section == "qnn" and args.qnn_command == "smoke":
        payload = _payload_with_overrides(args.payload, {"epochs": args.epochs, "test_size": args.test_size})
        return _emit(qnn_smoke(payload), as_json)

    if args.section == "neurobit":
        payload = _payload_with_overrides(
            args.payload,
            {
                "truth": args.truth,
                "indeterminacy": args.indeterminacy,
                "falsity": args.falsity,
                "delta_falsity": args.delta_falsity,
                "data": getattr(args, "data", None),
            },
        )
        runner = neurobit_gates if args.neurobit_command == "gates" else neurobit_tunnel
        return _emit(runner(payload), as_json)

    if args.section == "legacy" and args.legacy_command == "demo":
        return _emit(command_response("cerebrum-runtime-legacy-demo"), as_json)

    if args.section == "core" and args.core_command == "list":
        return _emit({"success": True, "research_boundary": RESEARCH_BOUNDARY, "data": list_core_commands()}, as_json)

    if args.section == "core" and args.core_command == "run":
        return _emit(run_core_command(args.name, load_json_payload(args.payload)), as_json)

    if args.section == "doctor":
        return _emit(run_doctor(full=args.full, probe_services=not args.no_probe_services), as_json)

    if args.section == "operator":
        if args.operator_command == "api" and args.api_command == "serve":
            return run_operator_command(api_serve_command(args.port))
        if args.operator_command == "panel" and args.panel_command == "serve":
            return run_operator_command(panel_serve_command(args.port))

    if args.section == "api" and args.api_alias_command == "serve":
        return run_operator_command(api_serve_command(args.port))

    if args.section == "panel" and args.panel_alias_command == "serve":
        return run_operator_command(panel_serve_command(args.port))

    if args.section == "validate":
        if args.validate_command == "tests":
            return run_operator_command(tests_command())
        if args.validate_command == "alpha":
            return run_operator_command(alpha_command())

    if args.section == "tui":
        from .tui import create_app

        if args.retro_82:
            return _emit(
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
                as_json,
            )
        app = create_app()
        if args.dry_run:
            return 0
        app.run()
        return 0

    if args.section == "retro-82":
        return _emit(
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
            as_json,
        )

    raise ValueError("unsupported command")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run_args(args)
    except Exception as exc:
        if getattr(args, "json", False):
            _print_json({"success": False, "type": "error", "error": f"{type(exc).__name__}: {exc}"})
        else:
            print(f"Error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
