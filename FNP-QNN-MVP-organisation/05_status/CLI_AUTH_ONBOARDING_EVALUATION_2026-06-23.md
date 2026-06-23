# CLI Auth Onboarding Evaluation — 2026-06-23

Repository: `C:\Users\jeans\Desktop\Case study\modele\FNP-QNN-MVP\FNP-QNN-MVP`

## Evaluated Sequence

The evaluated user sequence is:

1. User selects a provider: ChatGPT/OpenAI, Google/Gemini, or Ollama Cloud/OpenClaw.
2. CLI opens or runs the provider-specific login helper.
3. User approves local fingerprint storage.
4. CLI checks provider connection status.
5. CLI runs directed onboarding questions.
6. Onboarding writes simulator context:
   - `AGENTS.md`
   - `SOUL.md`
   - `USER.md`
   - `MEMORY.md`
   - `config/user_wiring.json`
   - `config/agent_wake_prompt_<provider>.md`
7. Selected agent receives a provider-specific wake prompt.
8. Optional delegation routes to the provider's native system.

## Result

The sequence is coherent if and only if the simulator keeps three layers separate:

- simulator core: Python commands, deterministic local behavior, no AI dependency;
- adapter layer: auth, provider status, MCP, external control, wake prompts;
- native agent layer: Codex, Antigravity/Gemini, or Ollama/OpenClaw.

This separation is now reflected in the implementation and docs.

## Provider-Specific Evaluation

### OpenAI / ChatGPT / Codex

Natural login path:

```powershell
fnp-qnn auth web-login openai --open
fnp-qnn external-ai connect codex --device-auth
fnp-qnn auth login-provider openai --token <openai-api-key>
```

Operational route:

```text
openai/chatgpt -> codex
```

Wake prompt requirement:

- place the agent inside Codex;
- tell it to use native Codex skills/plugins/MCP if enabled;
- do not imply Antigravity or Ollama capabilities;
- keep repo edits narrow and validation-driven.

### Google / Gemini / Antigravity

Natural login path:

```powershell
fnp-qnn auth web-login google --open
fnp-qnn auth web-login google --run-gcloud
fnp-qnn auth login-provider google --token <gemini-api-key>
```

Operational route:

```text
google/gemini -> antigravity
```

Wake prompt requirement:

- place the agent inside Antigravity/Gemini;
- tell it to use native Google-side tools already enabled by the user;
- do not assume Codex plugins are available;
- keep FNP-QNN as the local simulator target.

### Ollama Cloud / OpenClaw

Natural login path:

```powershell
fnp-qnn auth web-login ollama --open
fnp-qnn auth web-login ollama --run-ollama
fnp-qnn auth login-provider ollama --token <ollama-api-key>
```

Operational route:

```text
ollama -> ollama CLI/cloud model, optionally OpenClaw
```

Wake prompt requirement:

- place the agent in Ollama Cloud/OpenClaw context;
- use Ollama/OpenClaw native models/plugins/MCP/runtimes if configured;
- require `OLLAMA_API_KEY` or provider fingerprint for cloud authorization;
- do not treat CLI presence alone as cloud login proof.

## Security And Data Handling

Accepted:

- local fingerprint storage only;
- redacted OpenClaw inspection;
- explicit `--approve-fingerprint`;
- dry-run default for external control;
- explicit `--execute` and `--execute-delegate`;
- provider-specific wake prompts.

Rejected:

- storing raw tokens;
- scraping ChatGPT web cookies;
- assuming all agent systems share the same plugins;
- making simulator commands depend on AI;
- broad auto-editing after login.

## User Story Fit

The flow now supports the intended user story:

```text
Login naturally with one provider, approve a local fingerprint, answer directed
questions, generate context files, wake the selected native agent, and let that
agent wire the simulator only when explicitly delegated.
```

## Current Implementation Evidence

Core files added or updated:

- `fnp_qnn_cli/auth.py`
- `fnp_qnn_cli/external_ai.py`
- `fnp_qnn_cli/mcp_bridge.py`
- `fnp_qnn_cli/mcp_server.py`
- `fnp_qnn_cli/onboarding.py`
- `fnp_qnn_cli/agent_profiles.py`
- `fnp_qnn_cli/simulator_control.py`
- `fnp_qnn_cli/plugin_creator.py`
- `plugins/fnp-qnn-ai-control-mcp/`

Docs added:

- `FNP-QNN-MVP-organisation/04_implementation_planning/CLI_AUTH_ONBOARDING_USER_STORY.md`
- `FNP-QNN-MVP-organisation/04_implementation_planning/CLI_PROVIDER_MCP_REFERENCE.md`
- `FNP-QNN-MVP-organisation/05_status/CLI_AUTH_ONBOARDING_EVALUATION_2026-06-23.md`

## Acceptance Status

- Simulator functions remain callable without AI: accepted.
- Provider route exists for OpenAI/Codex: accepted.
- Provider route exists for Google/Antigravity: accepted.
- Provider route exists for Ollama/OpenClaw: accepted.
- Onboarding requires fingerprint approval: accepted.
- Wake prompts are provider-specific: accepted.
- MCP exposes provider status, control, onboarding, profile, and wake prompt tools: accepted.
- Plugin manifest validates: accepted after manifest shape correction.

## Residual Risks

- Antigravity CLI behavior may differ by installation; dry-run and explicit execute remain required.
- Ollama Cloud model availability depends on the user's Ollama account and selected model.
- OpenClaw plugin/runtime availability depends on the user's `~/.openclaw` configuration.
- Onboarding writes managed blocks into repo files; users should review diffs before commit.

## Recommended Next Check

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
.\.venv\Scripts\python.exe scripts\validate_alpha_readiness.py
python C:\Users\jeans\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py .\plugins\fnp-qnn-ai-control-mcp
```
