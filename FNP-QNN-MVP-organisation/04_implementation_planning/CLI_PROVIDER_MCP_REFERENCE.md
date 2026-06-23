# CLI Provider MCP Reference

Date: 2026-06-23

This document is the operator reference for the provider-aware FNP-QNN CLI and
MCP plugin.

## Principle

The simulator and the AI adapter are separate.

Simulator-only commands:

```powershell
fnp-qnn status
fnp-qnn runtime run --epochs 2
fnp-qnn qnn smoke --epochs 2 --test-size 0
fnp-qnn neurobit gates --truth 0.5
fnp-qnn doctor --full --no-probe-services
```

These commands do not require Codex, Antigravity, Ollama Cloud, OpenClaw, MCP,
or provider login.

## Provider Matrix

| Provider option | Tool/interface | Connection signal | Native assets |
| --- | --- | --- | --- |
| `openai` / `chatgpt` | Codex | Codex login status or OpenAI fingerprint | Codex skills, plugins, MCP, repo tools |
| `google` / `gemini` | Antigravity/Gemini | Google ADC or Google fingerprint | Antigravity/Gemini tools and integrations |
| `ollama` | Ollama Cloud/OpenClaw | `OLLAMA_API_KEY` or Ollama fingerprint | Ollama models, OpenClaw plugins/MCP/runtimes |

FNP-QNN does not import those native assets. It gives the selected agent a wake
prompt and MCP tools so the agent can use its own original system.

## Login Commands

Open provider page or native CLI login:

```powershell
fnp-qnn auth web-login openai --open
fnp-qnn auth web-login google --open
fnp-qnn auth web-login google --run-gcloud
fnp-qnn auth web-login ollama --open
fnp-qnn auth web-login ollama --run-ollama
```

Store local fingerprint only:

```powershell
fnp-qnn auth login-provider openai --token <openai-token>
fnp-qnn auth login-provider google --token <google-token>
fnp-qnn auth login-provider ollama --token <ollama-token>
```

Check local auth:

```powershell
fnp-qnn auth status
fnp-qnn auth check --token <token>
fnp-qnn auth logout
```

The raw token is not stored. The auth file stores a SHA-256 fingerprint and a
short preview.

## External Runtime Inspection

```powershell
fnp-qnn external-ai status
fnp-qnn external-ai inspect-openclaw
fnp-qnn external-ai connect codex --device-auth
fnp-qnn external-ai connect codex --api-key-env OPENAI_API_KEY
fnp-qnn external-ai connect antigravity
fnp-qnn external-ai connect ollama
```

`inspect-openclaw` reads shape only. It must not print decrypted credentials,
tokens, cookies, or API keys.

## LLM Support Diagnostics

Before debugging provider-specific behavior, generate a support report:

```powershell
fnp-qnn support all
fnp-qnn support provider openai
fnp-qnn support provider google
fnp-qnn support provider ollama
```

The support report is designed for LLM-assisted troubleshooting. It reports
provider readiness, missing tools, next steps, native asset policy, wake prompt
preview, and allowlisted control tasks without exposing raw secrets.

## MCP Plugin

Create or refresh the local plugin:

```powershell
fnp-qnn plugin create-ai-control-mcp --force
```

Generated plugin path:

```text
plugins/fnp-qnn-ai-control-mcp
```

Generated files:

```text
plugins/fnp-qnn-ai-control-mcp/.codex-plugin/plugin.json
plugins/fnp-qnn-ai-control-mcp/.mcp.json
plugins/fnp-qnn-ai-control-mcp/scripts/run_mcp_server.py
plugins/fnp-qnn-ai-control-mcp/README.md
```

Validate:

```powershell
python C:\Users\jeans\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py .\plugins\fnp-qnn-ai-control-mcp
```

## MCP Tools

The MCP server exposes:

- `fnp_qnn_provider_status`
- `fnp_qnn_control_simulator`
- `fnp_qnn_control_tasks`
- `fnp_qnn_onboarding_questions`
- `fnp_qnn_onboard_user`
- `fnp_qnn_agent_profile`
- `fnp_qnn_wake_prompt`

Direct CLI equivalents:

```powershell
fnp-qnn mcp manifest
fnp-qnn mcp provider-status openai
fnp-qnn mcp provider-status google
fnp-qnn mcp provider-status ollama
fnp-qnn mcp control openai status
fnp-qnn mcp control google qnn
fnp-qnn mcp control ollama status
fnp-qnn mcp serve
```

## Agent Wake Prompts

Preview profile:

```powershell
fnp-qnn agent profile openai
fnp-qnn agent profile google
fnp-qnn agent profile ollama
```

Preview wake prompt:

```powershell
fnp-qnn agent wake-prompt openai
fnp-qnn agent wake-prompt google
fnp-qnn agent wake-prompt ollama
```

Wake prompts are provider-specific. They are not interchangeable.

## Onboarding

Show questions:

```powershell
fnp-qnn onboarding questions
```

Apply default onboarding:

```powershell
fnp-qnn onboarding apply openai --approve-fingerprint
fnp-qnn onboarding apply google --approve-fingerprint
fnp-qnn onboarding apply ollama --approve-fingerprint
```

Apply onboarding with inline answers:

```powershell
fnp-qnn onboarding apply openai --approve-fingerprint `
  --primary-goal "Tune the CLI for my workflow" `
  --preferred-workflow "TUI first, dry-run before execute" `
  --success-signal "Tests and alpha gate pass"
```

Delegate after onboarding:

```powershell
fnp-qnn onboarding apply openai --approve-fingerprint --delegate
fnp-qnn onboarding apply google --approve-fingerprint --delegate
fnp-qnn onboarding apply ollama --approve-fingerprint --delegate
```

Execute delegate only when ready:

```powershell
fnp-qnn onboarding apply openai --approve-fingerprint --delegate --execute-delegate
```

## External Control

List tasks:

```powershell
fnp-qnn external-ai control-tasks
```

Dry-run control:

```powershell
fnp-qnn external-ai control status --tool auto
fnp-qnn external-ai control qnn --tool codex
fnp-qnn external-ai control runtime --tool antigravity
fnp-qnn external-ai control status --tool ollama
```

Execute control:

```powershell
fnp-qnn external-ai control validate --tool codex --execute
fnp-qnn external-ai control qnn --tool antigravity --execute
fnp-qnn external-ai control status --tool ollama --execute
```

## Required Validation

After changes to the CLI/MCP/onboarding lane:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_cli_tui_doctor
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
.\.venv\Scripts\python.exe scripts\validate_alpha_readiness.py
python C:\Users\jeans\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py .\plugins\fnp-qnn-ai-control-mcp
```
