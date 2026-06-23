import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from fnp_qnn_cli.agent_profiles import agent_profile, wake_prompt
from fnp_qnn_cli.auth import AUTH_HOME_ENV, login, logout, status, validate_token
from fnp_qnn_cli.celebrum import celebrum_clip_function
from fnp_qnn_cli.doctor import run_doctor
from fnp_qnn_cli.external_ai import control_simulator, inspect_openclaw, simulator_control_tasks
from fnp_qnn_cli.mcp_bridge import mcp_control_simulator, provider_connection_status
from fnp_qnn_cli.mcp_server import handle_request
from fnp_qnn_cli.main import main
from fnp_qnn_cli.onboarding import apply_onboarding
from fnp_qnn_cli.operator import alpha_command, api_serve_command, panel_serve_command, tests_command
from fnp_qnn_cli.plugin_creator import create_ai_control_mcp_plugin, create_plugin_scaffold
from fnp_qnn_cli.registry import list_core_commands, run_core_command
from fnp_qnn_cli.support import provider_support_report


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
                login("ollama-token", "ollama-unit", "ollama")
                ollama = mcp_control_simulator("ollama", "status")
                self.assertTrue(ollama["success"])
                self.assertEqual(ollama["tool"], "ollama")
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

    def test_agent_profiles_explain_native_system_without_emulation(self):
        codex = agent_profile("chatgpt")
        self.assertEqual(codex["tool"], "codex")
        self.assertIn("native Codex", codex["interface"])
        gemini_prompt = wake_prompt("google", {"primary_goal": "Tune CLI"})
        self.assertIn("Antigravity", gemini_prompt)
        self.assertIn("FNP-QNN is a local alpha-local", gemini_prompt)
        self.assertIn("Tune CLI", gemini_prompt)
        ollama_prompt = wake_prompt("ollama")
        self.assertIn("Ollama Cloud / OpenClaw", ollama_prompt)
        self.assertIn("does not copy or emulate", ollama_prompt)

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
        payload = provider_support_report("ollama")
        self.assertTrue(payload["success"])
        self.assertEqual(payload["provider"], "ollama")
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
        self.assertEqual(providers, {"openai", "google", "ollama"})
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
