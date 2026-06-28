import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
import sys

from fnp_qnn_cli.agent_profiles import agent_profile, wake_prompt
from fnp_qnn_cli.auth import AUTH_HOME_ENV, login, logout, status, validate_token
from fnp_qnn_cli.celebrum import celebrum_clip_function
from fnp_qnn_cli.doctor import run_doctor
from fnp_qnn_cli.external_ai import control_simulator, inspect_openclaw, simulator_control_tasks
from fnp_qnn_cli.gateway_bridge import _load_deepsearch_from_candidate, gateway_deepsearch_skill
from fnp_qnn_cli.mcp_bridge import mcp_control_simulator, provider_connection_status
from fnp_qnn_cli.mcp_server import handle_request
from fnp_qnn_cli.main import main
from fnp_qnn_cli.onboarding import apply_onboarding
from fnp_qnn_cli.operator import alpha_command, api_serve_command, panel_serve_command, tests_command
from fnp_qnn_cli.plugin_creator import create_ai_control_mcp_plugin, create_plugin_scaffold
from fnp_qnn_cli.qlc_mcp import qlc_gateway_submit_plan, qlc_status_inspect
from fnp_qnn_cli.registry import list_core_commands, run_core_command
from fnp_qnn_cli.support import provider_support_report


QLC_FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "qlc_contract"


def _qlc_mcp_bundle():
    mesh_payload = {
        "memories": [{"modality": "stimuli", "starting_time": 0.0, "ending_time": 1.0, "value": 0.7}],
        "label": 1.0,
        "epochs": 2,
        "run_qnn": True,
        "plugin_hook_enabled": True,
        "plugin_set": "mvp5",
        "plugin_context": {
            "sensitivity_weighted_obfuscation_policy": {
                "schema": "ffed.qlc.sensitivity_weighted_obfuscation_policy.v1",
                "media_type": "image",
                "sensitivity_level": "high",
            }
        },
    }


    return {
        "schema": "ffed.qlc.protection_workflow_bundle.v1",
        "contract_version": "qlc-wiring-contract.v2",
        "media_type": "image",
        "workflow_fingerprint": "wf-fp",
        "gateway_submission": {
            "schema": "ffed.qlc.gateway_submission.v1",
            "contract_version": "qlc-wiring-contract.v2",
            "workflow_fingerprint": "wf-fp",
            "target_endpoint": "POST /cerebrum/runtime/run",
            "route_action": "submit_to_cerebrum",
            "mesh_payload": mesh_payload,
            "mesh_payload_fingerprint": "mesh-fp",
            "raw_payload_embedded": False,
        },
    }


class CLITuiDoctorTests(unittest.TestCase):
    def test_direct_cli_status_json(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["--json", "status"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["success"])
        self.assertEqual(payload["type"], "cerebrum-runtime")

    def test_cerebrum_and_celebrum_commands_exist(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["--json", "celebrum", "clip"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["type"], "celebrum-ai-cli")
        self.assertEqual(payload["function_name"], "celebrum_clip_function")

    def test_auth_uses_fingerprint_only(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            old_home = os.environ.get(AUTH_HOME_ENV)
            os.environ[AUTH_HOME_ENV] = tmpdir
            try:
                auth = login("test-token", "unit")
                self.assertTrue(auth["authenticated"])
                self.assertEqual(auth["storage"], "fingerprint-only")
                self.assertTrue(validate_token("test-token")["success"])
                self.assertFalse(validate_token("wrong-token")["success"])
                self.assertNotIn("test-token", Path(tmpdir, "auth.json").read_text(encoding="utf-8"))
                self.assertTrue(logout()["success"])
                self.assertFalse(status()["authenticated"])
            finally:
                if old_home is None:
                    os.environ.pop(AUTH_HOME_ENV, None)
                else:
                    os.environ[AUTH_HOME_ENV] = old_home

    def test_skill_function_login_chatgpt_uses_fingerprint_only(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            old_home = os.environ.get(AUTH_HOME_ENV)
            os.environ[AUTH_HOME_ENV] = tmpdir
            try:
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["--json", "skill", "function", "login-chatgpt", "--token", "chatgpt-token"])
                self.assertEqual(exit_code, 0)
                payload = json.loads(stdout.getvalue())
                self.assertEqual(payload["function"], "login-chatgpt")
                self.assertFalse(payload["raw_token_stored"])
                self.assertNotIn("chatgpt-token", Path(tmpdir, "auth.json").read_text(encoding="utf-8"))
            finally:
                if old_home is None:
                    os.environ.pop(AUTH_HOME_ENV, None)
                else:
                    os.environ[AUTH_HOME_ENV] = old_home

    def test_provider_web_login_reports_official_flows_without_opening_browser(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["--json", "auth", "web-login", "openai"])
        self.assertEqual(exit_code, 0)
        openai_payload = json.loads(stdout.getvalue())
        self.assertEqual(openai_payload["provider"], "openai")
        self.assertIn("platform.openai.com", openai_payload["url"])
        self.assertFalse(openai_payload["opened_browser"])

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["--json", "auth", "web-login", "google"])
        self.assertEqual(exit_code, 0)
        google_payload = json.loads(stdout.getvalue())
        self.assertEqual(google_payload["provider"], "google")
        self.assertIn("aistudio.google.com", google_payload["url"])
        self.assertIn("gcloud auth application-default login", google_payload["gcloud_command"])

    def test_external_ai_inspects_openclaw_shape_without_secret_values(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            credentials = root / "credentials" / "auth-profiles"
            credentials.mkdir(parents=True)
            (credentials / "profile.json").write_text(
                json.dumps({"version": 1, "provider": "openai-codex", "encrypted": {"ciphertext": "secret"}}),
                encoding="utf-8",
            )
            (root / "openclaw.json").write_text(
                json.dumps(
                    {
                        "models": {
                            "providers": {
                                "openai-codex": {
                                    "api": "openai-codex-responses",
                                    "baseUrl": "https://chatgpt.com/backend-api/codex",
                                    "apiKey": "raw-secret",
                                    "models": [{"id": "gpt-test"}],
                                }
                            }
                        },
                        "agents": {
                            "defaults": {
                                "models": {
                                    "openai/gpt-test": {
                                        "agentRuntime": {"id": "codex"},
                                        "alias": "codex-test",
                                    }
                                }
                            }
                        },
                        "plugins": {"entries": {"codex": {"enabled": True}}},
                    }
                ),
                encoding="utf-8",
            )
            payload = inspect_openclaw(root)
            self.assertTrue(payload["success"])
            self.assertEqual(len(payload["credential_profiles"]), 1)
            self.assertIn("openai-codex", payload["providers"])
            self.assertEqual(payload["agent_runtimes"][0]["agentRuntime"], "codex")
            self.assertNotIn("raw-secret", json.dumps(payload))

    def test_external_ai_status_cli_returns_json(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["--json", "external-ai", "status"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["success"])
        self.assertIn("codex", payload)
        self.assertIn("openclaw", payload)

    def test_external_ai_lists_allowlisted_control_tasks(self):
        tasks = simulator_control_tasks()
        names = {item["name"] for item in tasks}
        self.assertIn("status", names)
        self.assertIn("runtime", names)
        self.assertIn("qnn", names)
        self.assertTrue(all("command" in item for item in tasks))

    def test_external_ai_control_dry_run_builds_agent_prompt(self):
        payload = control_simulator("status", tool="codex", execute=False, extra_prompt="unit-test")
        self.assertTrue(payload["success"])
        self.assertEqual(payload["task"], "status")
        self.assertEqual(payload["tool"], "codex")
        self.assertFalse(payload["execute"])
        self.assertIn("fnp_qnn_cli", payload["simulator_command_display"])
        self.assertIn("Run exactly this allowlisted simulator command", payload["prompt"])
        self.assertIn("unit-test", payload["prompt"])

    def test_external_ai_control_cli_returns_dry_run_json(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["--json", "external-ai", "control", "qnn", "--tool", "antigravity"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["task"], "qnn")
        self.assertEqual(payload["tool"], "antigravity")
        self.assertFalse(payload["execute"])
        self.assertIn("antigravity", payload["agent_command_display"])

    def test_function_login_google_ai_pro_uses_fingerprint_only(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            old_home = os.environ.get(AUTH_HOME_ENV)
            os.environ[AUTH_HOME_ENV] = tmpdir
            try:
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["--json", "function", "login-google-ai-pro", "--token", "google-token"])
                self.assertEqual(exit_code, 0)
                payload = json.loads(stdout.getvalue())
                self.assertEqual(payload["function"], "login-google-ai-pro")
                self.assertFalse(payload["raw_token_stored"])
                self.assertNotIn("google-token", Path(tmpdir, "auth.json").read_text(encoding="utf-8"))
            finally:
                if old_home is None:
                    os.environ.pop(AUTH_HOME_ENV, None)
                else:
                    os.environ[AUTH_HOME_ENV] = old_home

    def test_gateway_deepsearch_bridge_routes_antigravity_official(self):
        payload = gateway_deepsearch_skill(query="validate research", system="antigravity")
        self.assertTrue(payload["success"], payload)
        self.assertEqual(payload["search_route"]["route"], "antigravity-gemini-google-search")
        self.assertFalse(payload["search_route"]["fallback_used"])
        self.assertEqual(payload["simulator_gateway_block"]["entrypoint"], "fnp-qnn")
        self.assertFalse(payload["raw_secret_stored"])

    def test_gateway_deepsearch_candidate_loader_preserves_sys_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            package = Path(tmpdir) / "fnpqnn_gateway_mvp"
            package.mkdir()
            (package / "__init__.py").write_text("", encoding="utf-8")
            (package / "helper.py").write_text(
                "def route():\n    return 'candidate-route'\n",
                encoding="utf-8",
            )
            (package / "deepsearch_skill.py").write_text(
                "from .helper import route\n\n"
                "def build_deepsearch_skill(**kwargs):\n"
                "    return {'success': True, 'search_route': {'route': route()}, 'raw_secret_stored': False}\n\n"
                "def write_deepsearch_skill(payload, *, force=False):\n"
                "    return payload\n",
                encoding="utf-8",
            )
            before = list(sys.path)

            build, write = _load_deepsearch_from_candidate(Path(tmpdir))

            self.assertEqual(sys.path, before)
            self.assertEqual(build(query="x")["search_route"]["route"], "candidate-route")
            self.assertEqual(write({"ok": True}), {"ok": True})

    def test_gateway_deepsearch_cli_from_simulator(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "--json",
                    "gateway",
                    "deepsearch-skill",
                    "--query",
                    "validate research",
                    "--system",
                    "antigravity",
                    "--dry-run",
                ]
            )
        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["search_route"]["route"], "antigravity-gemini-google-search")
        self.assertEqual(payload["simulator_gateway_block"]["delegated_to"], "fnpqnn_gateway_mvp.deepsearch_skill")

    def test_function_deepsearch_cli_falls_back_for_docker(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "--json",
                    "function",
                    "deepsearch",
                    "--query",
                    "validate research",
                    "--system",
                    "docker",
                    "--dry-run",
                ]
            )
        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["search_route"]["fallback_used"])
        self.assertEqual(payload["search_route"]["route"], "antigravity-gemini-google-search")

    def test_skill_function_deepsearch_write_creates_gateway_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        "--json",
                        "skill",
                        "function",
                        "deepsearch",
                        "--query",
                        "validate research",
                        "--system",
                        "antigravity",
                        "--workspace",
                        tmpdir,
                        "--write",
                    ]
                )
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertTrue(Path(payload["paths"]["contract_json"]).exists())
            self.assertTrue(Path(payload["paths"]["contract_markdown"]).exists())
            self.assertFalse((Path(tmpdir) / ".env").exists())

    def test_celebrum_clip_redacts_secret_keys(self):
        payload = celebrum_clip_function({"token": "abc", "nested": {"api_key": "secret", "value": 1}})
        self.assertTrue(payload["success"])
        self.assertEqual(payload["sanitized_payload"]["token"], "[redacted]")
        self.assertEqual(payload["sanitized_payload"]["nested"]["api_key"], "[redacted]")
        self.assertEqual(payload["sanitized_payload"]["nested"]["value"], 1)

    def test_plugin_scaffold_creates_manifest_without_marketplace(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            payload = create_plugin_scaffold("CeLeBrUm CLI AI", tmpdir)
            self.assertTrue(payload["success"])
            self.assertFalse(payload["marketplace_updated"])
            manifest = Path(payload["manifest_path"])
            self.assertTrue(manifest.exists())
            data = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(data["name"], "celebrum-cli-ai")

    def test_ai_control_mcp_plugin_scaffold_creates_mcp_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            payload = create_ai_control_mcp_plugin(tmpdir)
            self.assertTrue(payload["success"])
            manifest = Path(payload["manifest_path"])
            mcp_path = Path(payload["mcp_path"])
            self.assertTrue(manifest.exists())
            self.assertTrue(mcp_path.exists())
            mcp = json.loads(mcp_path.read_text(encoding="utf-8"))
            server = mcp["mcpServers"]["fnp-qnn-ai-control"]
            self.assertIn("fnp_qnn_cli.mcp_server", server["args"])

    def test_mcp_provider_routing_requires_provider_auth(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            old_home = os.environ.get(AUTH_HOME_ENV)
            old_ignore_runtime = os.environ.get("FNP_QNN_MCP_IGNORE_RUNTIME_AUTH")
            os.environ[AUTH_HOME_ENV] = tmpdir
            os.environ["FNP_QNN_MCP_IGNORE_RUNTIME_AUTH"] = "1"
            try:
                unauth = mcp_control_simulator("openai", "status")
                self.assertFalse(unauth["success"])
                login("openai-token", "openai-unit", "openai")
                openai = provider_connection_status("chatgpt")
                self.assertTrue(openai["connected"])
                self.assertEqual(openai["tool"], "codex")
                control = mcp_control_simulator("openai", "status")
                self.assertTrue(control["success"])
                self.assertEqual(control["tool"], "codex")
                logout()
                login("google-token", "google-unit", "google")
                google = mcp_control_simulator("google", "qnn")
                self.assertTrue(google["success"])
                self.assertEqual(google["tool"], "antigravity")
                logout()
                with self.assertRaises(ValueError):
                    mcp_control_simulator("ollama", "status")
            finally:
                if old_home is None:
                    os.environ.pop(AUTH_HOME_ENV, None)
                else:
                    os.environ[AUTH_HOME_ENV] = old_home
                if old_ignore_runtime is None:
                    os.environ.pop("FNP_QNN_MCP_IGNORE_RUNTIME_AUTH", None)
                else:
                    os.environ["FNP_QNN_MCP_IGNORE_RUNTIME_AUTH"] = old_ignore_runtime

    def test_mcp_server_lists_tools(self):
        response = handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        self.assertEqual(response["id"], 1)
        names = {tool["name"] for tool in response["result"]["tools"]}
        self.assertIn("fnp_qnn_control_simulator", names)
        self.assertIn("fnp_qnn_provider_status", names)
        self.assertIn("fnp_qnn_wake_prompt", names)
        self.assertIn("qlc.workflow.build", names)
        self.assertIn("qlc.gateway.submit", names)
        self.assertIn("qlc.loop.receipt", names)
        self.assertIn("qlc.status.inspect", names)

    def test_mcp_qlc_tools_are_metadata_only(self):
        inspect_response = handle_request(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "qlc.status.inspect", "arguments": {"bundle": _qlc_mcp_bundle()}},
            }
        )
        payload = json.loads(inspect_response["result"]["content"][0]["text"])
        self.assertTrue(payload["success"])
        self.assertEqual(payload["swop_level"], "high")
        self.assertFalse(payload["raw_payload_embedded"])

        loop_response = handle_request(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "qlc.loop.receipt",
                    "arguments": {"bundle": _qlc_mcp_bundle(), "simulator_result": {"status": "ok", "runtime": {"feature_dimension": 4}}},
                },
            }
        )
        loop = json.loads(loop_response["result"]["content"][0]["text"])
        self.assertEqual(loop["schema"], "ffed.qlc.gateway_celebrum_loop_receipt.v1")
        self.assertIn("simulator_result", loop["fingerprints"])
        self.assertFalse(loop["raw_payload_embedded"])

    def test_mcp_qlc_status_accepts_shared_fixture(self):
        bundle = json.loads((QLC_FIXTURE_ROOT / "qlc_workflow_image.json").read_text(encoding="utf-8"))
        status = qlc_status_inspect(bundle)
        plan = qlc_gateway_submit_plan(bundle, simulator_url="http://localhost:8000", dry_run=True)

        self.assertTrue(status["success"])
        self.assertEqual(status["redaction_verdict"], "metadata_only_pass")
        self.assertEqual(status["swop_level"], "high")
        self.assertEqual(plan["status"]["mesh_payload_fingerprint"], "image-mesh-fingerprint")

    def test_mcp_qlc_status_rejects_shared_forbidden_fixture(self):
        bundle = json.loads((QLC_FIXTURE_ROOT / "qlc_workflow_forbidden_raw.json").read_text(encoding="utf-8"))

        with self.assertRaises(ValueError):
            qlc_status_inspect(bundle)

    def test_agent_profiles_explain_native_system_without_emulation(self):
        codex = agent_profile("chatgpt")
        self.assertEqual(codex["tool"], "codex")
        self.assertIn("native Codex", codex["interface"])
        gemini_prompt = wake_prompt("google", {"primary_goal": "Tune CLI"})
        self.assertIn("Antigravity", gemini_prompt)
        self.assertIn("FNP-QNN is a local alpha-local", gemini_prompt)
        self.assertIn("Tune CLI", gemini_prompt)
        with self.assertRaises(ValueError):
            wake_prompt("ollama")

    def test_onboarding_requires_approval_and_writes_context_files(self):
        with tempfile.TemporaryDirectory() as auth_tmp, tempfile.TemporaryDirectory() as repo_tmp:
            old_home = os.environ.get(AUTH_HOME_ENV)
            old_ignore_runtime = os.environ.get("FNP_QNN_MCP_IGNORE_RUNTIME_AUTH")
            os.environ[AUTH_HOME_ENV] = auth_tmp
            os.environ["FNP_QNN_MCP_IGNORE_RUNTIME_AUTH"] = "1"
            try:
                login("openai-token", "openai-unit", "openai")
                denied = apply_onboarding("openai", project_root=Path(repo_tmp))
                self.assertFalse(denied["success"])
                payload = apply_onboarding(
                    "openai",
                    approve_fingerprint=True,
                    overrides={"primary_goal": "Make the simulator fit my CLI workflow"},
                    project_root=Path(repo_tmp),
                )
                self.assertTrue(payload["success"])
                self.assertTrue(Path(payload["wiring_path"]).exists())
                self.assertTrue(Path(payload["wake_prompt_path"]).exists())
                self.assertIn("AGENTS.md", Path(payload["updated_files"][0]).name)
                self.assertIn("Make the simulator fit my CLI workflow", Path(payload["wake_prompt_path"]).read_text())
                self.assertIn("FNP-QNN-ONBOARDING-START", Path(repo_tmp, "AGENTS.md").read_text())
            finally:
                if old_home is None:
                    os.environ.pop(AUTH_HOME_ENV, None)
                else:
                    os.environ[AUTH_HOME_ENV] = old_home
                if old_ignore_runtime is None:
                    os.environ.pop("FNP_QNN_MCP_IGNORE_RUNTIME_AUTH", None)
                else:
                    os.environ["FNP_QNN_MCP_IGNORE_RUNTIME_AUTH"] = old_ignore_runtime

    def test_support_report_is_llm_safe_and_actionable(self):
        payload = provider_support_report("google")
        self.assertTrue(payload["success"])
        self.assertEqual(payload["provider"], "google")
        self.assertIn("next_steps", payload)
        self.assertFalse(payload["raw_token_stored"])
        self.assertIn("control_tasks", payload)
        self.assertNotIn("ollama-token", json.dumps(payload).lower())

    def test_support_all_cli_returns_provider_groups(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["--json", "support", "all"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        providers = {item["provider"] for item in payload["reports"]}
        self.assertEqual(providers, {"openai", "google"})
        self.assertIn("needs_action", payload)

    def test_doctor_payload_shape_without_service_probes(self):
        payload = run_doctor(full=False, probe_services=False)
        self.assertIn(payload["status"], {"pass", "warn", "fail"})
        self.assertIn("checks", payload)
        self.assertIn("totals", payload)
        self.assertTrue(any(check["name"] == "auth:fnp-qnn-cli" for check in payload["checks"]))

    def test_operator_builders_are_controlled(self):
        self.assertIn("uvicorn api.main:app", api_serve_command(8010).display())
        self.assertIn("panel serve panel_app.py", panel_serve_command(5010).display())
        self.assertIn("unittest discover", tests_command().display())
        self.assertIn("validate_alpha_readiness.py", alpha_command().display())

    def test_core_registry_lists_and_runs_default_profile(self):
        commands = list_core_commands()
        self.assertTrue(any(item["name"] == "normalize-df" for item in commands))
        payload = run_core_command("normalize-df", {"D_f": 1.5, "D_min": 1.0, "D_max": 2.0})
        self.assertTrue(payload["success"])
        self.assertEqual(payload["data"]["D_f_hat"], 0.5)

    def test_cloud_kit_status_cli_is_secret_safe(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["--json", "cloud-kit", "status"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["success"])
        self.assertIn("e2b", payload["data"])
        self.assertFalse(payload["data"]["e2b"]["api_key_value_printed"])

    def test_cloud_kit_e2b_plan_cli(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "--json",
                    "cloud-kit",
                    "e2b-ingest-plan",
                    "--source",
                    "https://example.com/data.csv",
                    "--title",
                    "External data",
                    "--tool-route",
                    "codex",
                ]
            )
        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["provider"], "e2b")
        self.assertFalse(payload["raw_secret_stored"])
        self.assertIn("E2B_API_KEY", payload["confirmed_source_behavior"]["api_key"])

    def test_ffed_p114_consensus_cli(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "--json",
                    "ffed",
                    "p114-consensus",
                    "--item",
                    "verified evidence passed with implementation proof",
                    "--item",
                    "partial risk remains pending",
                ]
            )
        payload = json.loads(stdout.getvalue())
        if payload["status"] == "disabled":
            self.skipTest(payload["metadata"].get("message", "p114 pluginpack disabled"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["plugin_id"], "p114_ffed_neutrosophic_consensus")
        self.assertIn("consensus", payload)
        self.assertIn("cli_gate", payload)

    def test_tui_retro_82_hidden_flash(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["--json", "tui", "--retro-82"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["type"], "operator-easter-egg")
        self.assertEqual(payload["year"], 1982)
        self.assertIn("RETRO 82", payload["output"])
        self.assertIn("trademark_boundary", payload)

    def test_tui_uses_requested_ascii_logo_assets(self):
        from fnp_qnn_cli.tui import (
            BRAND_FACTS,
            LOGO_ASSETS,
            bottom_logo_terminal,
            logo_asset_path,
            main_logo_terminal,
            top_logo_terminal,
        )

        self.assertEqual(LOGO_ASSETS["main_big"], "assets/logo/ASCII full logo.png")
        self.assertEqual(LOGO_ASSETS["top_small"], "assets/logo/ASCII logo 1.png")
        self.assertEqual(LOGO_ASSETS["bottom_center"], "assets/logo/ASCII logo 5.png")
        for name in ("main_big", "top_small", "bottom_center"):
            self.assertTrue(logo_asset_path(name).exists(), name)
            self.assertIn(LOGO_ASSETS[name], BRAND_FACTS["palette_source"])
        self.assertGreater(len(main_logo_terminal().strip()), 200)
        self.assertGreater(len(top_logo_terminal().strip()), 50)
        self.assertGreater(len(bottom_logo_terminal().strip()), 50)

    def test_cloud_kit_rag_runtime_cli_feeds_lvfm(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "--json",
                    "cloud-kit",
                    "rag-runtime",
                    "--title",
                    "Gateway RAG summary",
                    "--source",
                    "e2b://sandbox/result",
                    "--tool-route",
                    "openclaw",
                    "--content",
                    "Small admitted RAG note for LVFM.",
                    "--tag",
                    "lvfm",
                ]
            )
        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["type"], "cloud-rag")
        self.assertEqual(payload["runtime_payload"]["memories"][0]["provenance"]["bridge"], "cloud-rag-to-lvfm")
        self.assertIn("p114_consensus", payload)
        self.assertIn("p114_gate", payload["runtime_payload"]["memories"][0]["provenance"])
        self.assertIn("lvfm", payload["runtime"]["data"])

    def test_tui_constructs_when_textual_is_available(self):
        try:
            from fnp_qnn_cli.tui import create_app

            app = create_app()
        except Exception as exc:
            if exc.__class__.__name__ == "TextualUnavailable":
                self.skipTest("Textual is not installed in the current environment")
            raise
        self.assertEqual(app.TITLE, "FNP-QNN Control Terminal")


if __name__ == "__main__":
    unittest.main()
