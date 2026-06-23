# CLI Auth Onboarding User Story

Date: 2026-06-23

Scope: FNP-QNN CLI/TUI, provider login, MCP plugin, onboarding, and external agent handoff.

## Product Boundary

FNP-QNN remains a local alpha-local, non-clinical research simulator. Its base
commands must work without Codex, Antigravity, Ollama Cloud, OpenClaw, MCP, or
any external AI account.

External systems are optional adapters:

- OpenAI/ChatGPT account -> Codex interface and native Codex plugins/skills.
- Google/Gemini account -> Antigravity/Gemini interface and native Google-side tools.
- Ollama Cloud account -> Ollama CLI/cloud models and optional OpenClaw runtime.

The simulator does not copy, emulate, or flatten those native plugin systems.
It only generates context, prompts, and MCP calls that place the chosen agent in
its own native environment.

## Primary User Story

As a simulator user, I want to connect one of my existing AI accounts, approve a
local fingerprint, answer directed onboarding questions, and have the selected
agent understand my goals, my interface, and the FNP-QNN simulator boundary, so
that the agent can help wire the simulator to my actual use case without making
the simulator itself dependent on AI logic.

## Natural Login Flow

1. User opens the provider login helper:

```powershell
fnp-qnn auth web-login openai --open
fnp-qnn auth web-login google --open
fnp-qnn auth web-login ollama --open
fnp-qnn auth web-login ollama --run-ollama
```

2. User stores a provider fingerprint after approving the provider identity:

```powershell
fnp-qnn auth login-provider openai --token <openai-api-key>
fnp-qnn auth login-provider google --token <gemini-api-key>
fnp-qnn auth login-provider ollama --token <ollama-api-key>
```

3. User checks provider status:

```powershell
fnp-qnn mcp provider-status openai
fnp-qnn mcp provider-status google
fnp-qnn mcp provider-status ollama
```

4. User reviews onboarding questions:

```powershell
fnp-qnn onboarding questions
```

5. User applies onboarding after explicit fingerprint approval:

```powershell
fnp-qnn onboarding apply openai --approve-fingerprint
fnp-qnn onboarding apply google --approve-fingerprint
fnp-qnn onboarding apply ollama --approve-fingerprint
```

6. User optionally delegates a narrow wiring task to the chosen native agent:

```powershell
fnp-qnn onboarding apply openai --approve-fingerprint --delegate
fnp-qnn onboarding apply google --approve-fingerprint --delegate
fnp-qnn onboarding apply ollama --approve-fingerprint --delegate
```

`--execute-delegate` is the explicit control point that actually lets the
selected external agent run.

## Directed Questions

The onboarding question set shapes `AGENTS.md`, `SOUL.md`, `USER.md`,
`MEMORY.md`, and `config/user_wiring.json`.

Required dimensions:

- `primary_goal`: what the simulator should help the user do first.
- `audience`: who the simulator is for.
- `preferred_workflow`: how the CLI/TUI should feel.
- `data_boundary`: safety and data constraints.
- `agent_role`: what the selected agent should do after onboarding.
- `ui_preference`: preferred terminal/interface style.
- `success_signal`: how done should be measured.

## Generated Files

Onboarding writes:

- `config/user_wiring.json`
- `config/agent_wake_prompt_openai.md`
- `config/agent_wake_prompt_google.md`
- `config/agent_wake_prompt_ollama.md`
- managed onboarding blocks in `AGENTS.md`
- managed onboarding blocks in `SOUL.md`
- managed onboarding blocks in `USER.md`
- managed onboarding blocks in `MEMORY.md`

The managed blocks are idempotent and bounded by:

```text
<!-- FNP-QNN-ONBOARDING-START -->
<!-- FNP-QNN-ONBOARDING-END -->
```

## Wake Prompt Requirement

Each provider gets a different wake prompt:

- Codex: explains Codex CLI/app context and native Codex plugins/skills.
- Antigravity/Gemini: explains Google-side agent context and native tools.
- Ollama/OpenClaw: explains Ollama CLI/cloud model context and optional OpenClaw runtime.

All wake prompts must state:

- what FNP-QNN is;
- what FNP-QNN is not;
- which native interface the agent is using;
- that native plugins/skills remain in the original system;
- that simulator base functions must work without AI;
- that the boundary is non-clinical and alpha-local;
- that `I -> I_system^S -> D_f -> dF -> i_fractal` must be preserved.

## Acceptance Criteria

- Base commands such as `status`, `qnn smoke`, `runtime run`, and `doctor` work
  without provider login.
- Provider login stores only a SHA-256 fingerprint when using
  `auth login-provider`.
- The MCP bridge refuses provider-controlled actions when no accepted connection
  signal exists.
- `onboarding apply` refuses to write context without `--approve-fingerprint`.
- Onboarding writes the four context files plus `config/user_wiring.json`.
- Agent delegation remains dry-run unless `--execute-delegate` is provided.
- External agent prompts never imply that Codex, Antigravity, Ollama, or OpenClaw
  are the same system.
